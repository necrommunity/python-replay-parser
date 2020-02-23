from flask import Blueprint, Flask, jsonify, render_template
from __main__ import app
from app import get_replays
import sqlite3


@app.route("/")
def home_page():
    total_wins = 0
    total_runs = 0
    json_data = api_stats().get_json()["stats"]
    if len(json_data) > 0:
        total_runs = len(json_data)
        for x in json_data:
            if x["win"]:
                total_wins += 1
    return render_template(
        "stats.html",
        j_data=json_data,
        total_runs=total_runs,
        total_wins=total_wins
        )


@app.route("/api")
def api_home():
    api_data = {
        "version": 0.1,
        "game": "Crypt of the NecroDancer: Amplified",
        "writtenBy": "sillypears",
        "name": "ND Replay Parser"
    }
    return api_data


@app.route("/api/stats")
def api_stats():
    api_data={}
    with sqlite3.connect(app.config["DATABASE_FILE"]) as db:
        replays = get_replays(db)
        runs = []
        for run_hash in replays:
            run = {}

            cur_run = replays[run_hash]
            run["hash"] = run_hash
            run["date"] = cur_run.run_date
            run["file"] = cur_run.file
            run["version"] = cur_run.version
            run["amp"] = cur_run.amplified_full
            run["type"] = cur_run.run_type
            run["type_f"] = cur_run.f_run_type
            run["char"] = cur_run.char1
            run["char_f"] = cur_run.f_char1
            run["players"] = cur_run.players
            run["seed"] = cur_run.seed
            run["songs"] = cur_run.songs
            run["end_zone"] = cur_run.end_zone
            run["end_zone_f"] = cur_run.f_end_zone
            run["time"] = cur_run.run_time
            run["time_f"] = cur_run.f_run_time
            run["key_presses"] = cur_run.key_presses
            run["score"] = cur_run.score
            run["killed_by"] = cur_run.killed_by
            run["killed_by_f"] = cur_run.f_killed_by
            run["win"] = cur_run.win
            run["imported_date"] = cur_run.imported_date
            run["bugged"] = cur_run.bugged
            run["bugged_reason"] = cur_run.bugged_reason
            run["weapon_type"] = cur_run.weapon_type
            run["weapon_class"] = cur_run.weapon_class
            runs.append(run)
        api_data = {
            "stats": runs
        }
    return jsonify(api_data)

@app.route("/api/stats/secret")
def api_secrets():
    api_data = {}
    with sqlite3.connect(app.config["DATABASE_FILE"]) as db:
        c = db.cursor()
        try:
            c.execute("SELECT name FROM sqlite_master WHERE type='table'")
            test = c.fetchall()
            print(test)
            api_data = {
                "secrets": [{

                }]
            }
        except Exception as e:
            pass
    return api_data