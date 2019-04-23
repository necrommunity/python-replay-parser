#!py -3
import math
import os
import sqlite3
import sys
import time
from configparser import ConfigParser
from tkinter import filedialog
import hashlib
from dateutil import parser
from datetime import datetime
import json

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
        self.f_run_date = ""
        self.run_type = 0
        self.f_run_type = ""
        self.char1 = 0
        self.f_char1 = ""
        self.char2 = 0
        self.f_char2 = ""
        self.players = 0
        self.seed = 0
        self.songs = 0
        self.end_zone = -1
        self.f_end_zone = ""
        self.run_time = 0
        self.f_run_time = ""
        self.key_presses = 0
        self.score = 0
        self.killed_by = 0
        self.f_killed_by = ""
        self.win = False
        self.bugged = False
        self.bugged_reason = ""
        self.imported_date = ""

    # A simple way to output useful data when debugging :)
    def __str__(self):
        return("Date: {}, Seed: {}, Char: {}, Type: {}, EndZone: {}, RunTime: {}, KeyPresses: {}".format(
            self.f_run_date,
            self.seed,
            self.f_char1,
            self.f_run_type,
            self.f_end_zone,
            self.f_run_time,
            self.key_presses
        ))

    def to_json(self):
        j = {
            'version': self.version,
            'amplified': self.amplified,
            'amplifiedFull': self.amplified_full,
            'file': self.file,
            'fHash': self.f_hash,
            'runDate': self.run_date,
            'fRunDate': self.f_run_date,
            'runType': self.run_type,
            'fRunType': self.f_run_type,
            'char1': self.char1,
            'fChar1': self.f_char1,
            'seed': self.seed,
            'runTime': self.run_time,
            'fRunTime': self.f_run_time,
            'songs': self.songs,
            'endZone': self.f_end_zone,
            'keyPresses': self.key_presses,
            'score': self.score,
            'killedBy': self.f_killed_by,
            'win': self.win,
            'bugged': self.bugged,
            'buggedReason': self.bugged_reason,
            'importDate': self.imported_date
        }
        return j

# This function setups up the database if it doesn't exist


def setup_database(db):
    try:
        conn = sqlite3.connect(db)

        bugged = """
            CREATE TABLE IF NOT EXISTS bugged (
            id            INTEGER PRIMARY KEY ASC ON CONFLICT ABORT AUTOINCREMENT NOT NULL ON CONFLICT ABORT UNIQUE ON CONFLICT ABORT,
            run_id        INTEGER REFERENCES run (id),
            bugged        BOOLEAN,
            bugged_reason TEXT,
            bugged_data   TEXT
        );
        """

        run = """
            CREATE TABLE IF NOT EXISTS run (
            id             INTEGER  PRIMARY KEY ASC ON CONFLICT ABORT AUTOINCREMENT NOT NULL ON CONFLICT ABORT UNIQUE ON CONFLICT ABORT,
            version        INTEGER,
            amplified      BOOLEAN,
            amplified_full BOOLEAN,
            folder         TEXT,
            file           TEXT,
            f_hash         INTEGER,
            run_date       INTEGER,
            f_run_date     INTEGER,
            run_type       INTEGER,
            f_run_type     TEXT,
            seed           INTEGER,
            songs          INTEGER,
            end_zone       TEXT,
            run_time       INTEGER,
            f_run_time     TEXT,
            players        INTEGER,
            char1          INTEGER,
            f_char1        TEXT,
            char2          INTEGER,
            f_char_2       TEXT,
            win            BOOLEAN,
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
            run_id INTEGER REFERENCES run (id),
            tag_id INTEGER REFERENCES tag (id)
        );
        """

        tag = """
            CREATE TABLE IF NOT EXISTS tag (
            id        INTEGER PRIMARY KEY ASC ON CONFLICT ABORT AUTOINCREMENT NOT NULL ON CONFLICT ABORT UNIQUE ON CONFLICT ABORT,
            name      TEXT UNIQUE ON CONFLICT ABORT,
            color     TEXT,
            color_hex TEXT
        );
        """

        tag_data = [
            ("Win", "Green", "#3CB371"),
            ("Death By Enemy", "Red", "#FA8072"),
            ("Death By Curse", "Grey", "#708090")
        ]

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
            c.executemany(
                'INSERT INTO tag (name, color, color_hex) values (?, ?, ?)', tag_data)
            conn.commit()

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
    hashes = []
    c = db.cursor()
    c.execute("SELECT r.f_hash FROM run r")
    for run_hash in c.fetchall():
        hashes.append(run_hash[0])
    return hashes

# This function gets all the current tags from the database


def get_tags(db):
    tags = {}
    c = db.cursor()
    c.execute("SELECT t.id, t.name, t.color, t.color_hex FROM tag t")
    for tag in c.fetchall():
        tags[tag[0]] = tag
    return tags

# This function gets the replay data from the database


def get_replays(db):
    replays = {}
    c = db.cursor()
    try:
        c.execute("""
        SELECT 
                r.version,
                r.amplified,
                r.amplified_full,
                r.folder,
                r.file,
                r.f_hash,
                r.run_date,
                r.f_run_date,
                r.run_type,
                r.f_run_type,
                r.seed,
                r.songs,
                r.end_zone,
                r.run_time,
                r.f_run_time,
                r.players,
                r.char1,
                r.f_char1,
                r.win,
                r.killed_by,
                r.f_killed_by,
                r.key_presses,
                r.score,
                b.bugged,
                b.bugged_reason,
                r.imported_date
        FROM
            run r
        LEFT JOIN bugged b 
            ON b.run_id = r.id
        ORDER BY 
            r.run_date DESC
        ;""")
        for run in c.fetchall():
            p_replay = ParsedReplay()
            p_replay.version = run[0]
            p_replay.amplified = bool(run[1])
            p_replay.amplified_full = bool(run[2])
            p_replay.folder = run[3]
            p_replay.file = run[4]
            p_replay.f_hash = run[5]
            p_replay.run_date = run[6]
            p_replay.f_run_date = run[7]
            p_replay.run_type = run[8]
            p_replay.f_run_type = run[9]
            p_replay.seed = run[10]
            p_replay.songs = run[11]
            ez = run[12].split("-")
            p_replay.end_zone = {'zone': ez[0], 'floor': ez[1]}
            p_replay.f_end_zone = run[12]
            p_replay.run_time = run[13]
            p_replay.f_run_time = run[14]
            p_replay.players = run[15]
            p_replay.char1 = run[16]
            p_replay.f_char1 = run[17]
            p_replay.win = bool(run[18])
            p_replay.killed_by = run[19]
            p_replay.f_killed_by = run[20]
            p_replay.key_presses = run[21]
            p_replay.score = run[22]
            p_replay.bugged = bool(run[23])
            p_replay.bugged_reason = run[24]
            p_replay.imported_date = run[25]

            replays[p_replay.f_hash] = p_replay
    except Exception as e:
        print("Couldn't populate replay from db \'{}\': {}".format(run[5], e))
    return replays

# This function gets the listing of files needed to be parsed


def get_files(replays):
    try:
        files = os.listdir(replays)
        return files
    except Exception as e:
        print("Could not get replay files: {}".format(e))

# This function acts as a case statement for character's formatted name because Python :)


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

# This function acts as a case statement for the formatted run type because Python :)


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

# This function returns the zone that the replay ended on


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

# This function returns the formatted run time as seen as the end screen in game


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

# This function returns the number of keys pressed during a run, because why not


def get_key_presses(songs, data, replay):
    if songs < 0:
        return 0
    keys = 0
    for i in range(0, songs):
        keys += int(data[(i+1)*11])
    return keys

# This function saves a replay to the database


def save_run(run, db):

    try:
        # run_id = -1
        # bugged_id = -1
        # tag_id = -1
        # runtag_id = -1

        c = db.cursor()
        run_sql = """
        INSERT INTO run 
        (
            version,
            amplified,
            amplified_full,
            folder,
            file,
            f_hash,
            run_date,
            f_run_date,
            run_type,
            f_run_type,
            seed,
            songs,
            end_zone,
            run_time,
            f_run_time,
            players,
            char1,
            f_char1,
            win,
            killed_by,
            f_killed_by,
            key_presses,
            score,
            imported_date
        )
        VALUES
        (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ;
        """
        run_data = [
            (
                run.version,
                True if run.amplified else False,
                True if run.amplified_full else False,
                run.folder,
                run.file,
                run.f_hash,
                run.run_date,
                run.f_run_date,
                run.run_type,
                run.f_run_type,
                run.seed,
                run.songs,
                run.f_end_zone,
                run.run_time,
                run.f_run_time,
                run.players,
                run.char1,
                run.f_char1,
                run.win,
                run.killed_by,
                run.f_killed_by,
                run.key_presses,
                run.score,
                run.imported_date
            )
        ]
        c.executemany(run_sql, run_data)

        # Save the id of the last inserted row as the run_id
        # run_id = c.lastrowid

        # If the run was bugged, make a note of it
        # if run.bugged:
        #     c.execute("hehe insert bugged stuff")
        #     bugged_id = c.lastrowid

        # Insert the tag information
        # c.execute("hehe do the tag stuff")
        # tag_id = c.lastrowid

        # if run_id > 0 and tag_id > 0:
        #     c.execute("hehe add the runtag stuffs")
        #     runtag_id = c.lastrowid

        db.commit()
    except Exception as e:
        print("Couldn't insert run: {}, {}/{}\n{}".format(run.f_hash,
                                                          run.folder, run.file, e))

# This function outputs the replay data to a json file


def save_to_json(replays, json_file):
    try:
        if os.path.exists(json_file):
            os.remove(json_file)
        with open(json_file, 'w+') as f:
            f.write("[\n")
            f.write("{")
            f.write("\"data\": [")
            c_len = 0
            for replay in replays:
                f.write("{}{}\n".format(json.dumps(
                    replays[replay].to_json()), "," if c_len+1 < len(replays) else ""))
                c_len += 1
            f.write("]}]")
    except Exception as e:
        print("Couldn't save to json: {}".format(e))

# This function calculates the seed based off the first floor seed


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

# This function does all the heavy lifting and is where all replay parsing happens


def parse_files(r_folder, r_files, all_replays, hashes, tags, db):
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
            dt = parser.parse("{} {}".format(
                "/".join(split_name[3:6:]), ":".join(split_name[6:9])))
            f_dt = "{}/{}/{} {}:{}".format(dt.year,
                                           dt.month, dt.day, dt.hour, dt.minute)
            t = int(split_name[9])
            coop = True if int(split_data[8]) > 1 else False
            char1 = int(split_data[12].split("|")[0])
            players = int(split_data[8])
            seed = int(split_data[7])
            songs = int(int(split_data[6]))
            run_time = int(split_data[5])
            run_hash = hashlib.md5(
                "{}/{} {}".format(r_folder, r_f, char1).encode()).hexdigest()
            if char1 in [0, 10]:
                win = True if songs == 22 and len(
                    split_data[248]) > 0 else False
            elif char1 not in [0, 6, 10]:
                win = True if songs == 20 and len(
                    split_data[226]) > 0 else False
            elif char1 == 6:
                win = True if songs == 15 and len(
                    split_data[171]) > 0 else False
            if not coop:
                p_file.version = version
                p_file.amplified = amp
                p_file.amplified_full = amp_full
                p_file.folder = r_folder
                p_file.file = r_f
                p_file.f_hash = run_hash
                p_file.run_date = int(dt.timestamp())
                p_file.f_run_date = f_dt
                p_file.run_type = t
                p_file.f_run_type = get_type_name(t)
                p_file.char1 = char1
                p_file.f_char1 = get_char_name(char1)
                p_file.players = players
                p_file.seed = calculate_seed(seed, amp)
                p_file.songs = songs
                p_file.run_time = run_time
                p_file.f_run_time = get_time_from_replay(run_time)
                p_file.win = win
                p_file = get_end_zone(songs, char1, t, p_file)
                p_file.key_presses = get_key_presses(songs, split_data, p_file)
                p_file.imported_date = int(datetime.now().timestamp())
                # print(p_file.__dict__)
                print(p_file)
                if run_hash not in hashes:

                    save_run(p_file, db)
                    all_replays[p_file.f_hash] = p_file
                    hashes.append(run_hash)
            else:
                print("Too lazy to code in co-op runs")

        except Exception as e:
            print("Couldn't parse file: {} -> {}".format(r_f, e))

    return all_replays


# Pretty much everything was figured out by Grimy and/or AlexisYJ. Anything that looks complicated was them. Probably the simple stuff too :)
def main():
    # Grab the config data
    config = ConfigParser()
    config.read(CONFIG)
    dbfile = config.get('DEFAULT', 'DATABASE_FILE')
    replay_folder = config.get('DEFAULT', 'REPLAY_FOLDER')
    json_file = config.get('DEFAULT', 'JSON_FILE')

    # Setup the db connection
    db = setup_database(dbfile)

    # Get hashes for runs from the db
    run_hashes = get_run_hashes(db)
    tags = get_tags(db)
    replays = get_replays(db)

    # Setup the replay folder/files
    replay_folder = setup_replay_folder(replay_folder, config)

    # Loop this forever
    counter = 0
    while True:
        replay_files = get_files(replay_folder)

        # Parse the replay files
        replays = parse_files(replay_folder, replay_files,
                              replays, run_hashes, tags, db)
        save_to_json(replays, json_file)
        counter += 1
        print("Looped {} time{}".format(counter, "s" if counter != 1 else ""))
        time.sleep(30)
        

if __name__ == "__main__":
    sys.exit(main())
