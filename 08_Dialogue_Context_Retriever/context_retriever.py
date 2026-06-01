"""
========================================================
Context Retriever — Dialogue History Search & Restore
                                            (V2.0)
========================================================
Searches a local SQLite dialogue history database by
keyword or session ID, and outputs results in a
Markdown-formatted context block suitable for injection
into a new LLM conversation.

Usage:
    python context_retriever.py --query "encoding"
    python context_retriever.py --session "tech_design"
    python context_retriever.py --recent 5
    python context_retriever.py --query "test" --full
    python context_retriever.py --query "test" --export output.md

Options:
    --query   TEXT    Search dialogue content by keyword
                      (case-insensitive, partial match).
    --session TEXT    Filter by session ID
                      (partial match supported).
    --recent  INT     Show the N most recent exchanges
                      (default: 10 if no other flag).
    --limit   INT     Max results to return (default varies by mode).
    --full            Show full content instead of preview.
    --export  FILE    Export results to a Markdown file.

IMPORTANT: DB_PATH must remain in sync with
db_initializer.py. If you change the database filename
there, update it here as well.
========================================================
"""

import sqlite3
import os
import sys
import argparse
import textwrap

__version__ = "2.0.0"

# --- Encoding Safety for Windows terminals (CP932/CP950) ---
sys.stdout.reconfigure(errors='replace')

# --- Configuration ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "dialogue_history.db")


def get_connection():
    """
    Establish a READ-ONLY connection to the dialogue database.
    [P1-4] Uses URI mode with ?mode=ro to prevent accidental writes
    and avoid 'database is locked' conflicts with concurrent writers.
    Returns None and prints an error if the DB file is missing.
    """
    if not os.path.exists(DB_PATH):
        print("[ERROR] Database not found. Run db_initializer.py first.")
        print(f"[PATH] Expected: {DB_PATH}")
        return None
    # [P1-4] Read-only connection to avoid lock conflicts
    return sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)


def _escape_like(keyword: str) -> str:
    """
    [MAMA-FIX] Escape SQL LIKE wildcard characters (% and _).
    Without this, user input like '100%' would become '%100%%',
    causing search logic corruption and potential full-table match.
    """
    return keyword.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')


def search_by_keyword(keyword, limit=20):
    """
    Search dialogue content for a keyword (case-insensitive).
    Returns matching rows as a list of tuples.
    [MAMA-FIX] Uses _escape_like to sanitize LIKE wildcards.
    """
    conn = get_connection()
    if not conn:
        return []

    # [P1-5] Context manager ensures connection is always closed
    try:
        with conn:
            cursor = conn.cursor()
            safe_keyword = _escape_like(keyword)
            cursor.execute('''
                SELECT session_id, seq_number, timestamp, engine, speaker, content
                FROM dialogues
                WHERE content LIKE ? ESCAPE '\\'
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (f'%{safe_keyword}%', limit))
            return cursor.fetchall()
    finally:
        conn.close()


def search_by_session(session_id, limit=50):
    """
    Retrieve all dialogues belonging to a specific session.
    Supports partial matching on session_id.
    [MAMA-FIX] Uses _escape_like to sanitize LIKE wildcards.
    """
    conn = get_connection()
    if not conn:
        return []

    try:
        with conn:
            cursor = conn.cursor()
            safe_session = _escape_like(session_id)
            cursor.execute('''
                SELECT session_id, seq_number, timestamp, engine, speaker, content
                FROM dialogues
                WHERE session_id LIKE ? ESCAPE '\\'
                ORDER BY seq_number ASC
                LIMIT ?
            ''', (f'%{safe_session}%', limit))
            return cursor.fetchall()
    finally:
        conn.close()


def get_recent(count=10):
    """
    Retrieve the N most recent dialogue exchanges.
    """
    conn = get_connection()
    if not conn:
        return []

    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT session_id, seq_number, timestamp, engine, speaker, content
                FROM dialogues
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (count,))
            return cursor.fetchall()
    finally:
        conn.close()


def format_as_markdown(results, title="Retrieved Context", full_content=False, limit_used=None):
    """
    Format query results into a Markdown context block
    suitable for LLM context injection.
    [P2-7] Supports full content display mode.
    [P2-6] Shows truncation warning when results hit limit.
    """
    if not results:
        print("[INFO] No matching records found.")
        return ""

    lines = []
    lines.append(f"\n{'='*60}")
    lines.append(f"  {title}")
    lines.append(f"  Found {len(results)} record(s)")
    lines.append(f"{'='*60}\n")

    for row in results:
        session_id, seq, timestamp, engine, speaker, content = row

        if full_content:
            display = content
        else:
            # [P2-7] Preview expanded from 120 to 300 characters
            display = content[:300] + "..." if len(content) > 300 else content

        lines.append(f"### [{timestamp}] Session: {session_id} | Seq: {seq}")
        lines.append(f"**Speaker**: {speaker} | **Engine**: {engine}")
        lines.append("```")
        lines.append(display)
        lines.append("```")
        lines.append(f"{'-'*60}")

    # [P2-6] Truncation warning
    if limit_used is not None and len(results) >= limit_used:
        lines.append(f"\n⚠️ Results may be truncated (showing {limit_used}). Use --limit N to see more.")

    output = "\n".join(lines)
    print(output)
    return output


def export_to_file(content: str, filepath: str):
    """
    [P2-8] Export formatted results to a Markdown file.
    """
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"\n[OK] Results exported to: {filepath}")
    except Exception as e:
        print(f"[ERROR] Failed to export: {e}")


def main():
    parser = argparse.ArgumentParser(
        description=f"Dialogue History Context Retriever V{__version__}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              python context_retriever.py --query "database"
              python context_retriever.py --session "tech_design"
              python context_retriever.py --recent 5
              python context_retriever.py --query "test" --full
              python context_retriever.py --query "test" --export results.md
              python context_retriever.py --recent 20 --limit 50
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
    parser.add_argument(
        '--limit', type=int, default=None,
        help='Max results to return (overrides default limits)'
    )
    parser.add_argument(
        '--full', action='store_true',
        help='Show full content instead of preview'
    )
    parser.add_argument(
        '--export', type=str, default=None,
        metavar='FILE',
        help='Export results to a Markdown file'
    )

    args = parser.parse_args()

    output = ""

    if args.query:
        limit = args.limit if args.limit else 20
        print(f'[SEARCH] Keyword: "{args.query}" (limit: {limit})')
        results = search_by_keyword(args.query, limit=limit)
        output = format_as_markdown(
            results, title=f'Keyword Search: "{args.query}"',
            full_content=args.full, limit_used=limit
        )

    elif args.session:
        limit = args.limit if args.limit else 50
        print(f'[SEARCH] Session: "{args.session}" (limit: {limit})')
        results = search_by_session(args.session, limit=limit)
        output = format_as_markdown(
            results, title=f'Session: "{args.session}"',
            full_content=args.full, limit_used=limit
        )

    elif args.recent is not None:
        count = args.recent
        print(f'[SEARCH] Recent {count} exchanges')
        results = get_recent(count)
        output = format_as_markdown(
            results, title=f'Recent {count} Exchanges',
            full_content=args.full
        )

    else:
        # Default: show 10 most recent
        print('[INFO] No search flag specified. Showing 10 most recent.')
        results = get_recent(10)
        output = format_as_markdown(
            results, title='Recent 10 Exchanges',
            full_content=args.full
        )

    # [P2-8] Export to file if requested
    if args.export and output:
        export_to_file(output, args.export)


if __name__ == "__main__":
    main()
