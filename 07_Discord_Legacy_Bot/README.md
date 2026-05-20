# 💬 多機能・多模態対応AIチャットボットシステム (Discord Chatbot Bot)

## 📌 プロジェクト概要
Discord 上で動作し、Google Gemini API（`gemini-2.5-pro`）と連携することで、独自定義されたシステム指示書（System Prompt）に基づいた対話エージェントシステムです。

単なる一問一答のボットではなく、会話の流れを正確に記憶する「短期記憶（コンテキストセッション）管理」、対話が蓄積した際に日記やログとして自動/手動でディスクに書き出す「自動アーカイブ（メモリ結晶化）システム」、周囲の会話状況を察知して不要な処理を抑える「バックログ（コンテキストキュー）システム」など、実用性の高い高度な機能を搭載しています。

---

## 🛠️ 技術スタック
- **Language**: Python 3
- **Framework**: `discord.py` (v2.x, Client / event-driven)
- **AI Engine**: Google Gemini API (`gemini-2.5-pro` / 多模態モデル)
- **Key Technology**: 
  - メッセージキャプチャ＆バックログキュー
  - Discord 添付ファイル（Attachments）のバイナリパース＆多模態（画像＋テキスト）送信
  - 非同期タスク処理による長文スライス＆送信

---

## ⚙️ 主な特徴とシステム構造

### 1. 🧠 キャラクター性（ペルソナ）と動的変化
- 独自のシステムプロンプト（`system_instruction.txt`）を読み込み、完全な対話キャラクターとして機能。
- 相手（管理者、一般ユーザー等）に応じて応答の優先度やコンテキスト取得を動的に調整可能。

### 2. 💎 記憶のアーカイブ＆リセットシステム
- AIとの対話履歴が規定値（80回）に達するか、管理者から `!archive` コマンドを受け取ると、過去のチャットログを要約・テキスト化。
- 要約された「ダイジェスト（.md）」と「客観的なRAWログ原稿（.md）」をローカルディスクに自動保存。
- 会話メモリをリセットしつつ、要約データのみを次の会話セッションの「初期シード（Context Seed）」として大脳に再注入することで、トークンの爆発を防ぎながら長期的な文脈を維持します。

### 3. 👂 周囲の会話の学習（コンテキスト・バックログ）機能
- 特定のチャンネルで自分宛て（Bot宛て）でない周囲の会話が交わされている間、APIリクエストを送らずに裏でバックログキューにテキストを一時プール。
- 自分宛てに呼びかけられたタイミングで、プールしていたバックログをコンテキスト情報としてまとめてGeminiに投入し、「それまでの会話の流れを全て理解した上での割り込み返答」を実現します。

### 4. 🖼️ 画像認識（多模態）対応
- Discordにアップロードされた画像ファイルをバイナリデータとしてストリーム直読し、Gemini APIの多モーダルインターフェースに渡すことで、画像のディテールや意味解析を含めた高度な回答を可能にしています。

---

## 💡 本システムのエンジニアリング価値
このシステムは、**「LLMのコンテキスト制限（Token上限・コスト）と対話体験のトレードオフ」**に対する実用的なソリューションを示しています。
不要なAPIコールを抑えるバックログ蓄積、対話履歴を自動で要約・結晶化してメモリをスッキリさせる仕組みなど、プロダクションレベルの対話エージェントを構築する上で不可欠な設計パターン（Memory Management / Memory Consolidation）が組み込まれています。

<br>
<br>

---
---

# 💬 Multimodal Conversational Agent System (Discord Chatbot)

## 📌 Project Overview
An advanced Discord dialogue agent integrated with the Google Gemini API (`gemini-2.5-pro`) to conduct conversations based on a custom-defined system instruction file (`system_instruction.txt`).

Far from a simple reply-on-trigger bot, this agent incorporates state-of-the-art conversational mechanisms: dynamic session memory management, dialogue memory crystallization (summarizing and archiving active history to local Markdown documents once a threshold of 80 entries is hit or upon receiving `!archive`), and background conversation context queuing (backlogging background chat to reply with contextual awareness when addressed).

---

## 🛠️ Tech Stack
- **Language**: Python 3
- **Framework**: `discord.py` (v2.x, Client / Event-driven)
- **AI Engine**: Google Gemini API (`gemini-2.5-pro` Multimodal Model)
- **Core Technology**:
  - Chat logs queue / context backlog processor.
  - Multimodal parser handling image attachments (read as binary streams).
  - Asynchronous task runner for text-chunking and pagination.

---

## ⚙️ Key Features & Architecture

### 1. 🧠 Custom Persona Alignment
- Loads custom persona settings from `system_instruction.txt` to align the bot's behavior.
- Dynamically adjusts priorities and dialogue context depending on the conversational participants.

### 2. 💎 Memory Consolidation & Archival
- Once history reaches 80 records, or upon receiving the `!archive` command, the bot generates a summary of the active session.
- Saves both the finalized Markdown Summary and raw conversation transcript to the local storage disk.
- Flushes the session memory and seeds the new chat instance with the generated summary as a "Context Seed" to preserve continuity without causing prompt-token inflation.

### 3. 👂 Context Backlog Queue
- Monitors and stores ambient conversation logs in a background queue when not addressed directly.
- When pinged or replied to, it injects the queued backlog as conversation context, enabling the bot to respond with full contextual awareness of the preceding conversation flow.

### 4. 🖼️ Multimodal Capabilities
- Intercepts image attachments, reads them as binary byte streams, and inputs them alongside user prompts to Gemini to analyze and discuss visual details.

---

## 💡 Engineering Value & Architectural Patterns
This bot demonstrates a practical solution to **managing the trade-offs of LLM context window boundaries and token pricing**. By implementing smart ambient backlogs and automated memory crystallization (summarization cycles), it showcases key software design patterns (Memory Consolidation / State Persistence) required for production-level AI agent architectures.
