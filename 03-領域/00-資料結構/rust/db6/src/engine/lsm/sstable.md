# lsm/sstable.rs — SSTable 磁碟儲存

## 理論基礎

**SSTable (Sorted String Table)** 是磁碟上的有序唯讀資料檔案。每個 SSTable 是一組鍵值對的集合，按鍵排序，一旦寫入就不再修改。

### 與 B-Tree 的差異

| 特性 | B-Tree | SSTable |
|------|--------|---------|
| 可變性 | 可原地更新 | 唯讀 |
| 寫入方式 | 隨機寫入 | 順序寫入 |
| 合併 | 無需 | 需 compaction |
| 磁碟放大 | 較小 | 較大 (需合併) |

### SSTable 生命週期

1. **建立** — MemTable 滿時，flush 為 SSTable
2. **查詢** — 二分搜尋載入的 BTreeMap
3. **合併** — 多個 SSTable 合併為一個
4. **刪除** — 合併後刪除舊 SSTable

## 序列化

使用 `bincode` 將 BTreeMap 序列化到 `.sst` 檔案：

```rust
fn write_to_disk(&self) -> Result<()> {
    let data = bincode::serialize(&self.data)?;
    file.write_all(&data)?;
}
```

## 相關資源

- `lsm/memtable.rs` — MemTable 來源
- `lsm/engine.rs` — Flush 與 Compaction 邏輯
- `btree/storage.rs` — BTree 的 page 儲存對比
