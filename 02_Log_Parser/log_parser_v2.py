"""
=============================================================================
Log Parser V2.1 — Multi-Speaker Conversation Log Processor
=============================================================================
Project : AI Conversation Log Processor (V2.1 - Visual Formatting Upgrade)
Date    : 2026-05-30

[Architectural Overview]

1. Problem:
   Raw AI conversation logs contain dynamic speaker changes (users and AI
   personas that rename themselves mid-conversation). Manually tagging
   thousands of lines is impractical. Web-copied logs also contain junk
   lines and inconsistent formatting.

2. Solution:
   Uses regex-based pattern matching (defined in an external YAML config)
   to dynamically detect speaker changes, reformat headers into clean
   Markdown headings, strip junk lines, and inject a summary report.
   Supports multiple users, multiple AIs, and mid-conversation name changes.

3. Design Principles:
   - Zero hardcoded names: all patterns defined in parser_config.yaml
   - Safe I/O: original files are NEVER modified
   - Portable: output paths are relative to the script location
   - Idempotent: safe to run multiple times on the same input
   - Fault-tolerant: unmatched lines are labeled, not crashed
   - Visual clarity: reformatted headers + auto-generated summary
=============================================================================
"""

import os
import sys
import re
import argparse
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Error: 'pyyaml' is not installed.")
    print("Please run: pip install pyyaml")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Configuration Loader
# ---------------------------------------------------------------------------
def load_config(script_dir: Path) -> dict:
    """Load parser_config.yaml from the same directory as this script."""
    config_path = script_dir / "parser_config.yaml"
    if not config_path.exists():
        print(f"Error: Configuration file not found: {config_path}")
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Validate required fields
    if "speaker_pattern" not in config:
        print("Error: 'speaker_pattern' not found in config.")
        sys.exit(1)

    return config


# ---------------------------------------------------------------------------
# Line Ending Detection
# ---------------------------------------------------------------------------
def detect_line_ending(raw_content: str) -> str:
    """Detect the dominant line ending style in the raw content."""
    crlf_count = raw_content.count("\r\n")
    lf_count = raw_content.count("\n") - crlf_count
    return "\r\n" if crlf_count > lf_count else "\n"


# ---------------------------------------------------------------------------
# Core Processing Engine
# ---------------------------------------------------------------------------
def process_log(input_path: Path, output_path: Path, config: dict) -> dict:
    """
    Process a conversation log file.

    Returns a stats dict with processing metrics.
    """
    stats = {
        "total_lines": 0,
        "speaker_changes": 0,
        "unknown_blocks": 0,
        "speakers_found": [],
    }

    # --- Read (read-only, never write back) ---
    with open(input_path, "r", encoding="utf-8", newline="") as f:
        raw_content = f.read()

    line_ending = detect_line_ending(raw_content)
    lines = raw_content.split(line_ending)
    stats["total_lines"] = len(lines)

    # --- Compile regex from config ---
    speaker_regex = re.compile(config["speaker_pattern"])
    unknown_label = config.get("error_handling", {}).get(
        "unknown_label", "[Unknown Speaker]"
    )
    strategy = config.get("error_handling", {}).get("strategy", "continue")

    # --- V2.1: Load reformat & ignore settings ---
    reformat_cfg = config.get("reformat", {})
    reformat_enabled = reformat_cfg.get("enabled", False)
    header_template = reformat_cfg.get("header_template", "### 💬 {name}")
    remove_original = reformat_cfg.get("remove_original_header", True)

    ignore_cfg = config.get("ignore_lines", {})
    ignore_patterns = [re.compile(p) for p in ignore_cfg.get("patterns", [])]

    # --- Process lines ---
    new_lines = []
    current_speaker = None
    has_speaker_been_set = False

    for line in lines:
        stripped = line.strip()

        # --- V2.1: Skip ignored lines ---
        if ignore_patterns and any(p.match(stripped) for p in ignore_patterns):
            continue  # Remove junk lines entirely

        match = speaker_regex.match(stripped)

        if match:
            # This line IS a speaker header
            speaker_name = match.group("name").strip()

            if speaker_name != current_speaker:
                stats["speaker_changes"] += 1
                current_speaker = speaker_name

                if speaker_name not in stats["speakers_found"]:
                    stats["speakers_found"].append(speaker_name)

                has_speaker_been_set = True

            # --- V2.1: Reformat or keep original ---
            if reformat_enabled and remove_original:
                new_lines.append("")  # Blank line separator
                new_lines.append(header_template.format(name=speaker_name))
            else:
                new_lines.append(line)

        else:
            # This line is NOT a speaker header
            if not has_speaker_been_set and line.strip():
                # Content before any speaker header detected
                if strategy == "strict":
                    print(
                        f"Error: Content found before any speaker header. "
                        f"Line: '{line[:80]}...'"
                    )
                    sys.exit(1)
                else:
                    if current_speaker != unknown_label:
                        stats["unknown_blocks"] += 1
                        current_speaker = unknown_label
                        new_lines.append("")
                        new_lines.append(f"**{unknown_label}**：")

            new_lines.append(line)

    # --- Write to output (safe: temp file → rename) ---
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = output_path.with_suffix(".tmp")

    with open(temp_path, "w", encoding="utf-8", newline="") as f:
        # --- V2.1: Write summary header ---
        summary_cfg = config.get("summary", {})
        if summary_cfg.get("enabled", False):
            title = summary_cfg.get("title", "📊 Log Parser 解析報告")
            f.write(f"> **{title}**{line_ending}")
            f.write(f"> - **總行數**：{stats['total_lines']} 行{line_ending}")
            f.write(f"> - **發言者切換次數**：{stats['speaker_changes']} 次{line_ending}")
            speakers_count = len(stats['speakers_found'])
            f.write(f"> - **參與對話者 (共 {speakers_count} 位)**：{line_ending}")
            for i, name in enumerate(stats['speakers_found'], 1):
                f.write(f">   {i}. `{name}`{line_ending}")
            f.write(f">{line_ending}")
            f.write(f"> ---{line_ending}{line_ending}")

        f.write(line_ending.join(new_lines))

    # Atomic rename (safe: if crash during write, original + temp are separate)
    if output_path.exists():
        output_path.unlink()
    temp_path.rename(output_path)

    return stats


# ---------------------------------------------------------------------------
# Output Path Resolution
# ---------------------------------------------------------------------------
def resolve_output_path(
    input_path: Path, script_dir: Path, config: dict, user_output: str = None
) -> Path:
    """
    Determine the output file path.

    Priority:
    1. User-specified --output path
    2. Config-defined output directory (relative to script)
    3. Fallback: next to input file with suffix
    """
    suffix = config.get("output", {}).get("suffix", "_processed")
    stem = input_path.stem + suffix
    ext = input_path.suffix

    if user_output:
        return Path(user_output)

    out_dir_name = config.get("output", {}).get("directory", "")
    if out_dir_name:
        out_dir = script_dir / out_dir_name
    else:
        out_dir = input_path.parent

    return out_dir / f"{stem}{ext}"


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Log Parser V2: Multi-speaker conversation log processor.",
        epilog="Example: python log_parser_v2.py chat_log.md --output result.md",
    )
    parser.add_argument("input", help="Path to the input log file.")
    parser.add_argument(
        "--output", "-o",
        help="Custom output file path. Default: <script_dir>/output/<name>_processed.md",
        default=None,
    )
    parser.add_argument(
        "--config", "-c",
        help="Custom config file path. Default: parser_config.yaml next to this script.",
        default=None,
    )

    args = parser.parse_args()

    # Resolve paths
    script_dir = Path(__file__).resolve().parent
    input_path = Path(args.input).resolve()

    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)

    # Load config
    if args.config:
        config_path = Path(args.config).resolve()
        if not config_path.exists():
            print(f"Error: Config file not found: {config_path}")
            sys.exit(1)
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    else:
        config = load_config(script_dir)

    # Resolve output
    output_path = resolve_output_path(input_path, script_dir, config, args.output)

    # Process
    try:
        print(f"Processing: {input_path}")
        print(f"Output to:  {output_path}")
        print("-" * 60)

        stats = process_log(input_path, output_path, config)

        # Report
        print(f"[OK] Processing complete.")
        print(f"  Total lines:      {stats['total_lines']}")
        print(f"  Speaker changes:  {stats['speaker_changes']}")
        print(f"  Unknown blocks:   {stats['unknown_blocks']}")
        print(f"  Speakers found:   {len(stats['speakers_found'])}")
        for i, name in enumerate(stats["speakers_found"], 1):
            safe_name = name.encode(sys.stdout.encoding or 'utf-8', errors='replace').decode(sys.stdout.encoding or 'utf-8')
            print(f"    {i}. {safe_name}")
        print(f"\nOriginal file preserved: {input_path}")
        print(f"Processed output saved:  {output_path}")

    except UnicodeDecodeError as e:
        print(f"[FATAL] Encoding error: {e}")
        print("The input file may not be UTF-8. Original file is untouched.")
        sys.exit(1)
    except Exception as e:
        print(f"[FATAL] Unexpected error: {e}")
        print("Original file is untouched.")
        sys.exit(1)


if __name__ == "__main__":
    main()
