# lib.rs — db6 統一資料庫入口

## 架構概觀

db6 是一個採用**可插拔儲存引擎 (pluggable storage engine)** 架構的統一資料庫系統。本檔案為整個 crate 的入口點 (entry point)，負責匯出所有公開模組與型別。

## 模組結構

```
db6
├── engine/      — 儲存引擎層 (Memory / BTree / LSM)
├── sql/         — SQL 解析、規劃、執行
├── fts/         — 全文搜尋 (Full-Text Search)
├── kv/          — Key-Value API 層
├── query/       — 高階查詢介面 (Db)
├── msgq/        — 訊息佇列系統
└── error/       — 統一錯誤類型
```

## 關鍵設計理念

### 1. 可插拔儲存引擎

`StorageEngine` trait 定義了統一的 KV 操作介面，三個引擎實作可互換：

- **MemoryEngine** — 純記憶體 BTreeMap/HashMap，無持久化
- **BTreeEngine** — 磁碟 BTree 結構，支援持久化與交易
- **LsmEngine** — Log-Structured Merge-Tree，適合大量寫入

### 2. 能力特徵 (Capability Traits)

透過 `CanOrderBy`、`CanJoin`、`CanFts`、`CanTransaction`、`CanScan`、`CanBatch` 等標記 trait，在編譯期區分引擎支援的能力，實現**條件編譯 (conditional compilation)**。

### 3. 多種查詢方式

- **KV API** — 底層 Key-Value 介面，直接操作儲存引擎
- **SQL API** — 標準 SQL 語法，經由 Parser → Planner → Executor 三階段處理
- **Db API** — 高階封裝，提供類似文件的查詢風格
- **MSGQ API** — 佇列與 pub/sub 模式

## 對外匯出

```rust
// 主要引擎相關
pub use engine::{EngineStats, StorageEngine, KvStore, CanOrderBy, ...};

// KV 與錯誤
pub use kv::{KvStore as KvApi, KvEngine};
pub use error::{Error, Result};

// 全文搜尋
pub use fts::{FtsIndex, FtsTokenizer, CjkTokenizer, EnglishTokenizer};

// SQL
pub use sql::{parse, Executor, ResultSet, SqlExecutor};

// 訊息佇列
pub use msgq::{Msgq, SyncQueue, ..., AsyncPubSub, AsyncPubSubMessage};
```

## 相關資源

- `error.rs` — 錯誤型別定義
- `engine/mod.rs` — 儲存引擎架構
- `sql/mod.rs` — SQL 子系統
- `msgq/mod.rs` — 訊息佇列子系統
