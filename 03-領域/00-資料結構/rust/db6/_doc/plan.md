# db6 開發計劃

## 1. 專案目標

db6 是一個統一的資料庫框架，同時支援三種儲存引擎：

| 引擎 | 特性 | 適用場景 |
|------|------|---------|
| **Memory** | BTreeMap，記憶體純 KV | 快速實驗、高效能快取 |
| **BTree** | 移植自 sql6 的 pager/btree | 全功能 SQL（SQLite 相容語法） |
| **LSM** | 移植自 lsm5 | 高寫入量、寫優化場景 |

---

## 2. 版本策略

**v0.xx 系列：專注於 KV 層**
- 只實作 KV API（get/put/delete/scan + transactions）
- 先建立穩定的儲存引擎核心
- v0.1: Memory engine
- v0.2: BTree engine
- v0.3: LSM engine

**v1.xx 系列：加入 FTS 全文檢索**
- 基於 KV 介面實作 FTS
- 三個引擎都能支援 FTS
- CJK 分詞器（雙元分詞）

**v2.xx 系列：加入 SQL 層**
- 移植 sql6 的 parser/planner/executor
- SQL 建構在 KV 之上
- SELECT / INSERT / UPDATE / DELETE

---

## 3. 核心架構

```
db6/
├── src/
│   ├── lib.rs                      # 統一出口
│   ├── engine/
│   │   ├── mod.rs                  # StorageEngine trait（核心抽象）
│   │   ├── memory.rs               # Memory engine (BTreeMap)
│   │   ├── btree/                   # BTree engine
│   │   └── lsm.rs                  # LSM engine
│   ├── kv/
│   │   └── mod.rs                  # KvStore trait
│   ├── sql/                        # SQL 層 (v2.x 才加入)
│   │   ├── parser/
│   │   ├── planner/
│   │   └── executor/
│   └── fts/                        # FTS5 (基於 KV 介面，v1.x 才加入)
```

---

## 4. 核心抽象：StorageEngine trait

所有引擎必須實作此 trait：

```rust
pub trait StorageEngine: Send + Sync {
    // 工廠
    fn open(path: &Path) -> Result<Box<dyn StorageEngine>> where Self: Sized;
    fn open_memory() -> Box<dyn StorageEngine> where Self: Sized;

    // 引擎資訊
    fn engine_type(&self) -> &'static str;

    // 基本 KV 操作
    fn get(&self, table_id: u32, key: &[u8]) -> Result<Option<Vec<u8>>>;
    fn put(&mut self, table_id: u32, key: &[u8], value: &[u8]) -> Result<()>;
    fn delete(&mut self, table_id: u32, key: &[u8]) -> Result<()>;
    fn scan(&self, table_id: u32, start: &[u8], end: &[u8]) -> Result<Vec<(Vec<u8>, Vec<u8>)>>;

    // 持久化
    fn flush(&mut self) -> Result<()>;
    fn sync(&mut self) -> Result<()>;

    // 交易
    fn begin_transaction(&mut self) -> Result<()>;
    fn commit_transaction(&mut self) -> Result<()>;
    fn rollback_transaction(&mut self) -> Result<()>;
    fn has_transaction(&self) -> bool;

    // 可觀測性
    fn stats(&self) -> EngineStats;
}
```

---

## 5. 三種引擎實作

### 5.1 Memory Engine（v0.1 完成）

- BTreeMap-based in-memory storage
- 不支援交易
- flush/sync 是 no-op

### 5.2 BTree Engine（v0.2 目標）

- 移植自 sql6 的 pager/btree
- 支援完整交易
- 磁碟持久化

### 5.3 LSM Engine（v0.3 目標）

- 移植自 lsm5
- WAL + MemTable + SSTable + Compaction
- 有限交易支援

---

## 6. 版本里程碑

### v0.1 — KV 核心（已完成）

```
✅ StorageEngine trait 完成
✅ Memory engine 完成
✅ KvStore trait 完成
✅ 基本測試通過
```

### v0.2 — BTree Engine

```
✅ BTree engine 實作
✅ 完整交易支援
```

### v0.3 — LSM Engine

```
LSM engine 實作（移植自 lsm5）
WAL + Compaction
有限交易支援
```

### v0.4 — KV 整合測試

```
三個引擎統一測試
跨引擎 benchmark
```

### v1.0 — FTS 全文檢索

```
FTS5 全文檢索（基於 KV 介面）
CJK 分詞（雙元分詞）
倒排索引
MATCH 查詢
```

### v1.1 — FTS 進階

```
布林查詢（AND/OR/NOT）
前綴匹配
BM25 排序
```

### v2.0 — SQL 層

```
SQL parser 移植
SQL planner 移植
SQL executor 移植
SELECT / INSERT / UPDATE / DELETE
同一份 SQL 在三個引擎都能跑
```

### v2.1 — SQL 完整功能

```
JOIN 支援
複雜 ORDER BY
CLI / REPL
```

---

## 7. 實作順序

### Phase 1：KV 核心（v0.1）

```
1. StorageEngine trait
2. MemoryEngine
3. KvStore trait
4. 基本測試
```

### Phase 2：BTree Engine（v0.2）

```
1. 移植 sql6 pager/btree
2. BTreeStorageEngine
3. 持久化測試
```

### Phase 3：LSM Engine（v0.3）

```
1. 移植 lsm5
2. LsmStorageEngine
3. Compaction 測試
```

### Phase 4：整合測試（v0.4）

```
1. 統一測試框架
2. 跨引擎 benchmark
3. 效能調優
```

### Phase 5：SQL 層（v1.0）

```
1. 移植 sql6 parser/planner/executor
2. Executor 呼叫 StorageEngine
3. SQL 測試
```

---

## 8. 關鍵設計決策

### 8.1 Engine trait 接受 table_id

為什麼？因為 BTree engine 的 pager 是多 table 隔離的，scan 需要針對特定 table。

### 8.2 Memory engine 使用 BTreeMap

- 支援 `ORDER BY`（SQL 必要）
- 支援範圍查價 `scan`
- 記憶體佔用合理

### 8.3 v0.x 不加入 SQL

先建立穩定的 KV 核心，SQL 層可以之後再移植。

---

## 9. 依賴

```toml
[dependencies]
thiserror = "2.0"
serde = { version = "1.0", features = ["derive"] }
zstd = "0.13"

[dev-dependencies]
tempfile = "3.14"
```

---

## 10. 測試策略

### KV 測試（v0.x）

```rust
fn test_kv_all_engines() {
    let engines = [
        ("memory", MemoryEngine::open_memory()),
        ("btree", BTreeEngine::open(path).unwrap()),
        ("lsm", LsmEngine::open(path).unwrap()),
    ];

    for (name, engine) in engines {
        engine.put(1, b"key", b"value").unwrap();
        assert_eq!(engine.get(1, b"key").unwrap(), Some(b"value".to_vec()));
    }
}
```

### SQL 測試（v1.0+）

```rust
fn test_sql_all_engines(sql: &str) {
    let executor = Executor::new(engine);
    executor.execute(sql).unwrap();
}
```