# Log Parser V2.1 (AI Conversation Formatting Tool)

[English](#english) | [日本語](#日本語) | [繁體中文](#繁體中文)

---

<h2 id="english">🇬🇧 English</h2>

### 📖 Overview
Log Parser is a Python parsing tool designed specifically for cleaning and formatting AI conversation logs copied from web interfaces (such as ChatGPT, Claude, Gemini, etc.).
Raw web logs often contain redundant UI tags and inconsistent speaker formatting, making them difficult to read. This script uses external **YAML Regular Expression (Regex) rules** to automatically scan logs, strip away junk characters, and reformat them into clean Markdown files with auto-generated statistics—all under the strict safety premise of **zero hardcoded names**.

### ✨ Core Features
- **Zero Hardcoding**: Speaker names and parsing rules are defined entirely in `parser_config.yaml`. The script itself contains no hardcoded names.
- **Visual Reformatting**: Consolidates messy, multi-line speaker tags (e.g., `**AI Assistant** \n :`) into clean Markdown headers (e.g., `### 💬 AI Assistant`).
- **Junk Line Stripping**: Automatically removes residual UI noise (e.g., "Copy to clipboard" button text) generated during web copying.
- **Auto Summary Report**: Automatically injects a statistical block at the top of the output file, detailing total lines, speaker switch counts, and the participant list.
- **Safe I/O**: Original files are never modified. The script reads the input and saves the result as a new file.

### ⚠️ Known Limitations (Must Read)
> **"Honesty is the best policy."**

The underlying logic of this script relies on **Regex**, making it a tool that strictly recognizes formatting rather than comprehending content. Therefore, when processing natural language, it has unavoidable physical limitations:

1. **No Semantic AI**: The script cannot read the context. If a speaker introduces themselves as "I am Bob" in the text, but their web tag is the default "User", the script **cannot** automatically replace the tag with "Bob". It will faithfully print "User". *(Solution: Semantic judgment requires upgrading to an LLM API architecture, which brings high token costs and hallucination risks.)*
2. **The 1-to-N Tag Problem**: If multiple physical users share the same account during a session, the web interface will only output a single tag (e.g., `User`). The script cannot distinguish between different physical users under the same tag, requiring manual intervention to split the original log.
3. **Missing First-Line Header**: If the very first line of the copied log lacks a speaker tag, the script strictly categorizes it as `[Unknown Speaker]`.

### 🚀 Quick Start
```bash
# 1. Install dependencies
pip install pyyaml

# 2. Run parser
python log_parser_v2.py chat_log.md --output result.md
```

---

<h2 id="日本語">🇯🇵 日本語</h2>

### 📖 概要 (Overview)
Log Parser は、「Web版 AI 会話ログの抽出」に特化して設計された Python 解析ツールです。
Web 画面（ChatGPT、Claude、Gemini など）から会話ログをコピーすると、不要な UI タグや不規則な発言者フォーマットが混入し、可読性が低下します。
本スクリプトは、外部の **YAML 正規表現 (Regex) ルール**を利用し、「名前のハードコーディングゼロ」という安全性を保ちながら、自動でログをスキャンし、不要な文字を削除し、統計情報を含むクリーンな Markdown ファイルに再フォーマットします。

### ✨ 主な機能 (Features)
- **ゼロ・ハードコーディング**: 名前や判定ルールはすべて `parser_config.yaml` で定義され、スクリプト本体には特定の人名が含まれません。
- **タグの視覚的フォーマット**: 複数行にまたがる乱雑な発言者タグ（例: `**AI アシスタント** \n :`）を、きれいな Markdown 見出し（例: `### 💬 AI アシスタント`）に統合します。
- **不要な行のフィルタリング**: コピー時に混入した UI のノイズ（例: 「クリップボードにコピー」ボタンのテキスト）を自動的に削除します。
- **自動サマリーレポート**: 出力ファイルの先頭に、「総行数」「発言者の切り替え回数」「参加者リスト」を含む統計データを自動挿入します。
- **安全なファイル操作**: 元のファイルは一切変更されません。読み込んだ後、新しいファイルとして保存されます。

### ⚠️ 既知の欠陥と技術的制限 (必ずお読みください)
> **"Honesty is the best policy. ツールができること、できないことを正直に。"**

本スクリプトの基盤は **正規表現 (Regex)** であり、「文脈ではなくフォーマットのみを認識する」ツールです。そのため、自然言語を処理する上で以下の避けられない制限があります：

1. **意味理解能力の欠如 (No Semantic AI)**: スクリプトは文脈を理解できません。本文中で「私はボブです」と自己紹介しても、Web画面上の発言タグがシステムデフォルトの「ユーザー」である場合、タグを自動的に「ボブ」に置き換えることは**絶対に不可能**です。「ユーザー」として忠実に出力します。
2. **共有タグの誤判定 (The 1-to-N Tag Problem)**: 複数の物理的ユーザーが同じアカウントを共有して会話した場合、Web 側が吐き出すタグは 1 つ（例: `ユーザー`）だけです。スクリプトはこれを同一人物と見なすため、手動でのログ分割が必要になります。
3. **冒頭タグなし問題**: コピーしたログの最初の行に発言者タグがない場合、スクリプトは厳密に `[Unknown Speaker]` として分類します。

### 🚀 クイックスタート
```bash
# 1. 依存関係のインストール
pip install pyyaml

# 2. 実行
python log_parser_v2.py chat_log.md --output result.md
```

---

<h2 id="繁體中文">🇹🇼 繁體中文</h2>

### 📖 專案簡介 (Overview)
Log Parser 是一個專為「擷取自網頁版 AI 對話紀錄」所設計的 Python 解析工具。
當我們從網頁 (如 ChatGPT, Claude, Gemini 等) 複製對話紀錄時，往往會混入大量冗餘的 UI 標籤、不一致的發言者格式，導致閱讀困難。

本腳本透過**外置的 YAML 正規表示式 (Regex) 規則**，在「零寫死人名」的絕對安全前提下，自動掃描對話紀錄，洗去垃圾字元，並將其重新排版為極度乾淨、帶有自動統計的 Markdown 檔案。

### ✨ 核心功能 (Features)
- **零硬編碼 (Zero Hardcoding)**：人名與判斷規則完全交由 `parser_config.yaml` 定義，腳本本身不包含任何特定人名。
- **標籤美化 (Visual Reformatting)**：將原本佔據多行、雜亂無章的發言者標記（如 `**AI 助手** \n :`）整併為乾淨的 Markdown 標題（例如 `### 💬 AI 助手`）。
- **垃圾行過濾 (Junk Line Stripping)**：自動清除網頁複製時殘留的 UI 雜訊（例如「複製到剪貼簿」等按鈕文字）。
- **自動摘要報告 (Auto Summary)**：在輸出的檔案最頂部，自動注入包含「總行數」、「發言者切換次數」、「參與者列表」的統計數據。
- **無損寫入 (Safe I/O)**：絕對不修改原始檔案，所有操作皆為讀取後另存新檔。

### ⚠️ 已知缺陷與技術限制 (Known Limitations - 必讀)
> **"Honesty is the best policy. 不畫大餅，認清工具的極限。"**

本腳本的底層運作邏輯為 **Regex (正規表示式)**，它是一台「只認格式、不看內文」的機器。因此在處理自然語言對話時，存在以下無法避免的物理限制：

1. **沒有語意理解能力 (No Semantic AI)**：本腳本**無法閱讀空氣與上下文**。如果發言者在內文中自我介紹「我是 Bob」，但網頁上的發言標籤依然是系統預設的「User」，腳本**絕對無法**自動將標籤替換為「Bob」。它只能忠實地印出「User」。*(解法：若需語意級別的判斷，必須升級為呼叫 LLM API 的 V3 架構，但這會帶來極高的 Token 成本與幻覺風險。)*
2. **多人共用標籤的「連坐誤判」 (The 1-to-N Tag Problem)**：在現實場景中，如果多個物理使用者（例如 A 把手機遞給 B）共用同一個帳號對話，網頁吐出的標籤只會有一個（例如 `User`）。腳本無法分辨「這句話是 A 說的，下一句話是 B 說的」。它會將該標籤下的所有文字歸類給同一個發言者。這需要人工在原始 Log 中介入分割。
3. **開頭無標籤問題 (Missing First-Line Header)**：若複製的 Log 檔案最開頭的第一句話沒有附帶任何發言者標籤，腳本會嚴格地將其歸類為 `[Unknown Speaker]`。

### 🚀 快速開始 (Quick Start)
```bash
# 1. 安裝依賴
pip install pyyaml

# 2. 設定 YAML 規則
# 請編輯 parser_config.yaml 來設定您的正規表示式與替換規則

# 3. 執行解析
python log_parser_v2.py chat_log.md --output result.md
```
