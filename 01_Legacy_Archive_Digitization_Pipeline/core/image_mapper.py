"""
ImageMapper - Extracts page-to-image mappings and renames files.

Refactored from: organize_archive.py (Lines 11-43)
Original issues fixed:
  - Hardcoded LINE album date prefixes (L33-35) → config-driven
  - Hardcoded output prefix (L38) → config-driven
  - Hardcoded regex pattern (L19) → config-driven
  - No error handling on shutil.copy2 (L40) → try/except added
"""

import re
import shutil
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ImageMapper:
    """Maps raw image files to page numbers and performs safe copy/rename."""

    def __init__(self, config: dict):
        img_cfg = config["image_mapping"]
        self.pattern = re.compile(img_cfg["page_regex"])
        self.source_prefixes = img_cfg["source_prefixes"]
        self.output_prefix = img_cfg["output_prefix"]
        self.extension = img_cfg.get("extension", ".jpg")

    def extract_mappings(self, md_files: list[Path]) -> dict[str, str]:
        """
        Scan markdown files for page-number-to-raw-image-number mappings.

        Returns:
            dict mapping raw_image_number (str) → page_number (str)
        """
        mapping: dict[str, str] = {}

        for fpath in md_files:
            try:
                content = fpath.read_text(encoding="utf-8")
            except UnicodeDecodeError as e:
                logger.warning(f"Skipping {fpath.name} due to encoding error: {e}")
                continue

            matches = self.pattern.findall(content)
            for page_num, raw_img_num in matches:
                mapping[raw_img_num] = page_num

        logger.info(f"Extracted {len(mapping)} image-to-page mappings.")
        return mapping

    def rename_images(self, base_dir: Path, mappings: dict[str, str]) -> int:
        """
        Copy and rename images based on extracted mappings.

        Uses safe copy (shutil.copy2) with error handling.
        Skips files that already exist at the destination.

        Returns:
            Number of images successfully renamed.
        """
        renamed_count = 0

        for raw_img_num, page_num in mappings.items():
            src = self._find_source(base_dir, raw_img_num)
            if src is None:
                logger.warning(
                    f"Source image not found for raw #{raw_img_num} "
                    f"(tried prefixes: {self.source_prefixes})"
                )
                continue

            dst = base_dir / f"{self.output_prefix}{page_num}{self.extension}"
            if dst.exists():
                logger.debug(f"Skipping {dst.name} (already exists)")
                continue

            try:
                shutil.copy2(src, dst)
                renamed_count += 1
            except OSError as e:
                logger.error(f"Failed to copy {src.name} → {dst.name}: {e}")

        logger.info(f"Renamed {renamed_count} images successfully.")
        return renamed_count

    def _find_source(self, base_dir: Path, raw_img_num: str) -> Path | None:
        """Search for the source image file across all configured prefixes."""
        for prefix in self.source_prefixes:
            candidate = base_dir / f"{prefix}{raw_img_num}{self.extension}"
            if candidate.exists():
                return candidate
        return None
