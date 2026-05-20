# 📝 非構造化対話ログ解析・ペルソナ自動タグ付けツール (Log Parser)

## 📌 プロジェクト概要
LLM（大規模言語モデル）との膨大かつ無構造な対話テキストログ（数万字〜数百万字）から、発言者およびAIの動的なペルソナ（人格・役割）変化を自動で判別し、構造化されたMarkdown形式へ再構築するテキスト解析＆メタデータ注入ツールです。

AIとの継続的なディスカッションにおいて、AI側の人格表現や役割が時間の経過や文脈によって変遷するケースに対応するため、時間軸（行数インデックス）に基づいた区間判定アルゴリズムを導入しています。

---

## 🛠️ 技術スタック
- **Language**: Python 3
- **Libraries**: Built-in library (`os`, `sys`)
- **Key Algorithms**: 行数インデックススライス、2次元配列区間判定マッピング

---

## ⚙️ 動作メカニズム

1. **インプット**:
   無構造なMarkdown形式の対話ログ（発言者ヘッダーが欠落している、あるいは曖昧なプレーンテキスト）。
2. **区間判定 (Range Matching)**:
   ユーザーの発言行（`user_ranges`）と、AIのペルソナ名が定義された行範囲（`ai_persona_ranges`）の定義を参照し、行ごとに発言者を特定します。
   - 例: 行番号 3〜143 までは `**【Assistant (Base)】**：`
   - 例: 行番号 228〜343 までは `**【Assistant (Specialized - Expert)】**：`
3. **動的ヘッダー注入**:
   行をスキャンし、発言者が切り替わるタイミングで自動的にMarkdownヘッダー（例: `**User**：`）を動的挿入。
4. **アウトプット**:
   発言者が一目で分かり、役割の変化がラベリングされた構造的なMarkdownファイルを上書き・出力します。

---

## 💡 設計思想
このプロジェクトの真価は、コードの複雑さではなく**「手動で行うとミスが多く時間のかかる『テキスト意味解析・ラベリング作業』を、構造化されたデータ（二次元配列）の判定ロジックに置き換え、自動化した点」**にあります。
システム設計者としての「課題のパターンを見つけ、自動化ロジックに変換して効率化する」という問題解決アプローチを体現したツールです。

<br>
<br>

---
---

# 📝 Unstructured Log Parsing & Persona Auto-Tagging Tool (Log Parser)

## 📌 Project Overview
A text parser and metadata injection tool designed to analyze massive, unstructured conversation logs (ranging from tens of thousands to millions of characters) with LLMs. It automatically detects speaker transitions and dynamic AI persona (role) changes, rendering them into a structured, readable Markdown format.

In long-running discussions with AI models, their personas or target roles often shift depending on the context. This script addresses this by using a line-index interval mapping algorithm to identify who said what.

---

## 🛠️ Tech Stack
- **Language**: Python 3
- **Libraries**: Built-in modules (`os`, `sys`)
- **Core Algorithms**: Line-index array matching, 2D interval mapping.

---

## ⚙️ Operating Mechanism

1. **Input**:
   Unstructured Markdown dialogue logs (where speaker tags are missing or ambiguous).
2. **Interval Matching (Range Matching)**:
   Scans lines based on defined line number ranges for the User (`user_ranges`) and the AI (`ai_persona_ranges`), automatically matching each line to the corresponding active role.
   - Example: Lines 3 to 143 map to `**[Assistant (Base)]**: `
   - Example: Lines 228 to 343 map to `**[Assistant (Specialized - Expert)]**: `
3. **Dynamic Header Injection**:
   As it processes the lines, it injects speaker headers (e.g. `**User**: ` or persona titles) at speaker transition boundaries.
4. **Output**:
   Overwrites the input file with a fully-formatted Markdown log where roles and dialogue changes are clearly tagged.

---

## 💡 Engineering Rationale
The value of this script lies in **abstracting a time-consuming, error-prone manual labeling process into a clean, structured programmatic interval check**. It represents the classic system engineering methodology: identifying repeating manual patterns, formalizing them into a structured data format (2D range arrays), and delegating the execution to automated scripting.
