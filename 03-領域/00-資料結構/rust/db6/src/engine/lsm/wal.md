# lsm/wal.rs — WAL (Write-Ahead Log)

## 理論基礎

**WAL (Write-Ahead Log，預寫式日誌)** 是資料庫確保持久性的關鍵機制。核心原則是：**在修改實際資料結構前，先將操作寫入日誌**。

如果系統在寫入過程中崩潰，重啟時可以從 WAL 還原未完成的寫入。

### 日誌格式

每筆記錄包含：
- 鍵長度 (4 bytes, little-endian)
- 鍵內容
- 值長度 (4 bytes, little-endian)
- 值內容

```
[ key_len: u32 ][ key: bytes ][ val_len: u32 ][ value: bytes ]
```

### 還原流程

1. 啟動時檢查 `wal.log` 是否存在
2. 讀取所有記錄
3. 將記錄載入 MemTable
4. 清空 WAL

## 可靠性保證

WAL 使用 `append` 模式寫入，每次寫入後不立即 fsync，這在極端情況下可能遺失少量資料，但換來較高的寫入效能。

## 相關資源

- `lsm/engine.rs` — WAL 的建立與還原邏輯
- `lsm/memtable.rs` — 還原後的資料載入目標
