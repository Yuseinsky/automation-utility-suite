# 💾 常駐型AI対話ログ自動記録システム (Realtime Logger)

## 📌 プロジェクト概要
ユーザーとAIとのインタラクションログをリアルタイムでキャプチャし、一時バッファ（JSON）経由でリレーショナルデータベース（SQLite）へ永続化、かつ規定件数（10件）ごとにMarkdownフォーマットの美しいドキュメントとして自動フラッシュ（出力）するバックグラウンド常駐型監視システムです。

Windowsのスタートアップ時にVBScript（Windows Script Host）を介して非表示（Silent）の常駐監視スレッドを自動起動する仕組みを構築しており、OS起動からシャットダウンまでユーザーの操作を妨げることなく対話メモリの収集を自動化します。

---

## 🛠️ 技術スタック
- **Language**: Python 3, VBScript (WSH)
- **Database**: SQLite 3 (永続化ストレージ)
- **Key Technology**: 
  - バッファフラッシュ・アルゴリズム (JSON Buffering → DB Transaction)
  - VBScriptによるWindowsバックグラウンド常駐プロセス（Wscript.Shell）の隠し起動
  - Markdown構造化テキストジェネレータ

---

## 📂 コンポーネント構成

1. **`db_init.py` (データベース・初期化)**:
   - システムに必要なSQLiteデータベース（`system_memory.db`）および対話履歴テーブルを定義し、初期セットアップを行います。
2. **`push_log.py` (ログバッファング＆フラッシュ)**:
   - 1対話ごとのログをJSONファイル（`temp_log_buffer.json`）に一時バッファし、バッファ制限（10件）に到達した瞬間に自動的にトランザクションをコミットしてSQLiteにインサート。同時に、Markdown形式のフォーマットされた記録ファイルに整形出力します。
3. **`sys_heartbeat.py` (常駐型監視監視エンジン)**:
   - バックグラウンドでシステムの状態をリアルタイム監視するメイン・デーモンスレッドです。
4. **`start_heartbeat.vbs` (サイレントブート起動)**:
   - Windows起動時にコマンドプロンプトのコンソール画面を一切表示させずに、裏側で `sys_heartbeat.py` をサイレント起動・常駐化させるためのVBScriptです。
5. **`db_query.py` / `format_log.py` (ログ抽出＆フォーマッタ)**:
   - データベースに蓄積された非構造化データを抽出し、読みやすいログ構造に組み立て直すクエリとフォーマッタです。

---

## 💡 システムアーキテクチャの利点
- **データロスの防止**: メモリバッファとSQLite永続化を組み合わせることで、万が一のPCの強制終了やクラッシュが発生しても、対話記録が失われない耐障害性を備えています。
- **ゼロオーバーヘッド**: VBScriptによるサイレント起動により、コマンドプロンプトのポップアップ等によるユーザー体験の阻害を完全にゼロにしています。
- **データレイクの構築**: AIとの全対話を構造化データとしてローカルDBに蓄積し続けることで、将来的な独自RAG（検索拡張生成）システムやパーソナルAIアシスタントの学習用データセットとして直接再利用可能なパイプラインを形成しています。

<br>
<br>

---
---

# 💾 Daemon-Based Dialogue Logging System (Realtime Logger)

## 📌 Project Overview
A background daemon system that automatically captures dialogue history between a user and AI in real-time. It buffers interactions via a temporary JSON file, persists them to a relational database (SQLite), and automatically flushes the logs to beautifully structured Markdown records once a threshold (10 entries) is reached.

The daemon launches silently at Windows startup via VBScript (Windows Script Host) without displaying cmd console windows, automating conversation archival unobtrusively.

---

## 🛠️ Tech Stack
- **Language**: Python 3, VBScript (WSH)
- **Database**: SQLite 3 (Persistent Storage)
- **Core Technology**:
  - Buffer Flush Algorithm (JSON Buffering → DB Transaction)
  - Silent process execution using VBScript (`Wscript.Shell`)
  - Markdown structured text generator

---

## 📂 Component Structure

1. **`db_init.py` (Database Initializer)**:
   - Sets up the SQLite database schema (`system_memory.db`) and initializes tables.
2. **`push_log.py` (Log Buffer & SQLite Commit)**:
   - Stages dialogue entries to `temp_log_buffer.json` and pushes records to SQLite via a single transaction once the threshold (10 exchanges) is reached, trigger-calling the Markdown parser.
3. **`sys_heartbeat.py` (Heartbeat Monitor Daemon)**:
   - The main monitoring background thread checking state conditions periodically.
4. **`start_heartbeat.vbs` (Silent WSH Bootloader)**:
   - A WSH VBScript triggering `sys_heartbeat.py` silently on Windows startup without opening any terminal command prompts.
5. **`db_query.py` / `format_log.py` (Query & Markdown Parser)**:
   - Utility tools to query the SQLite DB and export structured dialogue segments into readable Markdown documents.

---

## 💡 System Architectural Advantages
- **Fault-Tolerant (No Data Loss)**: By combining atomic JSON buffers with SQLite transactions, data is preserved even in the event of unexpected power losses or system crashes.
- **Zero-Interruption (Zero Overhead)**: The VBScript integration eliminates console window popups, ensuring a seamless user environment.
- **Future-Proof Data Lake**: Accumulates structural conversational records locally, forming a database ready for RAG pipelines or personalized model training.
