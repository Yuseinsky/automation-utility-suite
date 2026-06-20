# 🛠️ PENG WEIMING — 実務課題から生まれたIT自動化プロジェクト集

このリポジトリは、私がITへのキャリアチェンジを進めるなかで、日常業務の「面倒だけど誰も手をつけない課題」を解決するために作った8つのツールをまとめたものです。
コーディングにはAIツール（Antigravity IDE, Claude, Gemini）の力を借りていますが、すべてのプロジェクトは、私自身が現場で直面した具体的な課題から出発しています。

---

## 📂 プロジェクト一覧

| フォルダ名 | プロジェクト名 | 使用技術 | きっかけと概要 |
| :--- | :--- | :--- | :--- |
| [01_Legacy_Archive_Digitization_Pipeline](./01_Legacy_Archive_Digitization_Pipeline) | **古書デジタルアーカイブ修復パイプライン** | Python, RegEx, YAML | 古い紙資料のデジタル化作業で、画像の紐付けやテキスト統合を手作業で行う限界を感じ、一括自動化するパイプラインを構築 |
| [02_Log_Parser](./02_Log_Parser) | **AI会話ログフォーマッター** | Python, RegEx, Markdown | WebUIの対話ログが乱雑で読み返せなかったため、自動でクリーンなMarkdownに整形するツールを作成 |
| [03_Media_Controller](./03_Media_Controller) | **OSメディアキー制御ツール** | Python, Windows API, argparse | CLIから一発でメディア操作をしたかったため、OSのAPIを直接叩く統合ツールを作成 |
| [04_Realtime_Logger](./04_Realtime_Logger) | **AI対話リアルタイム記録ツール** | Python, SQLite | AI対話の内容がセッション終了後に消えてしまう問題を防ぐため、リアルタイムでDBに永続化する仕組みを構築 |
| [05_Job_Cleaner](./05_Job_Cleaner) | **求人テキストクリーナー** | Python, BeautifulSoup4, Requests | 求人サイトからコピーしたテキストが広告やUI部品だらけで読めなかったため、自動除去ツールを作成 |
| [06_Discord_Bridge](./06_Discord_Bridge) | **Discord-PCリモート操作ブリッジ** | Python, discord.py, Gemini API | 外出先から自宅PCのファイルに安全にアクセスする必要があり、Discordを経由したリモート操作ツールを構築 |
| [07_Discord_Legacy_Bot](./07_Discord_Legacy_Bot) | **多機能対話Botエージェント** | Python, discord.py, Gemini API | 人格フィルタと対話記憶を持つ、より人間らしいチャットBotを作りたかったため開発 |
| [08_Dialogue_Context_Retriever](./08_Dialogue_Context_Retriever) | **対話コンテキスト復元ツール** | Python, SQLite | IDEの更新でAI対話履歴がすべて消失。大切な対話脈絡を取り戻すために、ログ解析と全文検索で復旧するツールを開発 |

---

## 💡 設計原則

すべてのプロジェクトは、以下の4つの原則に基づいています：

- 処理前に、必ず元データのバックアップを取る。
- APIキーや認証情報をコード内にハードコードしない。
- 不要なAPIコールを最小限に抑える。
- 学術的な正しさより、目の前の業務課題を解決することを優先する。

---

## 👨‍💻 私の貢献

本リポジトリのコーディングは、AIツール（Antigravity IDE, Claude, Gemini）の支援を受けています。
私の貢献は、以下の4つに集中しています：

- 業務上のボトルネックやシステム障害を正確に特定すること。
- 現場の課題を、AIが実装可能な明確な仕様に翻訳すること。
- AIが生成したコードを繰り返しテストすること。
- 各ツールが元の課題を安全かつ確実に解決しているかを検証すること。

このプロセスは、私が現場監督や顧客対応を通じて身につけた「複雑な状況を整理し、解決可能な手順に翻訳する力」を、IT領域で活かす試みです。

---

## 🚀 動作環境とセットアップ
各ツールの詳細な使用方法は、各サブディレクトリ内の `README.md` をご参照ください。

本リポジトリは、IT Supportへのキャリアチェンジを進めるなかで、引き続き成長していく予定です。

<br>
<br>

---
---

# 🛠️ PENG WEIMING — IT Projects Built from Real Problems

This repository documents my transition into IT through practical projects built to solve real operational problems. While AI tools (Antigravity IDE, Claude, Gemini) assisted with implementation, each project originated from a real workflow challenge that I identified, defined, tested, and refined.

---

## 📂 Project Directory

| Directory | Project Name | Tech Stack | Why I Built It |
| :--- | :--- | :--- | :--- |
| [01_Legacy_Archive_Digitization_Pipeline](./01_Legacy_Archive_Digitization_Pipeline) | **Legacy Archive Digitization Pipeline** | Python, RegEx, YAML | Digitizing old paper archives involved tedious manual image mapping and text consolidation. I built a pipeline to automate the entire process. |
| [02_Log_Parser](./02_Log_Parser) | **AI Conversation Log Formatter** | Python, RegEx, Markdown | AI conversation logs from WebUI were messy and unreadable. I built a tool to automatically reformat them into clean Markdown. |
| [03_Media_Controller](./03_Media_Controller) | **OS Media Key Control Tool** | Python, Windows API, argparse | I wanted one-command media control from CLI, so I built a tool that sends OS-level media key signals directly. |
| [04_Realtime_Logger](./04_Realtime_Logger) | **AI Dialogue Realtime Logger** | Python, SQLite | AI conversations would disappear after sessions ended. I built a system to persist them to a database in real-time. |
| [05_Job_Cleaner](./05_Job_Cleaner) | **Job Description Text Cleaner** | Python, BeautifulSoup4, Requests | Job postings copied from websites were cluttered with ads and UI junk. I built a cleaner to extract only the useful content. |
| [06_Discord_Bridge](./06_Discord_Bridge) | **Discord-PC Remote Bridge** | Python, discord.py, Gemini API | I needed secure access to my home PC files while away. I built a remote bridge using Discord as the interface. |
| [07_Discord_Legacy_Bot](./07_Discord_Legacy_Bot) | **Multimodal Conversational Agent** | Python, discord.py, Gemini API | I wanted a chatbot with personality and conversation memory, so I built one with persona filters and dialogue summarization. |
| [08_Dialogue_Context_Retriever](./08_Dialogue_Context_Retriever) | **Dialogue Context Recovery Tool** | Python, SQLite | An IDE update wiped all my AI conversation history. I built a recovery tool using log parsing and full-text search to rescue the lost context. |

---

## 💡 Design Principles

Every project follows four principles:

- Protect original data before any modification.
- Never hardcode credentials or API keys.
- Minimize unnecessary API calls.
- Solve practical workflow problems first.

---

## 👨‍💻 My Contribution

The code in this repository was implemented with assistance from AI tools (Antigravity IDE, Claude, Gemini).
My contribution focused on:

- Defining the operational problem.
- Translating practical problems into clear specifications for AI-assisted implementation.
- Iteratively testing AI-generated implementations.
- Validating whether each solution solved the original problem safely and reliably.

This workflow reflects skills I developed through previous experience in project coordination and customer support, and I am now applying those same problem-solving approaches to IT.

---

## 🚀 Environment and Setup
For detailed setup instructions for each tool, please refer to the `README.md` in their respective subdirectories.

This repository will continue to grow as I develop new skills through my transition into IT Support.
