# KV-Store（Key-Value Store，鍵值儲存）

## 概述

KV-Store（Key-Value Store，鍵值儲存）是最簡單的資料儲存抽象之一。它以「鍵-值」配對的方式儲存資料，類似於程式語言中的雜湊表（Hash Map）或字典（Dictionary）。KV-Store 的核心 API 通常只有四個操作：get（讀取）、put（寫入）、delete（刪除）、scan（範圍查詢）。

這種簡潔的設計使得 KV-Store 容易實作和擴展，同時因為底層不需要支援複雜的查詢語言，效能可以做得非常高。KV-Store 是建構更複雜資料庫系統（如文件資料庫、圖資料庫）的基礎。

## 核心 API

KV-Store 的標準操作集合非常精簡：

### 基本操作

```rust
// 根據鍵讀取值
fn get(key: &[u8]) -> Result<Option<Vec<u8>>>;

// 根據鍵寫入值
fn put(key: &[u8], value: &[u8]) -> Result<()>;

// 根據鍵刪除值
fn delete(key: &[u8]) -> Result<()>;

// 範圍查詢
fn scan(start: &[u8], end: &[u8]) -> Result<Vec<(Vec<u8>, Vec<u8>)>>;
```

### 進階操作

```rust
// 批次寫入
fn batch_put(pairs: Vec<(Key, Value)>) -> Result<()>;

// 範圍刪除
fn range_delete(start: &[u8], end: &[u8]) -> Result<()>;

// 取得多個鍵
fn batch_get(keys: Vec<Key>) -> Result<Vec<Option<Value>>>;
```

## 設計決策

### 1. 位元組 vs 字串

KV-Store 通常將鍵和值視為位元組陣列（`[u8]`），而非字串。這意味著：
- 應用程式負責序列化（serialization）和反序列化（deserialization）
- 可以儲存任意二進制資料
- 需要應用層面定義資料格式

### 2. 鍵的排序

KV-Store 可分為兩類：
- **有序 KV-Store**：鍵按字典順序排序，支持範圍查詢和有序掃描
- **無序 KV-Store**：鍵沒有順序，只支持精確匹配

db6 的 StorageEngine trait 是有序的，支持 scan 操作，這對 SQL 的 ORDER BY 和範圍查詢至關重要。

### 3. 單值 vs 多值

一些 KV-Store 支援每個鍵多個值：
- **單值（Single Value）**：每個鍵對應一個值（db6採用的模式）
- **多值（Multi-Value）**：每個鍵對應多個值（如 Redis 的 List）

## 實作方式

### 記憶體實現

最簡單的 KV-Store 是基於記憶體的結構：

```rust
use std::collections::BTreeMap;

pub struct MemoryKvStore {
    data: BTreeMap<Vec<u8>, Vec<u8>>,
}
```

B-Tree Map（如 Rust 的 BTreeMap、Java 的 TreeMap）因為：
- 自然保持鍵有序
- 支持範圍查詢
- 記憶體效率較高
- 實作相對簡單

### 磁碟實現

持久的 KV-Store 需要考慮：
- ** LSM Tree**：寫入優化，適合大量寫入場景
- ** B+Tree**：讀取優化，適合讀取密集場景
- **檔案系統**：簡單的 append-only 實現

## KV-Store 與 SQL 的關係

KV-Store 可以視為 SQL 的底層儲存：

```
┌─────────────────────────────┐
│         SQL 引擎             │
│   (Parser/Planner/Executor) │
└─────────────┬───────────────┘
              │ 讀取/寫入 KV 對
              ▼
┌─────────────────────────────┐
│      StorageEngine trait    │
│     (get/put/delete/scan)    │
└─────────────┬───────────────┘
              │
    ┌─────────┴─────────┐
    ▼                   ▼
┌────────┐      ┌─────────┐
│ Memory │      │  LSM    │
│ BTree  │      │  BTree   │
└────────┘      └─────────┘
```

SQL 引擎將：
- `SELECT * FROM users WHERE id = 1` → `get("users:1")`
- `SELECT * FROM users WHERE age > 18` → `scan("users:", "users;")`
- `INSERT INTO users VALUES (...)` → `put("users:" + new_id, serialized_data)`

## 知名 KV-Store 系統

### Redis

Redis 是最流行的記憶體 KV-Store，支援多種資料結構：
- **String**：簡單的字串值
- **Hash**：欄位-值配對
- **List**：有序列表
- **Set**：無序集合
- **Sorted Set**：帶分數的有序集合

Redis 常被用於：
- 快取層
- 工作階段儲存
- 即時排行榜
- 訊息佇列

### LevelDB / RocksDB

Google 的 LevelDB 和 Facebook 的 RocksDB 是基於 LSM Tree 的 KV-Store：
- 適合寫入密集場景
- 支援快照讀取
- 支援範圍掃描

### etcd

etcd 是一個分散式 KV-Store，用於服務發現和設定管理：
- 基於 Raft 共識演算法
- 提供強一致性保證
- 是 Kubernetes 的核心元件

### Cassandra

嚴格來說 Cassandra 是寬欄位儲存（Wide Column Store），但底層也是 KV 介面：
- 支援動態欄位
- 分散式架構
- 可調一致性

## 在 db6 中的應用

db6 的核心是 KV-Store，定義了 [StorageEngine trait](../src/engine/mod.rs)：

```rust
pub trait StorageEngine: Send + Sync {
    fn get(&self, table_id: u32, key: &[u8]) -> Result<Option<Vec<u8>>>;
    fn put(&mut self, table_id: u32, key: &[u8], value: &[u8]) -> Result<()>;
    fn delete(&mut self, table_id: u32, key: &[u8]) -> Result<()>;
    fn scan(&self, table_id: u32, start: &[u8], end: &[u8]) -> Result<Vec<(Vec<u8>, Vec<u8>)>>;
}
```

db6 的三個引擎都實作了這個 trait：
- **MemoryEngine**：基於 BTreeMap 的記憶體 KV-Store
- **BTreeEngine**：基於磁碟 B-Tree 的 KV-Store
- **LsmEngine**：基於 LSM Tree 的 KV-Store

## KV-Store 的限制

KV-Store 的簡潔性也帶來限制：

1. **無 schema**：需要應用程式自己解析和驗證資料
2. **無查詢語言**：只能通過鍵或範圍查詢
3. **無關聯查詢**：無法直接 JOIN 不同鍵的資料
4. **無交易隔離**：並發控制需要應用程式處理

這些限制是更高層級資料庫系統（關聯式資料庫、文件資料庫）存在的理由。

## 延伸閱讀

- Kleppmann, M. (2017). Designing Data-Intensive Applications. O'Reilly Media.
- Redis Documentation: https://redis.io/docs
- RocksDB Documentation: https://github.com/facebook/rocksdb/wiki