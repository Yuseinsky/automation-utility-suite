import os
import re

DIR = os.path.dirname(os.path.abspath(__file__))
FILE = os.path.join(DIR, "Fish_Senses_Perfect_Archive.md")

def main():
    with open(FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Remove markers like "（接自第1頁最後）：……" or "（接續前文遺失段落）：……" or "（接自第21頁最後）……"
    content = re.compile(r'（接.*?）[：:……\.\-]*').sub('', content)
    
    # 2. Remove markers like "（註：從前後文推測.*?）\n?"
    content = re.compile(r'（註：從前後文推測.*?）\s*\n?').sub('', content)
    content = re.compile(r'（註解：缺漏.*?）\s*\n?').sub('', content)

    # 3. Clean up leading elliptic dots at the beginning of a line/paragraph
    # e.g. "^……" or "^：……" or "^……"
    content = re.compile(r'^[\s：:……\.\-]*', re.MULTILINE).sub('', content)

    # 4. Remove leftover `<!-- ====== 04_MainText_Batch_3.md ====== -->` and related blocks
    content = re.compile(r'<!-- ====== .*? ====== -->\s*\n\s*# 魚の感覚 - 正文卷.*?\s*\n\s*> \*\*.*?的整理日誌：\*\*(.*?)\n\s*---\s*\n', re.DOTALL).sub('', content)

    # 5. Clean up multiple empty lines
    content = re.compile(r'\n{3,}').sub('\n\n', content)

    with open(FILE, "w", encoding="utf-8") as out:
        out.write(content)

    print("Pass 2 smoothing completed successfully!")

if __name__ == "__main__":
    main()
