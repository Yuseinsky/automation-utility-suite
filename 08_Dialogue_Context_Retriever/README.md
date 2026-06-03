# 💬 対話コンテキスト復元ツール (Dialogue Context Retriever)

## 📌 プロジェクト概要
ローカル環境で動作するAI対話履歴の永続化・検索・復元ツールです。SQLiteデータベースにAI-人間の対話を保存し、キーワード検索、セッション指定、直近履歴取得により、LLMの対話リセット時にシームレスなコンテキスト復元を可能にします。

---

## 🏗️ Origin Story / 開発の経緯

本プロジェクトは、**2026年5月20日に発生した実際のプロダクションインシデント**から誕生しました。

Google の **Antigravity IDE**（Geminiエコシステムの開発ツール）において、事前の通知なしにバージョン2.0への大規模アップデートが実施され、ローカルストレージのフォーマットが `.pb` から `.db` へと強制的に変更されました。この予期せぬアーキテクチャの激変により、進行中だったすべてのAI協業対話と重要な開発コンテキストが**瞬時に消失**しました。

本ツールは、Antigravity IDEの新しい `.db` アーキテクチャを解析し、失われた対話を抽出して新しい環境へ安全に復元・注入するための、**防御的エンジニアリング（Defensive Engineering）** に基づく緊急復旧メカニズムとして迅速に開発されたものです。

---

## 🛠️ 技術スタック
- **Language**: Python 3.9+
- **Database**: SQLite 3 (ファイルベース、サーバー不要)
- **CLI**: `argparse` (コマンドライン引数解析)
- **Key Technology**:
  - SQLite FTS5 (Full-Text Search)
  - JSONL Log Parsing & Extraction
  - Read-only DB connection (URI mode: `?mode=ro`)
  - Context Manager による安全な接続管理
  - SQL LIKE Wildcard Escape (萬用字元注入防護)
  - Parameterized Queries (SQL Injection 防護)
  - Performance Indexes (`session_id`, `timestamp DESC`)

---

## ⚡ Quick Start

### 1. Initialize the database / データベースの初期化
```bash
python db_initializer.py
```
Creates `dialogue_history.db` with the required schema and performance indexes.

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

**Full content display / 全文表示：**
```bash
python context_retriever.py --query "encoding" --full
```

**Export to file / ファイル出力：**
```bash
python context_retriever.py --query "encoding" --export results.md
```

**Custom limit / 結果数の指定：**
```bash
python context_retriever.py --recent 100 --limit 200
```

### 3. Recover from IDE logs (New in V4.0) / IDEログからの復元

**Scan IDE brain for sessions / セッションのスキャン：**
```bash
python context_retriever.py --scan-ide
```

**Recover specific session / 特定セッションの復元：**
```bash
python context_retriever.py --recover-ide "session-uuid" --export recovery.md
```

---

## ⚙️ 主な特徴

### 1. 🧠 リアルタイム永続化
各対話（ユーザーメッセージ＋AIレスポンス）をローカルのSQLiteデータベースに即座に書き込み、データ損失をゼロにします。

### 2. 🔍 精密な検索
CLIベースの検索インターフェースにより、キーワード検索、セッションIDフィルタリング、直近履歴クエリをサポートします。

### 3. 📤 LLM注入用の出力
検索結果はMarkdown形式で出力され、新規対話のプロンプトに直接注入できます。`--export` で直接ファイルに書き出すことも可能です。

---

## 📂 File Structure / ファイル構成

```
08_Dialogue_Context_Retriever/
├── db_initializer.py      # Database schema initializer
├── context_retriever.py   # CLI search, FTS5 & IDE log restoration tool (V4.0)
├── README.md              # This file
└── dialogue_history.db    # (Generated locally, git-ignored)
```

---

## 📊 Database Schema / データベーススキーマ

| Column       | Type    | Constraint       | Description                              |
|:-------------|:--------|:-----------------|:-----------------------------------------|
| `id`         | INTEGER | PRIMARY KEY AUTO | Auto-incrementing primary key            |
| `session_id` | TEXT    | NOT NULL         | Conversation session identifier          |
| `seq_number` | INTEGER | NOT NULL DEFAULT 0 | Sequential exchange number within session|
| `timestamp`  | TEXT    | NOT NULL         | ISO 8601 timestamp                       |
| `engine`     | TEXT    | NOT NULL DEFAULT 'unknown' | LLM engine name (e.g. Gemini, Claude) |
| `speaker`    | TEXT    | NOT NULL         | "User" or "AI Agent"                     |
| `content`    | TEXT    | NOT NULL         | Full message content                     |

**Indexes:**
- `idx_session` on `session_id` — Accelerates session-based queries
- `idx_timestamp` on `timestamp DESC` — Accelerates chronological sorting

---

## 🛡️ セキュリティ設計 (Defense in Depth)

| 防御層 | 機構 | 対象脅威 |
|---|---|---|
| **パラメータ化クエリ** | `cursor.execute(sql, params)` | SQL Injection |
| **ワイルドカードエスケープ** | `_escape_like()` + `ESCAPE '\\'` | LIKE Wildcard Injection (検索汚染) |
| **読み取り専用接続** | `?mode=ro` URI mode | 意図しない書き込み / DBロック競合 |
| **Context Manager** | `try...finally: conn.close()` | 接続リソースリーク |
| **パフォーマンスインデックス** | `idx_session`, `idx_timestamp` | 大量データ時の全表スキャン |

---

## ⚠️ Known Limitations / 制限事項

### 1. Terminal Encoding (Windows)
Windows terminals default to locale-specific encodings (e.g. CP932 for Japanese). The script includes `sys.stdout.reconfigure(errors='replace')` as mitigation. For best results: `chcp 65001`.

### 2. SQLite Concurrency
SQLite uses file-level locking. This tool uses read-only mode to minimize conflicts, but concurrent heavy writes from another process may still cause brief contention.

### 3. Database Portability
The `.db` file is generated locally and excluded from version control. Run `db_initializer.py` after cloning to create your own instance.

---

<br>
<br>

---
---

# 💬 Dialogue Context Retriever

## 📌 Project Overview
A lightweight local CLI tool that persists AI-human dialogue exchanges into a SQLite database and provides fast keyword / session-based retrieval, enabling seamless context restoration across LLM conversation resets.

---

## 🏗️ Origin Story
Born from a production incident on May 20, 2026 when Google's Antigravity IDE forcefully migrated its local storage from `.pb` to `.db` format without warning, instantly destroying all ongoing AI conversation threads. This tool was rapidly developed as an emergency **Defensive Engineering** countermeasure.

---

## 🛠️ Tech Stack
- **Language**: Python 3.9+
- **Database**: SQLite 3 (file-based, serverless)
- **CLI**: `argparse`
- **Core Technology**: SQLite FTS5, JSONL parsing, Read-only DB, Context Manager, Wildcard Escape, Parameterized Queries, Performance Indexes

---

## ⚙️ Key Features
1. **Real-time Persistence** — Zero data loss via immediate SQLite writes
2. **High-Performance Search** — Keyword, FTS5 semantic search, and chronological filtering
3. **IDE Log Rescue** — Direct parsing of IDE `transcript.jsonl` files to salvage lost states
4. **LLM-ready Output** — Markdown-formatted results for direct prompt injection
5. **File Export** — `--export` for direct Markdown file output

---

## 🛡️ Security (Defense in Depth)

| Layer | Mechanism | Threat Mitigated |
|---|---|---|
| **Parameterized Queries** | `cursor.execute(sql, params)` | SQL Injection |
| **Wildcard Escape** | `_escape_like()` + `ESCAPE '\\'` | LIKE Wildcard Injection |
| **Read-only Connection** | `?mode=ro` URI mode | Unintended writes / DB lock conflicts |
| **Context Manager** | `try...finally: conn.close()` | Connection resource leak |
| **Performance Indexes** | `idx_session`, `idx_timestamp` | Full table scan on large datasets |

---

## 💡 Engineering Value
This project demonstrates **incident-driven defensive engineering** — the ability to rapidly design and deploy a recovery tool under production pressure. The architecture showcases proper SQLite best practices (parameterized queries, wildcard escaping, read-only connections, connection lifecycle management) and CLI design patterns suitable for DevOps tooling.
