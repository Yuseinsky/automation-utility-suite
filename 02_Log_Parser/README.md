# Log Parser V2.1 (AI Conversation Formatting Tool)

## 📖 專案簡介 (Overview)
Log Parser 是一個專為「擷取自網頁版 AI 對話紀錄」所設計的 Python 解析工具。
當我們從網頁 (如 Gemini, Claude, NotebookLM 等) 複製對話紀錄時，往往會混入大量冗餘的 UI 標籤、不一致的發言者格式，導致閱讀困難。

本腳本透過**外置的 YAML 正規表示式 (Regex) 規則**，在「零寫死人名」的絕對安全前提下，自動掃描對話紀錄，洗去垃圾字元，並將其重新排版為極度乾淨、帶有自動目錄與統計的 Markdown 檔案。

---

## ✨ 核心功能 (Features)
- **零硬編碼 (Zero Hardcoding)**：人名與判斷規則完全交由 `parser_config.yaml` 定義，腳本本身不包含任何特定人名。
- **標籤美化 (Visual Reformatting)**：將原本佔據多行、雜亂無章的發言者標記（如 `花宮 朱音 💮 \n said`）整併為乾淨的 Markdown 標題（例如 `### 💬 花宮 朱音 💮`）。
- **垃圾行過濾 (Junk Line Stripping)**：自動清除網頁複製時殘留的 UI 雜訊（例如「自訂 Gem」）。
- **自動摘要報告 (Auto Summary)**：在輸出的檔案最頂部，自動注入包含「總行數」、「發言者切換次數」、「參與者列表」的統計數據。
- **無損寫入 (Safe I/O)**：絕對不修改原始檔案，所有操作皆為讀取後另存新檔。

---

## ⚠️ 已知缺陷與技術限制 (Known Limitations - 必讀)
> **"Honesty is the best policy. 不畫大餅，認清工具的極限。"**

本腳本的底層運作邏輯為 **Regex (正規表示式)**，它是一台「只認格式、不看內文」的機器。因此在處理自然語言對話時，存在以下無法避免的物理限制：

### 1. 沒有語意理解能力 (No Semantic AI)
本腳本**無法閱讀空氣與上下文**。
如果發言者在內文中自我介紹「我是啓邦」，但他的發言標籤依然是系統預設的「你說了」，腳本**絕對無法**自動將標籤替換為「啓邦」。它只能忠實地印出「你說了」。
*解法：若需語意級別的判斷，必須升級為呼叫 LLM API 的 V3 架構，但這會帶來極高的 Token 成本與幻覺風險。*

### 2. 多人共用標籤的「連坐誤判」 (The 1-to-N Tag Problem)
在現實場景中，如果多個物理使用者（例如 A 把手機遞給 B）共用同一個帳號對話，網頁吐出的標籤只會有一個（例如 `你說了`）。
腳本無法分辨「這句話是 A 說的，下一句話是 B 說的」。它會將該標籤下的所有文字歸類給同一個發言者。這需要人工在原始 Log 中介入分割。

### 3. 開頭無標籤問題 (Missing First-Line Header)
若複製的 Log 檔案最開頭的第一句話沒有附帶任何發言者標籤，腳本會嚴格地將其歸類為 `[Unknown Speaker]`。

---

## 🚀 快速開始 (Quick Start)

### 1. 安裝依賴
```bash
pip install pyyaml
```

### 2. 設定 YAML 規則
編輯 `parser_config.yaml`：
```yaml
speaker_pattern: '^(?P<name>你說了|.+? said)$'  # 你的 Regex 規則
reformat:
  enabled: true
  header_template: "### 💬 {name}"
ignore_lines:
  patterns:
    - '^自訂 Gem$'
summary:
  enabled: true
```

### 3. 執行解析
```bash
python log_parser_v2.py chat_log.md --output result.md
```
