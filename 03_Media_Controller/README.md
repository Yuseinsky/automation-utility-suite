# 🎵 Windows OS 低レベル API メディアコントローラー (Media Controller)

<h2 id="日本語">🇯🇵 日本語</h2>

### 📖 プロジェクト概要 (Overview)
Windows OS のネイティブ低レベル API を直接呼び出し、物理キーボードに触れることなく、プログラム経由でシステム全体のメディア操作を行うための**統合型 CLI ツール**です。

Python の `ctypes` ライブラリを利用して `user32.dll` のキーボードシミュレーション API に直接アクセスし、**仮想ハードウェア割り込み信号**をOSカーネルに注入します。
これにより、バックグラウンドで動作するブラウザ（YouTube 等）や音楽プレイヤーをコマンドラインから一撃で制御できます。

### 🛠️ 技術スタック (Tech Stack)
- **言語**: Python 3
- **OS 基盤**: Windows (OS Native API)
- **主要ライブラリ**: `ctypes`, `argparse`
- **コア技術**: Windows Low-Level API Integration (`user32.dll`), Virtual Key Code (VK_CODE) Emulation

### 📂 アーキテクチャ (Architecture)

```
03_Media_Controller/
├── media_controller.py   # 統合エントリーポイント (CLI + カーネル呼び出し)
└── README.md
```

#### `media_controller.py` — 統合メディアコントローラー
- **辞書マッピング (Dictionary Mapping)**: 全 VK_CODE を `VK_CODES` 辞書に集約。拡張時は辞書に1行追加するだけで完了。
- **クロスプラットフォーム防御**: `sys.platform != 'win32'` チェックにより、非 Windows 環境での実行を事前ブロック。
- **マジックナンバー排除**: `KEYEVENTF_KEYUP = 0x0002` を名前付き定数として定義。
- **共用関数 `send_media_key(action)`**: `ctypes.windll.user32.keybd_event` の呼び出しロジックを単一メソッドに集約し、DRY 原則を徹底。

### 🚀 クイックスタート (Quick Start)
```bash
# 再生 / 一時停止
python media_controller.py play_pause

# 次の曲へスキップ
python media_controller.py next

# 前の曲に戻る
python media_controller.py prev

# ミュート
python media_controller.py mute
```

### ⚠️ 既知の制限事項 (Known Limitations)
1. **Windows 専用**: `ctypes.windll` は Windows OS のネイティブ API です。macOS / Linux では `AttributeError` が発生します。本スクリプトは起動時に `sys.platform` チェックで事前にブロックします。
2. **メディアアプリ依存**: OS レベルのメディアキーイベントを送信するため、受信側のアプリケーション（Spotify, YouTube 等）がメディアキーに対応している必要があります。
3. **管理者権限不要**: 通常のユーザー権限で動作しますが、一部のセキュリティソフトが `keybd_event` をブロックする場合があります。

<br>
<br>

---
---

# 🎵 Windows OS Low-Level API Media Controller

<h2 id="english">🇺🇸 English</h2>

### 📖 Project Overview
A **unified CLI tool** that invokes Windows OS native low-level APIs to control system-wide media playback programmatically, without interacting with a physical keyboard.

By leveraging Python's `ctypes` library to directly access the keyboard simulation API within `user32.dll`, this tool **injects virtual hardware interrupt signals** into the OS kernel, enabling one-command control of background media applications (YouTube, Spotify, desktop players, etc.).

### 🛠️ Tech Stack
- **Language**: Python 3
- **OS Platform**: Windows (OS Native API)
- **Key Libraries**: `ctypes`, `argparse`
- **Core Technology**: Windows Low-Level API Integration (`user32.dll`), Virtual Key Code (VK_CODE) Emulation

### 📂 Architecture

```
03_Media_Controller/
├── media_controller.py   # Unified entry point (CLI + kernel calls)
└── README.md
```

#### `media_controller.py` — Unified Media Controller
- **Dictionary Mapping**: All VK_CODEs are centralized in a single `VK_CODES` dictionary. Adding a new media action requires only one line.
- **Cross-Platform Defense**: A `sys.platform != 'win32'` guard prevents execution on non-Windows systems, avoiding unrecoverable `AttributeError` crashes.
- **No Magic Numbers**: `KEYEVENTF_KEYUP = 0x0002` is defined as a named constant.
- **Shared Function `send_media_key(action)`**: All `ctypes.windll.user32.keybd_event` call logic is consolidated into a single method, strictly adhering to the DRY (Don't Repeat Yourself) principle.

### 🚀 Quick Start
```bash
# Play / Pause
python media_controller.py play_pause

# Skip to next track
python media_controller.py next

# Go to previous track
python media_controller.py prev

# Mute
python media_controller.py mute
```

### ⚠️ Known Limitations
1. **Windows Only**: `ctypes.windll` is a Windows-exclusive native API. Running on macOS/Linux will raise `AttributeError`. This script blocks execution at startup via a `sys.platform` check.
2. **Media App Dependent**: Sends OS-level media key events; the receiving application (Spotify, YouTube, etc.) must support media key handling.
3. **No Admin Required**: Runs under standard user privileges, though some security software may block `keybd_event` calls.

<br>
<br>

---
---

# 🎵 Windows OS 低階 API 媒體控制器

<h2 id="繁體中文">🇹🇼 繁體中文</h2>

### 📖 專案簡介 (Overview)
這是一個**統合型 CLI 工具**，透過直接呼叫 Windows OS 原生低階 API，以程式化的方式控制系統全域的媒體播放操作，完全不需要觸碰實體鍵盤。

利用 Python 的 `ctypes` 函式庫直接存取 `user32.dll` 的鍵盤模擬 API，**將虛擬硬體中斷訊號注入 OS 核心**，實現從命令列一鍵控制背景執行中的瀏覽器（YouTube 等）或音樂播放器。

### 🛠️ 技術棧 (Tech Stack)
- **語言**: Python 3
- **作業系統**: Windows (OS Native API)
- **主要函式庫**: `ctypes`, `argparse`
- **核心技術**: Windows Low-Level API Integration (`user32.dll`), Virtual Key Code (VK_CODE) Emulation

### 📂 架構 (Architecture)

```
03_Media_Controller/
├── media_controller.py   # 統合進入點 (CLI + 核心呼叫)
└── README.md
```

#### `media_controller.py` — 統合媒體控制器
- **字典對應 (Dictionary Mapping)**：所有 VK_CODE 集中管理於 `VK_CODES` 字典。新增媒體操作只需加一行。
- **跨平台防禦 (Cross-Platform Defense)**：透過 `sys.platform != 'win32'` 檢查，防止在非 Windows 系統上執行時引發無法復原的 `AttributeError` 崩潰。
- **消除魔術數字**：`KEYEVENTF_KEYUP = 0x0002` 定義為具名常數。
- **共用函式 `send_media_key(action)`**：所有 `ctypes.windll.user32.keybd_event` 的呼叫邏輯集中於單一方法，嚴格遵循 DRY (Don't Repeat Yourself) 原則。

### 🚀 快速開始 (Quick Start)
```bash
# 播放 / 暫停
python media_controller.py play_pause

# 下一首
python media_controller.py next

# 上一首
python media_controller.py prev

# 靜音
python media_controller.py mute
```

### ⚠️ 已知限制 (Known Limitations)
1. **僅限 Windows**：`ctypes.windll` 是 Windows OS 專屬的原生 API。在 macOS / Linux 上會引發 `AttributeError`。本腳本會在啟動時透過 `sys.platform` 檢查提前阻斷。
2. **依賴媒體應用程式**：發送的是 OS 層級的媒體按鍵事件，接收端的應用程式（Spotify、YouTube 等）必須支援媒體按鍵處理。
3. **不需要管理員權限**：以一般使用者權限即可執行，但部分防毒軟體可能會攔截 `keybd_event` 呼叫。
