# engine/mod.rs — 儲存引擎抽象層

## 設計核心：兩層架構

db6 的儲存引擎採用**兩層抽象 (two-layer abstraction)**，這是理解整個系統的關鍵：

### 第一層：StorageEngine (底層)

定義最基礎的 KV 操作，包含 `table_id` 參數實現**多表隔離 (multi-table isolation)**。這個 trait 是 `dyn` 相容的，透過 `where Self: Sized` 限制 `open()` 和 `open_memory()` 方法，讓 trait 物件可以動態建立引擎。

核心操作：
- `get/put/delete` — 單筆讀寫刪
- `scan` — 範圍掃描 `[start, end)`
- `batch_put` / `range_delete` — 批量操作
- `flush/sync` — 持久化
- `begin/commit/rollback_transaction` — 交易控制

### 第二層：KvStore (SQL 層介面)

為 SQL Executor 設計的精簡介面，無 `table_id` 參數（Executor 內部處理），方法使用 `&mut self` 確保單執行緒安全。

## 可插拔引擎

目前實作的四種引擎：

| 引擎 | 模組 | 持久化 | 交易 | 排序 |
|------|------|--------|------|------|
| HashMemoryEngine | memory/hash.rs | 無 | 無 | 無 |
| BTreeMemoryEngine | memory/btree.rs | 無 | 無 | 有 |
| BTreeEngine | btree/engine.rs | 有 | 有 | 有 |
| LsmEngine | lsm/engine.rs | 有 | 有 | 有 |

## 能力標記系統 (Capability System)

`capability.rs` 定義了一組 marker trait，用於在編譯期區分引擎能力：

```rust
pub trait CanOrderBy: StorageEngine {}  // 支援排序
pub trait CanJoin: StorageEngine {}     // 支援 JOIN
pub trait CanFts: StorageEngine {}      // 支援全文搜尋
pub trait CanTransaction: StorageEngine {}  // 支援交易
```

使用 `impl_capabilities!` 巨集簡化實作：

```rust
impl_capabilities!(BTreeEngine, CanOrderBy, CanScan, CanTransaction);
```

## 相關資源

- `capability.rs` — 能力標記 trait
- `memory/mod.rs` — 記憶體引擎
- `btree/mod.rs` — BTree 引擎
- `lsm/mod.rs` — LSM 引擎
