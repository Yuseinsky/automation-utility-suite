# 🧺 求人データスクレイピング＆クリーニングツール (Job Cleaner)

## 📌 プロジェクト概要
求人サイト（Wantedly、GREEN、リクナビなど）のWebページURL、またはコピペした生のHTML/プレーンテキストデータから、広告・Cookie同意バナー・ヘッダー/フッター・ナビゲーションリンクなどの不要な「ノイズ情報（HTML UI残骸）」を自動で検知・除去し、純粋な求人本文（職務内容、スキル要件、待遇など）のみを抽出して綺麗なMarkdown（.md）形式ファイルに変換するCLIデータパイプラインツールです。

「意味のある原文データを一切改変・欠落させない」というデータ完全性を最優先設計（無損失抽出ポリシー）とし、データのインポートからクリーニング、バックアップ、最終出力までをスムーズに行います。

---

## 🛠️ 技術スタック
- **Language**: Python 3
- **Libraries**: `BeautifulSoup4` (HTML Parser), `requests` (HTTP client), `lxml` (High-performance parsing engine)
- **CLI**: `argparse` (標準化されたコマンドライン引数処理)
- **Key Technology**: 
  - BeautifulSoup DOM ツリーの要素分解 (`decompose()`)
  - 完全一致クラス名フィルタリング（偽陽性を排除する防御的マッチング）
  - 多言語・マルチエンコーディングの自動検出 (`charset-normalizer` / `chardet` フォールバック)

---

## 📂 アーキテクチャ (Architecture)

```
05_Job_Cleaner/
├── job_cleaner.py   # メインCLIツール (HTML解析 + テキスト整形 + argparse)
├── README.md
├── Cleaned/         # (自動生成) クリーニング済みMarkdownの出力先
│   └── [company]/   #   会社名別サブディレクトリ
└── Raw/             # (自動生成) 取得した生HTMLの自動バックアップ先
    └── [company]/
```

#### `job_cleaner.py` — 統合クリーナー
- **`wash()` 関数**: URL またはローカルファイルからデータを取得し、2段階クリーニングを実行。構造化された辞書 (`{"success", "output_path", "error"}`) を返却し、外部スクリプトからの統合を容易にします。
- **`clean_html()`**: BeautifulSoup DOM 解析で広告・ナビ・Cookie バナーを除去。完全一致クラス名マッチにより、`cad-operator` や `admin` 等の誤削除を防止。
- **`clean_text()`**: 正規表現による空行圧縮 + UIゴミフィルタ。
- **`_read_local_file()`**: UTF-8 → `charset-normalizer` → `chardet` → UTF-8 (replace) の3段階フォールバックで、Shift-JIS 等の日本語エンコーディングに自動対応。

---

## ⚙️ 主な機能と処理フロー

### 1. 📥 マルチインプット対応
- **URL入力モード**: 直接WebページのURLを指定してデータを自動クローリング（最新版 User-Agent ヘッダーを付与してロボット検知を低減）。
- **ローカルファイル入力モード**: WebページをCtrl+Aで全コピーしたテキスト（またはHTML）を読み込む手動バックアップ処理にも対応。エンコーディングは自動検出。

### 2. 🧽 2段階クリーニングエンジン
- **HTMLノイズ除去 (Step 1)**:
  - `<script>`, `<style>`, `<noscript>`, `<iframe>` を完全排除。
  - セマンティックタグの解析に基づき、`<nav>`, `<header>`, `<footer>` を自動除去。
  - **完全一致クラス名マッチング**で広告・Cookie バナーを検知・排除。部分一致による偽陽性（False Positive）を防止する防御的設計。
- **テキスト平滑化 (Step 2)**:
  - 不要なUIパーツ（「応募画面へ進む」「気になる」などのボタン文字など）を完全一致ブラックリストフィルタで一括クリア。
  - `re.sub()` による正規表現で連続空行を最大1行に圧縮。

### 3. 📂 安全なデータ管理構造
- クリーニング前のデータは自動的にタイムスタンプ付きで `Raw/` ディレクトリに完全保存（バックアップ）。
- 洗い落とされたデータは、指定した会社名別のサブディレクトリ（例: `Cleaned/company_name/`）にMarkdown形式で美しく自動生成されます。

---

## 🚀 クイックスタート (Quick Start)

### CLI から実行
```bash
# 基本: URL から取得してクリーニング
python job_cleaner.py -s "https://example.com/job/123" -c "company_name"

# ローカルファイルから
python job_cleaner.py -s "paste.txt" -c "company_name"

# カスタム出力ディレクトリ指定
python job_cleaner.py -s "paste.txt" -c "company_name" -o "./output"

# ヘルプ表示
python job_cleaner.py -h
```

### Python から統合 (Import)
```python
from job_cleaner import wash

# 基本呼び出し
result = wash("https://example.com/job/123", company_name="ACME Corp")

# 結果は構造化辞書で返却
if result["success"]:
    print(f"Output: {result['output_path']}")
else:
    print(f"Error: {result['error']}")

# カスタム出力先を指定
result = wash("paste.txt", company_name="ACME", output_dir="./my_output")
```

---

## ⚠️ 既知の制限事項 (Known Limitations)
1. **JavaScript レンダリング非対応**: SPAやクライアントサイドレンダリングのページは、HTMLソースに求人内容が含まれない場合があります。その場合はローカルファイルモードをご利用ください。
2. **User-Agent の鮮度**: 一部の高度なWAFは古いUser-Agentを拒否します。定期的な更新を推奨します。
3. **エンコーディング検出精度**: `charset-normalizer` / `chardet` がインストールされていない場合、非UTF-8ファイルは置換文字（`�`）が含まれる可能性があります。

---

## 💡 本ツールの価値とビジネス価値
本ツールは、RPA（Robotic Process Automation）における**非構造化データ（Unstructured Web Content）から構造化情報（Structured Data）へのデータプレパレーション（前処理）**の課題を解決します。
AIエージェントやRAGエンジンに対して本ツールで前処理したデータを投入することで、不要なToken消費を大幅に削減し、コンテキスト抽出精度を向上させるデータクリーナーとしての高い実用性を有しています。

<br>
<br>

---
---

# 🧺 Job Description Scraping & Text Cleaning Tool (Job Cleaner)

## 📌 Project Overview
A CLI data pipeline utility designed to extract core job description details (such as role responsibilities, required skills, and working conditions) from job posting web pages (e.g. Wantedly, Green, Rikunabi) or pasted HTML/plain text. It automatically detects and filters out non-content noises such as advertisements, cookie consent banners, headers, footers, and social share links into a clean, formatted Markdown (.md) file.

The system is designed with a "Zero-Data-Loss" philosophy, prioritizing data integrity. It guarantees that meaningful texts (salary figures, overtime rules, etc.) are never altered or deleted during formatting.

---

## 🛠️ Tech Stack
- **Language**: Python 3
- **Libraries**: `BeautifulSoup4` (HTML Parser), `requests` (HTTP client), `lxml` (High-performance parsing engine)
- **CLI**: `argparse` (Standardized command-line argument parsing)
- **Core Technology**:
  - BeautifulSoup DOM tree manipulation and decomposition (`decompose()`).
  - Exact-match CSS class name filtering (defensive matching to eliminate false positives).
  - Multi-encoding detection and auto-decoding (`charset-normalizer` / `chardet` fallback chain).

---

## 📂 Architecture

```
05_Job_Cleaner/
├── job_cleaner.py   # Main CLI tool (HTML parsing + text formatting + argparse)
├── README.md
├── Cleaned/         # (Auto-generated) Cleaned Markdown output
│   └── [company]/   #   Per-company subdirectories
└── Raw/             # (Auto-generated) Raw HTML backup
    └── [company]/
```

#### `job_cleaner.py` — Unified Cleaner
- **`wash()` function**: Fetches data from URL or local file, executes 2-stage cleaning, and returns a structured dictionary (`{"success", "output_path", "error"}`) for easy integration with external scripts.
- **`clean_html()`**: BeautifulSoup DOM analysis to remove ads, navigation, and cookie banners. Uses exact class name matching to prevent false deletion of legitimate content like `cad-operator` or `admin`.
- **`clean_text()`**: Regex-based blank line compression + UI residual filter.
- **`_read_local_file()`**: 3-stage encoding fallback (UTF-8 → `charset-normalizer` → `chardet` → UTF-8 with replace) for automatic Japanese encoding support (Shift-JIS, EUC-JP, etc.).

---

## ⚙️ Key Features & Processing Flow

### 1. 📥 Multi-Input Processing
- **URL Mode**: Fetches HTML from a target webpage (utilizing up-to-date User-Agents to prevent anti-scraping blocks).
- **Local Fallback Mode**: Reads local `.txt` or `.html` files containing pasted webpage contents if direct scraping is blocked. Encoding is auto-detected.

### 2. 🧽 Two-Stage Cleaning Engine
- **HTML DOM Cleanup (Stage 1)**:
  - Discards `<script>`, `<style>`, `<noscript>`, and `<iframe>` elements entirely.
  - Automatically identifies and removes semantic elements: `<nav>`, `<header>`, and `<footer>`.
  - **Exact class name matching** to scrub ad banners, social widgets, and cookie popups — preventing false positives on legitimate classes like `cad-operator` or `admin-panel`.
- **Text Formatting (Stage 2)**:
  - Filters out UI noise (like "Apply Now" or "Save Job" button text) using exact-match blacklists.
  - Uses `re.sub()` regex to condense consecutive empty lines down to a single blank line.

### 3. 📂 Structured Staging & Archival
- Auto-saves the original crawled content under the `Raw/` directory with timestamps.
- Saves the finalized cleaned text inside subfolders matching the target company name (e.g. `Cleaned/[company_name]/`) in Markdown format.

---

## 🚀 Quick Start

### CLI Usage
```bash
# Basic: Fetch from URL and clean
python job_cleaner.py -s "https://example.com/job/123" -c "company_name"

# From local file
python job_cleaner.py -s "paste.txt" -c "company_name"

# Custom output directory
python job_cleaner.py -s "paste.txt" -c "company_name" -o "./output"

# Show help
python job_cleaner.py -h
```

### Python Integration (Import)
```python
from job_cleaner import wash

# Basic call
result = wash("https://example.com/job/123", company_name="ACME Corp")

# Returns a structured dictionary
if result["success"]:
    print(f"Output: {result['output_path']}")
else:
    print(f"Error: {result['error']}")

# Custom output directory
result = wash("paste.txt", company_name="ACME", output_dir="./my_output")
```

---

## ⚠️ Known Limitations
1. **No JavaScript Rendering**: SPA or client-side rendered pages may not include job content in the HTML source. Use the local file mode as a fallback.
2. **User-Agent Freshness**: Some advanced WAFs reject outdated User-Agents. Periodic updates are recommended.
3. **Encoding Detection Accuracy**: If `charset-normalizer` / `chardet` is not installed, non-UTF-8 files may contain replacement characters (`�`).

---

## 💡 Engineering Value & Business Application
This tool solves the challenge of **data preparation (converting unstructured web text to structured formatting)** in RPA systems. By feeding clean preprocessed texts into LLM pipelines or RAG search indices, it reduces token consumption and eliminates noise, resulting in significantly higher accuracy in automated prompt workflows.
