# lsm/ — LSM 引擎模組

## 目錄結構

- `mod.rs` — 模組入口
- `engine.rs` — LsmEngine 主體實作
- `memtable.rs` — 記憶體寫入緩衝區
- `sstable.rs` — 磁碟 SSTable
- `wal.rs` — Write-Ahead Log
- `bloom.rs` — Bloom Filter 加速查詢

## 架構圖

```
寫入:  WAL → MemTable → (flush) → SSTable
讀取:  Bloom Filter → MemTable → SSTable (由新到舊)
```

## 適用場景

- 大量寫入 (write-heavy) 的工作負載
- 寫入效能優先於讀取效能
- 需要磁碟持久化與交易支援

## 相關資源

- `engine/mod.md` — 引擎架構總覽
- `btree/engine.md` — B-Tree 引擎對比
