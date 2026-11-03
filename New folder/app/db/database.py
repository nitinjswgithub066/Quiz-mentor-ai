"""
database.py
-----------
Minimal SQLite setup for the ai-engine trial. No ORM yet (no SQLAlchemy
available offline) -- just raw sqlite3 + a schema. This is intentional for
the trial stage: fewer moving parts to debug first. Swap in SQLAlchemy
later once the shape of the data is proven out.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "quiz_engine.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    firebase_uid TEXT UNIQUE NOT NULL,
    name TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS languages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

-- This table IS the "memory model": what the system remembers about
-- each user's ability in each language.
CREATE TABLE IF NOT EXISTS skill_levels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    language_id INTEGER NOT NULL,
    level INTEGER NOT NULL DEFAULT 1,       -- 1 to 10
    attempts_count INTEGER NOT NULL DEFAULT 0,
    correct_count INTEGER NOT NULL DEFAULT 0,
    last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, language_id),
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(language_id) REFERENCES languages(id)
);

CREATE TABLE IF NOT EXISTS attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    language_id INTEGER NOT NULL,
    trial_number INTEGER NOT NULL,
    difficulty INTEGER NOT NULL,
    is_correct INTEGER NOT NULL,            -- 0 or 1
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(language_id) REFERENCES languages(id)
);
"""


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()


def reset_db():
    """Wipe the trial DB so repeated test runs start clean."""
    if DB_PATH.exists():
        DB_PATH.unlink()
    init_db()


if __name__ == "__main__":
    reset_db()
    print(f"Initialized fresh DB at {DB_PATH}")
