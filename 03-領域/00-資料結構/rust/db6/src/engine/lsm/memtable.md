# lsm/memtable.rs — MemTable 記憶體緩衝區

## 理論基礎

**MemTable (Memory Table)** 是 LSM-Tree 的第一層，所有寫入請求先進入 MemTable。MemTable 使用 **BTreeMap** 儲存，確保資料有序，方便後續刷入 SSTable。

### 刪除標記 (Tombstone)

LSM-Tree 的刪除不直接從磁碟移除資料，而是插入一個**墓碑標記 (tombstone)**：

```rust
pub enum Value {
    Data(Vec<u8>),   // 實際資料
    Tombstone,        // 刪除標記
}
```

在合併 (compaction) 時，tombstone 會清除對應的舊資料。

### 刷入 (Flush)

當 MemTable 達到大小門檻時，會**刷入 (flush)** 磁碟成為 SSTable：

```rust
fn flush(&mut self) -> Vec<(Vec<u8>, Vec<u8>)> {
    let data: Vec<_> = self.map.iter()
        .filter(|(_, v)| v.is_data())
        .map(|(k, v)| (k.clone(), v.get_data().unwrap().clone()))
        .collect();
    self.map.clear();
    data
}
```

## 相關資源

- `lsm/engine.rs` — LsmEngine 主體
- `lsm/sstable.rs` — SSTable 磁碟儲存
