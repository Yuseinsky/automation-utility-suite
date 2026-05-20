import os
import re

DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(DIR, "Fish_Senses_Complete_Archive.md")
OUTPUT_FILE = os.path.join(DIR, "Fish_Senses_Perfect_Archive.md")

def page_sort_key(page_str):
    # Front matter pages
    if "封面" in page_str or "扉頁" in page_str: return -100
    if "莊子" in page_str: return -90
    if "序" in page_str: return -80
    if "目錄" in page_str: return -70
    
    # Back matter pages
    if "無頁碼" in page_str or "奧付" in page_str: return 1000
    if "版權" in page_str: return 1001
    
    # Try extracting numbers
    nums = re.findall(r'\d+', page_str)
    if nums:
        # If range like 60 ~ 63, use 60
        return int(nums[0])
    
    # Unknown/Fallback
    return 500

def main():
    print("[System] Started Polishing Archive...")
    
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Split contents by the page header marker "## 📖 頁碼："
    parts = content.split("## 📖 頁碼：")
    
    header_part = parts[0]
    blocks = []
    
    for part in parts[1:]:
        # Extract the full first line as the header
        first_line_end = part.find('\n')
        if first_line_end == -1:
            first_line_end = len(part)
        
        header_line = part[:first_line_end].strip()
        body = part[first_line_end:]
        
        # Clean up transitional seams in the translation
        # Remove markers indicating "continued from page XX"
        body = re.sub(r'（接.*?頁）[…\.\-]*', '', body)
        
        # Remove literal continuation dots preceding specific sentences
        body = re.sub(r'\.\.\.+力了」', '力了」', body)
        
        # Clean up chapter boundary markers to present the text as a seamless book
        body = re.sub(r'---\s*\n\s*\*\*\(本章結束，換章\)\*\*\s*\n\s*---', '', body)
        
        blocks.append((header_line, body))

    # Sort blocks based on physical book page sequence
    blocks.sort(key=lambda x: page_sort_key(x[0]))
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write("# 🐟《魚の感覚》全譯本完美打磨版 (照實體頁碼排序無縫版)\n\n")
        out.write("> **修復：デジタルアーカイブ修復プログラム**\n\n---\n\n")
        
        for header, body in blocks:
            out.write(f"## 📖 頁碼：{header}\n")
            out.write(body)
            out.write("\n\n")
            
    print(f"Success! Processed {len(blocks)} page blocks.")
    print("Archive is now perfectly ordered and seamless!")

if __name__ == "__main__":
    main()
