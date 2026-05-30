"""
Legacy Archive Digitization Pipeline - Main Entry Point

A modular, config-driven pipeline that replaces the original 3 scripts:
  - organize_archive.py  → ImageMapper + text consolidation
  - polish_archive.py    → LayoutSorter + TextCleaner (pass 1)
  - polish_archive_pass_2.py → TextCleaner (pass 2, merged)

Key improvements over the original:
  1. Single execution: one command replaces 3 sequential script runs.
  2. Atomic Write: uses .tmp + rename to prevent data corruption.
  3. Config-driven: all hardcoded values externalized to config.yaml.
  4. Error handling: proper try/except with logging throughout.
"""

import glob
import logging
import sys
from pathlib import Path

import yaml

from core import ImageMapper, LayoutSorter, TextCleaner

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("pipeline")


def load_config(config_path: Path) -> dict:
    """Load and validate the YAML configuration file."""
    if not config_path.exists():
        logger.error(f"Configuration file not found: {config_path}")
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    logger.info(f"Loaded configuration from {config_path.name}")
    return config


def gather_files(base_dir: Path, config: dict) -> tuple[list[Path], list[Path]]:
    """Gather main text and reading notes files based on config patterns."""
    file_cfg = config["file_patterns"]

    md_files = sorted(
        Path(p) for p in glob.glob(str(base_dir / file_cfg["main_text"]))
    )
    reading_notes = sorted(
        Path(p) for p in glob.glob(str(base_dir / file_cfg["reading_notes"]))
    )

    # Filter out excluded files
    exclude_set = set(file_cfg.get("exclude", []))
    md_files = [f for f in md_files if f.name not in exclude_set]

    logger.info(f"Found {len(md_files)} main text files, {len(reading_notes)} reading note files.")
    return md_files, reading_notes


def consolidate_texts(md_files: list[Path]) -> str:
    """Read and concatenate all markdown files with batch separators."""
    parts: list[str] = []

    for fpath in md_files:
        try:
            content = fpath.read_text(encoding="utf-8")
        except UnicodeDecodeError as e:
            logger.warning(f"Skipping {fpath.name} due to encoding error: {e}")
            continue

        parts.append(f"\n\n<!-- ====== {fpath.name} ====== -->\n\n")
        parts.append(content)

    logger.info(f"Consolidated {len(md_files)} files into raw archive.")
    return "".join(parts)


def consolidate_reading_notes(reading_notes: list[Path], config: dict) -> str:
    """Consolidate reading notes into a single document."""
    out_cfg = config["output"]
    parts: list[str] = [
        f"{out_cfg['notes_title']}\n\n",
        f"{out_cfg['notes_subtitle']}\n\n---\n\n",
    ]

    for fpath in reading_notes:
        try:
            content = fpath.read_text(encoding="utf-8")
        except UnicodeDecodeError as e:
            logger.warning(f"Skipping {fpath.name} due to encoding error: {e}")
            continue

        parts.append(f"\n\n<!-- ====== {fpath.name} ====== -->\n\n")
        parts.append(content)

    return "".join(parts)


def write_atomic(filepath: Path, content: str) -> None:
    """
    Atomic write: write to a .tmp file first, then rename.

    This ensures the target file is never left in a corrupted state,
    even if the process is interrupted mid-write (e.g., power failure).
    This is the same safety mechanism used in Log Parser V2.1.
    """
    temp_path = filepath.with_suffix(".tmp")

    try:
        temp_path.write_text(content, encoding="utf-8")
        temp_path.replace(filepath)
        logger.info(f"Atomic write completed: {filepath.name}")
    except OSError as e:
        logger.error(f"Failed to write {filepath.name}: {e}")
        # Clean up temp file if it exists
        if temp_path.exists():
            temp_path.unlink()
        raise


# ---------------------------------------------------------------------------
# Main Pipeline
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("  Legacy Archive Digitization Pipeline")
    print("=" * 60)

    # Load configuration
    config = load_config(BASE_DIR / "config.yaml")
    out_cfg = config["output"]

    # Gather source files
    md_files, reading_notes = gather_files(BASE_DIR, config)

    # ── Stage 1: Image Mapping & Renaming ──────────────────────
    logger.info("── Stage 1: Image Mapping & Renaming ──")
    mapper = ImageMapper(config)
    mappings = mapper.extract_mappings(md_files)
    mapper.rename_images(BASE_DIR, mappings)

    # ── Stage 2: Text Consolidation ────────────────────────────
    logger.info("── Stage 2: Text Consolidation ──")
    raw_content = consolidate_texts(md_files)

    # ── Stage 3: Layout Sorting ────────────────────────────────
    logger.info("── Stage 3: Layout Sorting ──")
    sorter = LayoutSorter(config)
    sorted_blocks = sorter.split_and_sort(raw_content)

    # ── Stage 4: Text Cleaning ─────────────────────────────────
    logger.info("── Stage 4: Text Cleaning ──")
    cleaner = TextCleaner(config)
    cleaned_blocks = [(header, cleaner.clean(body)) for header, body in sorted_blocks]

    # ── Stage 5: Final Assembly & Atomic Write ─────────────────
    logger.info("── Stage 5: Final Assembly & Atomic Write ──")

    # Build the final archive document
    archive_parts: list[str] = [
        f"{out_cfg['archive_title']}\n\n",
        f"{out_cfg['archive_subtitle']}\n\n---\n\n",
    ]
    for header, body in cleaned_blocks:
        archive_parts.append(f"## 📖 頁碼：{header}\n")
        archive_parts.append(body)
        archive_parts.append("\n\n")

    archive_content = "".join(archive_parts)

    # Atomic write: archive
    write_atomic(BASE_DIR / out_cfg["archive"], archive_content)

    # Atomic write: reading notes
    if reading_notes:
        notes_content = consolidate_reading_notes(reading_notes, config)
        write_atomic(BASE_DIR / out_cfg["reading_notes"], notes_content)

    # ── Done ───────────────────────────────────────────────────
    print("=" * 60)
    print(f"  ✅ Archive: {out_cfg['archive']} ({len(cleaned_blocks)} pages)")
    if reading_notes:
        print(f"  ✅ Notes:   {out_cfg['reading_notes']}")
    print("  All tasks completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
