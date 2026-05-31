# 💾 汎用型 AI 対話ログフレームワーク (Universal Dialogue Logger)

<h2 id="日本語">🇯🇵 日本語</h2>

### 📖 プロジェクト概要 (Overview)
あらゆる AI アプリケーション（OpenAI、Gemini、Claude、Discord Bot、カスタム LLM パイプラインなど）に統合可能な**イベント駆動型対話ログフレームワーク**です。

外部スケジューラやポーリングループを一切使用せず、AI が応答を返した**その瞬間**に SQLite へ直接書き込む設計により、データの欠損を原理的に排除しています。さらに、設定可能な閾値（デフォルト: 10件）に到達すると、自動的に美しい Markdown トランスクリプトを生成・出力します。

Python 標準ライブラリのみで動作し、外部依存は一切ありません。

### 🛠️ 技術スタック (Tech Stack)
- **言語**: Python 3
- **データベース**: SQLite 3 (ACID トランザクション保証)
- **コア技術**: イベント駆動アーキテクチャ、アトミックトランザクション、自動 Markdown エクスポート

### 📂 アーキテクチャ (Architecture)

```
04_Realtime_Logger/
├── universal_logger.py   # DialogueLogger クラス (DB 操作 + Markdown 生成)
├── demo_usage.py         # 統合デモスクリプト
└── README.md
```

#### `universal_logger.py` — 統合 Logger クラス
- **`DialogueLogger` クラス**: 初期化時に SQLite データベースとテーブルを自動作成。
- **`log_exchange()` メソッド**: ユーザーメッセージと AI レスポンスを単一のアトミックトランザクションで書き込み。`os.remove()` やバッファファイルは一切使用しない安全設計。
- **`export_to_markdown()` メソッド**: セッション単位で対話履歴を構造化 Markdown として出力。月別サブディレクトリに自動整理。
- **`query_session()` メソッド**: 特定セッションの全対話を辞書リストとして取得。
- **閾値ベースの自動フラッシュ**: `log_exchange()` 内部で自動カウントし、閾値到達時に Markdown エクスポートを自動トリガー。

### 🚀 クイックスタート (Quick Start)
```python
from universal_logger import DialogueLogger

# 初期化（DB が存在しなければ自動作成）
logger = DialogueLogger(db_path="memory.db", auto_flush_threshold=10)

# AI が応答を返した瞬間に 1 行で記録
logger.log_exchange("session_001", "こんにちは", "こんにちは！", engine="Gemini")

# セッションの全対話を取得
data = logger.query_session("session_001")

# 手動で Markdown エクスポート
logger.export_to_markdown("session_001")
```

### ⚠️ 既知の制限事項 (Known Limitations)
1. **単一プロセス設計**: SQLite は同時書き込み（Write-Ahead Logging 非使用時）に制約があるため、複数プロセスからの同時書き込みには対応していません。
2. **ローカル専用**: クラウドデータベース（PostgreSQL 等）との統合は本フレームワークのスコープ外です。

<br>
<br>

---
---

# 💾 Universal AI Dialogue Logger Framework

<h2 id="english">🇺🇸 English</h2>

### 📖 Project Overview
An **event-driven dialogue logging framework** designed to integrate with any AI application — OpenAI, Gemini, Claude, Discord Bots, or custom LLM pipelines.

Instead of relying on external schedulers or polling loops, this framework writes directly to SQLite **the instant** the AI produces a response, eliminating data loss by design. When a configurable threshold (default: 10 exchanges) is reached, it automatically generates and exports a beautifully structured Markdown transcript.

Runs entirely on the Python standard library with zero external dependencies.

### 🛠️ Tech Stack
- **Language**: Python 3
- **Database**: SQLite 3 (ACID transaction guarantee)
- **Core Technology**: Event-Driven Architecture, Atomic Transactions, Auto Markdown Export

### 📂 Architecture

```
04_Realtime_Logger/
├── universal_logger.py   # DialogueLogger class (DB ops + Markdown generation)
├── demo_usage.py         # Integration demo script
└── README.md
```

#### `universal_logger.py` — Unified Logger Class
- **`DialogueLogger` class**: Auto-creates the SQLite database and schema on initialization.
- **`log_exchange()` method**: Writes both user message and AI response in a single atomic transaction. No `os.remove()`, no buffer files — safe by design.
- **`export_to_markdown()` method**: Exports session dialogue history as structured Markdown, auto-organized into monthly subdirectories.
- **`query_session()` method**: Retrieves all exchanges for a given session as a list of dictionaries.
- **Threshold-based auto-flush**: Internally counts exchanges within `log_exchange()` and automatically triggers Markdown export when the threshold is reached.

### 🚀 Quick Start
```python
from universal_logger import DialogueLogger

# Initialize (auto-creates DB if not exists)
logger = DialogueLogger(db_path="memory.db", auto_flush_threshold=10)

# Record an exchange the instant the AI responds — one line
logger.log_exchange("session_001", "Hello!", "Hi there!", engine="GPT-4")

# Query all exchanges for a session
data = logger.query_session("session_001")

# Manually export to Markdown
logger.export_to_markdown("session_001")
```

### ⚠️ Known Limitations
1. **Single-process design**: SQLite has write concurrency constraints (without WAL mode), so simultaneous writes from multiple processes are not supported.
2. **Local-only**: Integration with cloud databases (PostgreSQL, etc.) is outside the scope of this framework.

<br>
<br>

---
---

# 💾 通用型 AI 對話紀錄框架

<h2 id="繁體中文">🇹🇼 繁體中文</h2>

### 📖 專案簡介 (Overview)
一個**事件驅動式的對話紀錄框架**，可與任何 AI 應用程式整合 — 包括 OpenAI、Gemini、Claude、Discord Bot 或自訂 LLM 管線。

不使用任何外部排程器或輪詢迴圈，而是在 AI 產生回應的**那一瞬間**直接寫入 SQLite，從設計層面消除資料遺失的可能性。當可設定的閾值（預設：10 筆）達到時，自動生成並匯出格式精美的 Markdown 逐字稿。

完全基於 Python 標準函式庫，零外部依賴。

### 🛠️ 技術棧 (Tech Stack)
- **語言**: Python 3
- **資料庫**: SQLite 3 (ACID 交易保證)
- **核心技術**: 事件驅動架構、原子交易、自動 Markdown 匯出

### 📂 架構 (Architecture)

```
04_Realtime_Logger/
├── universal_logger.py   # DialogueLogger 類別 (資料庫操作 + Markdown 生成)
├── demo_usage.py         # 整合示範腳本
└── README.md
```

#### `universal_logger.py` — 統合 Logger 類別
- **`DialogueLogger` 類別**：初始化時自動建立 SQLite 資料庫與資料表結構。
- **`log_exchange()` 方法**：以單一原子交易 (Atomic Transaction) 同時寫入使用者訊息與 AI 回應。不使用 `os.remove()`，不使用暫存檔案 — 從設計層面保障安全。
- **`export_to_markdown()` 方法**：以會話為單位，將對話歷史匯出為結構化 Markdown，自動依月份歸檔。
- **`query_session()` 方法**：將指定會話的所有對話以字典列表形式取回。
- **閾值式自動排版**：在 `log_exchange()` 內部自動計數，達到閾值時自動觸發 Markdown 匯出。

### 🚀 快速開始 (Quick Start)
```python
from universal_logger import DialogueLogger

# 初始化（資料庫不存在時自動建立）
logger = DialogueLogger(db_path="memory.db", auto_flush_threshold=10)

# AI 回應的瞬間，一行搞定紀錄
logger.log_exchange("session_001", "你好", "你好！", engine="Gemini")

# 查詢會話的所有對話
data = logger.query_session("session_001")

# 手動匯出 Markdown
logger.export_to_markdown("session_001")
```

### ⚠️ 已知限制 (Known Limitations)
1. **單一進程設計**：SQLite 在未啟用 WAL 模式時，不支援多進程同時寫入。
2. **僅限本地端**：與雲端資料庫（PostgreSQL 等）的整合不在本框架的範圍內。
