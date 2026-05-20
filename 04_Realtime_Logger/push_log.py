import json
import os
import subprocess
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_PATH = os.path.join(BASE_DIR, "temp_log_buffer.json")
BUFFER_PATH = os.path.join(BASE_DIR, "conversation_buffer.json")
FORMAT_SCRIPT = os.path.join(BASE_DIR, "format_log.py")
DB_PATH = os.path.join(BASE_DIR, "system_memory.db")
MAX_EXCHANGES = 10

def main():
    if not os.path.exists(TEMP_PATH):
        print(f"[WARN] temp_log_buffer.json not found: {TEMP_PATH}")
        return

    # 1. Read dialogue data from temporary JSON buffer
    with open(TEMP_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 2. Read conversation log buffer file (initialize if not exists)
    if os.path.exists(BUFFER_PATH):
        with open(BUFFER_PATH, "r", encoding="utf-8") as f:
            try:
                buffer_data = json.load(f)
            except json.JSONDecodeError:
                buffer_data = {}
    else:
        buffer_data = {}

    if "exchanges" not in buffer_data:
        buffer_data = {
            "session_id": data.get("session_id", "Default_Session"),
            "started_at": data.get("started_at", data.get("exchange", {}).get("timestamp", "")),
            "last_updated": "",
            "exchanges": []
        }

    # 3. Add new record to buffer array
    exchange = data.get("exchange")
    if exchange:
        if not buffer_data["session_id"] and data.get("session_id"):
            buffer_data["session_id"] = data["session_id"]
            buffer_data["started_at"] = data.get("started_at", exchange.get("timestamp"))

        buffer_data["last_updated"] = exchange.get("timestamp", "")
        buffer_data["exchanges"].append(exchange)

        # 4. Save buffer to JSON
        with open(BUFFER_PATH, "w", encoding="utf-8") as f:
            json.dump(buffer_data, f, ensure_ascii=False, indent=2)
            
        print(f"[OK] Added seq {exchange.get('seq')} to buffer. Current size: {len(buffer_data['exchanges'])}")

        # 4.5. Write to SQLite database (persistent storage)
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            session_id = data.get("session_id", "Default_Session")
            seq = exchange.get("seq", 0)
            timestamp = exchange.get("timestamp", "")
            engine = exchange.get("engine", "Unknown")
            
            # Insert User message
            if "user" in exchange:
                cursor.execute(
                    "INSERT INTO dialogues (session_id, seq_number, timestamp, engine, speaker, content) VALUES (?, ?, ?, ?, ?, ?)",
                    (session_id, seq, timestamp, engine, "User", exchange["user"])
                )
            
            # Insert Assistant message
            if "assistant" in exchange:
                cursor.execute(
                    "INSERT INTO dialogues (session_id, seq_number, timestamp, engine, speaker, content) VALUES (?, ?, ?, ?, ?, ?)",
                    (session_id, seq, timestamp, engine, "Assistant", exchange["assistant"])
                )
                
            conn.commit()
            conn.close()
            print(f"[DB OK] Saved seq {seq} to database.")
        except Exception as e:
            print(f"[DB ERROR] Database save failed: {e}")

    # 5. Clean up processed temporary buffer file
    os.remove(TEMP_PATH)

    # 6. Auto-flush trigger: when buffer reaches threshold, format and output automatically
    if len(buffer_data.get("exchanges", [])) >= MAX_EXCHANGES:
        print(f"[AUTO-FLUSH] Buffer reached {MAX_EXCHANGES}. Executing format script...")
        subprocess.run(["python", FORMAT_SCRIPT])
        print("[AUTO-FLUSH] Flush completed.")

if __name__ == "__main__":
    main()
