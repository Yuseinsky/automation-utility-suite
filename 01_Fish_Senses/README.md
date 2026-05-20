# 🐟 古書デジタルアーカイブ自動修復・整形パイプライン (Fish Senses)

## 📌 プロジェクト概要
昭和21年（1946年）発行の学術古書《魚の感覚》の翻訳データを、デジタル修復・保存（デジタルアーカイブ化）するための3段階自動処理パイプラインです。
本システムは、欠落や不規則な連番を持つ画像ファイルと、バラバラに作成された複数の翻訳Markdownテキストを正規表現で動的にマッピングし、自動的な「リネーム・結合・整形・クレンジング」を一挙に行うために開発されました。

手作業で行うと数時間以上かかる煩雑な整理プロセスを、Pythonによる自動化スクリプトで一瞬で完了させます。

---

## 🛠️ 技術スタック
- **Language**: Python 3
- **Libraries**: Built-in libraries (`os`, `re`, `glob`, `shutil`)
- **Key Technology**: 複雑な正規表現パターンマッチング、ファイルシステム操作 (I/O)、動的ソーティングロジック

---

## ⚙️ パイプライン構成 (3-Stage Pipeline)

本システムは、責務を分離した3つのPythonスクリプトから構成されています。

### 📂 Step 1: `organize_archive.py` (テキスト結合 & 画像マッピング・自動リネーム)
- **役割**: 分割された翻訳ファイル群からページ対応関係を解析し、画像ファイルと自動マッチングしてリネームコピーします。
- **主な処理**:
  1. 複数の翻訳Markdownファイル内の特定記述（例: `## 📖 頁碼：53 (原圖63)`）から、正規表現を用いて「実本のページ番号」と「元画像ファイル番号」のマッピングテーブルを動的生成。
  2. マッピングに基づき、乱雑な画像ファイル（例: `LINE_ALBUM_魚の感覚_xxxx_63.jpg`）を `Fish_Senses_Page_53.jpg` のように自動リネームしてコピー。
  3. 各Markdownファイルから無駄なテストファイルを除外し、ひとつの統合ファイル `Fish_Senses_Complete_Archive.md` に自動結合。

### 🌟 Step 2: `polish_archive.py` (ページ順ソーティング & 一次整形)
- **役割**: 結合されたファイルを実体書の正しい構成順（表紙 → 序文 → 目次 → 本文 → 奥付など）に並び替えます。
- **主な処理**:
  1. `page_sort_key` 関数を用いて、数字以外の文字列（例: "封面", "目録", "奧付"）を含む特殊ページを判定し、独自の重み付けによる高精度な並び替えを実現。
  2. 翻訳時に入り込んだ移行用の不要なトランジション記述（例: `（接第XX頁）……` などのテキストの継ぎ目）を正規表現で自動検出しクレンジング。

### 🧹 Step 3: `polish_archive_pass_2.py` (詳細クレンジング & 最終平滑化)
- **役割**: 最終的な可読性を向上させるための、微細なテキストクレンジング（ノイズ除去）を行います。
- **主な処理**:
  1. テキスト内に残存した編集マーカー（例: `（註：從前後文推測...）`）を正規表現で一括削除。
  2. 段落の先頭に残った三点リーダーや不要なコロン等の記号を除去し、テキストの流れを平滑化。
  3. 複数行にわたる不要な空行を圧縮し、ドキュメント全体のフォーマットを統一。

---

## 💡 本プロジェクトの開発背景と意義
このシステムは、単に「コードを書く」だけでなく、**「非構造化されたレガシーデータ（バラバラの画像とテキスト）の整合性をいかに効率よく取り、統一されたデータベース/文書構造に落とし込むか」**という、実業務におけるデータ移行・システム統合の課題に対するソリューションとして設計されています。

<br>
<br>

---
---

# 🐟 Antique Book Digital Archive Recovery & Formatting Pipeline (Fish Senses)

## 📌 Project Overview
A 3-stage automated pipeline designed to digitize, reconstruct, and restore translated text and illustrations from the academic antique book "Fish Senses" (published in 1946 / Showa 21).
This system uses Python and Regular Expressions to dynamically map translation text fragments to missing/irregular numbered illustrations, automating the process of renaming files, consolidating text, and cleaning formatting seams.

This script replaces hours of manual alignment with a single execution.

---

## 🛠️ Tech Stack
- **Language**: Python 3
- **Libraries**: Built-in modules (`os`, `re`, `glob`, `shutil`)
- **Core Technology**: Complex RegEx pattern matching, file system operations (I/O), and custom sorting algorithms.

---

## ⚙️ Pipeline Architecture (3-Stage Pipeline)

The system consists of three specialized scripts with distinct separation of concerns:

### 📂 Step 1: `organize_archive.py` (Text Consolidation & Image Mapping/Renaming)
- **Role**: Parses page relationships across split translation documents, matches them with corresponding illustrations, and performs automated copy and renaming operations.
- **Operations**:
  1. Dynamically constructs a map of physical pages to raw image numbers by matching specific markdown tags (e.g. `## 📖 頁碼：53 (原圖63)`) using RegEx.
  2. Copies and renames chaotic image files (e.g. `LINE_ALBUM_魚の感覚_xxxx_63.jpg`) to clean formats like `Fish_Senses_Page_53.jpg`.
  3. Excludes draft/test markdown files and consolidates all translated chapters into `Fish_Senses_Complete_Archive.md`.

### 🌟 Step 2: `polish_archive.py` (Sequence Sorting & Format Cleanup)
- **Role**: Re-orders consolidated chapters into the correct book layout (Cover → Preface → Index → Main Text → Colophon) and performs initial formatting cleanup.
- **Operations**:
  1. Implements `page_sort_key` to recognize non-numeric page headers (e.g. "Cover", "Index", "Colophon") and sorts them using a custom priority algorithm.
  2. Uses RegEx to scan and eliminate text transitions left during translation (e.g., "continued from page XX...").

### 🧹 Step 3: `polish_archive_pass_2.py` (Detail Cleansing & Final Text Smoothing)
- **Role**: Polishes the final text to maximize readability by filtering out micro-noises.
- **Operations**:
  1. Mass deletes editing notes and translator annotations (e.g., "Translators note: inferred from context...") using regex.
  2. Strips leading punctuation marks (like leading ellipses `...` or colons `:`) from the beginning of paragraphs to smooth text transitions.
  3. Compresses consecutive empty lines to unify document spacing.

---

## 💡 Background & Rationale
This pipeline represents a programmatic solution to real-world data migration issues: **how to maintain consistency and structure when merging unstructured legacy files (scattered images and draft translations) into a clean, unified document format.**
