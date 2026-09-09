# hash.rs — Hash 記憶體引擎

## 理論基礎：Hash Table

**雜湊表 (hash table)** 是一種關聯式容器，透過**雜湊函數 (hash function)** 將鍵映射到陣列索引，實現平均 O(1) 的查詢、插入與刪除時間。

然而，hash table 有兩個重要的特性限制：

1. **無序性** — 雜湊函數的輸出是偽隨機的，儲存的鍵不具備任何順序
2. **不支援範圍查詢** — 無法像 B-Tree 一樣做 `key BETWEEN 'a' AND 'm'` 的查詢

## 實作細節

Rust 標準庫提供 `HashMap<K, V>`，底層使用 SipHash 作為雜湊函數，具有抵抗 HashDoS 攻擊的能力。db6 使用雙層 HashMap：

```rust
HashMap<u32, HashMap<Vec<u8>, Vec<u8>>>
```

外層以 `table_id` (u32) 作為鍵，實現多表隔離；內層以 `Vec<u8>` 作為實際資料的鍵。

## scan 的實作問題

由於 HashMap 不支援範圍掃描，`scan()` 方法退化為回傳該 table 的所有鍵值對。這表示：

- `SELECT * FROM t WHERE key > 100` 會先取出所有資料再做過濾
- 在大量資料時效率極低

因此 HashMemoryEngine 沒有實作 `CanOrderBy`、`CanScan` 能力標記。

## 持久化策略

使用 `bincode`（二進制序列化）將整個 HashMap 寫入檔案。寫入採用**原子寫入 (atomic write)** 策略：先寫到 `.tmp` 暫存檔，再用 `std::fs::rename` 原子性地取代 `.dat` 檔案。這樣即使系統崩潰，也不會留下半寫的檔案。

## 相關資源

- `memory/btree.rs` — BTree 版本，支援排序與範圍掃描
- `engine/mod.rs` — StorageEngine trait
