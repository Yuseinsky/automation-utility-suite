"""
========================================================
DB Initializer — Dialogue History Store
========================================================
Initializes a local SQLite database for persisting
AI-human dialogue exchanges. The schema supports
session-based grouping, sequential ordering, and
multi-engine tracking.

Usage:
    python db_initializer.py

Output:
    Creates 'dialogue_history.db' in the same directory.
========================================================
"""

import sqlite3
import os
import sys

# --- Encoding Safety for Windows terminals (CP932/CP950) ---
sys.stdout.reconfigure(errors='replace')

# --- Configuration ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "dialogue_history.db")


def create_database():
    """
    Create the SQLite database and define the 'dialogues' table schema.
    If the database or table already exists, this operation is idempotent.
    """
    print(f"[INIT] Creating dialogue history database...")
    print(f"[PATH] {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ------------------------------------------------
    # Schema: dialogues table
    # ------------------------------------------------
    # Each row represents one message (either from
    # the user or the AI agent) within a conversation.
    # ------------------------------------------------
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dialogues (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id  TEXT    NOT NULL,
            seq_number  INTEGER,
            timestamp   TEXT    NOT NULL,
            engine      TEXT,
            speaker     TEXT    NOT NULL,
            content     TEXT    NOT NULL
        )
    ''')

    conn.commit()
    conn.close()
    print("[OK] Database schema created successfully.")


if __name__ == "__main__":
    create_database()
