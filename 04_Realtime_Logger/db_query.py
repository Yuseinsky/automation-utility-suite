import sqlite3
import os
import sys

# Configure encoding for Windows console
sys.stdout.reconfigure(errors='replace')

# ==========================================
# 🔍 Dialogue History Query Script
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "system_memory.db")

def read_memories():
    print("[READ] Reading dialogue history database...")
    print("-" * 50)
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Query dialogues in chronological order
    cursor.execute('''
        SELECT timestamp, engine, speaker, content 
        FROM dialogues 
        ORDER BY timestamp ASC
    ''')
    
    records = cursor.fetchall()
    
    if not records:
        print("[EMPTY] No dialogue history found in database.")
    else:
        print(f"[SUCCESS] Found {len(records)} records.\n")
        for row in records:
            timestamp, engine, speaker, content = row
            # Trim content preview to 30 characters
            short_content = content[:30] + "..." if len(content) > 30 else content
            
            print(f"[{timestamp}]")
            print(f"[SPEAKER] {speaker} (Engine: {engine}):")
            print(f"[CONTENT] {short_content}")
            print("-" * 50)
            
    conn.close()

if __name__ == "__main__":
    read_memories()
