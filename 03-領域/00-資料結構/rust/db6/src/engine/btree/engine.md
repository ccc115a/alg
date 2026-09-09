# btree/engine.rs — BTree 磁碟引擎

## 架構：三層設計

BTreeEngine 採用三層架構：

```
BTreeEngine (引擎層)
    └── BTree (資料層：BTreeMap 封裝)
        └── FileStorage / MemoryStorage (儲存層)
```

## 交易實作

BTreeEngine 使用**寫入緩衝區 (write buffer)** 實作交易：

```rust
tx_buffer: BTreeMap<u32, BTreeMap<Vec<u8>, Option<Vec<u8>>>>
```

- `begin_transaction()` — 啟用交易模式
- 寫入操作轉向 `tx_buffer`，不直接修改 `BTree`
- `commit_transaction()` — 將 buffer 中的變更全部應用到 BTree
- `rollback_transaction()` — 直接丟棄 buffer

## 執行緒安全

使用 `RwLock` 實現執行緒安全：

```rust
tree: RwLock<BTree>                    // 資料的讀寫鎖
in_transaction: RwLock<bool>           // 交易狀態
tx_buffer: RwLock<...>                 // 交易緩衝區
```

RwLock 允許多個讀取者同時存取，但寫入時互斥。

## 能力標記

```rust
impl_capabilities!(BTreeEngine, 
    CanOrderBy, CanScan, CanTransaction, CanBatch, CanFts, CanGroupBy
);
```

BTreeEngine 支援全部能力，是功能最完整的引擎。

## 相關資源

- `btree/tree.rs` — BTreeMap 封裝
- `btree/storage.rs` — Page 層級儲存
- `engine/mod.rs` — 引擎抽象層
