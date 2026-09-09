# db6 KV vs Redis 功能對照

## 概述

Redis 是「資料結構伺服器」，每個 key 可以是不同的資料結構（String、Hash、List、Set、ZSet...）。
db6 是「KV 儲存引擎」，value 全是 bytes，SQL 層只是把 value 當 JSON 解析。

**核心限制：db6 的 value 是 opaque bytes，沒有辦法做 field-level 的操作（Hash/List/Set/ZSet）**

---

## 功能對照表

### 已有（相當於 Redis 的）

| Redis 功能 | db6 支援 | 實作方式 |
|------------|---------|---------|
| `GET/SET/DEL` | ✅ | `get/put/delete` |
| `EXISTS` | ✅ | 可用 `get` 回傳 `None` 判斷 |
| `SCAN` | ✅ | `scan(start, end)` 範圍查詢 |
| `KEYS pattern` | ⚠️ | 無 pattern matching，只能全表掃描 |
| `FLUSHDB` | ⚠️ | 可刪整個 table，無專屬指令 |
| `DBSIZE` | ✅ | `stats()` 的 `key_count` |
| `INCR/INCRBY` | ⚠️ | SQL 層可模擬，KV 層無原生支援 |
| `APPEND` | ❌ | 無 |
| `GETSET` | ❌ | 無 |

---

## db6 KV 已有方法

### StorageEngine Trait

```rust
pub trait StorageEngine: Send + Sync {
    fn open(path: &Path) -> Result<Box<dyn StorageEngine>>;
    fn open_memory() -> Box<dyn StorageEngine>;

    fn engine_type(&self) -> &'static str;

    fn get(&self, table_id: u32, key: &[u8]) -> Result<Option<Vec<u8>>>;
    fn put(&mut self, table_id: u32, key: &[u8], value: &[u8]) -> Result<()>;
    fn delete(&mut self, table_id: u32, key: &[u8]) -> Result<()>;
    fn scan(&self, table_id: u32, start: &[u8], end: &[u8]) -> Result<Vec<(Vec<u8>, Vec<u8>)>>;

    fn batch_put(&mut self, table_id: u32, pairs: Vec<(Vec<u8>, Vec<u8>)>) -> Result<()>;
    fn range_delete(&mut self, table_id: u32, start: &[u8], end: &[u8]) -> Result<()>;
    fn flush(&mut self) -> Result<()>;
    fn sync(&mut self) -> Result<()>;

    fn begin_transaction(&mut self) -> Result<()>;
    fn commit_transaction(&mut self) -> Result<()>;
    fn rollback_transaction(&mut self) -> Result<()>;
    fn has_transaction(&self) -> bool;

    fn stats(&self) -> EngineStats;
}
```

### KvStore Trait

```rust
pub trait KvStore {
    fn put(&mut self, table_id: u32, key: &[u8], value: &[u8]) -> Result<()>;
    fn get(&self, table_id: u32, key: &[u8]) -> Result<Option<Vec<u8>>>;
    fn delete(&mut self, table_id: u32, key: &[u8]) -> Result<()>;
    fn scan(&self, table_id: u32, start: &[u8], end: &[u8]) -> Result<Vec<(Vec<u8>, Vec<u8>)>>;
    fn batch_put(&mut self, table_id: u32, pairs: Vec<(Vec<u8>, Vec<u8>)>) -> Result<()>;
    fn range_delete(&mut self, table_id: u32, start: &[u8], end: &[u8]) -> Result<()>;
    fn flush(&mut self) -> Result<()>;
    fn engine_type(&self) -> &'static str;
}
```

### 引擎支援矩陣

| Operation | HashMemory | BTreeMem | BTree | LSM |
|-----------|------------|----------|-------|-----|
| `get` | Yes | Yes | Yes | Yes |
| `put` | Yes | Yes | Yes | Yes* |
| `delete` | Yes | Yes | Yes | Yes* |
| `scan` | Yes (all) | Yes | Yes | Yes |
| `batch_put` | Yes | Yes | Yes | Yes |
| `range_delete` | Yes (all) | Yes | Yes | Yes |
| `flush` | Yes | Yes | Yes | Yes |
| `sync` | Yes | Yes | Yes | Yes |
| `transaction` | No | No | Yes | Yes |
| `stats` | Yes | Yes | Yes | Yes |

\* LSM only supports `table_id=1`

---

## 完全缺少的 Redis 功能

### String 系列（Redis 的基礎類型）

| Redis 功能 | db6 狀態 | 說明 |
|-----------|---------|------|
| `APPEND key value` | ❌ | 將 value 附加到現有字串末尾 |
| `GETSET key value` | ❌ | 原子設定新值並回傳舊值 |
| `SETNX key value` | ❌ | 不存在才設定（needs_exists semantic） |
| `SETRANGE key offset value` | ❌ | 從 offset 開始替換 |
| `GETRANGE key start end` | ❌ | 子字串取得 |
| `INCRBYFLOAT key increment` | ❌ | 浮點數遞增 |
| `STRLEN key` | ❌ | 回傳字串長度 |
| `SETBIT/GETBIT/BITCOUNT` | ❌ | 位元運算，可用於活躍天數統計 |

### Hash 系列

| Redis 功能 | db6 狀態 | 說明 |
|-----------|---------|------|
| `HSET key field value` | ❌ | 設定 hash 欄位，O(1) |
| `HGET key field` | ❌ | 取得 hash 欄位，O(1) |
| `HGETALL key` | ❌ | 取得所有欄位 |
| `HSETNX key field value` | ❌ | 欄位不存在才設定 |
| `HINCRBY key field increment` | ❌ | 欄位遞增 |
| `HEXISTS key field` | ❌ | 檢查欄位是否存在 |
| `HDEL key field [field...]` | ❌ | 刪除欄位 |
| `HLEN key` | ❌ | 欄位數量 |
| `HKEYS/HVALS key` | ❌ | 所有欄位名/值 |
| `HMSET key field value [field value...]` | ❌ | 批量設定 |

### List 系列（雙向列表）

| Redis 功能 | db6 狀態 | 說明 |
|-----------|---------|------|
| `LPUSH key value [value...]` | ❌ | 左側推入 |
| `RPUSH key value [value...]` | ❌ | 右側推入 |
| `LPOP key` | ❌ | 左側彈出 |
| `RPOP key` | ❌ | 右側彈出 |
| `LRANGE key start stop` | ❌ | 範圍取得 |
| `LLEN key` | ❌ | 清單長度 |
| `LREM key count value` | ❌ | 移除元素 |
| `LSET key index value` | ❌ | 設定指定位置值 |
| `LTRIM key start stop` | ❌ | 修剪清單 |
| `RPOPLPUSH src dst` | ❌ | 移動元素（队列操作） |

### Set 系列（無重複集合）

| Redis 功能 | db6 狀態 | 說明 |
|-----------|---------|------|
| `SADD key member [member...]` | ❌ | 添加成員 |
| `SREM key member [member...]` | ❌ | 移除成員 |
| `SMEMBERS key` | ❌ | 所有成員 |
| `SISMEMBER key member` | ❌ | 是否為成員 |
| `SCARD key` | ❌ | 成員數量 |
| `SINTER key [key...]` | ❌ | 交集 |
| `SUNION key [key...]` | ❌ | 聯集 |
| `SDIFF key [key...]` | ❌ | 差集 |
| `SRANDMEMBER key [count]` | ❌ | 隨機成員 |

### Sorted Set 系列（分數排序）

| Redis 功能 | db6 狀態 | 說明 |
|-----------|---------|------|
| `ZADD key score member [score member...]` | ❌ | 添加/更新分數 |
| `ZRANGE key start stop [WITHSCORES]` | ❌ | 按分數範圍取得 |
| `ZREVRANGE key start stop [WITHSCORES]` | ❌ | 反向排序取得 |
| `ZRANGEBYSCORE key min max [WITHSCORES]` | ❌ | 按分數範圍 |
| `ZSCORE key member` | ❌ | 取得成員分數 |
| `ZRANK key member` | ❌ | 取得排名 |
| `ZREM key member [member...]` | ❌ | 移除成員 |
| `ZCARD key` | ❌ | 成員數量 |
| `ZCOUNT key min max` | ❌ | 分數範圍內成員數 |

### Key 管理

| Redis 功能 | db6 狀態 | 說明 |
|-----------|---------|------|
| `RENAME key newkey` | ❌ | 重新命名 |
| `RENAMENX key newkey` | ❌ | 不存在才重新命名 |
| `MOVE key db` | ❌ | 移動到其他 DB |
| `COPY key newkey [REPLACE]` | ❌ | 複製 key |
| `SORT key [BY pattern] [LIMIT offset count]` | ❌ | 排序（List/Set/ZSet） |
| `WAIT numslaves timeout` | ❌ | 複製等待 |

### 過期時間（TTL/PEXPIRE）

| Redis 功能 | db6 狀態 | 說明 |
|-----------|---------|------|
| `EXPIRE key seconds` | ❌ | 設定過期秒數 |
| `PEXPIRE key milliseconds` | ❌ | 毫秒精度過期 |
| `TTL key` | ❌ | 剩餘過期秒數 |
| `PTTL key` | ❌ | 毫秒精度剩餘過期 |
| `EXPIREAT key timestamp` | ❌ | 定時過期（Unix timestamp） |
| `PERSIST key` | ❌ | 移除過期設定 |

### HyperLogLog（基數估計）

| Redis 功能 | db6 狀態 | 說明 |
|-----------|---------|------|
| `PFADD key element [element...]` | ❌ | 添加元素 |
| `PFCOUNT key [key...]` | ❌ | 估計基數 |
| `PFMERGE destkey sourcekey [sourcekey...]` | ❌ | 合併 |

### Geospatial（地理空間）

| Redis 功能 | db6 狀態 | 說明 |
|-----------|---------|------|
| `GEOADD key longitude latitude member` | ❌ | 添加座標 |
| `GEOPOS key member [member...]` | ❌ | 取得座標 |
| `GEODIST key member1 member2 [unit]` | ❌ | 距離計算 |
| `GEORADIUS key longitude latitude radius unit` | ❌ | 半徑查詢 |
| `GEOHASH key member [member...]` | ❌ | geohash 字串 |

### Pub/Sub（發布訂閱）

| Redis 功能 | db6 狀態 | 說明 |
|-----------|---------|------|
| `PUBLISH channel message` | ❌ | 發布訊息 |
| `SUBSCRIBE channel [channel...]` | ❌ | 訂閱頻道 |
| `PSUBSCRIBE pattern [pattern...]` | ❌ | 模式訂閱 |
| `UNSUBSCRIBE [channel [channel...]]` | ❌ | 取消訂閱 |

### Stream（資料流）

| Redis 功能 | db6 狀態 | 說明 |
|-----------|---------|------|
| `XADD key ID field string [field string...]` | ❌ | 添加項目 |
| `XRANGE key start end [COUNT n]` | ❌ | 範圍讀取 |
| `XREAD [COUNT n] [BLOCK ms] STREAMS key` | ❌ | 阻塞讀取 |
| `XLEN key` | ❌ | 流長度 |
| `XDEL key ID [ID...]` | ❌ | 刪除項目 |

### Transaction（事務）

| Redis 功能 | db6 狀態 | 說明 |
|-----------|---------|------|
| `WATCH key [key...]` | ❌ | 樂觀鎖監控 |
| `UNWATCH` | ❌ | 取消監控 |
| `MULTI` | ✅ | 交易開始（db6 有 `begin_transaction`） |
| `EXEC` | ✅ | 執行交易（db6 有 `commit_transaction`） |
| `DISCARD` | ⚠️ | 交易回滾（db6 有 `rollback_transaction`） |

### Scripting（Lua 腳本）

| Redis 功能 | db6 狀態 | 說明 |
|-----------|---------|------|
| `EVAL script numkeys key [key...] arg [arg...]` | ❌ | 執行 Lua 腳本 |
| `EVALSHA sha1 numkeys key [key...] arg [arg...]` | ❌ | 執行快取腳本 |
| `SCRIPT EXISTS sha1 [sha1...]` | ❌ | 腳本是否存在 |

### 管理指令

| Redis 功能 | db6 狀態 | 說明 |
|-----------|---------|------|
| `INFO [section]` | ⚠️ | 引擎 stats 可取得部分資訊 |
| `CONFIG GET parameter` | ❌ | 取得設定 |
| `CONFIG SET parameter value` | ❌ | 設定參數 |
| `CLIENT LIST` | ❌ | 客戶端清單 |
| `CLIENT KILL ip:port` | ❌ | 關閉客戶端 |
| `SLOWLOG subcommand [argument]` | ❌ | 慢查詢日誌 |
| `MONITOR` | ❌ | 即時監控 |

---

## 差異原因分析

### 1. 架構根本差異

Redis 是**資料結構伺服器**，每個 value 根據類型有不同的內部結構（sds、list、dict、ziplist、intset...），操作直接在 value 內部進行。

db6 是**儲存引擎**，value 是**不透明的 bytes**。所有結構都在 SQL 層或應用層解讀，KV 引擎只負責存取的穩定性和效能。

### 2. 效能考量

Redis 的 O(1) 操作（HSET、HGET、SADD...）需要在 value 內部維護額外索引。
db6 每次 `put` 都是完整覆寫，無法做到增量更新。

### 3. 交易模型

Redis 的 WATCH/MULTI/EXEC 是樂觀併發控制。
db6 的交易是悲觀鎖（write-ahead log + 頁級鎖），模型不同。

### 4. 叢集支援

Redis Cluster 有 hash slot 分散式設計。
db6 目前只有單機，無分散式規劃。

---

## 未來可能實作的方向（SQL 層模擬）

在 SQL 層可以部分模擬 Redis 功能（但效能較差）：

```sql
-- INCR 模拟（需要 atomic 操作支援）
UPDATE counter SET value = value + 1 WHERE key = 'mycounter';

-- Hash 模拟（JSON 存儲）
UPDATE user:1 SET profile = json_set(profile, '$.name', 'Alice');

-- Set 模拟
SELECT * FROM tags WHERE json_contains(set, 'urgent');

-- ZSet 模拟
SELECT * FROM leaderboard ORDER BY score DESC LIMIT 10;
```

但這些都是**應用層解決方案**，不是引擎原生支援，效能和功能完整性無法與 Redis 原生相比。