# db6

## 概述

db6 是一個統一的資料庫框架，同時支援三種儲存引擎（Memory、BTree、LSM），提供 KV API 和可選的 SQL 查詢介面。專案的目標是建立一個輕量、模块化且效能優異的資料庫系統，讓應用程式可以根據場景選擇最適合的儲存引擎。

## 設計理念

db6 的核心設計理念是「統一介面，多種引擎」：

```
┌─────────────────────────────────────────────┐
│                db6 應用程式                  │
│         (使用同一組 API 訪問資料)              │
└─────────────────┬───────────────────────────┘
                  │
    ┌─────────────┼─────────────┐
    ▼             ▼             ▼
┌────────┐   ┌────────┐   ┌────────┐
│ Memory │   │  BTree │   │  LSM   │
│Engine  │   │ Engine │   │ Engine │
└────────┘   └────────┘   └────────┘
```

## 支援的引擎

### Memory Engine

基於 Rust 的 BTreeMap，適用於：
- 快速實驗和原型開發
- 高效能快取場景
- 不需要持久化的場景

### BTree Engine

基於移植的 SQLite pager/btree，適用於：
- 需要完整交易支援的 OLTP 場景
- 需要 SQL 查詢的場景
- 需要磁碟持久化的場景

### LSM Engine

基於移植的 lsm5，適用於：
- 高寫入量場景（如日誌、IoT）
- 寫入密集、讀取較少的場景
- 需要壓縮的場景

## 核心 API

### StorageEngine Trait

```rust
pub trait StorageEngine: Send + Sync {
    fn open(path: &Path) -> Result<Box<dyn StorageEngine>> where Self: Sized;
    fn open_memory() -> Box<dyn StorageEngine> where Self: Sized;
    
    fn engine_type(&self) -> &'static str;
    
    fn get(&self, table_id: u32, key: &[u8]) -> Result<Option<Vec<u8>>>;
    fn put(&mut self, table_id: u32, key: &[u8], value: &[u8]) -> Result<()>;
    fn delete(&mut self, table_id: u32, key: &[u8]) -> Result<()>;
    fn scan(&self, table_id: u32, start: &[u8], end: &[u8]) -> Result<Vec<(Vec<u8>, Vec<u8>)>>;
    
    fn flush(&mut self) -> Result<()>;
    fn sync(&mut self) -> Result<()>;
    
    fn begin_transaction(&mut self) -> Result<()>;
    fn commit_transaction(&mut self) -> Result<()>;
    fn rollback_transaction(&mut self) -> Result<()>;
    fn has_transaction(&self) -> bool;
    
    fn stats(&self) -> EngineStats;
}
```

## 專案結構

```
db6/
├── src/
│   ├── lib.rs              # 統一出口
│   ├── engine/
│   │   ├── mod.rs          # StorageEngine trait
│   │   ├── memory.rs       # Memory 引擎
│   │   ├── btree/          # BTree 引擎
│   │   └── lsm.rs          # LSM 引擎
│   ├── kv/
│   │   └── mod.rs          # KvStore trait
│   ├── sql/                # SQL 層
│   │   ├── parser/
│   │   ├── planner/
│   │   └── executor/
│   └── fts/                # FTS5 全文檢索
├── _wiki/                  # 本 Wiki
├── _doc/                   # 計劃文件
└── _book/                  # 書籍（規劃中）
```

## 版本歷史

### v0.x - KV 核心

專注於 KV API 和儲存引擎實作：

| 版本 | 完成內容 |
|------|----------|
| v0.1 | StorageEngine trait、Memory engine |
| v0.2 | BTree engine、完整交易支援 |
| v0.3 | LSM engine、WAL、MemTable、SSTable |

### v1.x - FTS 全文檢索

基於 KV 介面實作全文檢索：

| 版本 | 完成內容 |
|------|----------|
| v1.0 | FTS5 介面、CJK 分詞器 |
| v1.1 | 布林查詢（AND/OR/NOT）、BM25 排序 |

### v2.x - SQL 層

建構在 KV 之上的 SQL 引擎：

| 版本 | 完成內容 |
|------|----------|
| v2.0 | SQL Parser、Planner、Executor |
| v2.1 | JOIN、複雜 ORDER BY |

## 與其他系統的比較

| 特性 | db6 | SQLite | Redis | LevelDB |
|------|-----|--------|-------|---------|
| 儲存引擎 | 多種 | B-Tree | Memory | LSM |
| SQL | 可選 | 完整 | 無 | 無 |
| 交易 | 引擎相關 | 完整 | 有限 | 無 |
| FTS | 有 | 有（FTS5） | 有（模組） | 無 |
| 分散式 | 未來 | 無 | Cluster | 無 |

## 使用範例

### Rust API

```rust
use db6::{StorageEngine, MemoryEngine};

let engine = MemoryEngine::open_memory();
engine.put(1, b"key1", b"value1").unwrap();

let result = engine.get(1, b"key1").unwrap();
assert_eq!(result, Some(b"value1".to_vec()));
```

### SQL REPL

```bash
$ cargo run
> CREATE TABLE users (id INT, name TEXT);
> INSERT INTO users VALUES (1, 'Tom');
> SELECT * FROM users WHERE id = 1;
+----+------+
| id | name |
+----+------+
|  1 | Tom  |
+----+------+
```

### 切換引擎

```rust
// 使用 Memory 引擎
.engine memory

// 使用 BTree 引擎
.engine btree

// 使用 LSM 引擎
.engine lsm
```

## 未來規劃

1. **分散式支援**：實現 Raft 共識，支持副本複製
2. **更多索引類型**：Gin、GiST 等
3. **壓縮增強**：支援更多壓縮演算法
4. **效能優化**：批次操作、並行掃描

## 參與貢獻

歡迎提交 Issue 和 Pull Request：

- 報告問題：GitHub Issues
- 功能建議：GitHub Discussions
- 程式碼貢獻：Fork 後提交 PR

## 延伸閱讀

- [設計文件](../_doc/plan.md)
- [版本歷史](../_doc/)
- [本 Wiki](../_wiki/)