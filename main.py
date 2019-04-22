#!py -3
import math
import os
import sqlite3
import sys
from configparser import ConfigParser
from tkinter import filedialog

from dateutil import parser

CONFIG = "config.ini"

# ParsedReplay holds all needed information about each run that has been parsed
class ParsedReplay:
    def __init__(self):
        self.version = 0
        self.amplified = True
        self.amplified_full = True
        self.folder = ""
        self.file = ""
        self.f_hash = 0
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
        self.key_presses = 0
        self.win = False
        self.bugged = False
        self.bugged_reason = ""

    # A simple way to output useful data when debugging :)
    def __str__(self):
        return("Date: {}, Seed: {}, Char: {}, Type: {}, EndZone: {}, RunTime: {}, KeyPresses: {}".format(
            self.run_date,
            self.seed,
            self.f_char,
            self.f_run_type,
            self.f_end_zone,
            self.f_run_time,
            self.key_presses
        ))

# This function setups up the database if it doesn't exist
def setup_database(db):
    try:
        conn = sqlite3.connect(db)

        bugged = """
            CREATE TABLE IF NOT EXISTS bugged (
            id            INTEGER PRIMARY KEY ASC ON CONFLICT ABORT AUTOINCREMENT NOT NULL ON CONFLICT ABORT UNIQUE ON CONFLICT ABORT,
            run_id        INTEGER REFERENCES run (run_id),
            bugged_reason TEXT,
            bugged_data   TEXT
        );
        """

        run = """
            CREATE TABLE IF NOT EXISTS run (
            id             INTEGER  PRIMARY KEY ASC ON CONFLICT ABORT AUTOINCREMENT NOT NULL ON CONFLICT ABORT UNIQUE ON CONFLICT ABORT,
            version        INTEGER,
            amplified      INTEGER,
            amplified_full INTEGER,
            folder         TEXT,
            file           TEXT,
            hash           INTEGER,
            run_date       INTEGER,
            f_run_date     INTEGER
            run_type       INTEGER,
            f_run_type     TEXT,
            time           INTEGER,
            f_time         TEXT,
            seed           INTEGER,
            songs          INTEGER,
            end_zone       TEXT,
            run_time       INTEGER,
            f_run_time     TEXT,
            players        INTEGER,
            char1          INTEGER,
            win            INTEGER,
            killed_by      INTEGER,
            f_killed_by    TEXT,
            key_presses    INTEGER,
            score          INTEGER,
            imported_date  INTEGER
        );
        """

        run_tag = """
            CREATE TABLE IF NOT EXISTS run_tag (
            id     INTEGER PRIMARY KEY ASC ON CONFLICT ABORT AUTOINCREMENT NOT NULL ON CONFLICT ABORT UNIQUE ON CONFLICT ABORT,
            run_id INTEGER REFERENCES run (run_id),
            tag_id INTEGER REFERENCES tag (tag_id)
        );
        """

        tag = """
            CREATE TABLE IF NOT EXISTS tag (
            id      INTEGER PRIMARY KEY ASC ON CONFLICT ABORT AUTOINCREMENT NOT NULL ON CONFLICT ABORT UNIQUE ON CONFLICT ABORT,
            name   TEXT,
            color  TEXT
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
        sys.exit()

# This function configures where the replays are located if not default and writes it to the config file
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

# This function gets the hashes from the database so we don't write old replays to the db
def get_run_hashes(db):
    c = db.cursor()
    c.execute("SELECT r.f_hash FROM runs")
    hashes = c.fetchall()
    return hashes

# This functions gets the listing of files needed to be parsed
def get_files(replays):
    try:
        files = os.listdir(replays)
        return files
    except Exception as e:
        print("Could not get replay files: {}".format(e))

# This functions acts as a case statement for character's formatted name because Python :)
def get_char_name(c):
    switcher = {
        0: "Cadence",
        1: "Melody",
        2: "Aria",
        3: "Dorian",  # Dad
        4: "Eli",  # Best
        5: "Monk",  # Bad
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

# This functions acts as a case statement for the formatted run type because Python :)
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

# This functions returns the zone that the replay ended on
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
                replay.bugged, replay.bugged_reason = True, "Number of songs is bugged: {}".format(
                    songs)
            zone = zones
            floor = 5
        elif zone < 1:  # Aria
            replay.bugged, replay.bugged_reason = True, "Number of songs is bugged: {}".format(
                songs)
            zone = 1
            floor = 4
        replay.end_zone = {'zone': zone, 'floor': floor}
        replay.f_end_zone = "{}-{}".format(zone, floor)
    elif char in [6]:  # Dove
        zone = t if t < zones + \
            1 and t > 0 else math.floor(((songs - 1)/3) + 1)
        floor = ((songs - 1) % 3) + 1
        replay.end_zone = {'zone': zone, 'floor': floor}
        replay.f_end_zone = "{}-{}".format(zone, floor)

    return(replay)

# This functions returns the formatted run time as seen as the end screen in game
def get_time_from_replay(ms_time):

    if ms_time < 0:
        return "00:00:00.000"
    millis = int(((ms_time/1000) % 1)*100)
    seconds = math.floor((ms_time/1000) % 60)
    minutes = math.floor((ms_time/(1000*60)) % 60)
    hours = math.floor((ms_time/(1000*60*60)) % 24)
    time_to_return = ""
    time_to_return += '{:>02}:'.format(str(hours)) if hours > 0 else "00:"
    time_to_return += '{:>02}:'.format(str(minutes)) if minutes > 0 else "00:"
    time_to_return += '{:>02}.'.format(str(seconds)) if seconds > 0 else "00."
    time_to_return += '{:>02}'.format(str(millis)) if millis > 0 else "00"

    return time_to_return

# This functions returns the number of keys pressed during a run, because why not
def get_key_presses(songs, data, replay):
    if songs < 0:
        return 0
    keys = 0
    for i in range(0, songs):
        keys += int(data[(i+1)*11])
    return keys

# This functions calculates the seed based off the first floor seed       
def calculate_seed(zone_1_seed, amplified):
    # seed.add(0x40005e47).times(0xd6ee52a).mod(0x7fffffff).mod(0x713cee3f);
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

# This functions does all the heavy lifting and is where all replay parsing happens
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
            dt = "{} {}".format(
                "/".join(split_name[3:6:]), ":".join(split_name[6:9]))
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
                p_file.f_hash = hash("{}/{}".format(r_folder, r_f))
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
                p_file.key_presses = get_key_presses(songs, split_data, p_file)
                #print(p_file.__dict__)
                print(p_file)
            else:
                print("Too lazy to code in co-op runs")

        except Exception as e:
            print("Couldn't parse file: {} -> {}".format(r_f, e))

# Pretty much everything was figured out by Grimy and/or AlexisYJ. Anything that looks complicated was them. Probably the simple stuff too :)
def main():
    # Grab the config data
    config = ConfigParser()
    config.read(CONFIG)
    dbfile = config.get('DEFAULT', 'DATABASE_FILE')
    replay_folder = config.get('DEFAULT', 'REPLAY_FOLDER')

    # Setup the db connection
    db = setup_database(dbfile)

    # Get hashes for runs from the db
    run_hashes = get_run_hashes(db)

    # Setup the replay folder/files 
    replay_folder = setup_replay_folder(replay_folder, config)
    replay_files = get_files(replay_folder)

    # Parse the replay files
    parse_files(replay_folder, replay_files)

    # Save any new runs to the db

if __name__ == "__main__":
    sys.exit(main())