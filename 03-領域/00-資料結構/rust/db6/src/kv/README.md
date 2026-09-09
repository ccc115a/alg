# kv/ — 統一的 KV API 介面

## 概覽

kv 層是 StorageEngine 的上層封裝，提供統一的工廠介面，讓使用者透過字串名稱選擇儲存引擎。

## 模組列表

| 檔案 | 說明 |
|------|------|
| `mod.rs` | KvStore trait、KvEngine 列舉 |

## 核心型別

`KvEngine` 列舉封裝四種引擎：

```rust
pub enum KvEngine {
    Hash(Arc<RwLock<HashMemoryEngine>>),    // 記憶體 HashMap (new "memory")
    BTreeMem(Arc<RwLock<BTreeMemoryEngine>>),  // 記憶體 BTree (new "btree")
    BTree(Arc<RwLock<BTreeEngine>>),         // 磁碟 BTree (open "btree")
    Lsm(Arc<RwLock<LsmEngine>>),             // 磁碟 LSM (open "lsm")
}
```

## 使用方式

```rust
let kv = KvEngine::new("memory")?;             // 記憶體
let kv = KvEngine::open("btree", &path)?;      // 持久化
```

## 設計原則

- **KvStore trait** — 統一的 put/get/delete/scan/batch_put/range_delete/flush/engine_type 介面
- **執行緒安全** — 使用 `Arc<RwLock<...>>` 實現共享存取
- **字串選擇** — 避開泛型參數，簡化使用者體驗

## 相關連結

- `kv.md` — KV API 詳解
- `engine/README.md` — 底層儲存引擎
- `query/README.md` — 上層查詢介面
