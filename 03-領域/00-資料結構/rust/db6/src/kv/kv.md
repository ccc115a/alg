# kv/mod.rs — KV API 統一介面

## 設計目的

KV API 層的目的是提供一個統一的工廠介面，讓使用者可以透過字串名稱選擇儲存引擎，而不需要直接操作具體的引擎型別。

## KvEngine 列舉

```rust
pub enum KvEngine {
    Hash(Arc<RwLock<HashMemoryEngine>>),        // 記憶體 HashMap
    BTreeMem(Arc<RwLock<BTreeMemoryEngine>>),   // 記憶體 BTree
    BTree(Arc<RwLock<BTreeEngine>>),            // 磁碟 BTree
    Lsm(Arc<RwLock<LsmEngine>>),                // 磁碟 LSM
}
```

使用 `Arc<RwLock<...>>` 實現執行緒安全的共享存取。

## 工廠方法

```rust
// 記憶體模式
let kv = KvEngine::new("memory").unwrap();

// 磁碟模式（僅 BTree/LSM 支援）
let kv = KvEngine::open("btree", &path).unwrap();
```

## KvStore Trait

定義了統一的 KV 操作介面，與 `StorageEngine` trait 類似，但不需要 `table_id` 參數（由內部處理）。

## 相關資源

- `engine/mod.md` — StorageEngine 抽象層
- `query/query.md` — 高階查詢介面
