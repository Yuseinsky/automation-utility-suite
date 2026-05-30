# Legacy Archive Digitization Pipeline

[English](#english) | [日本語](#日本語) | [繁體中文](#繁體中文)

---

<h2 id="english">🇬🇧 English</h2>

### 📖 Overview
A modular, config-driven Python pipeline designed to digitize, reconstruct, and restore translated text and illustrations from antique books.
Originally built for the academic book "Fish Senses" (published in 1946 / Showa 21), this system automates the tedious process of mapping scattered images to page numbers, consolidating fragmented translation files, sorting them by physical book order, and cleaning translation noise—all in a single execution.

### 🛠️ Tech Stack
- **Language**: Python 3
- **Libraries**: Built-in modules (`os`, `re`, `glob`, `shutil`, `logging`, `pathlib`) + `pyyaml`
- **Architecture**: Modular pipeline with Separation of Concerns and externalized YAML configuration

### ⚙️ Architecture (Modular Pipeline)

```text
main_pipeline.py           # Single entry point (orchestrator)
├── core/
│   ├── image_mapper.py    # Maps raw images to page numbers via RegEx
│   ├── layout_sorter.py   # Sorts pages by physical book order (config weights)
│   └── text_cleaner.py    # Applies sequential regex cleaning rules
└── config.yaml            # All rules, weights, and patterns externalized
```

**Pipeline Stages:**
1. **Image Mapping & Renaming**: Dynamically maps raw image filenames to physical page numbers using RegEx patterns defined in `config.yaml`, then safely copies and renames them.
2. **Text Consolidation**: Merges fragmented translation Markdown files into a single archive, excluding configured test/draft files.
3. **Layout Sorting**: Re-orders page blocks into correct physical book sequence (Cover → Preface → Index → Main Text → Colophon) using configurable keyword weights.
4. **Text Cleaning**: Applies a sequence of regex rules (defined in `config.yaml`) to remove translation artifacts, editor notes, and formatting noise.
5. **Atomic Write**: Final output uses `.tmp` + `rename()` to guarantee data integrity even during unexpected interruptions.

### ⚠️ Known Limitations (Must Read)
> **"Honesty is the best policy."**

1. **Regex-Only Processing**: This pipeline uses Regular Expressions for all text operations. It cannot understand context or semantics—only pattern matching.
2. **Config Dependency**: The pipeline's effectiveness depends entirely on the quality of the regex rules and weights defined in `config.yaml`. Adapting to a new book format requires updating the config, not the code.
3. **No OCR**: This tool processes existing digital text files. It does not perform optical character recognition on scanned images.

### 🚀 Quick Start
```bash
# 1. Install dependencies
pip install pyyaml

# 2. Configure rules
# Edit config.yaml to match your archive's format

# 3. Run the pipeline
python main_pipeline.py
```

---

<h2 id="日本語">🇯🇵 日本語</h2>

### 📖 概要 (Overview)
古書のデジタルアーカイブ修復に特化した、モジュール式・設定駆動型の Python パイプラインです。
昭和21年（1946年）発行の学術古書「魚の感覚」の復元用に開発されました。バラバラの画像ファイルとページ番号のマッピング、分割された翻訳ファイルの統合、実体書のページ順への並び替え、翻訳ノイズの除去を、**ワンコマンドで自動実行**します。

### 🛠️ 技術スタック
- **言語**: Python 3
- **ライブラリ**: 標準モジュール (`os`, `re`, `glob`, `shutil`, `logging`, `pathlib`) + `pyyaml`
- **設計思想**: 職責分離 (Separation of Concerns) によるモジュール式パイプライン、外部 YAML 設定ファイル駆動

### ⚙️ アーキテクチャ (モジュール式パイプライン)

```text
main_pipeline.py           # 唯一の実行エントリポイント（オーケストレーター）
├── core/
│   ├── image_mapper.py    # 正規表現による画像→ページ番号マッピング
│   ├── layout_sorter.py   # 設定可能な重み付けによるページ順ソート
│   └── text_cleaner.py    # 逐次適用される正規表現クレンジングルール
└── config.yaml            # すべてのルール・重み・パターンを外部化
```

**パイプラインのステージ:**
1. **画像マッピング＆リネーム**: `config.yaml` で定義された正規表現パターンを使用して、元画像ファイル名を物理ページ番号に動的マッピングし、安全にコピー＆リネームします。
2. **テキスト統合**: 分割された翻訳 Markdown ファイルを、設定されたテスト/下書きファイルを除外しながら統合します。
3. **レイアウトソート**: 設定可能なキーワード重み付けにより、ページブロックを実体書の正しい構成順（表紙→序文→目次→本文→奥付）に並び替えます。
4. **テキストクレンジング**: `config.yaml` で定義された正規表現ルールを順次適用し、翻訳アーティファクト、編集ノート、フォーマットノイズを除去します。
5. **アトミック書き込み**: 最終出力は `.tmp` + `rename()` を使用し、予期せぬ中断時でもデータの整合性を保証します。

### ⚠️ 既知の制限事項 (必ずお読みください)
> **"Honesty is the best policy. ツールの限界を正直に。"**

1. **正規表現のみの処理**: 本パイプラインはすべてのテキスト操作に正規表現を使用します。文脈や意味の理解は不可能で、パターンマッチングのみです。
2. **設定ファイル依存**: パイプラインの有効性は `config.yaml` で定義された正規表現ルールと重みの品質に完全に依存します。新しい書籍形式への対応にはコードではなく設定の更新が必要です。
3. **OCR 非対応**: 本ツールは既存のデジタルテキストファイルを処理します。スキャン画像の光学文字認識は行いません。

### 🚀 クイックスタート
```bash
# 1. 依存関係のインストール
pip install pyyaml

# 2. ルールの設定
# config.yaml を編集し、アーカイブのフォーマットに合わせてください

# 3. パイプラインの実行
python main_pipeline.py
```

---

<h2 id="繁體中文">🇹🇼 繁體中文</h2>

### 📖 專案簡介 (Overview)
一個專為古書數位典藏修復而設計的**模組化、組態驅動** Python 流水線。
原為修復昭和 21 年（1946 年）發行的學術古書《魚の感覚》而開發。本系統將散亂的圖片檔案與頁碼映射、分散的翻譯檔案合併、依照實體書頁序重新排列、以及清除翻譯殘留雜訊等繁瑣流程，整合為**一鍵式自動化執行**。

### 🛠️ 技術棧
- **語言**：Python 3
- **函式庫**：標準模組 (`os`, `re`, `glob`, `shutil`, `logging`, `pathlib`) + `pyyaml`
- **設計思想**：透過職責分離 (Separation of Concerns) 實現模組化流水線，所有規則外置於 YAML 設定檔

### ⚙️ 架構 (模組化流水線)

```text
main_pipeline.py           # 唯一執行入口（調度中心）
├── core/
│   ├── image_mapper.py    # 透過 RegEx 將原始圖片映射至頁碼
│   ├── layout_sorter.py   # 依照可設定的權重進行實體頁碼排序
│   └── text_cleaner.py    # 依序套用正則清理規則
└── config.yaml            # 所有規則、權重、模式全部外置
```

**流水線階段：**
1. **圖片映射與重新命名**：使用 `config.yaml` 中定義的正則表達式，將原始圖片檔名動態映射至實體頁碼，並安全地複製與重新命名。
2. **文本合併**：將分散的翻譯 Markdown 檔案合併為單一典藏檔案，自動排除設定中指定的測試/草稿檔案。
3. **排版排序**：使用可設定的關鍵字權重，將頁面區塊重新排列為實體書的正確順序（封面 → 序文 → 目錄 → 正文 → 版權頁）。
4. **文字清理**：依序套用 `config.yaml` 中定義的正則規則，移除翻譯痕跡、編輯註記與排版雜訊。
5. **原子寫入 (Atomic Write)**：最終輸出使用 `.tmp` + `rename()` 機制，即使在寫入過程中發生意外中斷，也能保證資料完整性。

### ⚠️ 已知缺陷與技術限制 (Known Limitations - 必讀)
> **"Honesty is the best policy. 不畫大餅，認清工具的極限。"**

1. **僅限正則處理 (Regex-Only)**：本流水線的所有文字操作皆依賴正規表示式，無法理解上下文語意，僅能進行格式匹配。
2. **組態品質決定效果**：流水線的有效性完全取決於 `config.yaml` 中定義的正則規則與權重品質。若要適用於不同書籍格式，只需修改設定檔而非程式碼。
3. **不支援 OCR**：本工具處理的是已存在的數位文字檔案，不具備掃描圖片的光學字元辨識功能。

### 🚀 快速開始 (Quick Start)
```bash
# 1. 安裝依賴
pip install pyyaml

# 2. 設定規則
# 請編輯 config.yaml 來設定您的正規表示式與權重規則

# 3. 執行流水線
python main_pipeline.py
```
