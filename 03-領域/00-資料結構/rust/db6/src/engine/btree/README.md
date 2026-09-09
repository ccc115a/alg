# btree/ — BTree 引擎模組

## 目錄結構

- `mod.rs` — 模組入口
- `tree.rs` — BTreeMap 封裝（資料層）
- `storage.rs` — Page 儲存抽象與實作
- `engine.rs` — BTreeEngine（引擎層）

## 檔案關係

1. `storage.rs` 定義底層 page 讀寫（檔案或記憶體）
2. `tree.rs` 在 storage 之上提供 BTreeMap API
3. `engine.rs` 包裝 tree 加上交易支援，實作 `StorageEngine`

## 使用方式

```rust
use db6::engine::BTreeEngine;

let mut engine = BTreeEngine::open(&path).unwrap();
engine.put(1, b"key", b"value").unwrap();
engine.begin_transaction().unwrap();
// ... 操作 ...
engine.commit_transaction().unwrap();
```

## 相關資源

- `memory/btree.md` — 記憶體版 BTree
- `engine/mod.md` — 引擎總覽
