# btree.rs — BTree 記憶體引擎

## 理論基礎：B-Tree

**B-Tree (平衡搜尋樹)** 是一種自平衡的樹狀資料結構，廣泛應用於資料庫與檔案系統：

- 所有葉節點在同一深度，保證 O(log n) 的操作時間
- 節點可包含多個鍵，降低樹高，減少磁碟存取次數
- **中序遍歷 (in-order traversal)** 可取得有序序列

Rust 標準庫的 `BTreeMap` 使用 B-Tree 實作，鍵值按照鍵的自然順序排列，因此可以高效支援範圍查詢與排序。

## 與 Hash 引擎的關鍵差異

| 面向 | Hash | BTree |
|------|------|-------|
| 查詢複雜度 | O(1) | O(log n) |
| 鍵的順序 | 無序 | 有序 |
| 範圍查詢 | 不支援 | 支援 |
| ORDER BY | 需額外排序 | 直接掃描 |
| 記憶體開銷 | 較小 | 較大 |

## 範圍掃描實作

使用 `BTreeMap::range()` 搭配 Rust 的 `Bound` API：

```rust
use std::collections::Bound;

let start = if start.is_empty() { Bound::Unbounded }
            else { Bound::Included(start) };
let end = if end.is_empty() { Bound::Excluded(end) }
          else { Bound::Unbounded };
table.range((start, end))
```

`Bound::Unbounded` 代表無限邊界，空字串作為「不限制」的標記是 db6 的慣例。

## 能力標記

BTreeMemoryEngine 實作了大量能力標記：

```rust
impl CanOrderBy for BTreeMemoryEngine {}  // BTree 天然有序
impl CanScan for BTreeMemoryEngine {}     // 支援範圍掃描
impl CanGroupBy for BTreeMemoryEngine {}  // 支援聚合
```

## 相關資源

- `memory/hash.rs` — Hash 引擎，適合物件查詢
- `btree/tree.rs` — 磁碟版 B-Tree 實作
- `engine/mod.rs` — 引擎介面定義
