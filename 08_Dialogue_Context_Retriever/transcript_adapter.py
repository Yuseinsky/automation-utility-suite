"""
========================================================
Transcript Adapter — IDE Log Format Abstraction Layer
                                            (V1.0.0)
========================================================
Provides a pluggable adapter interface for parsing
IDE session logs. Isolates the core retriever engine
from vendor-specific log formats.

When the IDE updates its log schema, only the adapter
needs to change — the retriever stays untouched.

Supported Adapters:
    - AntigravityAdapter: Antigravity IDE transcript.jsonl

Adding a new adapter:
    1. Subclass TranscriptAdapter
    2. Implement parse_session() and scan_sessions()
    3. Register it in get_adapter()

========================================================
"""

import json
import glob
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


# --- Standardized Data Structures ---
# These are the "universal plugs" that the core retriever
# always works with, regardless of which IDE produced them.

@dataclass
class StandardContext:
    """
    A single dialogue turn, normalized from any IDE format.
    The retriever only ever sees this shape — never raw JSON.
    """
    timestamp: str
    role: str          # "user" | "assistant"
    content: str
    source_type: str   # original event type, e.g. "USER_INPUT"


@dataclass
class SessionSummary:
    """
    A lightweight summary of one IDE session,
    used by the --scan-ide listing view.
    """
    session_id: str
    timestamp: str
    theme: str


# --- Base Adapter Interface ---

class TranscriptAdapter(ABC):
    """
    Abstract base class for all IDE transcript adapters.
    Subclass this and implement the two methods below
    to support a new IDE's log format.
    """

    @abstractmethod
    def scan_sessions(self, brain_path: str) -> List[SessionSummary]:
        """
        Scan the brain folder and return a list of session summaries.
        """
        ...

    @abstractmethod
    def parse_session(self, brain_path: str, session_id: str) -> List[StandardContext]:
        """
        Parse a specific session's transcript and return
        a list of StandardContext objects.
        """
        ...


# --- Antigravity IDE Adapter ---

class AntigravityAdapter(TranscriptAdapter):
    """
    Adapter for Antigravity IDE's transcript.jsonl format.

    Expected path pattern:
        {brain_path}/{session_id}/.system_generated/logs/transcript.jsonl

    Each line is a JSON object with keys like:
        type, source, content, created_at
    """

    TRANSCRIPT_GLOB = os.path.join(
        "*", ".system_generated", "logs", "transcript.jsonl"
    )

    def _get_transcript_path(self, brain_path: str, session_id: str) -> str:
        return os.path.join(
            brain_path, session_id,
            ".system_generated", "logs", "transcript.jsonl"
        )

    @staticmethod
    def _extract_user_request(content: str) -> str:
        """
        Extract the actual user message from the
        <USER_REQUEST>...</USER_REQUEST> wrapper if present.
        """
        if '<USER_REQUEST>' in content:
            parts = content.split('<USER_REQUEST>')
            if len(parts) > 1 and '</USER_REQUEST>' in parts[1]:
                return parts[1].split('</USER_REQUEST>')[0].strip()
        return content.strip()

    def scan_sessions(self, brain_path: str) -> List[SessionSummary]:
        """
        Walk through all transcript.jsonl files under brain_path
        and build a list of SessionSummary objects.
        """
        sessions: List[SessionSummary] = []
        search_pattern = os.path.join(brain_path, self.TRANSCRIPT_GLOB)

        for transcript_path in glob.glob(search_pattern):
            session_id = Path(transcript_path).parents[2].name

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
                            raw = step.get('content', '')
                            theme = self._extract_user_request(raw)[:80].replace('\n', ' ')
                            timestamp = step.get('created_at', 'Unknown Time')
                            break
            except Exception as e:
                theme = f"Error reading file: {e}"

            sessions.append(SessionSummary(
                session_id=session_id,
                timestamp=timestamp,
                theme=theme,
            ))

        sessions.sort(key=lambda s: s.timestamp, reverse=True)
        return sessions

    def parse_session(self, brain_path: str, session_id: str) -> List[StandardContext]:
        """
        Parse one session's transcript.jsonl into a list of
        StandardContext objects (user turns + assistant turns).
        """
        transcript_path = self._get_transcript_path(brain_path, session_id)
        if not os.path.exists(transcript_path):
            return []

        contexts: List[StandardContext] = []

        with open(transcript_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    step = json.loads(line)
                except json.JSONDecodeError:
                    continue

                step_type = step.get('type', '')
                source = step.get('source', '')
                content = step.get('content', '')
                timestamp = step.get('created_at', '')

                if not content:
                    continue

                if source == 'USER_EXPLICIT' and step_type == 'USER_INPUT':
                    content = self._extract_user_request(content)
                    contexts.append(StandardContext(
                        timestamp=timestamp,
                        role="user",
                        content=content,
                        source_type=step_type,
                    ))
                elif source == 'MODEL' and step_type == 'PLANNER_RESPONSE':
                    contexts.append(StandardContext(
                        timestamp=timestamp,
                        role="assistant",
                        content=content,
                        source_type=step_type,
                    ))

        return contexts


# --- Adapter Registry ---

_ADAPTERS = {
    "antigravity": AntigravityAdapter,
    # Future: "cursor": CursorAdapter,
    # Future: "windsurf": WindsurfAdapter,
}


def get_adapter(name: str = "antigravity") -> TranscriptAdapter:
    """
    Factory function to retrieve an adapter by name.
    Defaults to 'antigravity' if not specified.

    Raises KeyError if the adapter name is not registered.
    """
    adapter_cls = _ADAPTERS.get(name)
    if adapter_cls is None:
        available = ", ".join(_ADAPTERS.keys())
        raise KeyError(
            f"Unknown adapter '{name}'. Available: {available}"
        )
    return adapter_cls()
