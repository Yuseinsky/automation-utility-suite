"""
=============================================================
  Job Description Text Cleaner (Job Cleaner)
  Version: 3.0

  Design Principles:
  - Remove HTML clutter (tags, navigation, advertising banners)
  - Do not alter or delete the actual content of job postings
  - Maintain 100% of salary, overtime rules, employment types, etc.
  - Algorithms are designed for simplicity and maximum data integrity

  Input: URL or path to a local .txt file
  Output: Cleaned .md text file saved to "Cleaned" directory
  Safety: Raw files are strictly read-only and never modified
=============================================================
"""

__version__ = "3.0"

import argparse
import os
import re
import sys
from datetime import datetime

sys.stdout.reconfigure(errors='replace')

# ============================================================
# Configurations
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Navigation / Menu tags and class keywords for HTML cleaning
NAV_TAGS = ['nav', 'header', 'footer']

# Exact-prefix class names for ad/junk detection.
# IMPORTANT: Each entry must be a full class name or unambiguous prefix.
# DO NOT use short fragments like 'ad-' which cause false positives
# (e.g. 'cad-operator', 'admin-panel', 'advisor-section').
JUNK_CLASSES = [
    'cookie-banner', 'cookie-consent', 'cookie-notice',
    'advertisement', 'ad-banner', 'ad-container', 'ad-slot', 'ad-wrapper',
    'popup', 'modal-overlay', 'overlay',
    'sidebar',
    'breadcrumb',
    'social-share', 'sns-share', 'share-button', 'share-buttons',
    'global-nav', 'global-header', 'global-footer',
    'site-header', 'site-footer',
]

# Skip lines that are exactly equal to these UI elements
# Matches exact strings only to prevent false positives in paragraph text
UI_EXACT_MATCH_BLACKLIST = {
    'Image',
    '▼',
    '応募画面へ進む',
    '気になる',
    '問題を報告する',
    'ApplySuccess',
}

# ============================================================
# HTML Cleaning Engine
# ============================================================

def clean_html(html_content):
    """
    Extract meaningful text content from raw HTML.

    Principles:
    - Remove non-content blocks like <script>, <style>, <nav>, <header>, <footer>
    - Filter out cookies and ad-related divs
    - Preserve all text within <main>, <article>, <section>, and <div>
    - Strict design: When in doubt, preserve the text!
    """
    from bs4 import BeautifulSoup

    # Graceful parser fallback: lxml (fast) → html.parser (built-in)
    try:
        soup = BeautifulSoup(html_content, 'lxml')
    except Exception:
        soup = BeautifulSoup(html_content, 'html.parser')

    # Step 1: Remove script and style tags (definitely not text content)
    for tag in soup.find_all(['script', 'style', 'noscript', 'iframe']):
        tag.decompose()

    # Step 2: Remove navigation blocks (<nav>, <header>, <footer>)
    for tag_name in NAV_TAGS:
        for tag in soup.find_all(tag_name):
            tag.decompose()

    # Step 3: Remove ad and cookie blocks based on class names
    # Uses exact class name matching to prevent false positives
    for junk_class in JUNK_CLASSES:
        for tag in soup.find_all(class_=lambda c: c and junk_class in c.split()):
            tag.decompose()

    # Step 4: Extract remaining text separated by newlines
    text = soup.get_text(separator='\n')

    return text


# ============================================================
# Text Formatting Engine (Shared by HTML and Raw Text)
# ============================================================

def clean_text(raw_text):
    """
    Clean formatting without deleting any actual information.

    Format Operations:
    - Skip lines that exactly match UI residual text
    - Condense multiple consecutive blank lines down to a single blank line
    - Strip leading and trailing whitespaces on each line
    - Preserve all languages (Japanese, Chinese, English) and special characters
    """
    # Step 1: Filter out UI blacklist items
    lines = raw_text.split('\n')
    filtered = '\n'.join(
        line.strip() for line in lines
        if line.strip() not in UI_EXACT_MATCH_BLACKLIST
    )

    # Step 2: Condense consecutive blank lines into a single blank line
    result = re.sub(r'\n\s*\n', '\n\n', filtered)

    # Step 3: Trim leading/trailing blank lines
    return result.strip()


# ============================================================
# URL Fetch Engine
# ============================================================

def fetch_url(url):
    """
    Fetch webpage HTML from the specified URL.

    Returns None if blocked by anti-scraping measures.
    """
    import requests

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
        'Accept-Language': 'ja,en;q=0.9',
    }

    try:
        print(f"🌐 Fetching URL...")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        response.encoding = response.apparent_encoding  # Auto-detect encoding (e.g. Shift-JIS / UTF-8)

        print(f"✅ Fetch success! (Status Code: {response.status_code})")
        return response.text

    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response else None
        if status == 403:
            print(f"🚫 Blocked by anti-scraping system! (403 Forbidden)")
        elif status == 429:
            print(f"🚫 Request rate limit exceeded! (429 Too Many Requests)")
        else:
            print(f"❌ HTTP Error: {e}")
        return None

    except requests.exceptions.ConnectionError:
        print(f"❌ Connection error. Unable to reach target host.")
        return None

    except requests.exceptions.Timeout:
        print(f"⏱️ Request timed out (exceeded 15 seconds).")
        return None

    except Exception as e:
        print(f"❌ Unexpected error occurred: {e}")
        return None


# ============================================================
# Local File Encoding Detection
# ============================================================

def _read_local_file(filepath):
    """
    Read a local text file with automatic encoding detection.

    Attempts UTF-8 first (most common), then falls back to
    charset_normalizer / chardet for Japanese encodings
    (Shift-JIS, EUC-JP, ISO-2022-JP, etc.).
    Final fallback: UTF-8 with replacement characters.
    """
    # Attempt 1: Try UTF-8 (most common modern encoding)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        pass

    # Attempt 2: Auto-detect encoding via charset_normalizer or chardet
    raw_bytes = open(filepath, 'rb').read()

    try:
        from charset_normalizer import from_bytes
        result = from_bytes(raw_bytes).best()
        if result:
            detected_encoding = result.encoding
            print(f"🔍 Detected encoding: {detected_encoding}")
            return str(result)
    except ImportError:
        pass

    try:
        import chardet
        detection = chardet.detect(raw_bytes)
        detected_encoding = detection.get('encoding', 'utf-8')
        print(f"🔍 Detected encoding: {detected_encoding} (confidence: {detection.get('confidence', 'N/A')})")
        return raw_bytes.decode(detected_encoding, errors='replace')
    except ImportError:
        pass

    # Attempt 3: Final fallback — UTF-8 with replacement
    print("⚠️ No encoding detection library found. Using UTF-8 with replacement characters.")
    return raw_bytes.decode('utf-8', errors='replace')


# ============================================================
# Filename Sanitization
# ============================================================

def _sanitize_filename(name):
    """
    Remove or replace characters that are illegal in Windows filenames.
    Illegal characters: < > : " / \\ | ? *
    """
    return re.sub(r'[<>:"/\\|?*]', '_', name).strip('. ')


# ============================================================
# Main Processing Method
# ============================================================

def wash(source, company_name=None, output_dir=None):
    """
    Main job cleaner process.

    Args:
        source: URL string or local text file path
        company_name: Name of the company for output file names
        output_dir: Custom output base directory (default: script's own directory)

    Returns:
        dict: {"success": bool, "output_path": str or None, "error": str or None}
    """
    print("=" * 60)
    print(f"  Job Description Text Cleaner 🧺 V{__version__}")
    print("  Rule: Clean formats only, preserve original text data!")
    print("=" * 60)

    # Resolve output directories
    base = output_dir or BASE_DIR
    cleaned_dir = os.path.join(base, "Cleaned")
    raw_dir = os.path.join(base, "Raw")

    # Initialize output directories
    os.makedirs(cleaned_dir, exist_ok=True)
    os.makedirs(raw_dir, exist_ok=True)

    # Generate timestamp once for consistent naming
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")

    is_url = source.startswith('http')
    raw_content = None

    # ----------------------------------------------------------
    # Step 1: Retrieve raw content
    # ----------------------------------------------------------
    if is_url:
        print(f"\n📥 Mode: URL Fetch")
        print(f"   Target URL: {source}")

        raw_content = fetch_url(source)

        if raw_content is None:
            msg = "URL fetch failed. Use manual fallback (Ctrl+A → paste to .txt)."
            print(f"\n{'=' * 60}")
            print(f"⚠️  {msg}")
            print("   1. Open the URL in your web browser.")
            print("   2. Select all text (Ctrl+A) and copy (Ctrl+C).")
            print("   3. Paste the contents into a local .txt file.")
            print('   4. Re-run: wash("path_to_txt_file.txt", "company_name")')
            print("=" * 60)
            return {"success": False, "output_path": None, "error": msg}

        # Save raw backup HTML
        company_folder = _sanitize_filename(company_name) if company_name else 'unknown'
        raw_company_dir = os.path.join(raw_dir, company_folder)
        os.makedirs(raw_company_dir, exist_ok=True)

        raw_filename = f"raw_{timestamp}_{company_folder}.html"
        raw_path = os.path.join(raw_company_dir, raw_filename)
        with open(raw_path, 'w', encoding='utf-8') as f:
            f.write(raw_content)
        print(f"💾 Raw HTML backed up → {raw_path}")

    else:
        print(f"\n📥 Mode: Local File Fallback")
        print(f"   Source File: {source}")

        if not os.path.exists(source):
            msg = f"File not found: {source}"
            print(f"❌ {msg}")
            return {"success": False, "output_path": None, "error": msg}

        raw_content = _read_local_file(source)

        print(f"✅ Loaded local file (Length: {len(raw_content)} chars)")

    # ----------------------------------------------------------
    # Step 2: Determine document type (HTML vs Plain Text)
    # ----------------------------------------------------------
    is_html = bool(re.search(r'<html|<body|<div|<script', raw_content, re.IGNORECASE))

    if is_html:
        print("\n🔍 HTML markup detected → Launching HTML Cleaning Engine")
        text_content = clean_html(raw_content)
    else:
        print("\n🔍 Plain text detected → Direct format cleaning (No content deletion)")
        text_content = raw_content

    # ----------------------------------------------------------
    # Step 3: Format cleanup
    # ----------------------------------------------------------
    cleaned_content = clean_text(text_content)

    # ----------------------------------------------------------
    # Step 4: Quality assurance check
    # ----------------------------------------------------------
    line_count = len(cleaned_content.split('\n'))
    char_count = len(cleaned_content)

    print(f"\n📊 Cleanup Statistics:")
    print(f"   Line Count: {line_count} lines")
    print(f"   Character Count: {char_count} characters")

    if char_count < 100:
        print("⚠️  Warning: Cleaned content is exceptionally short. Important details might be missing.")
        print("   Suggest re-processing using manual fallback method.")

    # ----------------------------------------------------------
    # Step 5: Save cleaned file to company folder
    # ----------------------------------------------------------
    company_folder = _sanitize_filename(company_name) if company_name else 'unknown'
    clean_company_dir = os.path.join(cleaned_dir, company_folder)
    os.makedirs(clean_company_dir, exist_ok=True)

    clean_filename = f"cleaned_{timestamp}_{company_folder}.md"
    clean_path = os.path.join(clean_company_dir, clean_filename)

    with open(clean_path, 'w', encoding='utf-8') as f:
        f.write(f"# {company_name or 'Job Description'}\n")
        f.write(f"> Clean Date: {datetime.now().strftime('%Y/%m/%d %H:%M')}\n")
        f.write(f"> Source: {'URL' if is_url else 'Local File'}\n")
        f.write(f"> ⚠️ Auto-cleaned result. Please verify that all numbers and requirements are accurate.\n\n")
        f.write("---\n\n")
        f.write(cleaned_content)

    print(f"\n✅ Cleaned file output → {clean_path}")

    # ----------------------------------------------------------
    # Step 6: Process summary report
    # ----------------------------------------------------------
    print("\n" + "=" * 60)
    print("🧺 Cleaning Completed!")
    print(f"   📂 Output File: {clean_path}")
    print(f"   💾 Original Backup: {raw_dir}")
    print("   📋 Next Step: Please verify the output file.")
    print("=" * 60)

    return {"success": True, "output_path": clean_path, "error": None}


# ============================================================
# Command Line Entry Point
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description=f"Job Description Text Cleaner 🧺 V{__version__} — "
                    "Clean formats only, preserve original text data!",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            '  python job_cleaner.py -s "C:/path/to/paste.txt" -c "company_name"\n'
            '  python job_cleaner.py -s "https://example.com/job/123" -c "company_name"\n'
            '  python job_cleaner.py -s "paste.txt" -c "company" -o "./output"\n'
        )
    )
    parser.add_argument(
        '-s', '--source', required=True,
        help='URL or path to a local .txt/.html file'
    )
    parser.add_argument(
        '-c', '--company', default=None,
        help='Company name for output directory and filename'
    )
    parser.add_argument(
        '-o', '--out-dir', default=None,
        help='Custom output base directory (default: script directory)'
    )
    parser.add_argument(
        '-v', '--version', action='version',
        version=f'%(prog)s V{__version__}'
    )

    args = parser.parse_args()
    result = wash(args.source, args.company, args.out_dir)

    if not result["success"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
