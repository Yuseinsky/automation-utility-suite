"""
========================================================
Context Retriever — Dialogue History Search & Restore
========================================================
Searches a local SQLite dialogue history database by
keyword or session ID, and outputs results in a
Markdown-formatted context block suitable for injection
into a new LLM conversation.

Usage:
    python context_retriever.py --query "encoding"
    python context_retriever.py --session "tech_design"
    python context_retriever.py --recent 5

Options:
    --query   TEXT    Search dialogue content by keyword
                      (case-insensitive, partial match).
    --session TEXT    Filter by session ID
                      (partial match supported).
    --recent  INT     Show the N most recent exchanges
                      (default: 10 if no other flag).

Potential Risks & Limitations:
    - Encoding: On non-UTF-8 terminals (e.g. Windows
      CP932/CP950), multilingual characters may render
      as '?' replacement chars. Configure your terminal
      to UTF-8 (chcp 65001) for best results.
    - DB Locking: SQLite does not support high-concurrency
      writes. This tool is designed for single-user local
      use only. Concurrent write access may cause
      'database is locked' errors.
========================================================
"""

import sqlite3
import os
import sys
import argparse
import textwrap

# --- Encoding Safety for Windows terminals (CP932/CP950) ---
sys.stdout.reconfigure(errors='replace')

# --- Configuration ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "dialogue_history.db")


def get_connection():
    """
    Establish a read-only connection to the dialogue database.
    Returns None and prints an error if the DB file is missing.
    """
    if not os.path.exists(DB_PATH):
        print("[ERROR] Database not found. Run db_initializer.py first.")
        print(f"[PATH] Expected: {DB_PATH}")
        return None
    return sqlite3.connect(DB_PATH)


def search_by_keyword(keyword, limit=20):
    """
    Search dialogue content for a keyword (case-insensitive).
    Returns matching rows as a list of tuples.
    """
    conn = get_connection()
    if not conn:
        return []

    cursor = conn.cursor()
    cursor.execute('''
        SELECT session_id, seq_number, timestamp, engine, speaker, content
        FROM dialogues
        WHERE content LIKE ?
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (f'%{keyword}%', limit))

    results = cursor.fetchall()
    conn.close()
    return results


def search_by_session(session_id, limit=50):
    """
    Retrieve all dialogues belonging to a specific session.
    Supports partial matching on session_id.
    """
    conn = get_connection()
    if not conn:
        return []

    cursor = conn.cursor()
    cursor.execute('''
        SELECT session_id, seq_number, timestamp, engine, speaker, content
        FROM dialogues
        WHERE session_id LIKE ?
        ORDER BY seq_number ASC
        LIMIT ?
    ''', (f'%{session_id}%', limit))

    results = cursor.fetchall()
    conn.close()
    return results


def get_recent(count=10):
    """
    Retrieve the N most recent dialogue exchanges.
    """
    conn = get_connection()
    if not conn:
        return []

    cursor = conn.cursor()
    cursor.execute('''
        SELECT session_id, seq_number, timestamp, engine, speaker, content
        FROM dialogues
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (count,))

    results = cursor.fetchall()
    conn.close()
    return results


def format_as_markdown(results, title="Retrieved Context"):
    """
    Format query results into a Markdown context block
    suitable for LLM context injection.
    """
    if not results:
        print("[INFO] No matching records found.")
        return

    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"  Found {len(results)} record(s)")
    print(f"{'='*60}\n")

    for row in results:
        session_id, seq, timestamp, engine, speaker, content = row

        # Truncate long content for preview display
        preview = content[:120] + "..." if len(content) > 120 else content

        print(f"### [{timestamp}] Session: {session_id} | Seq: {seq}")
        print(f"**Speaker**: {speaker} | **Engine**: {engine}")
        print(f"```")
        print(preview)
        print(f"```")
        print(f"{'-'*60}")


def main():
    parser = argparse.ArgumentParser(
        description="Dialogue History Context Retriever",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              python context_retriever.py --query "database"
              python context_retriever.py --session "tech_design"
              python context_retriever.py --recent 5
        """)
    )
    parser.add_argument(
        '--query', type=str, default=None,
        help='Search keyword (case-insensitive, partial match)'
    )
    parser.add_argument(
        '--session', type=str, default=None,
        help='Filter by session ID (partial match)'
    )
    parser.add_argument(
        '--recent', type=int, default=None,
        help='Show N most recent exchanges'
    )

    args = parser.parse_args()

    if args.query:
        print(f'[SEARCH] Keyword: "{args.query}"')
        results = search_by_keyword(args.query)
        format_as_markdown(results, title=f'Keyword Search: "{args.query}"')

    elif args.session:
        print(f'[SEARCH] Session: "{args.session}"')
        results = search_by_session(args.session)
        format_as_markdown(results, title=f'Session: "{args.session}"')

    elif args.recent is not None:
        print(f'[SEARCH] Recent {args.recent} exchanges')
        results = get_recent(args.recent)
        format_as_markdown(results, title=f'Recent {args.recent} Exchanges')

    else:
        # Default: show 10 most recent
        print('[INFO] No search flag specified. Showing 10 most recent.')
        results = get_recent(10)
        format_as_markdown(results, title='Recent 10 Exchanges')


if __name__ == "__main__":
    main()
