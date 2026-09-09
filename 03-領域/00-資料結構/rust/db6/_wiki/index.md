# 資料庫技術百科 (db6 Wiki)

本 wiki 收錄與 db6 專案相關的資料庫技術詞條，涵蓋儲存引擎、查詢語言、知名資料庫系統等主題。

## 詞條索引

### 儲存引擎與資料結構

| 詞條 | 說明 |
|------|------|
| [B-tree.md](B-tree.md) | B 樹，一種自平衡的搜尋樹，廣泛用於資料庫索引 |
| [B+tree.md](B+tree.md) | B+ 樹，B 樹的變體，葉節點串連，適合範圍查詢 |
| [LSM-tree.md](LSM-tree.md) | Log-Structured Merge-tree，寫優化的資料結構 |
| [Red-black-tree.md](Red-black-tree.md) | 紅黑樹，統計效能優異的平衡二叉樹 |
| [Skip-list.md](Skip-list.md) | 跳表，多層有序鏈結串列，LSM 常用於 MemTable |

### 資料庫系統

| 詞條 | 說明 |
|------|------|
| [SQLite.md](SQLite.md) | 輕量級嵌入式關聯式資料庫，無伺服器程序 |
| [PostgreSQL.md](PostgreSQL.md) | 進階開源關聯式資料庫，功能豐富 |
| [MySQL.md](MySQL.md) | 熱門開源關聯式資料庫 |
| [Redis.md](Redis.md) | 記憶體 key-value 儲存，支援多資料結構 |
| [MongoDB.md](MongoDB.md) | 文件導向 NoSQL 資料庫 |
| [LevelDB.md](LevelDB.md) | Google 開源的 LSM 儲存引擎 |
| [RocksDB.md](RocksDB.md) | LevelDB 的改良版，支援 column family |

### 核心概念

| 詞條 | 說明 |
|------|------|
| [KV-store.md](KV-store.md) | Key-Value 儲存，最基本的儲存抽象 |
| [SQL.md](SQL.md) | 結構化查詢語言，關聯式資料庫的標準語言 |
| [關聯式資料庫.md](關聯式資料庫.md) | 基於關聯模型的資料庫系統 |
| [NoSQL.md](NoSQL.md) | 非關聯式資料庫的分類與特性 |
| [ACID.md](ACID.md) | 交易的四大特性：原子性、一致性、隔離性、持久性 |
| [CAP-theorem.md](CAP-theorem.md) | 分散式系統的 CAP 定理 |
| [Transaction.md](Transaction.md) | 資料庫交易的概念與實作 |
| [資料庫索引.md](資料庫索引.md) | 資料庫索引的原理與類型 |
| [Query-planner.md](Query-planner.md) | 查詢規劃器，如何將 SQL 轉為執行計畫 |
| [FTS.md](FTS.md) | 全文檢索，支援文字搜尋的技術 |
| [Inverted-index.md](Inverted-index.md) | 倒排索引，全文檢索的核心資料結構 |
| [Tokenizer.md](Tokenizer.md) | 分詞器，文字分析的基礎元件 |

### 相關專案

| 詞條 | 說明 |
|------|------|
| [db6.md](db6.md) | 本專案，一個支援多引擎的統一資料庫框架 |

---

## 編輯指南

- 所有詞條使用繁體中文（台灣用語）
- 專有名詞第一次出現時加註英文
- 詞條內容約 300 行，涵蓋理論背景、歷史、應用場景
- 詞條之間可相互引用，使用 `[詞條名稱](詞條名稱.md)` 格式
- 歡迎提出 issue 或 pull request 補充內容