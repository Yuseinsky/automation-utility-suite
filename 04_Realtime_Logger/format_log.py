import json
import os
import shutil
from datetime import datetime

# === Paths Config (Relative to script's directory) ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BUFFER_PATH = os.path.join(BASE_DIR, "conversation_buffer.json")
ARCHIVE_DIR = os.path.join(BASE_DIR, "Archive")
RAW_LOGS_BASE = os.path.join(BASE_DIR, "Formatted_Logs")

def main():
    # 1. Verify existence of conversation_buffer.json and load
    if not os.path.exists(BUFFER_PATH):
        print(f"[ERROR] conversation_buffer.json not found: {BUFFER_PATH}")
        return

    with open(BUFFER_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    exchanges = data.get("exchanges", [])
    if not exchanges:
        print("[WARN] Buffer is empty. Skipping export.")
        return

    print(f"[PROCESS] Detected {len(exchanges)} records. Starting formatting...")

    # 2. Generate Markdown Document
    session_id = data.get("session_id", "Default_Session")
    started_at = data.get("started_at", "Unknown")
    
    topic = session_id.replace("_", " ").strip()

    md_lines = []
    md_lines.append(f"# 📜 Dialogue Log: {topic}")
    md_lines.append(f"**Started At**: {started_at}")
    md_lines.append(f"**Participants**: User, Assistant")
    md_lines.append(f"**Method**: Background logging via format_log.py")
    md_lines.append("")
    md_lines.append("---")
    md_lines.append("")

    current_engine = None

    for ex in exchanges:
        # Show engine switch
        exchange_engine = ex.get("engine", "Unknown")
        if exchange_engine != current_engine:
            current_engine = exchange_engine
            md_lines.append(f"### ⚙️ [Engine Switch] Model: {current_engine}")
            md_lines.append("---")
            md_lines.append("")

        # User Input
        md_lines.append(f"**User**:\n{ex['user']}")
        md_lines.append("")
        
        # Assistant Output (Restore newlines)
        assistant_text = ex.get("assistant", "").replace("\\n", "\n")
        md_lines.append(f"**Assistant**:\n{assistant_text}")
        md_lines.append("")
        md_lines.append("---")
        md_lines.append("")

    md_lines.append("> *(System Message: Log output completed)*")

    md_content = "\n".join(md_lines)

    # 3. Create monthly subdirectory and save Markdown
    now = datetime.now()
    year_month = now.strftime("%Y-%m")
    output_dir = os.path.join(RAW_LOGS_BASE, year_month)
    os.makedirs(output_dir, exist_ok=True)

    # Output filename: Log_YYYYMMDD_HHMM_[Topic].md
    timestamp_str = now.strftime("%Y%m%d_%H%M")
    safe_topic = topic[:20].replace(" ", "_")
    output_filename = f"Log_{timestamp_str}_[{safe_topic}].md"
    output_path = os.path.join(output_dir, output_filename)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"[OK] Log exported to: {output_path}")

    # 4. Archive buffer file for safety
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    archive_filename = f"buffer_{now.strftime('%Y%m%d_%H%M')}.json"
    archive_path = os.path.join(ARCHIVE_DIR, archive_filename)
    shutil.copy2(BUFFER_PATH, archive_path)
    print(f"[ARCHIVE] Staged buffer archived to: {archive_path}")

    # 5. Initialize buffer file
    empty_buffer = {
        "session_id": "",
        "started_at": "",
        "last_updated": "",
        "exchanges": []
    }
    with open(BUFFER_PATH, "w", encoding="utf-8") as f:
        json.dump(empty_buffer, f, ensure_ascii=False, indent=2)

    print(f"[CLEAN] Buffer successfully initialized.")
    print(f"\n[DONE] Finished! Exported {len(exchanges)} entries.")

if __name__ == "__main__":
    main()
