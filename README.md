# 🛠️ 彭威銘 (PENG WEIMING) 's AI-Collaborative Automation Suite (AI協調型・業務自動化ツール集)

こんにちは、彭威銘 (PENG WEIMING) の技術ポートフォリオへようこそ。
本リポジトリは、日頃の業務における「手作業だと面倒な課題」を解決するため、**AIアシスタントとの協調開発（AI-Assisted Development）を通じて構築した7つの実践的自動化ツール群**をまとめたコードベースです。

---

## 📂 収録プロジェクト一覧

| フォルダ名 | プロジェクト名 | 使用技術 / スタック | 解決する課題 / 概要 |
| :--- | :--- | :--- | :--- |
| [01_Fish_Senses](./01_Fish_Senses) | **古書デジタルアーカイブ修復** | Python, 正規表現, ファイルI/O | 欠落・不規則な連番画像の自動マッピング、結合、テキストクリーニング |
| [02_Log_Parser](./02_Log_Parser) | **非構造化ログペルソナ解析** | Python, 二次元配列区間マッピング | LLM対話ログから、名前変遷に対応して発言者（ペルソナ）を自動タグ付け |
| [03_Media_Controller](./03_Media_Controller) | **OS低レベルAPIメディア制御** | Python, Windows API (`user32.dll`) | 物理キーを使わずに、プログラム経由で音楽の再生・スキップを制御 |
| [04_Realtime_Logger](./04_Realtime_Logger) | **常駐型対話ログ自動記録** | Python, SQLite, JSON, VBScript | バックグラウンド常駐で対話をJSONに蓄積し、SQLiteへ自動永続化＆MD書き出し |
| [05_Job_Cleaner](./05_Job_Cleaner) | **求人データスクレイピング** | BeautifulSoup4, Requests, Regex | コピペした求人テキストやHTMLから広告や不要UIパーツを自動除去してMD保存 |
| [06_Discord_Bridge](./06_Discord_Bridge) | **Discord-PCリモートブリッジ** | discord.py, Gemini API, OS I/O | 外出先からDiscordを叩いて自宅PCのファイルを安全に読み書き・遠隔操作 |
| [07_Discord_Legacy_Bot](./07_Discord_Legacy_Bot) | **多機能多模態対話エージェント** | discord.py, Gemini API (マルチモーダル) | 人格（ペルソナ）フィルタ、短期記憶結晶化、察言観色バックログ搭載のBot |

---

## 💡 開発における基本理念（設計思想）

本リポジトリに収録されているすべてのスクリプトは、以下の理念に基づいて設計されています。

1. **データ完全性の保証 (No Data Loss)**
   - クリーニングや処理を行う際は、必ず原本（Raw data）の自動バックアップを作成し、予期せぬ破壊や情報欠損を防止します。
2. **安全性の重視 (Security First)**
   - APIキーやアクセストークンなどの機密情報は、コード内にハードコードせず、必ず環境変数または `.env` 経由で動的に注入する設計に徹底されています。
3. **無駄なAPIコールの削減 (Resource Efficiency)**
   - バックログキューを用いた賢い割り込み処理（察言観色システム）や、対話メモリの結晶化（要約圧縮）により、LLMに対する不要なリクエストとトークンコストを最小限に抑えています。
4. **現場優先の問題解決 (Pragmatism)**
   - 学術的な難しさを追求するのではなく、「実際に目の前にある業務課題や不便さ」を解決するための最短ルートをRPA的に具現化しています。

---

## 🚀 動作環境とセットアップ
各ツールの詳細な使用方法やパラメータ設計については、各サブディレクトリ内の `README.md` をご参照ください。

<br>
<br>

---
---

# 🛠️ 彭威銘 (PENG WEIMING)'s AI-Collaborative Automation Suite

Welcome to the technical portfolio of 彭威銘 (PENG WEIMING).
This repository compiles **7 practical tools developed through AI-collaborative engineering to automate tedious daily tasks and facilitate workflow efficiency** using Python, OS APIs, and AI integrations.

---

## 📂 Project Directory

| Directory | Project Name | Tech Stack | Overview / Problem Solved |
| :--- | :--- | :--- | :--- |
| [01_Fish_Senses](./01_Fish_Senses) | **Antique Book Digital Archive Recovery** | Python, RegEx, File I/O | Automatically maps, merges, and cleans missing/irregular numbered images and texts. |
| [02_Log_Parser](./02_Log_Parser) | **Unstructured Log Persona Parser** | Python, 2D Array Mapping | Automatically parses and tags dynamic speakers (personas) from LLM log index ranges. |
| [03_Media_Controller](./03_Media_Controller) | **OS Low-Level API Media Control** | Python, Windows API (`user32.dll`) | Simulates media play, pause, and skip commands programmatically without hardware keys. |
| [04_Realtime_Logger](./04_Realtime_Logger) | **Daemon-Based Real-time Logger** | Python, SQLite, JSON, VBScript | Runs silently in the background, buffering logs to JSON and persisting to SQLite/Markdown. |
| [05_Job_Cleaner](./05_Job_Cleaner) | **Job Description Text Cleaner** | BeautifulSoup4, Requests, RegEx | Automatically extracts job details and filters out advertisements/junk HTML formats to Markdown. |
| [06_Discord_Bridge](./06_Discord_Bridge) | **Discord-PC Remote Bridge** | discord.py, Gemini API, OS I/O | Accesses, reads, and writes local PC files securely through Discord slash commands from anywhere. |
| [07_Discord_Legacy_Bot](./07_Discord_Legacy_Bot) | **Multimodal Conversational Agent** | discord.py, Gemini API (Multimodal) | A chatbot featuring persona filters, dialogue memory crystallization, and smart backlog context. |

---

## 💡 Engineering Core Principles (Design Philosophy)

All scripts included in this repository are designed with the following engineering core values:

1. **Data Integrity Guarantee (No Data Loss)**
   - Prior to any destructive format modifications or cleanups, original source data (Raw data) is automatically backed up to prevent unexpected data loss.
2. **Security-First Approach (Security First)**
   - Under no circumstances are credentials, API keys, or access tokens hardcoded in the scripts. All authentications are dynamically loaded via environment variables or `.env` configurations.
3. **Optimized Resource Consumption (Resource Efficiency)**
   - Smart background queues and context memory crystallization (summarization compressions) are used to minimize unnecessary API calls and token consumption.
4. **Pragmatic Problem Solving (Pragmatism)**
   - Focuses on resolving immediate operational bottlenecks and automating daily routines through efficient scripting rather than over-engineering.

---

## 🚀 Environment and Setup
For detailed setup instructions and usage details for each tool, please refer to the `README.md` file in their respective subdirectories.
