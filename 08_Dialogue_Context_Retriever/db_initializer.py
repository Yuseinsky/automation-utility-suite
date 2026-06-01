"""
========================================================
DB Initializer — Dialogue History Store (V2.0)
========================================================
Initializes a local SQLite database for persisting
AI-human dialogue exchanges. The schema supports
session-based grouping, sequential ordering, and
multi-engine tracking.

Usage:
    python db_initializer.py

Output:
    Creates 'dialogue_history.db' in the same directory.

IMPORTANT: DB_PATH must remain in sync with
context_retriever.py. If you change the database
filename here, update it there as well.
========================================================
"""

import sqlite3
import os
import sys

__version__ = "2.0.0"

# --- Encoding Safety for Windows terminals (CP932/CP950) ---
sys.stdout.reconfigure(errors='replace')

# --- Configuration ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "dialogue_history.db")


def create_database():
    """
    Create the SQLite database and define the 'dialogues' table schema.
    If the database or table already exists, this operation is idempotent.
    Includes performance indexes for session_id and timestamp queries.
    """
    db_exists = os.path.exists(DB_PATH)

    if db_exists:
        # Check existing record count
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM dialogues")
            count = cursor.fetchone()[0]
            conn.close()
            print(f"[INFO] Database already exists. Contains {count} record(s).")
            print(f"[PATH] {DB_PATH}")
            print(f"[INFO] Verifying schema and indexes...")
        except Exception:
            # Table might not exist yet in an empty db
            print(f"[INFO] Database file exists but may need schema initialization.")
    else:
        print(f"[INIT] Creating dialogue history database...")
        print(f"[PATH] {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ------------------------------------------------
    # Schema: dialogues table (V2.0)
    # ------------------------------------------------
    # [P1-2] Added NOT NULL DEFAULT constraints to
    # seq_number and engine to prevent NULL sorting
    # inconsistencies.
    # ------------------------------------------------
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dialogues (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id  TEXT    NOT NULL,
            seq_number  INTEGER NOT NULL DEFAULT 0,
            timestamp   TEXT    NOT NULL,
            engine      TEXT    NOT NULL DEFAULT 'unknown',
            speaker     TEXT    NOT NULL,
            content     TEXT    NOT NULL
        )
    ''')

    # ------------------------------------------------
    # [P1-1] Performance Indexes
    # ------------------------------------------------
    # idx_session: Accelerates WHERE session_id LIKE ?
    # idx_timestamp: Accelerates ORDER BY timestamp DESC
    # ------------------------------------------------
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_session
        ON dialogues(session_id)
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_timestamp
        ON dialogues(timestamp DESC)
    ''')

    conn.commit()
    conn.close()

    if db_exists:
        print("[OK] Schema and indexes verified successfully.")
    else:
        print("[OK] Database schema and indexes created successfully.")


if __name__ == "__main__":
    create_database()
