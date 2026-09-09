# btree/storage.rs — Page 儲存抽象

## 理論基礎：Page 管理

**分頁儲存 (page-level storage)** 是資料庫引擎的核心概念。資料被分割成固定大小的頁 (page，通常 4KB 或 8KB)，每頁有唯一 ID。這樣的好處：

1. **空間管理** — 磁碟與記憶體以 page 為單位映射
2. **快取效率** — page 大小對齊作業系統的 block size
3. **備份與復原** — 以 page 為單位做 checkpoint

## 儲存抽象

`Storage` trait 定義了五個基本操作：

```rust
pub trait Storage {
    fn read_page(&mut self, page_id: u64) -> Option<Page>;
    fn write_page(&mut self, page: &Page);
    fn alloc_page(&mut self) -> u64;        // 配置新 page
    fn flush(&mut self) -> Result<()>;
    fn header(&self) -> Option<BTreeHeader>; // 根節點位置
}
```

## 兩種實作

### FileStorage

將 page 儲存在 `data` 目錄下的多個檔案 (`data/page_00000001.dat`) 中。每次 flush 會將所有 page 寫入磁碟。

### MemoryStorage

將 page 儲存在 `HashMap<u64, Page>` 中，無持久化。

## BTreeHeader

```rust
struct BTreeHeader {
    root_page: u64,   // 根節點 page ID
    page_count: u64,  // 總 page 數
}
```

header 記錄 B-Tree 的根節點位置，是 tree 存取的起點。

## 相關資源

- `btree/tree.rs` — BTree 資料結構
- `btree/engine.rs` — 引擎層
- `lsm/sstable.rs` — LSM 的 SSTable 設計
