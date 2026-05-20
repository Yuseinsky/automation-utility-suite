import sqlite3
import os

# ==========================================
# 🗄️ System Memory Database Initialization
# ==========================================

# Set database path in the script's directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "system_memory.db")

def create_database():
    print(f"✨ Creating database...\nPath: {DB_PATH}")
    
    # Establish connection (auto-creates if it doesn't exist)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # ==========================================
    # 📚 Dialogues Table Schema Definition
    # ==========================================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dialogues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Auto-incrementing primary key ID
            session_id TEXT NOT NULL,              -- Session identifier
            seq_number INTEGER,                    -- Sequence number in dialogue flow
            timestamp TEXT NOT NULL,               -- ISO-8601 formatted timestamp
            engine TEXT,                           -- LLM Engine name (e.g. gemini-2.5-pro)
            speaker TEXT NOT NULL,                 -- Speaker (User or Assistant)
            content TEXT NOT NULL                  -- Content of the message
        )
    ''')
    
    # Commit changes and close
    conn.commit()
    conn.close()
    print("✅ Database schema initialized successfully!")

if __name__ == "__main__":
    create_database()
