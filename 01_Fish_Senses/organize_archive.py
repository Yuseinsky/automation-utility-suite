import os
import glob
import re
import shutil

DIR = os.path.dirname(os.path.abspath(__file__))

# Pattern to find page numbers and original image numbers in markdown files
# e.g., "## 📖 頁碼：53 (原圖63)" or "... (原圖 63)"

def main():
    print("[System] Start running: Fish_Senses Archive Consolidation...")
    
    # 1. Gather all MD files in order
    md_files = sorted(glob.glob(os.path.join(DIR, "[0-1][0-9]_*.md")))
    reading_notes = sorted(glob.glob(os.path.join(DIR, "100_Reading_Notes_Part*.md")))
    
    mapping = {}
    pattern = re.compile(r"頁碼：([0-9\-\w]+)\s*\([^\d]*原圖\s*(\d+)[^\d]*\)")
    
    for fpath in md_files:
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
            matches = pattern.findall(content)
            for page_num, raw_img_num in matches:
                mapping[raw_img_num] = page_num
    
    print(f"Success: Extracted {len(mapping)} image-to-page mappings.")
    
    # Perform the copy/rename operation for mapped images
    renamed_count = 0
    for raw_img_num, page_num in mapping.items():
        src = os.path.join(DIR, f"LINE_ALBUM_魚の感覚_260327_{raw_img_num}.jpg")
        if not os.path.exists(src):
            src = os.path.join(DIR, f"LINE_ALBUM_魚の感覚_260328_{raw_img_num}.jpg")
        
        if os.path.exists(src):
            dst = os.path.join(DIR, f"Fish_Senses_Page_{page_num}.jpg")
            if not os.path.exists(dst):
                shutil.copy2(src, dst)
                renamed_count += 1
    
    print(f"Success Renamed: {renamed_count} images copied and renamed.")

    # Part B: Consolidate the main texts into Fish_Senses_Complete_Archive.md
    print("Consolidating Main Text Archive...")
    with open(os.path.join(DIR, "Fish_Senses_Complete_Archive.md"), "w", encoding="utf-8") as out:
        out.write("# 🐟《魚の感覚》全譯本終極典藏版 (昭和21年發行)\n\n")
        out.write("> **修復：デジタルアーカイブ修復プログラム**\n\n---\n\n")
        
        for fpath in md_files:
            fname = os.path.basename(fpath)
            # Exclude tests and progress files
            if fname in ["00_Test_Parsing_Result.md", "00_Project_Progress.md"]:
                continue
            
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
                out.write(f"\n\n<!-- ====== {fname} ====== -->\n\n")
                out.write(content)
                
    print("Complete Archive generated: Fish_Senses_Complete_Archive.md")

    # Part C: Consolidate reading notes into Reading_Notes_Complete.md
    print("Consolidating Reading Notes...")
    with open(os.path.join(DIR, "Reading_Notes_Complete.md"), "w", encoding="utf-8") as out:
        out.write("# 🐟《魚の感覚》科学解説と考察ノート\n\n")
        out.write("> 翻訳の過程で蓄積された専門用語、魚類生理学の科学解説と考察ノートです。\n\n---\n\n")
        
        for fpath in reading_notes:
            fname = os.path.basename(fpath)
            with open(fpath, "r", encoding="utf-8") as f:
                out.write(f"\n\n<!-- ====== {fname} ====== -->\n\n")
                out.write(f.read())
    
    print("Reading notes generated: Reading_Notes_Complete.md")
    print("All tasks finished perfectly!")

if __name__ == "__main__":
    main()
