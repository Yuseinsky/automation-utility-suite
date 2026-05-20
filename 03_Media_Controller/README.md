# 🎵 Windows OS低レベルAPIメディア制御スクリプト (Media Controller)

## 📌 プロジェクト概要
Windows OS の低レベル API を直接呼び出し、物理キーボードに触れることなく、プログラム経由でシステム全体のメディア操作（再生・一時停止・次の曲へスキップ）を行うための自動化スクリプト群です。

Python の `ctypes` ライブラリを利用して、動的リンクライブラリである `user32.dll` のキーボードシミュレーションAPIを叩くことで、バックグラウンドで動作しているブラウザ（YouTube等）や音楽プレイヤーアプリをコマンドラインから一撃で制御できます。

---

## 🛠️ 技術スタック
- **Language**: Python 3
- **OS Platform**: Windows (OS Native API)
- **Key Libraries**: `ctypes`
- **Key Technology**: Windows Low-Level API Integration (`user32.dll`), Virtual Key Code (VK_CODE) Emulation

---

## 📂 スクリプト構成

### 1. ⏸️ `media_toggle.py` (再生 / 一時停止)
- **役割**: システムに対して「再生/一時停止」のキーイベントを送信します。
- **仕組み**:
  - `VK_MEDIA_PLAY_PAUSE = 0xB3` (仮想キーコード: 179) を定義。
  - `ctypes.windll.user32.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, 0, 0)` を呼び出し、キーの「押し下げ」をシミュレート。
  - 続けて `keybd_event` にKeyUpフラグ（`2`）を渡し、キーの「解放」をシミュレートします。

### 2. ⏭️ `media_next.py` (次の曲へスキップ)
- **役割**: システムに対して「次の曲へスキップ」のキーイベントを送信します。
- **仕組み**:
  - `VK_MEDIA_NEXT_TRACK = 0xB0` (仮想キーコード: 176) を定義。
  - 同様に押し下げ（KeyDown）と解放（KeyUp）をシミュレートしてOSに仮想シグナルを注入します。

---

## 💡 技術的な意義と応用
本スクリプトは、規模こそ数行〜数十行と非常に軽量ですが、**「PythonとOS（Windows）ネイティブカーネル間のブリッジ接続」**を実装しています。
このアプローチにより、GUI自動化ツールやRPAシステム、あるいはDiscord Botなどからサーバー/ローカルマシンのハードウェア制御やシステム制御をプログラムから直接ハンドリングできるようになり、高機能なRPA自動化パイプラインの基礎技術として活用可能です。

<br>
<br>

---
---

# 🎵 Windows OS Low-Level API Media Control Scripts (Media Controller)

## 📌 Project Overview
A set of automation scripts designed to invoke Windows OS native low-level APIs to control system-wide media playback (Play/Pause, Next Track) programmatically without interacting with a physical keyboard.

By leveraging Python's `ctypes` library to call keyboard simulation APIs within `user32.dll`, this tool allows you to control background music applications, browsers (like YouTube), or desktop media players directly from the command line.

---

## 🛠️ Tech Stack
- **Language**: Python 3
- **OS Platform**: Windows (OS Native API)
- **Key Libraries**: `ctypes`
- **Core Technology**: Windows Low-Level API Integration (`user32.dll`), Virtual Key Code (VK_CODE) Emulation.

---

## 📂 Scripts Structure

### 1. ⏸️ `media_toggle.py` (Play / Pause)
- **Role**: Sends a system-wide "Play/Pause" key event.
- **Mechanism**:
  - Defines `VK_MEDIA_PLAY_PAUSE = 0xB3` (Virtual Key Code: 179).
  - Calls `ctypes.windll.user32.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, 0, 0)` to simulate the key press.
  - Follows up by passing the KeyUp flag (`2`) to simulate the key release.

### 2. ⏭️ `media_next.py` (Skip to Next Track)
- **Role**: Sends a system-wide "Next Track" key event.
- **Mechanism**:
  - Defines `VK_MEDIA_NEXT_TRACK = 0xB0` (Virtual Key Code: 176).
  - Similarly simulates KeyDown and KeyUp events to inject virtual signals into the OS.

---

## 💡 Engineering Value & Application
While lightweight, this project demonstrates **bridging execution between Python and the native Windows OS kernel**. This low-level approach enables GUI automation suites, RPA workflows, or Discord bots to execute system hardware commands directly, serving as a fundamental component for advanced desktop automation pipelines.
