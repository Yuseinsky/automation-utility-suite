# 💬 多機能・多模態対応AIチャットボットシステム (Discord Chatbot Bot)

## 📌 プロジェクト概要
Discord 上で動作し、Google Gemini API（`gemini-2.5-pro`）と連携する対話エージェントシステムです。

単なる一問一答のボットではなく、会話の流れを正確に記憶する「短期記憶（コンテキストセッション）管理」、対話が蓄積した際にディスクに自動/手動で書き出す「自動アーカイブ（メモリ結晶化）システム」、周囲の会話状況を察知して不要な処理を抑える「バックログ（コンテキストキュー）システム」など、実用性の高い高度な機能を搭載しています。

---

## 🛠️ 技術スタック
- **Language**: Python 3.9+
- **Framework**: `discord.py` (v2.x, Client / event-driven)
- **AI Engine**: Google Gemini API (`gemini-2.5-pro` / Multimodal)
- **Key Technology**:
  - Non-blocking async I/O (`send_message_async` / `asyncio.to_thread`)
  - Per-channel `asyncio.Lock()` for concurrent state protection
  - Multi-encoding file reader with 3-tier fallback
  - Rate-limited message chunking with hard page limits
  - Memory Consolidation with Context Seed injection

---

## ⚡ Quick Start

### 1. Install Dependencies
```bash
pip install discord.py google-generativeai python-dotenv
# Optional (recommended): pip install charset-normalizer
```

### 2. Set Environment Variables (or .env file)
```bash
# Required
DISCORD_TOKEN="your_discord_bot_token"
GEMINI_API_KEY="your_gemini_api_key"

# Recommended
ADMIN_USER_ID="your_discord_user_id"

# Optional
ALLOWED_CHANNEL_ID="0"  # 0 = all channels
```

> ⚠️ **Critical**: `ADMIN_USER_ID` must be set to a Discord User ID (numeric). If left as 0, admin-only features will be disabled.

### 3. Run
```bash
python discord_chatbot.py
```

---

## ⚙️ 主な特徴とシステム構造

### 1. 🧠 キャラクター性（ペルソナ）と動的変化
- 独自のシステムプロンプト（`system_instruction.txt`）を読み込み、完全な対話キャラクターとして機能。
- 多段エンコーディング検出により、非UTF-8の指示書もクラッシュせず読み込み可能。

### 2. 💎 記憶のアーカイブ＆リセットシステム (Memory Consolidation)
- 対話履歴が規定値（80回）に達するか、管理者から `!archive` コマンドを受け取ると自動/手動でアーカイブ。
- 要約「ダイジェスト（.md）」と「RAWログ原稿（.md）」をローカルディスクに非同期保存。
- 要約データを次のセッションの「Context Seed」として再注入し、トークン爆発を防ぎながら長期文脈を維持。
- **Death Loop Prevention**: Context Seed 注入失敗時も、セッションを必ずリセットし、無限アーカイブループを防止。

### 3. 👂 周囲の会話の学習（コンテキスト・バックログ）機能
- Bot宛てでない会話をバックログキューにプール（上限: 15件）。
- 呼びかけ時にプール済みの文脈を一括注入し、「空気を読む」返答を実現。
- メモリリーク防止のため、`MAX_BACKLOG` でキューサイズを強制制限。

### 4. 🖼️ 画像認識（多模態）対応
- 画像のみ（テキストなし）のメッセージにも正しく応答。
- Discord添付ファイルをバイナリストリームとしてGemini APIに直接送信。

---

## 🛡️ セキュリティ設計 (Defense in Depth)

| 防御層 | 機構 | 対象脅威 |
|---|---|---|
| **管理者認証** | `ADMIN_USER_ID` (数値ID, 偽造不可) | ユーザー名偽装によるなりすまし |
| **非同期API呼出** | `await chat.send_message_async()` | Event Loop凍結・心拍断線 |
| **チャネルロック** | per-channel `asyncio.Lock()` | 並行メッセージによる履歴汚染 |
| **非同期ファイルI/O** | `asyncio.to_thread()` | ディスクI/Oによるボット凍結 |
| **レート制限保護** | `MAX_CHUNKS` ハードリミット | Discord 429 Rate Limit |
| **バックログ制限** | `MAX_BACKLOG` (15件) | メモリリーク / OOM |
| **Death Loop防止** | seed失敗時も強制セッションリセット | 無限アーカイブループ |
| **多段エンコーディング** | UTF-8 → charset_normalizer → chardet → replace | 起動時エンコーディングクラッシュ |
| **環境変数隔離** | `os.environ.get()` + `.env` | リポジトリ上のトークン漏洩 |
| **パス秘匿** | アーカイブ通知にファイル名のみ表示 | ディレクトリ構造の漏洩 |
| **監査ログ** | `[AUDIT]` 形式のターミナル記録 | フォレンジック追跡 |

---

## ⚠️ Known Limitations

1. **Single-process Architecture**: メモリ内のセッションとバックログはプロセス再起動で消失します。
2. **Image-only Multimodal**: テキスト添付ファイル（.txt, .pdf等）はサポートされていません。
3. **Keyword Trigger Sensitivity**: `bot`, `assistant`, `system` などのキーワードが含まれるメッセージは全て応答トリガーとなります。

<br>
<br>

---
---

# 💬 Multimodal Conversational Agent System (Discord Chatbot)

## 📌 Project Overview
An advanced Discord dialogue agent integrated with Google Gemini API (`gemini-2.5-pro`) featuring intelligent session memory, automated conversation archival, ambient context queuing, and multimodal image recognition.

---

## 🛠️ Tech Stack
- **Language**: Python 3.9+
- **Framework**: `discord.py` (v2.x, Client / Event-driven)
- **AI Engine**: Google Gemini API (`gemini-2.5-pro` Multimodal)
- **Core Technology**:
  - Non-blocking async I/O (`send_message_async` / `asyncio.to_thread`)
  - Per-channel concurrency locks (`asyncio.Lock`)
  - Multi-encoding file reader with 3-tier fallback
  - Rate-limited chunked output with hard page limits
  - Memory Consolidation with Context Seed injection

---

## ⚙️ Key Features & Architecture

### 1. 🧠 Custom Persona Alignment
- Loads persona from `system_instruction.txt` with multi-encoding fallback.

### 2. 💎 Memory Consolidation & Archival
- Auto-archives at 80 history entries (or via `!archive` command).
- Dual-track output: Markdown Summary + Raw Transcript.
- Seeds new sessions with summary for context continuity.
- **Death Loop Prevention**: Session always resets even if seed fails.

### 3. 👂 Context Backlog Queue
- Pools ambient conversation (max 15 entries) without API calls.
- Injects pooled context when addressed for contextual awareness.

### 4. 🖼️ Multimodal Capabilities
- Responds to image-only messages (no text required).
- Binary stream image input to Gemini API.

---

## 🛡️ Security & Performance (Defense in Depth)

| Layer | Mechanism | Threat Mitigated |
|---|---|---|
| **Admin Auth** | `ADMIN_USER_ID` (immutable numeric ID) | Username spoofing |
| **Async API** | `await chat.send_message_async()` | Event Loop freeze / heartbeat disconnect |
| **Channel Locks** | Per-channel `asyncio.Lock()` | Concurrent history corruption |
| **Async File I/O** | `asyncio.to_thread()` | Disk I/O bot freeze |
| **Rate Limit Guard** | `MAX_CHUNKS` hard limit | Discord 429 Rate Limit |
| **Backlog Limit** | `MAX_BACKLOG` (15 entries) | Memory leak / OOM |
| **Death Loop Guard** | Force session reset on seed failure | Infinite archive loop |
| **Multi-Encoding** | UTF-8 → charset_normalizer → chardet → replace | Startup encoding crash |
| **Secret Isolation** | `os.environ.get()` + `.env` | Token leakage |
| **Path Concealment** | Archive notifications show filename only | Directory structure exposure |
| **Audit Trail** | `[AUDIT]` structured terminal logging | Forensic tracing |

---

## 💡 Engineering Value
This bot demonstrates practical solutions to **managing LLM context window boundaries and token pricing trade-offs**. The Memory Consolidation pattern (summarize → archive → seed) implements an Infinite Context Sliding Window, while the Ambient Backlog Queue enables context-aware responses without wasteful API calls. Combined with Defense in Depth security (channel locks, async I/O, rate limiting), it showcases production-grade AI agent architecture.
