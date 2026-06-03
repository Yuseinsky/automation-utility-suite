# 🛠️ PENG WEIMING's AI-Collaborative Automation Suite (AI協調型・業務自動化ツール集)

こんにちは、PENG WEIMING の技術ポートフォリオへようこそ。
本リポジトリは、日頃の業務における「手作業だと面倒な課題」を解決するため、**AIアシスタントとの協調開発（AI-Assisted Development）を通じて構築した8つの実践的自動化ツール群**をまとめたコードベースです。

---

## 📂 収録プロジェクト一覧

| フォルダ名 | プロジェクト名 | 使用技術 / スタック | 解決する課題 / 概要 |
| :--- | :--- | :--- | :--- |
| [01_Legacy_Archive_Digitization_Pipeline](./01_Legacy_Archive_Digitization_Pipeline) | **古書デジタルアーカイブ修復パイプライン** | Python, 正規表現 (YAML), モジュール式設計 | 設定駆動型のモジュール式パイプラインで、画像マッピング・テキスト統合・ページ順ソート・ノイズ除去を一括自動化 |
| [02_Log_Parser](./02_Log_Parser) | **AI会話ログ自動フォーマッター** | Python, 正規表現 (YAML), Markdown | WebUIの乱雑な対話ログを、ハードコーディングなしでクリーンなMarkdownへ再構築・解析 |
| [03_Media_Controller](./03_Media_Controller) | **OS低レベルAPIメディア制御** | Python, Windows API (`user32.dll`), argparse | 辞書マッピング＋クロスプラットフォーム防御により、CLI一発でOS低レベルメディアキーを送信する統合型ツール |
| [04_Realtime_Logger](./04_Realtime_Logger) | **汎用型AI対話ログフレームワーク** | Python, SQLite 3 (ACID) | イベント駆動型アーキテクチャでAI対話をSQLiteに即時永続化し、自動Markdownエクスポート |
| [05_Job_Cleaner](./05_Job_Cleaner) | **求人データスクレイピング (V3.0)** | BeautifulSoup4, Requests, Regex | コピペした求人テキストやHTMLから広告や不要UIパーツを自動除去してMD保存 |
| [06_Discord_Bridge](./06_Discord_Bridge) | **Discord-PCリモートブリッジ (V4.0)** | discord.py, Gemini API, OS I/O | 外出先からDiscordを叩いて自宅PCのファイルを安全に読み書き・遠隔操作 |
| [07_Discord_Legacy_Bot](./07_Discord_Legacy_Bot) | **多機能多模態対話エージェント (V4.0)** | discord.py, Gemini API (マルチモーダル) | 人格（ペルソナ）フィルタ、短期記憶結晶化、察言観色バックログ搭載のBot |
| [08_Dialogue_Context_Retriever](./08_Dialogue_Context_Retriever) | **対話コンテキスト復元システム (V2.0)** | Python, SQLite, argparse | IDEアーキテクチャ変更で失われたAI対話脈絡をデータベースから抽出し復旧する防御的ツール |

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

# 🛠️ PENG WEIMING's AI-Collaborative Automation Suite

Welcome to the technical portfolio of PENG WEIMING.
This repository compiles **8 practical tools developed through AI-collaborative engineering to automate tedious daily tasks and facilitate workflow efficiency** using Python, OS APIs, and AI integrations.

---

## 📂 Project Directory

| Directory | Project Name | Tech Stack | Overview / Problem Solved |
| :--- | :--- | :--- | :--- |
| [01_Legacy_Archive_Digitization_Pipeline](./01_Legacy_Archive_Digitization_Pipeline) | **Legacy Archive Digitization Pipeline** | Python, RegEx (YAML), Modular Design | Config-driven modular pipeline automating image mapping, text consolidation, page sorting, and noise removal. |
| [02_Log_Parser](./02_Log_Parser) | **AI Conversation Log Formatter** | Python, RegEx (YAML), Markdown | Reformats messy web AI logs into clean Markdown with auto-summaries using zero-hardcoded YAML rules. |
| [03_Media_Controller](./03_Media_Controller) | **OS Low-Level API Media Control** | Python, Windows API (`user32.dll`), argparse | Unified CLI tool using dictionary mapping and cross-platform defense to send OS-level media key signals. |
| [04_Realtime_Logger](./04_Realtime_Logger) | **Universal AI Dialogue Logger** | Python, SQLite 3 (ACID) | Event-driven framework for instant SQLite persistence and automatic Markdown transcript export. |
| [05_Job_Cleaner](./05_Job_Cleaner) | **Job Description Text Cleaner (V3.0)** | BeautifulSoup4, Requests, RegEx | Automatically extracts job details and filters out advertisements/junk HTML formats to Markdown. |
| [06_Discord_Bridge](./06_Discord_Bridge) | **Discord-PC Remote Bridge (V4.0)** | discord.py, Gemini API, OS I/O | Accesses, reads, and writes local PC files securely through Discord slash commands from anywhere. |
| [07_Discord_Legacy_Bot](./07_Discord_Legacy_Bot) | **Multimodal Conversational Agent (V4.0)** | discord.py, Gemini API (Multimodal) | A chatbot featuring persona filters, dialogue memory crystallization, and smart backlog context. |
| [08_Dialogue_Context_Retriever](./08_Dialogue_Context_Retriever) | **Dialogue Context Recovery (V4.0)** | Python, SQLite FTS5, argparse | Advanced IDE log parser and high-performance FTS5 search to seamlessly rescue AI dialogues. |

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
