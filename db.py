import sqlite3
from __main__ import app

db = app.config["DATABASE_FILE"]
conn = sqlite3.connect(db)
