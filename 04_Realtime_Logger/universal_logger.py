"""
Universal AI Dialogue Logger
==============================
A lightweight, event-driven dialogue logging framework that captures
AI conversation history into a local SQLite database and automatically
exports beautifully formatted Markdown transcripts.

Designed for any AI integration — OpenAI, Gemini, Claude, Discord Bots,
or custom LLM pipelines. Zero external dependencies beyond the Python
standard library.

Usage:
    from universal_logger import DialogueLogger

    logger = DialogueLogger()
    logger.log_exchange("session_001", "Hello!", "Hi there!", engine="GPT-4")
"""
import sqlite3
import os
from datetime import datetime

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DEFAULT_DB_NAME = "dialogue_memory.db"
DEFAULT_FLUSH_THRESHOLD = 10
DEFAULT_LOG_DIR = "Formatted_Logs"


class DialogueLogger:
    """Event-driven AI dialogue logger with SQLite persistence and
    automatic Markdown export.

    Architecture:
        1. Every call to ``log_exchange()`` immediately inserts the
           dialogue pair into SQLite via a single atomic transaction.
        2. An internal counter tracks the number of exchanges per
           session. When the configured threshold is reached, the
           logger automatically exports a Markdown transcript and
           resets the counter.

    This design eliminates the need for external schedulers, polling
    loops, or temporary buffer files — removing entire categories of
    bugs (race conditions, data loss from overwrites, stale file locks).
    """

    def __init__(
        self,
        db_path: str = DEFAULT_DB_NAME,
        auto_flush_threshold: int = DEFAULT_FLUSH_THRESHOLD,
        log_dir: str = DEFAULT_LOG_DIR,
    ):
        """Initialize the logger and ensure the database schema exists.

        Args:
            db_path: Path to the SQLite database file.
            auto_flush_threshold: Number of exchanges before auto-export.
            log_dir: Directory for Markdown transcript output.
        """
        self.db_path = db_path
        self.auto_flush_threshold = auto_flush_threshold
        self.log_dir = log_dir
        
        self._session_counters = {}

        self._init_db()

    # ------------------------------------------------------------------
    # Database Layer
    # ------------------------------------------------------------------

    def _init_db(self) -> None:
        """Create the dialogues table if it does not exist."""
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS dialogues (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id  TEXT    NOT NULL,
                seq_number  INTEGER NOT NULL,
                timestamp   TEXT    NOT NULL,
                engine      TEXT    DEFAULT 'Unknown',
                speaker     TEXT    NOT NULL,
                content     TEXT    NOT NULL
            )
            """
        )
        conn.commit()
        conn.close()

    def _get_session_count(self, session_id: str) -> int:
        """Return the number of exchange-pairs already stored for a session."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            "SELECT COUNT(*) FROM dialogues "
            "WHERE session_id = ? AND speaker = 'User'",
            (session_id,),
        )
        count = cursor.fetchone()[0]
        conn.close()
        return count

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def log_exchange(
        self,
        session_id: str,
        user_text: str,
        assistant_text: str,
        engine: str = "Unknown",
    ) -> int:
        """Record a single user-assistant exchange to the database.

        This method writes both the user message and the assistant
        response in a single atomic SQLite transaction, guaranteeing
        that data is never lost — even during unexpected shutdowns.

        Args:
            session_id:     Unique identifier for the conversation session.
            user_text:      The user's input message.
            assistant_text: The AI assistant's response.
            engine:         Name of the AI engine (e.g. "GPT-4", "Gemini").

        Returns:
            The sequence number assigned to this exchange.
        """
        if session_id not in self._session_counters:
            self._session_counters[session_id] = self._get_session_count(session_id)
            
        self._session_counters[session_id] += 1
        seq = self._session_counters[session_id]
        
        ts = datetime.now().astimezone().isoformat()

        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                "INSERT INTO dialogues "
                "(session_id, seq_number, timestamp, engine, speaker, content) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (session_id, seq, ts, engine, "User", user_text),
            )
            conn.execute(
                "INSERT INTO dialogues "
                "(session_id, seq_number, timestamp, engine, speaker, content) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (session_id, seq, ts, engine, "Assistant", assistant_text),
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

        print(f"[LOG] seq {seq} recorded for session '{session_id}'.")

        # Auto-flush check
        if seq % self.auto_flush_threshold == 0:
            print(
                f"[AUTO-FLUSH] Threshold ({self.auto_flush_threshold}) reached. "
                f"Exporting Markdown..."
            )
            self.export_to_markdown(session_id)

        return seq

    # ------------------------------------------------------------------
    # Markdown Export
    # ------------------------------------------------------------------

    def export_to_markdown(self, session_id: str) -> str:
        """Export all exchanges for a session as a Markdown document.

        The output file is saved under ``log_dir/YYYY-MM/`` with an
        auto-generated filename containing the timestamp and session ID.

        Args:
            session_id: The session to export.

        Returns:
            The absolute path to the generated Markdown file.
        """
        conn = sqlite3.connect(self.db_path)
        rows = conn.execute(
            "SELECT seq_number, timestamp, engine, speaker, content "
            "FROM dialogues WHERE session_id = ? ORDER BY id",
            (session_id,),
        ).fetchall()
        conn.close()

        if not rows:
            print(f"[WARN] No data found for session '{session_id}'. Skipping.")
            return ""

        # Build Markdown content
        lines = [
            f"# Dialogue Log: {session_id}",
            f"**Exported At**: {datetime.now().astimezone().isoformat()}",
            f"**Total Exchanges**: {rows[-1][0]}",
            "",
            "---",
            "",
        ]

        current_engine = None
        for seq, ts, engine, speaker, content in rows:
            if engine != current_engine:
                current_engine = engine
                lines.append(f"### Engine: {current_engine}")
                lines.append("---")
                lines.append("")
            lines.append(f"**{speaker}**:\n{content}")
            lines.append("")
            if speaker == "Assistant":
                lines.append("---")
                lines.append("")

        lines.append("> *(Export completed by DialogueLogger)*")

        # Write to file
        now = datetime.now().astimezone()
        month_dir = os.path.join(self.log_dir, now.strftime("%Y-%m"))
        os.makedirs(month_dir, exist_ok=True)

        safe_id = session_id[:30].replace(" ", "_")
        filename = f"Log_{now.strftime('%Y%m%d_%H%M')}_{safe_id}.md"
        output_path = os.path.join(month_dir, filename)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        print(f"[EXPORT] Markdown saved to: {output_path}")
        return os.path.abspath(output_path)

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def query_session(self, session_id: str) -> list[dict]:
        """Retrieve all exchanges for a given session as a list of dicts.

        Args:
            session_id: The session to query.

        Returns:
            A list of dicts with keys: seq, timestamp, engine, speaker, content.
        """
        conn = sqlite3.connect(self.db_path)
        rows = conn.execute(
            "SELECT seq_number, timestamp, engine, speaker, content "
            "FROM dialogues WHERE session_id = ? ORDER BY id",
            (session_id,),
        ).fetchall()
        conn.close()

        return [
            {
                "seq": r[0],
                "timestamp": r[1],
                "engine": r[2],
                "speaker": r[3],
                "content": r[4],
            }
            for r in rows
        ]
