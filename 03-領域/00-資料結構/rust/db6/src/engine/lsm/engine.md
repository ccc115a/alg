# lsm/engine.rs — LSM 引擎實作

## 理論基礎：LSM-Tree

**LSM-Tree (Log-Structured Merge-Tree)** 是一種專為高寫入吞吐量設計的資料結構，由 Patrick O'Neil 等人於 1996 年提出。核心思想是將隨機寫入轉換為順序寫入，大幅提升寫入效能。

### 寫入路徑

```
寫入請求 → WAL (順序寫入) → MemTable (記憶體 Buffer)
                              ↓ (當 MemTable 滿時)
                       SSTable (磁碟，唯讀)
```

### 讀取路徑

```
查詢請求 → Bloom Filter (快速排除)
          → MemTable (最新資料)
          → SSTable 由新到舊依序查詢
```

### 合併 (Compaction)

當 SSTable 數量過多時，背景執行合併操作：讀取多個 SSTable，合併相同鍵（保留最新版本），寫入新的 SSTable，刪除舊的。

## LsmEngine 元件

| 元件 | 位置 | 功能 |
|------|------|------|
| MemTable | `memtable.rs` | 記憶體寫入緩衝區 |
| SSTable | `sstable.rs` | 磁碟唯讀資料檔 |
| WAL | `wal.rs` | Write-Ahead Log 確保持久性 |
| Bloom Filter | `bloom.rs` | 加速不存在的鍵查詢 |

## 交易實作

與 BTreeEngine 類似，使用 `tx_buffer` 在交易期間暫存變更。

## 能力標記

```rust
impl_capabilities!(LsmEngine, CanOrderBy, CanScan, CanTransaction, CanBatch, CanFts, CanGroupBy);
```

## 相關資源

- `lsm/memtable.md` — 記憶體緩衝區
- `lsm/sstable.md` — 磁碟 SSTable
- `lsm/wal.md` — WAL 日誌
- `lsm/bloom.md` — Bloom Filter
