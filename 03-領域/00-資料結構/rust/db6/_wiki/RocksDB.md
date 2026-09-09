# RocksDB

## 概述

RocksDB 是 Facebook 在 2012 年開發的高效能嵌入式鍵值儲存庫，基於 LevelDB 改進而來。RocksDB 保留了 LevelDB 的核心 LSM Tree 架構，但增加了許多企業級功能，使其能夠支援更廣泛的應用場景。

RocksDB 廣泛應用於：
- 資料庫儲存引擎（MyRocks、Partitioned RAFT）
- 區塊鏈（Ethereum、R Solana）
- 資料庫（MySQL、Cassandra、Kafka）
- 深度學習儲存（Gradient Checkpointing）

## 與 LevelDB 的主要差異

| 特性 | LevelDB | RocksDB |
|------|---------|---------|
| Column Family | 不支援 | 支援 |
| 壓縮 | 簡單 | 多種壓縮演算法 |
| 併發 | 受限 | 支援併發讀寫 |
| 事務 | 無 | 支援（樂觀/悲觀） |
| 記憶體 | 固定 | 可配置 |
| 快照 | 簡單 | 完整快照支援 |

## 架構

```
┌─────────────────────────────────────────────────────────────┐
│                        RocksDB                              │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                    Column Family 1                       ││
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐                  ││
│  │  │MemTable│  │ WAL     │  │ SSTable │ ←── Compaction    ││
│  │  └─────────┘  └─────────┘  └─────────┘                  ││
│  └─────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────┐│
│  │                    Column Family 2                       ││
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐                  ││
│  │  │MemTable│  │ WAL     │  │ SSTable │ ←── Compaction    ││
│  │  └─────────┘  └─────────┘  └─────────┘                  ││
│  └─────────────────────────────────────────────────────────┘│
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                    Column Family 3                       ││
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐                  ││
│  │  │MemTable│  │ WAL     │  │ SSTable │ ←── Compaction    ││
│  │  └─────────┘  └─────────┘  └─────────┘                  ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

## Column Family

Column Family 是 RocksDB 最重要的特性之一：

```cpp
// 建立 Column Family
rocksdb::ColumnFamilyHandle* cf1;
db->CreateColumnFamily(rocksdb::ColumnFamilyOptions(), "cf1", &cf1);

// 寫入到特定 Column Family
db->Put(WriteOptions(), cf1, "key1", "value1");

// 讀取
db->Get(ReadOptions(), cf1, "key1", &value);

// 刪除 Column Family
db->DropColumnFamily(cf1);
```

Column Family 的用途：
- **隔離不同型別的資料**
- **獨立壓縮配置**
- **獨立的 Compaction 策略**

## 儲存格式

### SSTable 結構

RocksDB 的 SSTable 與 LevelDB 類似，但增強了：

```
┌─────────────────────────────────────────────┐
│  Data Block (keys, values)                  │
├─────────────────────────────────────────────┤
│  Index Block (key → block offset)           │
├─────────────────────────────────────────────┤
│  Filter Block (Bloom Filter)                │
├─────────────────────────────────────────────┤
│  Properties Block (統計資訊)                 │
├─────────────────────────────────────────────┤
│  Range Delete Block                         │
├─────────────────────────────────────────────┤
│  Footer                                     │
└─────────────────────────────────────────────┘
```

## 交易支援

RocksDB 支援兩種交易模式：

### 樂觀交易（Optimistic Transaction）

適合低競爭場景：
```cpp
Transaction* txn = db->BeginTransaction(write_options);

// 讀取（作為交易的一部分）
txn->Get(read_options, "key1", &value);

// 寫入
txn->Put("key2", "value2");
txn->Put("key3", "value3");

// 提交
Status s = txn->Commit();
```

### 悲觀交易（Pessimistic Transaction）

適合高競爭場景：
```cpp
Transaction* txn = db->BeginTransaction(write_options);
txn->SetSnapshot();

// 取得鎖
txn->GetForUpdate(read_options, "key1", &value);

// 寫入
txn->Put("key1", new_value);

txn->Commit();
```

## Compaction 策略

RocksDB 支援多種 Compaction 策略：

| 策略 | 說明 |
|------|------|
| Level Compaction | 傳統 LevelDB 風格，分層合併 |
| Universal Compaction | 所有層合併，減少寫入放大 |
| FIFO | 淘汰最舊的檔案，適合時序資料 |
| Clock Compaction | 基於時鐘的淘汰 |

```cpp
// 配置 Compaction 策略
ColumnFamilyOptions cf_opts;
cf_opts.compaction_style = CompactionStyle::kCompactionStyleLevel;
cf_opts.level0_file_num_compaction_trigger = 4;
cf_opts.max_bytes_for_level_base = 256 * 1024 * 1024;  // 256MB
```

## 壓縮

RocksDB 支援每層獨立的壓縮配置：

```cpp
// 每層使用不同壓縮
cf_opts.compression_per_level = {
    kNoCompression,     // L0: 無壓縮（快速寫入）
    kNoCompression,     // L1: 無壓縮
    kSnappyCompression, // L2-L3: 快速壓縮
    kZlibCompression,   // L4-L5: 較高壓縮率
    kZstdCompression,   // L6: 最高壓縮率
};
```

## 監控與統計

RocksDB 提供豐富的監控統計：

```cpp
// 獲取統計
uint64_t num_keys = 0;
db->GetProperty("rocksdb.estimate-num-keys", &num_keys);

// 獲取記憶體使用
uint64_t memtable_usage = 0;
db->GetProperty("rocksdb.cur-size-all-mem-tables", &memtable_usage);
```

常見監控指標：
| 指標 | 說明 |
|------|------|
| `rocksdb.num-get-hits` | Get 命中次數 |
| `rocksdb.mem-table-flush-pending` | 等待 flush 的 MemTable 數 |
| `rocksdb.compaction-pending` | 等待 Compaction 的層數 |
| `rocksdb.storage-engine` | 引擎類型 |

## 區塊快取

RocksDB 支援可配置的區塊快取：

```cpp
// 配置快取
std::shared_ptr<Cache> cache = NewLRUCache(1024 * 1024 * 1024);  // 1GB
cf_opts.block_cache = cache;

// 壓縮的區塊快取
cf_opts.block_cache_compressed = NewLRUCache(256 * 1024 * 1024);  // 256MB
```

## 使用範例（C++）

```cpp
#include "rocksdb/db.h"
#include "rocksdb/options.h"

rocksdb::DB* db;
rocksdb::Options options;

// 基本配置
options.create_if_missing = true;
options.max_total_wal_size = 64 * 1024 * 1024;  // 64MB WAL

// 打開資料庫
rocksdb::Status status = rocksdb::DB::Open(options, "/path/to/db", &db);

// 基本操作
db->Put(rocksdb::WriteOptions(), "key1", "value1");
std::string value;
db->Get(rocksdb::ReadOptions(), "key1", &value);
db->Delete(rocksdb::WriteOptions(), "key1");

// 批次操作
rocksdb::WriteBatch batch;
batch.Put("key1", "value1");
batch.Put("key2", "value2");
batch.Delete("key3");
db->Write(rocksdb::WriteOptions(), &batch);

delete db;
```

## Python綁定

```python
from pyrrocks import DB, Options, WriteBatch

options = Options()
options.create_if_missing = True

db = DB.open("/path/to/db", options)

# 基本操作
db.put(b"key1", b"value1")
value = db.get(b"key1")
db.delete(b"key1")

# 批次操作
batch = WriteBatch()
batch.put(b"key1", b"value1")
batch.put(b"key2", b"value2")
db.write(batch)
```

## 應用場景

### MyRocks

MySQL + RocksDB 的組合，提供：
- 更高的寫入效能
- 更好的壓縮率
- 更低的 I/O

### Kafka

Kafka 0.9+ 支援使用 RocksDB 儲存消費者偏移量。

### Cassandra

SSTable 的格式基於 RocksDB 的實現。

## 在 db6 中的借鑒

db6 的 LSM 引擎可以借鑒 RocksDB 的以下設計：

1. **Column Family**：用於隔離不同表的資料
2. **交易支援**：增強並發控制
3. **監控統計**：完善的可觀測性
4. **多種 Compaction**：適配不同場景

## 延伸閱讀

- RocksDB GitHub: https://github.com/facebook/rocksdb
- RocksDB Wiki: https://github.com/facebook/rocksdb/wiki
- "RocksDB: A Persistent Key-Value Store for Flash and RAM" - 原始論文