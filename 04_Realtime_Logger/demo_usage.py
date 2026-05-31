"""
Demo: Universal AI Dialogue Logger
====================================
A minimal working example showing how to integrate the DialogueLogger
into any AI application — from Discord Bots to custom LLM pipelines.

Run:
    python demo_usage.py
"""
import os
from universal_logger import DialogueLogger

DEMO_DB = "demo_memory.db"


def main():
    # Clean up previous demo artifacts for a fresh, repeatable demo
    if os.path.exists(DEMO_DB):
        os.remove(DEMO_DB)

    # 1. Initialize the logger (auto-creates DB if not exists)
    logger = DialogueLogger(
        db_path=DEMO_DB,
        auto_flush_threshold=5,   # Export Markdown every 5 exchanges
        log_dir="Demo_Logs",
    )

    # 2. Simulate a conversation session
    session = "demo_session_001"
    conversations = [
        ("What is Python?",
         "Python is a high-level, interpreted programming language."),
        ("What about its typing system?",
         "Python uses dynamic typing with optional type hints (PEP 484)."),
        ("How does garbage collection work?",
         "Python uses reference counting with a cyclic garbage collector."),
        ("What is a virtual environment?",
         "An isolated Python runtime that avoids dependency conflicts."),
        ("Explain list comprehensions.",
         "A concise syntax: [expr for item in iterable if condition]."),
    ]

    for user_msg, ai_msg in conversations:
        logger.log_exchange(session, user_msg, ai_msg, engine="Demo-GPT")

    # 3. Query back the stored data
    print("\n--- Stored Exchanges ---")
    for entry in logger.query_session(session):
        print(f"  [seq {entry['seq']}] {entry['speaker']}: "
              f"{entry['content'][:60]}...")

    print("\nDemo completed. Check 'Demo_Logs/' for the auto-exported Markdown.")


if __name__ == "__main__":
    main()
