import hashlib
import sqlite3
from pathlib import Path

# game.db is found in the project folder (next to api, game and client folders),
# Independant of which map the server was launched from 
DB_PATH = Path(__file__).resolve().parent.parent / "game.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player TEXT NOT NULL,
            score INTEGER NOT NULL
        )""")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS players (
            name TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            token TEXT
        )""")
    return conn


def hash_password(password):
    data = password.encode()
    return hashlib.sha256(data).hexdigest()