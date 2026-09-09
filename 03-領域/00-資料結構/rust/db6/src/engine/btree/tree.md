# btree/tree.rs — BTreeMap 封裝

## 文件名稱的背景

雖然命名為 `tree.rs`，但實際上這是一個 **BTreeMap 的輕量封裝 (lightweight wrapper)**，而非傳統的 B-Tree 節點實作。db6 的磁碟 BTree 引擎在底層重用了 Rust 標準庫的 `std::collections::BTreeMap`，而不是自己實作節點分裂與合併。

這個設計取捨的考量：
- 開發速度快，不需處理 B-Tree 的複雜演算法
- Rust 的 BTreeMap 經過完善測試，穩定性高
- 缺點是無法精細控制 page 層級的優化

## 核心介面

- `get(key)` — O(log n) 查詢
- `put(key, value)` — O(log n) 插入或更新
- `delete(key)` — O(log n) 移除
- `scan(start, end)` — 範圍掃描，回傳有序結果

## 掃描實作

使用 `BTreeMap::range()` 支援四種模式：

```rust
(None, None)     → 全部資料
(Some(s), None)  → [s, ∞)
(None, Some(e))  → (-∞, e)
(Some(s), Some(e)) → [s, e)
```

## 持久化

使用 `bincode` 將整個 BTreeMap 序列化到 `btree.dat` 檔案。這種「全量序列化」方式在資料量大時效率會下降，因為每次 flush 都要寫入全部資料。

## 相關資源

- `btree/engine.rs` — BTreeEngine 外部包裝
- `btree/storage.rs` — Page-level storage 抽象
- `memory/btree.rs` — 記憶體版 BTree 引擎
