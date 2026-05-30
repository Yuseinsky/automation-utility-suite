"""
TextCleaner - Applies regex-based cleaning rules to remove translation noise.

Refactored from: polish_archive.py (Lines 49-57) + polish_archive_pass_2.py (Lines 11-26)
Original issues fixed:
  - 🔴 pass_2.py L20: r'^[\\s：:……\\.\\-]*' with MULTILINE stripped leading
    whitespace and dashes, destroying Markdown lists and indented blocks.
    → Fixed: narrowed to r'^[：:]{1}[……\\.\\-]*' (only strips colon+ellipsis)
  - All 10+ regex rules hardcoded inline → config-driven
  - pass_2.py L23: Unused capture group in complex DOTALL regex → simplified
"""

import re
import logging

logger = logging.getLogger(__name__)


class TextCleaner:
    """Applies a sequence of regex cleaning rules loaded from config."""

    def __init__(self, config: dict):
        self.rules: list[tuple[re.Pattern, str, str]] = []

        for rule in config.get("cleaning_rules", []):
            # Determine regex flags
            flags = 0
            flag_str = rule.get("flags", "")
            if flag_str == "MULTILINE":
                flags = re.MULTILINE
            elif flag_str == "DOTALL":
                flags = re.DOTALL

            try:
                compiled = re.compile(rule["pattern"], flags)
            except re.error as e:
                logger.error(f"Invalid regex pattern '{rule['pattern']}': {e}")
                continue

            replacement = rule.get("replacement", "")
            desc = rule.get("desc", "(no description)")
            self.rules.append((compiled, replacement, desc))

        logger.info(f"Loaded {len(self.rules)} cleaning rules from config.")

    def clean(self, text: str) -> str:
        """
        Apply all cleaning rules sequentially to the input text.

        Args:
            text: Raw text content to be cleaned.

        Returns:
            Cleaned text with all rules applied in order.
        """
        for pattern, replacement, desc in self.rules:
            before_len = len(text)
            text = pattern.sub(replacement, text)
            after_len = len(text)

            if before_len != after_len:
                diff = before_len - after_len
                logger.debug(f"Rule '{desc}': removed {diff} characters")

        return text
