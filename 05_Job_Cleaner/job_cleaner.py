"""
=============================================================
  Job Description Text Cleaner (Job Cleaner)
  
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

import os
import re
import sys
from datetime import datetime

sys.stdout.reconfigure(errors='replace')

# ============================================================
# Configurations
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLEANED_DIR = os.path.join(BASE_DIR, "Cleaned")
RAW_DIR = os.path.join(BASE_DIR, "Raw")

# Navigation / Menu tags and class keywords for HTML cleaning
NAV_TAGS = ['nav', 'header', 'footer']
JUNK_CLASSES = [
    'cookie', 'banner', 'advertisement', 'ad-', 'popup',
    'modal', 'overlay', 'sidebar', 'breadcrumb',
    'social-share', 'sns-', 'share-button',
    'global-nav', 'global-header', 'global-footer',
    'site-header', 'site-footer',
]

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
    
    soup = BeautifulSoup(html_content, 'lxml')
    
    # Step 1: Remove script and style tags (definitely not text content)
    for tag in soup.find_all(['script', 'style', 'noscript', 'iframe']):
        tag.decompose()
    
    # Step 2: Remove navigation blocks (<nav>, <header>, <footer>)
    for tag_name in NAV_TAGS:
        for tag in soup.find_all(tag_name):
            tag.decompose()
    
    # Step 3: Remove ad and cookie blocks based on class names
    for junk_class in JUNK_CLASSES:
        for tag in soup.find_all(class_=re.compile(junk_class, re.IGNORECASE)):
            tag.decompose()
    
    # Step 4: Extract remaining text separated by newlines
    text = soup.get_text(separator='\n')
    
    return text


# ============================================================
# UI Residual Filter (Lint Roller)
# ============================================================

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
    lines = raw_text.split('\n')
    cleaned_lines = []
    blank_count = 0
    
    for line in lines:
        stripped = line.strip()
        
        # Skip blacklisted exact UI matches
        if stripped in UI_EXACT_MATCH_BLACKLIST:
            continue
        
        if stripped == '':
            blank_count += 1
            if blank_count <= 1:  # Keep at most one blank line
                cleaned_lines.append('')
        else:
            blank_count = 0
            cleaned_lines.append(stripped)
    
    # Trim leading/trailing blank lines
    result = '\n'.join(cleaned_lines).strip()
    
    return result


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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
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
        if response.status_code == 403:
            print(f"🚫 Blocked by anti-scraping system! (403 Forbidden)")
        elif response.status_code == 429:
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
# Main Processing Method
# ============================================================

def wash(source, company_name=None):
    """
    Main job cleaner process.
    
    Args:
        source: URL string or local text file path
        company_name: Name of the company for output file names
    """
    print("=" * 60)
    print("  Job Description Text Cleaner 🧺")
    print("  Rule: Clean formats only, preserve original text data!")
    print("=" * 60)
    
    # Initialize output directories
    os.makedirs(CLEANED_DIR, exist_ok=True)
    os.makedirs(RAW_DIR, exist_ok=True)
    
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
            print("\n" + "=" * 60)
            print("⚠️  URL fetch failed. Please use manual fallback:")
            print("   1. Open the URL in your web browser.")
            print("   2. Select all text (Ctrl+A) and copy (Ctrl+C).")
            print("   3. Paste the contents into a local .txt file.")
            print("   4. Re-run: wash('path_to_txt_file.txt', 'company_name')")
            print("=" * 60)
            return None
        
        # Save raw backup HTML
        company_folder = company_name or 'unknown'
        raw_company_dir = os.path.join(RAW_DIR, company_folder)
        os.makedirs(raw_company_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        raw_filename = f"raw_{timestamp}_{company_folder}.html"
        raw_path = os.path.join(raw_company_dir, raw_filename)
        with open(raw_path, 'w', encoding='utf-8') as f:
            f.write(raw_content)
        print(f"💾 Raw HTML backed up → {raw_path}")
        
    else:
        print(f"\n📥 Mode: Local File Fallback")
        print(f"   Source File: {source}")
        
        if not os.path.exists(source):
            print(f"❌ File not found: {source}")
            return None
        
        with open(source, 'r', encoding='utf-8') as f:
            raw_content = f.read()
        
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
    company_folder = company_name or 'unknown'
    clean_company_dir = os.path.join(CLEANED_DIR, company_folder)
    os.makedirs(clean_company_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
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
    print(f"   💾 Original Backup: {RAW_DIR}")
    print("   📋 Next Step: Please verify the output file.")
    print("=" * 60)
    
    return clean_path


# ============================================================
# Command Line Entry Point
# ============================================================

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        # Command line parameters: python job_cleaner.py [source] [company_name]
        source_arg = sys.argv[1]
        company_arg = sys.argv[2]
        wash(source_arg, company_arg)
    elif len(sys.argv) == 2:
        source_arg = sys.argv[1]
        wash(source_arg)
    else:
        print("=" * 60)
        print("  Job Description Text Cleaner 🧺 V2.1")
        print("=" * 60)
        print("\nUsage:")
        print('  python job_cleaner.py "C:/path/to/paste.txt" "company_name"')
        print('  python job_cleaner.py "https://example.com/job/123" "company_name"')
        print()
        print("  * Run from any directory.")
        print("  * Output files are created in Cleaned/[company_name]/ directory.")
        print("=" * 60)
