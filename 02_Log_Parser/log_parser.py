"""
=============================================================================
[System Architecture & Automation Script: Log Context Parsing & Persona Tagging]
=============================================================================
Project: AI Conversation Log Processor
Author: Systems Architect & AI Automation Agent
Date: 2026-04-29

[Architectural Rationale]

1. The Problem:
   When parsing large volumes of AI conversation logs (tens of thousands of characters),
   raw outputs are unstructured plain text. 
   As the dialogue progresses, the AI persona or role changes dynamically.
   Adding correct conversation speaker headers manually is extremely inefficient.

2. The Solution:
   Rather than performing manual editing, this script models log structures 
   by defining line number ranges for both User and AI roles, and automates 
   the tagging process.

3. Technical Implementation:
   Reads lines of the log file, maps line numbers to the user and AI persona ranges,
   injects correct labels, and saves the formatted markdown file.
=============================================================================
"""

import os
import sys

def process_log(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()

    # Define User ranges (start_line, end_line)
    user_ranges = [
        (1, 1), (19, 19), (47, 51), (72, 78), (102, 104), (121, 124),
        (145, 147), (159, 161), (190, 190), (218, 226), (247, 247),
        (276, 280), (300, 304), (345, 347), (369, 373), (401, 405)
    ]

    # Define AI persona ranges ((start_line, end_line), label_name)
    ai_persona_ranges = [
        ((3, 143), "**[Assistant (Base)]**: "),
        ((149, 157), "**[Assistant (Specialized - Observer)]**: "),
        ((163, 216), "**[Assistant (Specialized - Analyst)]**: "),
        ((228, 343), "**[Assistant (Specialized - Expert)]**: "),
        ((349, 441), "**[Assistant (Specialized - Final)]**: ")
    ]

    def get_speaker(line_num):
        for start, end in user_ranges:
            if start <= line_num <= end:
                return "**User**: "
        for (start, end), name in ai_persona_ranges:
            if start <= line_num <= end:
                return name
        return None

    new_lines = []
    current_speaker = None

    for i, line in enumerate(lines):
        line_num = i + 1
        speaker = get_speaker(line_num)
        
        # Insert header when speaker changes
        if speaker and speaker != current_speaker:
            if new_lines and new_lines[-1] != "":
                new_lines.append("")
            new_lines.append(speaker)
            current_speaker = speaker
        
        new_lines.append(line)

    # Overwrite and update file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(new_lines))
    print(f"Success: Processed and updated {file_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python log_parser.py <path_to_markdown_log>")
    else:
        process_log(sys.argv[1])
