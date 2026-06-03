"""
========================================================
Context Retriever — Dialogue History Search & Restore
                                            (V4.0)
========================================================
Searches a local SQLite dialogue history database or 
directly scans the IDE brain to rescue broken contexts.
Outputs results in a Markdown-formatted context block 
suitable for injection into a new LLM conversation.

Usage:
    python context_retriever.py --query "encoding"
    python context_retriever.py --session "tech_design"
    python context_retriever.py --recent 5
    python context_retriever.py --scan-ide
    python context_retriever.py --recover-ide "uuid" --export out.md

Options:
    --query       TEXT    Search dialogue content by keyword.
    --session     TEXT    Filter by session ID.
    --recent      INT     Show the N most recent exchanges.
    --scan-ide            Scan the local IDE brain folder for sessions.
    --recover-ide TEXT    Recover a specific IDE session ID safely.
    --limit       INT     Max results to return (default varies by mode).
    --full                Show full content instead of preview.
    --export      FILE    Export results to a Markdown file.

========================================================
"""

import sqlite3
import os
import sys
import argparse
import textwrap
import json
import glob
from pathlib import Path

__version__ = "4.0.0"

# --- Encoding Safety for Windows terminals (CP932/CP950) ---
sys.stdout.reconfigure(encoding='utf-8')

# --- Configuration ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "dialogue_history.db")
IDE_BRAIN_PATH = os.path.expanduser(r"~\.gemini\antigravity-ide\brain")

# The Recovery Prompt
RECOVERY_PROMPT = """<CONTEXT_RECOVERY_PACKAGE>
[SYSTEM PROMPT: CONTEXT RECOVERY INITIATED]
The previous session encountered an unexpected termination (cascade ID mismatch).
A Context Recovery Script (V4.0) has been executed to restore dialogue history.

Please review the following historical dialogue records and synchronize your context state to the timestamp of the last message.
Acknowledge by replying: "Context synchronization complete. Ready for next instructions."
========================================================"""

def get_connection():
    """
    Establish a READ-ONLY connection to the dialogue database.
    Uses URI mode with ?mode=ro to prevent accidental writes
    and avoid 'database is locked' conflicts with concurrent writers.
    Returns None and prints an error if the DB file is missing.
    """
    if not os.path.exists(DB_PATH):
        print("[ERROR] Database not found. Run db_initializer.py first.")
        print(f"[PATH] Expected: {DB_PATH}")
        return None
    # Read-only connection to avoid lock conflicts
    return sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)


def _escape_like(keyword: str) -> str:
    """
    [SECURITY FIX] Escape SQL LIKE wildcard characters (% and _).
    Without this, user input like '100%' would become '%100%%',
    causing search logic corruption and potential full-table match.
    """
    return keyword.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')


def search_by_keyword(keyword, limit=20):
    """
    Search dialogue content for a keyword (case-insensitive).
    Returns matching rows as a list of tuples.
    [SECURITY FIX] Uses _escape_like to sanitize LIKE wildcards.
    """
    conn = get_connection()
    if not conn:
        return []

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
    [SECURITY FIX] Uses _escape_like to sanitize LIKE wildcards.
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


def search_memories_fts(keyword, limit=5):
    """
    Search memories using SQLite FTS5 extension.
    Requires a virtual table 'virtual_memories' to exist in the database.
    Used for high-performance semantic-like full-text search.
    """
    conn = get_connection()
    if not conn:
        return []
    try:
        with conn:
            cursor = conn.cursor()
            # FTS5 uses MATCH for full-text search
            cursor.execute('''
                SELECT session_id, summary, tags, importance, source, updated_at
                FROM virtual_memories
                WHERE virtual_memories MATCH ?
                ORDER BY rank
                LIMIT ?
            ''', (keyword, limit))
            return cursor.fetchall()
    except sqlite3.OperationalError as e:
        print(f"[WARNING] FTS5 search failed (table might not exist): {e}")
        return []
    finally:
        conn.close()


def scan_ide_brain():
    """
    Scan the local IDE brain folder for session logs.
    Reads transcript.jsonl to extract themes and timestamps.
    """
    print(f"[SCAN] Scanning IDE brain folder: {IDE_BRAIN_PATH}")
    if not os.path.exists(IDE_BRAIN_PATH):
        print(f"[ERROR] IDE brain path not found: {IDE_BRAIN_PATH}")
        return

    sessions = []
    # Find all transcript.jsonl files
    search_pattern = os.path.join(IDE_BRAIN_PATH, "*", ".system_generated", "logs", "transcript.jsonl")
    for transcript_path in glob.glob(search_pattern):
        # Extract session id from path (parent's parent's parent)
        session_id = Path(transcript_path).parents[2].name
        
        # Read the first user input as the theme
        theme = "Unknown Theme"
        timestamp = "Unknown Time"
        try:
            with open(transcript_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        step = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if step.get('type') == 'USER_INPUT':
                        content = step.get('content', '')
                        # extract text from <USER_REQUEST> if it exists
                        if '<USER_REQUEST>' in content:
                            parts = content.split('<USER_REQUEST>')
                            if len(parts) > 1 and '</USER_REQUEST>' in parts[1]:
                                content = parts[1].split('</USER_REQUEST>')[0]
                        theme = content.strip()[:80].replace('\n', ' ')
                        timestamp = step.get('created_at', 'Unknown Time')
                        break
        except Exception as e:
            theme = f"Error reading file: {e}"
            
        sessions.append({
            'session_id': session_id,
            'timestamp': timestamp,
            'theme': theme
        })
        
    sessions.sort(key=lambda x: x['timestamp'], reverse=True)
    
    print(f"\n{'='*80}")
    print(f"  IDE Memory Scan Complete - Found {len(sessions)} sessions")
    print(f"{'='*80}\n")
    
    for s in sessions:
        print(f"[{s['timestamp']}] ID: {s['session_id']}")
        print(f"  => Theme: {s['theme']}...\n")

def recover_ide_session(session_id):
    """
    Recover a specific IDE session ID by reading transcript.jsonl
    and generating a Markdown Recovery Package.
    """
    print(f"[RECOVER] Attempting to recover IDE session: {session_id}")
    transcript_path = os.path.join(IDE_BRAIN_PATH, session_id, ".system_generated", "logs", "transcript.jsonl")
    if not os.path.exists(transcript_path):
        print(f"[ERROR] transcript.jsonl not found for session {session_id}")
        return ""
        
    lines = []
    lines.append(RECOVERY_PROMPT)
    lines.append("")
    
    try:
        with open(transcript_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    step = json.loads(line)
                except json.JSONDecodeError:
                    continue
                step_type = step.get('type')
                source = step.get('source')
                content = step.get('content', '')
                timestamp = step.get('created_at', '')
                
                if not content:
                    continue
                    
                if source == 'USER_EXPLICIT' and step_type == 'USER_INPUT':
                    # Extract text from <USER_REQUEST> if it exists
                    if '<USER_REQUEST>' in content:
                        parts = content.split('<USER_REQUEST>')
                        if len(parts) > 1 and '</USER_REQUEST>' in parts[1]:
                            content = parts[1].split('</USER_REQUEST>')[0].strip()
                    lines.append(f"### USER [{timestamp}]")
                    lines.append(content)
                    lines.append(f"{'-'*60}\n")
                elif source == 'MODEL' and step_type == 'PLANNER_RESPONSE':
                    lines.append(f"### AI ASSISTANT [{timestamp}]")
                    lines.append(content)
                    lines.append(f"{'-'*60}\n")
    except Exception as e:
        print(f"[ERROR] Failed to read transcript: {e}")
        return ""
        
    lines.append("\n<END_OF_RECOVERY_PACKAGE>")
    
    output = "\n".join(lines)
    print(f"[OK] Recovery package generated for {session_id} (Length: {len(output)} chars)")
    return output

def format_as_markdown(results, title="Retrieved Context", full_content=False, limit_used=None):
    """
    Format query results into a Markdown context block
    suitable for LLM context injection.
    Supports full content display mode.
    Shows truncation warning when results hit limit.
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
            display = content[:300] + "..." if len(content) > 300 else content

        lines.append(f"### [{timestamp}] Session: {session_id} | Seq: {seq}")
        lines.append(f"**Speaker**: {speaker} | **Engine**: {engine}")
        lines.append("```")
        lines.append(display)
        lines.append("```")
        lines.append(f"{'-'*60}")

    # Truncation warning
    if limit_used is not None and len(results) >= limit_used:
        lines.append(f"\n⚠️ Results may be truncated (showing {limit_used}). Use --limit N to see more.")

    output = "\n".join(lines)
    print(output)
    return output


def export_to_file(content: str, filepath: str):
    """
    Export formatted results to a Markdown file.
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
              python context_retriever.py --scan-ide
              python context_retriever.py --recover-ide "uuid" --export out.md
        """)
    )
    parser.add_argument('--query', type=str, default=None, help='Search keyword')
    parser.add_argument('--session', type=str, default=None, help='Filter by session ID')
    parser.add_argument('--recent', type=int, default=None, help='Show N most recent exchanges')
    parser.add_argument('--scan-ide', action='store_true', help='Scan IDE brain folder for sessions')
    parser.add_argument('--recover-ide', type=str, default=None, help='Recover a specific IDE session ID')
    parser.add_argument('--limit', type=int, default=None, help='Max results to return')
    parser.add_argument('--full', action='store_true', help='Show full content instead of preview')
    parser.add_argument('--export', type=str, default=None, metavar='FILE', help='Export results to a Markdown file')

    args = parser.parse_args()
    output = ""

    if args.scan_ide:
        scan_ide_brain()
        return
        
    elif args.recover_ide:
        output = recover_ide_session(args.recover_ide)
        if args.export and output:
            export_to_file(output, args.export)
        elif output:
            print("\n[HINT] Use --export FILE to save this recovery package.")
        return

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

    # Export to file if requested
    if args.export and output:
        export_to_file(output, args.export)


if __name__ == "__main__":
    main()
