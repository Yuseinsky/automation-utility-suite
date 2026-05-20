# 🧺 求人データスクレイピング＆クリーニングツール (Job Cleaner)

## 📌 プロジェクト概要
求人サイト（Wantedly、GREEN、リクナビなど）のWebページURL、またはコピペした生のHTML/プレーンテキストデータから、広告・Cookie同意バナー・ヘッダー/フッター・ナビゲーションリンクなどの不要な「ノイズ情報（HTML UI残骸）」を自動で検知・除去し、純粋な求人本文（職務内容、スキル要件、待遇など）のみを抽出して綺麗なMarkdown（.md）形式ファイルに変換するCLIデータパイプラインツールです。

「意味のある原文データを一切改変・欠落させない」というデータ完全性を最優先設計（無損失抽出ポリシー）とし、データのインポートからクリーニング、バックアップ、最終出力までをスムーズに行います。

---

## 🛠️ 技術スタック
- **Language**: Python 3
- **Libraries**: `BeautifulSoup4` (HTML Parser), `requests` (Web Crawler), `lxml` (Fast parser engine)
- **Key Technology**: 
  - BeautifulSoup DOM ツリーの要素分解 (`decompose()`)
  - 正規表現によるクラス名・ID名のワイルドカードマッチ判定
  - 多言語・マルチエンコーディングの自動検出

---

## ⚙️ 主な機能と処理フロー

### 1. 📥 マルチインプット対応
- **URL入力モード**: 直接WebページのURLを指定してデータを自動クローリング（偽装User-Agentヘッダーを付与してロボット検知を低減）。
- **ローカルファイル入力モード**: WebページをCtrl+Aで全コピーしたテキスト（またはHTML）を読み込む手動バックアップ処理にも対応。

### 2. 🧽 2段階クリーニングエンジン
- **HTMLノイズ除去 (Step 1)**:
  - `<script>`, `<style>`, `<noscript>`, `<iframe>` を完全排除。
  - セマンティックタグの解析に基づき、`<nav>`, `<header>`, `<footer>` を自動除去。
  - `cookie`, `banner`, `advertisement`, `sns-` 等の広告・ソーシャル系CSSクラス/IDを持つタグを動的検知して排除。
- **テキスト平滑化 (Step 2 - "Lint Roller")**:
  - 不要なUIパーツ（「応募画面へ進む」「気になる」などのボタン文字など）を完全一致ブラックリストフィルタで一括クリア。
  - 連続する空行を自動的に最大1行に圧縮し、文章構造をスッキリ整理。

### 3. 📂 安全なデータ管理構造
- クリーニング前のデータは自動的にタイムスタンプ付きで `Raw/` ディレクトリに完全保存（バックアップ）。
- 洗い落とされたデータは、指定した会社名別のサブディレクトリ（例: `Cleaned/company_name/`）にMarkdown形式で美しく自動生成されます。

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
- **Core Technology**:
  - BeautifulSoup DOM tree manipulation and decomposition (`decompose()`).
  - Wildcard RegEx matching for CSS class names and element IDs.
  - Multi-encoding detection and auto-decoding (Shift-JIS, UTF-8, etc.).

---

## ⚙️ Key Features & Processing Flow

### 1. 📥 Multi-Input Processing
- **URL Mode**: Fetches HTML from a target webpage (utilizing pseudo User-Agents to prevent anti-scraping blocks).
- **Local Fallback Mode**: Reads local `.txt` or `.html` files containing pasted webpage contents if direct scraping is blocked.

### 2. 🧽 Two-Stage Cleaning Engine
- **HTML DOM Cleanup (Stage 1)**:
  - Discards `<script>`, `<style>`, `<noscript>`, and `<iframe>` elements entirely.
  - Automatically identifies and removes semantic elements: `<nav>`, `<header>`, and `<footer>`.
  - Scrubs divs matching regex patterns for ad banners, social widgets, and cookie popups (e.g. `cookie`, `banner`, `ad-`, `sns-`).
- **Text Formatting ("Lint Roller" Stage 2)**:
  - Filters out UI noise (like "Apply Now" or "Save Job" button text) using exact-match blacklists.
  - Strips leading and trailing whitespaces and condenses consecutive empty lines down to a single blank line to clean layout spacing.

### 3. 📂 Structured Staging & Archival
- Auto-saves the original crawled content under the `Raw/` directory with timestamps.
- Saves the finalized cleaned text inside subfolders matching the target company name (e.g. `Cleaned/[company_name]/`) in Markdown format.

---

## 💡 Engineering Value & Business Application
This tool solves the challenge of **data preparation (converting unstructured web text to structured formatting)** in RPA systems. By feeding clean preprocessed texts into LLM pipelines or RAG search indices, it reduces token consumption and eliminates noise, resulting in significantly higher accuracy in automated prompt workflows.
