#!py -3
import sys
import os
import sqlite3
from configparser import ConfigParser

from tkinter import filedialog
from dateutil import parser
import math

CONFIG = "config.ini"

class ParsedReplay:
    def __init__(self):
        self.version = 0
        self.amplified = True
        self.amplified_full = True
        self.folder = ""
        self.file = ""
        self.run_date = ""
        self.run_type = 0
        self.f_run_type = ""
        self.char = 0
        self.f_char = ""
        self.seed = 0
        self.songs = 0
        self.end_zone = -1
        self.f_end_zone = ""
        self.run_time = 0
        self.f_run_time = ""
        self.win = False
        self.bugged = False
        self.bugged_reason = ""

    def __str__(self):
        return("Date: {}, Seed: {}, Char: {}, Type: {}, EndZone: {}, RunTime: {}".format(
            self.run_date, 
            self.seed, 
            self.f_char, 
            self.f_run_type, 
            self.f_end_zone,
            self.f_run_time
            ))
   

def setup_database(db):
    try:
        conn = sqlite3.connect(db)
        
        bugged = """
            CREATE TABLE IF NOT EXISTS bugged (
            run_id        INTEGER REFERENCES run (run_id),
            bugged_reason TEXT,
            bugged_data   TEXT,
            PRIMARY KEY (
                run_id,
                bugged_reason
            )
            ON CONFLICT ABORT
        );
        """

        run = """
            CREATE TABLE IF NOT EXISTS run (
            run_id        INTEGER,
            file          TEXT,
            version       INTEGER,
            run_date      INTEGER,
            type          TEXT,
            time          INT,
            fromated_time TEXT,
            seed          INT,
            players       INT,
            char1         TEXT,
            char2         TEXT,
            songs         INT,
            end_zone      TEXT,
            finished      INTEGER,
            killed_by     TEXT,
            score         INTEGER,
            imported_date INTEGER,
            PRIMARY KEY (
                run_id
            )
            ON CONFLICT ABORT
        );
        """


        run_tag = """
            CREATE TABLE IF NOT EXISTS run_tag (
            run_id INTEGER REFERENCES run (run_id),
            tag_id INTEGER REFERENCES tag (tag_id),
            PRIMARY KEY (
                run_id,
                tag_id
            )
            ON CONFLICT ABORT
        );


        """

        tag = """
            CREATE TABLE IF NOT EXISTS tag (
            tag_id INTEGER,
            name   TEXT,
            color  TEXT,
            PRIMARY KEY (
                tag_id
            )
            ON CONFLICT ABORT
        );
        """
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        test = c.fetchall()
        if len(test) < 1:
            print("Creating new DB")
            c = conn.cursor()
            c.execute(run)
            c.execute(tag)
            c.execute(bugged)
            c.execute(run_tag)

        return conn
    except Exception as e:
        print("Error: {}".format(e))

def setup_replay_folder(r_folder, config):
    if not os.path.exists(r_folder):
        try:
            print("Getting replay folder")
            folder = filedialog.askdirectory()
            config.set('DEFAULT', 'REPLAY_FOLDER', folder)
            with open(CONFIG, 'w') as cfg:
                config.write(cfg)
            return folder
        except Exception as e:
            print("Could not open folder: {}".format(e))
    else:
        return r_folder

def get_files(replays):
    try:
        files = os.listdir(replays)
        return files
    except Exception as e:
        print("Could not get replay files: {}".format(e))

def get_char_name(c):
    switcher = {
        0: "Cadence",
        1: "Melody",
        2: "Aria",
        3: "Dorian", # Dad
        4: "Eli", # Best
        5: "Monk", # Bad
        6: "Dove", 
        7: "Coda",
        8: "Bolt",
        9: "Bard",
        10: "Nocturna",
        11: "Diamond",
        12: "Mary",
        13: "Tempo"
    }
    return switcher.get(c, "Unknown")

def get_type_name(t):
    t = int(t)
    switcher = {
        1: "Zone 1",
        2: "Zone 2",
        3: "Zone 3",
        4: "Zone 4",
        5: "Zone 5",
        6: "All-Zones",
        7: "Daily",
        8: "Seeded All-Zones",
        -7: "All-Zones",
        -8: "Dance Pad",
        -9: "Daily",
        -10: "Seeded All-Zones",
        -50: "Story Mode",
        -52: "No Return",
        -53: "Seeded No Return",
        -55: "Hard Mode",
        -56: "Seeded Hard Mode",
        -59: "Phasing",
        -60: "Randomizer",
        -61: "Mystery",
        -62: "Seeded Phasing",
        -63: "Seeded Randomizer",
        -64: "Seeded Mystery"
    }
    
    return switcher.get(t, "Unknown")

def get_end_zone(songs, char, t, replay):
    if not replay.amplified_full:
        print("Too lazy to code non-amplified full release")
        replay.bugged = True
        replay.bugged_reason = "Too lazy to code for non-amplified full release"
        return replay
    zones = 5
    if char in [0, 1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13]:
        zone = t if t < 5 and t > 0 else math.floor(((songs - 1) / 4) + 1)
        floor = ((songs - 1) % 4) + 1
        if char == 2 and (t >= zones+1 or t < 5):
            zone = (zones + 1) - zone
        if zone > zones:
            if zone > zones + 1 or floor > 2:
                replay.bugged, replay.bugged_reason = True, "Number of songs is bugged: {}".format(songs)
            zone = zones
            floor = 5
        elif zone < 1: # Aria
            replay.bugged, replay.bugged_reason = True, "Number of songs is bugged: {}".format(songs)
            zone = 1
            floor = 4
        replay.end_zone = {'zone': zone, 'floor': floor}
        replay.f_end_zone = "{}-{}".format(zone, floor)
    elif char in [6]: # Dove
        zone = t if t < zones + 1 and t > 0 else math.floor(((songs - 1)/3) + 1)
        floor = ((songs - 1) % 3) + 1
        replay.end_zone = {'zone': zone, 'floor': floor}
        replay.f_end_zone = "{}-{}".format(zone, floor)
    
    return(replay)

def get_time_from_replay(ms_time):
    
    if ms_time < 0:
        return "00:00:00.000"
    millis = int(((ms_time/1000)%1)*100)
    seconds = math.floor((ms_time/1000)%60)
    minutes = math.floor((ms_time/(1000*60))%60)
    hours = math.floor((ms_time/(1000*60*60))%24
    time_to_return = ""
    time_to_return += '{:>02}:'.format(str(hours)) if hours > 0 else "00:"
    time_to_return += '{:>02}:'.format(str(minutes)) if minutes > 0 else "00:"
    time_to_return += '{:>02}.'.format(str(seconds)) if seconds > 0 else "00."
    time_to_return += '{:>03}'.format(str(millis)) if millis > 0 else "000"

    return time_to_return

def calculate_seed(zone_1_seed, amplified):
    #seed.add(0x40005e47).times(0xd6ee52a).mod(0x7fffffff).mod(0x713cee3f);
    add1 = int("0x40005e47", 16)
    mult1 = int("0xd6ee52a", 16)
    mod1 = int("0x7fffffff", 16)
    mod2 = int("0x713cee3f", 16)

    if amplified:
        zone_1_seed += add1
        zone_1_seed *= mult1
        zone_1_seed %= mod1
        seed = zone_1_seed % mod2
        #print("Seed: {}".format(seed))
        return seed
    else: 
        print("Not calculating this seed: {}".format(zone_1_seed))

def parse_files(r_folder, r_files):
    for r_f in r_files:
        try:
            p_file = ParsedReplay()
            print("Parsing: \"{}/{}\"".format(r_folder, r_f))
            split_name = r_f.split(".")[0].split("_")
            with open("{}/{}".format(r_folder, r_f)) as r:
                data = r.read()
            split_data = data.split("\\n")
            version = int(split_name[0])
            amp = True if version > 75 else False
            amp_full = True if version > 84 else False
            dt = "{} {}".format("/".join(split_name[3:6:]), ":".join(split_name[6:9]))
            t = int(split_name[9])
            coop = True if int(split_data[8]) > 1 else False
            char = int(split_data[12].split("|")[0])
            seed = int(split_data[7])
            songs = int(int(split_data[6]))
            run_time = int(split_data[5])
            if not coop:
                p_file.version = version
                p_file.amplified = amp
                p_file.amplified_full = amp_full 
                p_file.folder = r_folder
                p_file.file = r_f
                p_file.run_date = parser.parse(dt)
                p_file.run_type = t 
                p_file.f_run_type = get_type_name(t)
                p_file.char = char
                p_file.f_char = get_char_name(char)
                p_file.seed = calculate_seed(seed, amp)
                p_file.songs = songs
                p_file.run_time = run_time
                p_file.f_run_time = get_time_from_replay(run_time)
                p_file = get_end_zone(songs, char, t, p_file)                        
                print(p_file)
            else:
                print("Too lazy to code in co-op runs")

        except Exception as e:
            print("Couldn't parse file: {} -> {}".format(r_f, e))

        

def main():
    config = ConfigParser()
    config.read(CONFIG)
    dbfile = config.get('DEFAULT', 'DATABASE_FILE')
    replay_folder = config.get('DEFAULT', 'REPLAY_FOLDER')
    
    db = setup_database(dbfile)

    replay_folder = setup_replay_folder(replay_folder, config)
    replay_files = get_files(replay_folder)

    parse_files(replay_folder, replay_files)

if __name__ == "__main__":
    sys.exit(main())