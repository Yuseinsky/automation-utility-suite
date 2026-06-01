# 🌉 Discord-PCリモートファイル管理ブリッジ (Discord Bridge)

## 📌 プロジェクト概要
外出先のスマートフォンや任意のデバイスのDiscordクライアントから、スラッシュコマンド（Slash Commands）を介して自宅のローカルPC（開発マシン）内のファイルを直接読み書き・操作できる、遠隔ファイルシステム制御ブリッジツールです。

セキュリティを最優先に設計されており、管理者（Administrator）のDiscordユーザーIDのみに応答する「アクセス制限チェック（Check Filter）」や、パス・トラバーサル攻撃を防ぐ「パスジェイル（Path Jail）」、Discord APIの仕様制限を回避する「自動長文スライシングエンジン」を搭載しています。

---

## 🛠️ 技術スタック
- **Language**: Python 3.9+
- **Framework**: `discord.py` (v2.x, Slash Commands / application commands)
- **AI Engine**: Google Gemini API (`gemini-2.5-pro`)
- **Key Technology**:
  - Discord Slash Commands (`bot.tree`) with AOP decorator-based auth
  - Non-blocking async I/O (`asyncio.to_thread`) for file operations
  - Multi-encoding file reader with 3-tier fallback (UTF-8 → charset_normalizer → chardet)
  - Output Sanitization (Markdown escape hatch prevention)
  - Structured audit logging for all file operations

---

## ⚡ Quick Start

### 1. Install Dependencies
```bash
pip install discord.py google-generativeai
# Optional (recommended): pip install charset-normalizer
```

### 2. Set Environment Variables
```bash
# Required
export DISCORD_TOKEN="your_discord_bot_token"
export GEMINI_API_KEY="your_gemini_api_key"
export ADMIN_USER_ID="your_discord_user_id"

# Optional
export BRIDGE_WORKSPACE="/path/to/allowed/directory"  # Default: script directory
```

> ⚠️ **Critical**: If `ADMIN_USER_ID` is not set, ALL commands will be silently rejected with "Access Denied". The bot will appear online but non-functional.

### 3. Run
```bash
python discord_bridge.py
```

---

## ⚙️ 主な機能とコマンド構成

### 1. 📁 `/read [file_path]` (リモートファイル読み込み)
- **動作**: ローカルPC内のテキストファイルを読み込み、Discord上に埋め込み（Embed）テキストとして出力。
- **防御機構**:
  - パスジェイル（Path Jail）：`SAFE_WORKSPACE` 外へのアクセスを完全遮断。
  - 非同期I/O（`asyncio.to_thread`）：大きなファイルを読んでもBotがフリーズしない。
  - 多段エンコーディング自動検出：UTF-8、Shift-JIS、EUC-JP 等に自動対応。
  - Markdown出力サニタイズ：ファイル内の ` ``` ` がDiscordの表示を壊さない。

### 2. 💾 `/write [file_path] [content]` (リモートファイル書き込み)
- **動作**: Discord入力欄からローカルPC内のファイルを新規作成・上書き保存。
- **防御機構**:
  - パスジェイル：書き込み先も `SAFE_WORKSPACE` 内に限定。
  - 空文字列保護：空のコンテンツによる意図しないファイル消去を防止。
  - 親ディレクトリ自動作成（`os.makedirs`）。
  - 改行エスケープ復元（`\\n` → 実際の改行）。

### 3. 💬 `/chat [message]` (AI連携アシスタント)
- **動作**: AIモデル（Gemini API）と連携し、コンテキスト記憶セッションを用いて対話。
- **防御機構**:
  - セッション履歴の肥大化警告（閾値超過時に自動通知）。
  - API エラーの精密分類（400/403/429 を判別し、具体的な対処法を提示）。

### 4. 🔄 `/clear` (セッションリセット)
- **動作**: AIチャットセッションのメモリを手動リセット。Token超過やコスト膨張を防止。

---

## 🛡️ セキュリティ設計 (Security & Performance)

### Defense in Depth (縦深防御)

| 防御層 | 機構 | 対象脅威 |
|---|---|---|
| **管理者認証** | `@app_commands.check(is_admin)` AOP デコレータ | 不正ユーザーの全コマンド遮断 |
| **パスジェイル** | `os.path.commonpath` による実行時パス検証 | Path Traversal 攻撃 (例: `../../System32`) |
| **非同期I/O** | `asyncio.to_thread` によるファイル操作の非ブロッキング化 | Event Loop 凍結・心拍断線 |
| **出力サニタイズ** | Markdown 反引号のゼロ幅スペース挿入 | Discord表示崩壊・コード注入 |
| **多段エンコーディング** | UTF-8 → charset_normalizer → chardet → replace | Shift-JIS/EUC-JP ファイル読み込みクラッシュ |
| **レート制限保護** | `MAX_CHUNKS` による出力ページ数ハードリミット | Discord 429 Rate Limit による Bot 凍結 |
| **環境変数隔離** | `os.environ.get()` によるシークレット管理 | リポジトリ上のトークン漏洩 |
| **起動時バリデーション** | Token/API Key/Admin ID の三重検証 | Silent Failure（無言死亡）|
| **監査ログ** | `[AUDIT]` 形式のターミナル操作記録 | 不正アクセスのフォレンジック追跡 |
| **ダブルレスポンス防止** | `interaction.response.is_done()` チェック | エラーハンドラ自身のクラッシュ |

### Auto-Chunking Buffer
出力テキストがDiscordの制限（Embed Description: 4,096文字）を超える場合、`chunk_and_send` 処理により自動ページ分割されます。安全上限（デフォルト: 5ページ）を超える場合は自動的に截断され、警告メッセージが表示されます。

<br>
<br>

---
---

# 🌉 Discord-PC Remote File Management Bridge (Discord Bridge)

## 📌 Project Overview
A remote file-system administration bridge tool that enables developers to securely read, write, and manage files on a home PC (development machine) via Discord Slash Commands from a smartphone or any external device.

Designed with a **Defense in Depth** security architecture, the bot includes a strict Admin Check Filter, Path Jail sandboxing, non-blocking async I/O, output sanitization, multi-encoding file support, and structured audit logging.

---

## 🛠️ Tech Stack
- **Language**: Python 3.9+
- **Framework**: `discord.py` (v2.x, Slash Commands / App Commands)
- **AI Engine**: Google Gemini API (`gemini-2.5-pro`)
- **Core Technology**:
  - AOP decorator-based authentication (`@app_commands.check`)
  - Non-blocking file I/O via `asyncio.to_thread`
  - 3-tier encoding detection fallback (UTF-8 → charset_normalizer → chardet)
  - Markdown output sanitization (zero-width space injection)
  - Rate-limited chunked message delivery with hard page limits
  - Terminal-based audit trail logging

---

## ⚙️ Features & Command Architecture

### 1. 📁 `/read [file_path]` (Remote File Read)
- Reads local text files and renders them in Discord embeds.
- **Defenses**: Path Jail, async I/O, multi-encoding fallback, Markdown sanitization, chunked output with page limits.

### 2. 💾 `/write [file_path] [content]` (Remote File Write)
- Writes/overwrites text content on the host PC from Discord.
- **Defenses**: Path Jail, async I/O, empty content protection, auto directory creation, newline escape reconstruction.

### 3. 💬 `/chat [message]` (Contextual AI Assistant)
- Interacts with Gemini API using persistent chat session with context memory.
- **Defenses**: Session size warning, API error classification (400/403/429), actionable hints.

### 4. 🔄 `/clear` (Session Reset)
- Manually resets the AI chat session to prevent token explosion and cost overrun.

---

## 🛡️ Security & Performance Design

| Defense Layer | Mechanism | Threat Mitigated |
|---|---|---|
| **Admin Auth** | `@app_commands.check(is_admin)` AOP decorator | Unauthorized command execution |
| **Path Jail** | `os.path.commonpath` runtime path validation | Path Traversal (`../../System32`) |
| **Async I/O** | `asyncio.to_thread` for all file operations | Event Loop freeze / heartbeat disconnect |
| **Output Sanitization** | Zero-width space injection in triple backticks | Discord Markdown escape hatch |
| **Multi-Encoding** | UTF-8 → charset_normalizer → chardet → replace | Shift-JIS/EUC-JP decode crashes |
| **Rate Limit Guard** | `MAX_CHUNKS` hard limit on output pages | Discord 429 Rate Limit bot freeze |
| **Secret Isolation** | `os.environ.get()` for all credentials | Repository token leakage |
| **Startup Validation** | Triple check: Token + API Key + Admin ID | Silent failure / delayed bomb |
| **Audit Trail** | `[AUDIT]` structured terminal logging | Forensic tracing of unauthorized access |
| **Double Response Guard** | `interaction.response.is_done()` check | Error handler self-crash |

---

## ⚠️ Known Limitations

1. **No File Upload/Download**: Only text content is supported. Binary files (images, archives) cannot be read or written through this bridge.
2. **Chat Memory Persistence**: Chat session history is stored in-memory only. Restarting the bot clears all conversation context.
3. **Single Admin**: Only one administrator ID is supported. Multi-admin support would require a role-based access control system.
4. **Encoding Detection Accuracy**: If neither `charset-normalizer` nor `chardet` is installed, non-UTF-8 files may contain replacement characters (`�`).

---

## 💡 Engineering Value & Business Application
This tool demonstrates a practical implementation of **secure remote system administration via chat-based interfaces (ChatOps)**. By combining Discord's ubiquitous mobile client with file system access controls and AI-powered assistance, it enables developers to perform critical file operations from any device without exposing SSH ports or VPN infrastructure. The Defense in Depth security architecture (Path Jail, async I/O, audit logging) showcases enterprise-grade security thinking applied to a lightweight automation tool.
