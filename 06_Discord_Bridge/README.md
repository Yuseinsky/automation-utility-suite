# 🌉 Discord-PCリモートファイル管理ブリッジ (Discord Bridge)

## 📌 プロジェクト概要
外出先のスマートフォンや任意のデバイスのDiscordクライアントから、スラッシュコマンド（Slash Commands）を介して自宅のローカルPC（開発マシン）内のファイルを直接読み書き・操作できる、遠隔ファイルシステム制御ブリッジツールです。

セキュリティを最優先に設計されており、管理者（Administrator）のDiscordユーザーIDのみに応答する「アクセス制限チェック（Check Filter）」や、Discord APIの仕様制限（メッセージ最大2000文字）を回避する「自動長文スライシングエンジン」を搭載しています。

---

## 🛠️ 技術スタック
- **Language**: Python 3
- **Framework**: `discord.py` (v2.x, Slash Commands / application commands)
- **AI Engine**: Google Gemini API (`gemini-2.5-pro`)
- **Key Technology**: 
  - Discord Slash Commands (`bot.tree`)
  - OS ファイルシステム操作、例外エラーハンドリング
  - Discord Embeds による動的システムUI表示

---

## ⚙️ 主な機能とコマンド構成

### 1. 📁 `/read [ファイルパス]` (リモートファイル読み込み)
- **動作**: ローカルPC内のテキストファイル（Markdownやソースコード）を読み込み、Discord上に埋め込み（Embed）テキストとして出力。
- **機能**: 
  - 相対パス（自動的に絶対パスに解決）と絶対パスの両方に対応。
  - ファイル未検出（FileNotFoundError）やI/Oエラーを安全に例外キャッチし、ユーザーに分かりやすく通知。

### 2. 💾 `/write [ファイルパス] [書き込み内容]` (リモートファイル書き込み)
- **動作**: Discord的入力欄からローカルPC內的ファイル新規作成・上書き保存。
- **機能**:
  - 親ディレクトリが存在しない場合、自動的に再帰作成（`os.makedirs`）。
  - モバイル端などの入力制限による改行崩れ（`\n` 文字）を、システム側で本物の改行コードに復元して保存。

### 3. 💬 `/chat [メッセージ]` (AI連携アシスタント)
- **動作**: AIモデル（Gemini API）と連携し、コンテキスト記憶セッションを用いて対話を行います。対話の流れを維持したスマートな返答が可能です。

---

## 🛡️ セキュリティ設計 (Security & Performance)
- **管理者チェック（Admin Check Filter）**: `@app_commands.check(is_admin)` デコレータにより、管理者以外のすべてのDiscordユーザーからのコマンド実行をシャットアウトします。権限のないユーザーが実行した場合、アクセス拒否 Embed を返します。
- **セキュアな設計**: Discord Token、Gemini APIキー、および管理者ユーザーIDは環境変数 (`os.environ`) から取得する設計になっており、ソースコードのリポジトリ上での漏洩を防止します。
- **自動文字数スライサー**: 出力テキストがDiscordの制限（Embed Description: 4096文字）を超える場合、`chunk_and_send` 処理により、自動的にページ分割されて連続送信されます。

<br>
<br>

---
---

# 🌉 Discord-PC Remote File Management Bridge (Discord Bridge)

## 📌 Project Overview
A remote file-system administration bridge tool that enables developers to securely read, write, and manage files on a home PC (development machine) via Discord Slash Commands from a smartphone or any external device.

Designed with a security-first approach, the bot includes a strict Check Filter to restrict command execution solely to the designated administrator's Discord User ID, as well as a dynamic text-chunking engine to safely handle Discord API message limit boundaries (2000/4000 chars limit).

---

## 🛠️ Tech Stack
- **Language**: Python 3
- **Framework**: `discord.py` (v2.x, Slash Commands / App Commands)
- **AI Engine**: Google Gemini API (`gemini-2.5-pro`)
- **Core Technology**:
  - Discord Slash Commands (`bot.tree`)
  - OS file system interaction, recursive path resolution, and error handling.
  - Interactive system UI layout rendering via Discord Embeds.

---

## ⚙️ Features & Command Architectures

### 1. 📁 `/read [file_path]` (Remote File Read)
- **Action**: Reads the contents of a local text file (e.g. Markdown or source files) on the host PC and renders it directly as an embedded block on Discord.
- **Details**:
  - Handles absolute and relative file paths (auto-resolves against working directory).
  - Gracefully handles filesystem exceptions (FileNotFoundError, encoding errors) and logs them to the chat interface.

### 2. 💾 `/write [file_path] [content]` (Remote File Write)
- **Action**: Writes or overwrites text contents directly onto the host PC filesystem from Discord input.
- **Details**:
  - Automatically creates parent directories if they do not exist (`os.makedirs`).
  - Restores escaped newline strings (`\n`) back into actual formatting block breaks to counter mobile client input constraints.

### 3. 💬 `/chat [message]` (Integrated Contextual AI Assistant)
- **Action**: Interacts with the Gemini API using an active chat session to maintain dialog history and assist with system-related prompts.

---

## 🛡️ Security & Performance Designs
- **Administrator Check (Admin Check Filter)**: Uses `@app_commands.check(is_admin)` decorators to reject commands from non-authorized Discord accounts. Attempts at executing command strings return an access denied UI Embed card.
- **Zero Hardcoded Secrets**: Discord Tokens, Gemini API Keys, and target Administrator IDs are injected via OS environment variables (`os.environ`) to prevent repo credential leakage.
- **Auto-Chunking Buffer**: Outputs exceeding Discord's embed description limit (4,096 chars) are sliced by the `chunk_and_send` method and sent as paginated message arrays.
