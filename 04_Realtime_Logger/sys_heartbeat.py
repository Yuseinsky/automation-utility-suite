import schedule
import time
import json
import os
import subprocess
from datetime import datetime

# ==========================================
# 💓 Background Heartbeat Monitor Daemon
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_JSON_PATH = os.path.join(BASE_DIR, "temp_log_buffer.json")
PUSH_LOG_SCRIPT = os.path.join(BASE_DIR, "push_log.py")
MAX_EXCHANGES = 10  # Threshold for auto-flushing/committing logs

def log_status(message):
    """Output daemon status logs"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[💓 Heartbeat | {current_time}] {message}")

def check_and_flush_logs():
    """Inspect log buffer file and trigger flush if threshold exceeded"""
    try:
        if not os.path.exists(TEMP_JSON_PATH):
            return  # Skip if buffer file does not exist

        with open(TEMP_JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Inspect sequence number in JSON
        if "exchange" in data and "seq" in data["exchange"]:
            current_seq = data["exchange"]["seq"]
            log_status(f"Current log buffer sequence: {current_seq} / {MAX_EXCHANGES}")
            
            if current_seq >= MAX_EXCHANGES:
                log_status("🚨 Auto-commit threshold reached. Triggering flush script...")
                result = subprocess.run(["python", PUSH_LOG_SCRIPT], capture_output=True, text=True, errors='replace')
                if result.returncode == 0:
                    log_status("✅ Auto-commit completed successfully.")
                else:
                    log_status(f"❌ Auto-commit failed:\n{result.stderr}")
                    
    except json.JSONDecodeError:
        log_status("⚠️ JSON parsing failed (file might be in write state). Skipping...")
    except Exception as e:
        log_status(f"❌ Error during daemon execution: {e}")

# ==========================================
# 🕒 Schedule Configurations
# ==========================================
# Run verification check every 1 minute
schedule.every(1).minutes.do(check_and_flush_logs)

if __name__ == "__main__":
    log_status("✨ Heartbeat monitor daemon started. Beginning background processing...")
    log_status("Press Ctrl+C to terminate.")
    
    # Execution loop
    while True:
        schedule.run_pending()
        time.sleep(1)
