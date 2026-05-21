# 08 — Dialogue Context Retriever

A lightweight local tool that persists AI-human dialogue exchanges into a SQLite database and provides fast keyword / session-based retrieval, enabling seamless context restoration across LLM conversation resets.

---

## Origin Story & Background / 開発の経緯と背景

This project was born out of an actual production incident on May 20, 2026. Google's **Antigravity IDE** (a Gemini ecosystem development tool) underwent an unannounced major update to version 2.0. This update introduced breaking changes to the local storage architecture, forcefully migrating the IDE's internal conversation logs from `.pb` to `.db` format without prior warning. 

As a direct result of this sudden environmental shift, all ongoing AI-assisted conversation threads and critical development contexts within the IDE were instantly lost. This tool was rapidly developed as an emergency **defensive engineering** countermeasure specifically designed to parse the new `.db` architecture of Antigravity IDE, retrieve the lost conversations, and securely inject them back into the new environment.

本プロジェクトは、2026年5月20日に発生した実際のインシデントから誕生しました。Googleの**Antigravity IDE**（Geminiエコシステムの開発ツール）において、事前の通知なしにバージョン2.0への大規模なアップデートが実施され、ローカルストレージのフォーマットが強制的に `.pb` から `.db` へと変更されるという破壊的なアーキテクチャの変更が行われました。

この予期せぬ環境の激変により、IDE内で進行中だったすべてのAI協業対話と、重要な開発コンテキストが瞬時に失われました。本ツールは、Antigravity IDEの新しい `.db` アーキテクチャを解析し、失われた対話を抽出して新しい環境へ安全に復元・注入するための、**防御的エンジニアリング（Defensive Engineering）** に基づく緊急復旧メカニズムとして迅速に開発されたものです。

---

## Solution / 解決策

This tool addresses the problem by:

1. **Persisting dialogues in real-time** — Each exchange (user message + AI response) is immediately written to a local SQLite database (`dialogue_history.db`), ensuring zero data loss.
2. **Enabling precise retrieval** — A CLI-based search interface supports keyword search, session ID filtering, and recent-history queries.
3. **Outputting LLM-ready context** — Retrieved results are formatted as Markdown blocks, ready for direct injection into a new conversation prompt.

本ツールは以下の方法で課題を解決します：
1. **リアルタイム永続化** — 各対話（ユーザーメッセージ＋AIレスポンス）をローカルのSQLiteデータベースに即座に書き込み、データ損失をゼロにします。
2. **精密な検索** — CLIベースの検索インターフェースにより、キーワード検索、セッションIDフィルタリング、直近履歴クエリをサポートします。
3. **LLM注入用の出力** — 検索結果はMarkdown形式で出力され、新規対話のプロンプトに直接注入できます。

---

## Tech Stack / 技術スタック

`Python` / `SQLite` / `argparse` / `RegExp` / `PowerShell (Windows)`

---

## File Structure / ファイル構成

```
08_Dialogue_Context_Retriever/
├── db_initializer.py      # Database schema initializer
├── context_retriever.py   # CLI search & context restoration tool
├── README.md              # This file
└── dialogue_history.db    # (Generated locally, git-ignored)
```

---

## Usage / 使い方

### 1. Initialize the database / データベースの初期化

```bash
python db_initializer.py
```

This creates `dialogue_history.db` with the required schema.

### 2. Search dialogues / 対話の検索

**Keyword search / キーワード検索：**
```bash
python context_retriever.py --query "encoding"
```

**Session filter / セッション指定：**
```bash
python context_retriever.py --session "tech_design"
```

**Recent history / 直近の履歴：**
```bash
python context_retriever.py --recent 5
```

### Example Output / 出力例

```
[SEARCH] Keyword: "encoding"

============================================================
  Keyword Search: "encoding"
  Found 1 record(s)
============================================================

### [2026-05-20T10:00:00+09:00] Session: tech_design_session_01 | Seq: 1
**Speaker**: User | **Engine**: Gemini 3.1 Pro
\```
How should we handle UTF-8 encoding on Windows terminals?
\```
------------------------------------------------------------
```

---

## Database Schema / データベーススキーマ

| Column       | Type    | Description                              |
|:-------------|:--------|:-----------------------------------------|
| `id`         | INTEGER | Auto-incrementing primary key            |
| `session_id` | TEXT    | Conversation session identifier          |
| `seq_number` | INTEGER | Sequential exchange number within session|
| `timestamp`  | TEXT    | ISO 8601 timestamp                       |
| `engine`     | TEXT    | LLM engine name (e.g. Gemini, Claude)    |
| `speaker`    | TEXT    | "User" or "AI Agent"                     |
| `content`    | TEXT    | Full message content                     |

---

## Potential Risks & Limitations / 潜在的リスクと制限事項

### 1. Terminal Encoding (Windows) / ターミナルエンコーディング

Windows terminals default to locale-specific encodings (e.g. CP932 for Japanese, CP950 for Traditional Chinese). When displaying multilingual dialogue content, special characters may render as `?` replacement characters.

**Mitigation:** The scripts include `sys.stdout.reconfigure(errors='replace')` as a defensive measure. For best results, configure your terminal to UTF-8:
```bash
chcp 65001
```

Windowsターミナルはロケール固有のエンコーディング（例：CP932）をデフォルトで使用します。多言語対話を表示する際、特殊文字が `?` に置換される場合があります。スクリプトには防御措置として `sys.stdout.reconfigure(errors='replace')` が含まれていますが、最良の結果を得るには `chcp 65001` でUTF-8に設定してください。

### 2. SQLite Concurrency / SQLiteの同時実行制限

SQLite uses file-level locking and does not support high-concurrency write operations. This tool is designed for **single-user, local use only**. Running multiple processes that write to the same database simultaneously may cause `database is locked` errors.

SQLiteはファイルレベルのロックを使用し、高い同時書き込みをサポートしていません。本ツールは**シングルユーザーのローカル使用**を前提に設計されています。

### 3. Database File Portability / データベースファイルの移植性

The `dialogue_history.db` file is generated locally and excluded from version control via `.gitignore`. Each user must run `db_initializer.py` after cloning to create their own database instance.

`dialogue_history.db` はローカルで生成され、`.gitignore` によりバージョン管理から除外されます。クローン後、各ユーザーが `db_initializer.py` を実行して独自のデータベースインスタンスを作成する必要があります。

---

## License

This project is part of the `automation-utility-suite` repository.
