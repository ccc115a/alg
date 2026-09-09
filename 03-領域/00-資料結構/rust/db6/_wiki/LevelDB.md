# LevelDB

## 概述

LevelDB 是 Google 開發的一個快速的鍵值儲存庫，由 San Ghaimat 和 Jeff Dean 在 2011 年的論文中發表。LevelDB 是一個嵌入式資料庫，適用於直接在你的應用程式中使用，而非作為網路服務。它是 Chrome 瀏覽器中 IndexedDB 的底層引擎，也是諸多流行系統（如 Ethereum 區塊鏈客戶端）的儲存後端。

## 設計目標

LevelDB 的設計目標：
1. **高寫入效能**：適合寫入密集型應用
2. **順序 I/O**：充分利用磁碟的順序讀寫能力
3. **簡單可靠**：不依賴網路，專注於本地儲存
4. **緊湊儲存**：支援壓縮

## 架構

LevelDB 的核心架構：

```
┌──────────────────────────────────────────────────────┐
│                    LevelDB                          │
│                                                      │
│  ┌────────────────────────────────────────────────┐ │
│  │                  MemTable                      │ │
│  │              (跳表實現)                         │ │
│  │   Key1 → Value1, Key2 → Value2, Key3 → Value3  │ │
│  └────────────────────────────────────────────────┘ │
│                        │                            │
│  ┌─────────────────────▼────────────────────────┐  │
│  │                  WAL                          │ │
│  │            (Write-Ahead Log)                  │ │
│  └───────────────────────────────────────────────┘  │
│                        │                            │
│  ┌─────────────────────▼────────────────────────┐  │
│  │            Immutable MemTable                 │ │
│  └───────────────────────────────────────────────┘  │
│                        │                            │
│  ┌─────────────────────▼────────────────────────┐  │
│  │              Compaction                       │ │
│  │   L0 → L1 → L2 → L3 → L4 → L5 → L6          │ │
│  └───────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────┘
```

## 資料結構

### MemTable

記憶體中的有序資料結構，使用跳表（Skip List）實現：
- 新寫入的資料首先進入 MemTable
- 支援 O(log n) 的插入和查詢
- 當 MemTable 滿了後，轉換為 Immutable MemTable 並觸發 flush

### WAL（Write-Ahead Log）

在將資料寫入 MemTable 之前，先寫入日誌檔案：
- 確保 crash 後可以恢復
- 故障時可以從日誌重建 MemTable

### SSTable（Sorted String Table）

磁碟上的持久化儲存結構：

```
┌────────────────────────────────────────────────┐
│  SSTable File                                  │
├────────────────────────────────────────────────┤
│  Data Block 1    │ Data Block 2 │ ... │ Block │
├────────────────────────────────────────────────┤
│  Index Block     │ (key → offset)              │
├────────────────────────────────────────────────┤
│  Filter Block    │ (Bloom Filter)              │
├────────────────────────────────────────────────┤
│  Meta Index      │ (filter location)          │
├────────────────────────────────────────────────┤
│  Footer          │ (index + meta index loc)   │
└────────────────────────────────────────────────┘
```

### 日誌格式

```
┌────────────────────────────────────────────────┐
│ Log File                                       │
├────────────────────────────────────────────────┤
│  Record 1 (size: 100 bytes)                    │
│  Record 2 (size: 50 bytes)                    │
│  Record 3 (size: 200 bytes)                   │
│  ...                                          │
└────────────────────────────────────────────────┘
```

## LSM Tree 結構

LevelDB 使用 LSM Tree（Log-Structured Merge-tree）：

```
L0:  [sst_1, sst_2]     ← 來自 MemTable flush，鍵範圍可能重疊
     ↓
L1:  [sst_1, sst_2, sst_3, ...]  ← 鍵範圍不重疊，總大小 limit
     ↓
L2:  [sst_a, sst_b, ...]        ← 總大小 limit × 10
     ↓
L3:  [sst_x, sst_y, ...]        ← 總大小 limit × 100
     ↓
...
L6:  [sst_m, sst_n, ...]        ← 最大層
```

每層的容量限制是前一層的 10 倍。

## 讀取流程

查詢鍵 "Key3"：

1. 先查詢 MemTable
2. 查詢 Immutable MemTable（如果存在的話）
3. 從 L0 開始，由新到舊遍歷所有 SSTable
4. 每個 SSTable 先用 Bloom Filter 判斷鍵是否可能存在
5. 如果可能存在，用 Index Block 定位並讀取 Data Block

```
MemTable → Immutable → L0.sst → L1.sst → L2.sst → ...
```

## 寫入流程

寫入鍵值對 (Key, Value)：

1. 寫入 WAL
2. 寫入 MemTable
3. 返回成功

```
WAL.append((Key, Value)) → MemTable.insert((Key, Value)) → return OK
```

## Compaction

當某層的 SSTable 數量或大小達到限制時，觸發 Compaction：

### Minor Compaction

MemTable flush 到 L0。

### Major Compaction

L0 和 L1 的 SSTable 合併：
1. 選擇 L1 中的一個 SSTable
2. 找出所有與其鍵範圍重疊的 L0 SSTable
3. 合併所有相關的 SSTable
4. 產生新的 L1 SSTable
5. 刪除舊的 SSTable

```
Before:
L1: [A-C] [D-F] [G-I]
L0: [B-D] [F-H]

After:
L1: [A-C] [C-H] [G-I]  ← 重新分割
```

## Bloom Filter

每個 SSTable 包含一個 Bloom Filter，用於快速判斷鍵是否不存在：

```rust
// 查詢時
if !bloom_filter.might_contain(key) {
    // 鍵肯定不存在於這個 SSTable，可以跳過讀取
    return None;
}
// 否則可能存在，需要讀取 SSTable 確認
```

## 壓縮

LevelDB 支援多种压缩算法：
- **Snappy**（預設）：快速，壓縮率一般
- **Zlib**：較慢，壓縮率高
- **LZ4**：快速，壓縮率高

```rust
// 啟用不同壓縮
let options = Options {
    compression: SNAPPY_COMPRESSION,
    ..Default::default()
};
```

## 限制

LevelDB 的限制：
1. **非網路資料庫**：不是網路服務，需要嵌入使用
2. **單線程寫入**：預設只有一個寫入者
3. **單進程訪問**：不支援多進程並發
4. **簡單修復**：沒有線上修復功能

## 使用範例

```rust
use leveldb::database::Database;
use leveldb::options::{Options, ReadOptions};

// 打開資料庫
let mut options = Options::new();
options.create_if_missing = true;
let db = Database::open("path/to/db", options).unwrap();

// 寫入
db.put(WriteOptions::default(), b"key1", b"value1").unwrap();

// 讀取
let result = db.get(ReadOptions::default(), b"key1").unwrap();

// 刪除
db.delete(WriteOptions::default(), b"key1").unwrap();
```

## 衍生項目

LevelDB 的設計啟發了許多衍生專案：

| 專案 | 特點 |
|------|------|
| **RocksDB** | Facebook 開發，支持更多功能 |
| **HyperLevelDB** | Hyperdex 的改進版本 |
| **LevelDB LevelDB** | Rust 實現 |
| **FastDB** | 高效能改進 |

## 在 db6 中的角色

db6 的 [LsmEngine](../src/engine/lsm.rs) 移植自 lsm5，借鑒了 LevelDB 的 LSM 架構。主要參考了：
- MemTable + WAL 的寫入流程
- SSTable 的檔案格式
- 分層 Compaction 策略
- Bloom Filter 的使用

## 延伸閱讀

- LevelDB 原始論文：https://www.researchgate.net/publication/263149197_LevelDB
- LevelDB GitHub：https://github.com/google/leveldb
- RocksDB Wiki：https://github.com/facebook/rocksdb/wiki