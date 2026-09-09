# Redis

## 概述

Redis（REmote DIctionary Server）是一個開源的記憶體鍵值資料庫，由 Salvatore Sanfilippo 在 2009 年創建。Redis 以其高性能、豐富的資料結構支援和靈活的持久化選項著稱，廣泛用於快取、工作階段儲存、訊息佇列、排行榜等場景。

## 歷史

- **2009**：Redis 首次發布，用於解決 LLOOGG 即時分析的需求
- **2010**：VMware 僱用 Salvatore 專注於 Redis 開發
- **2013**：Redis Labs 成立，繼續主導開發
- **2015**：Redis Cluster 發布
- **2018**：Redis 5.0 引入 Stream 資料結構
- **2022**：Redis 7.0 發布

## 核心特性

### 記憶體優先

Redis 的所有資料主要儲存在記憶體中，這使得它的讀寫延遲可以達到微秒級：

```
記憶體存取延遲： ~100 奈秒
SSD 讀取延遲：  ~100 微秒
網路存取延遲： ~1 毫秒
```

### 豐富的資料結構

Redis 不只是簡單的 KV 儲存，它支援多種高階資料結構：

| 資料結構 | 命令範例 | 說明 |
|----------|----------|------|
| String | `SET name "Tom"` | 簡單字串 |
| Hash | `HSET user:1 name "Tom" age 25` | 欄位-值對 |
| List | `LPUSH list a b c` | 雙向鏈結串列 |
| Set | `SADD tags "db" "redis"` | 無序集合 |
| Sorted Set | `ZADD leaderboard 100 "Tom"` | 带分數的有序集合 |
| Stream | `XADD stream * field value` | 日誌流 |
| Bitmap | `SETBIT bit 0 1` | 位圖 |
| HyperLogLog | `PFADD unique * item` | 基數估計 |

### TTL（生存時間）

Redis 支援為鍵設置過期時間：

```bash
SET cache "data" EX 3600    # 1 小時後自動刪除
EXPIRE cache 3600
TTL cache                    # 查詢剩餘時間
```

### 發布/訂閱

```bash
SUBSCRIBE channel
PUBLISH channel message
```

### 交易

Redis 的交易是原子的，但不像 SQL 那樣有隔離級別：

```bash
MULTI
SET key1 value1
SET key2 value2
INCR counter
EXEC
```

## 持久化

Redis 支援兩種持久化方式：

### RDB（Redis Database）

定時快照，整個資料庫的壓縮二進制檔案：

```bash
# 配置
save 900 1      # 900 秒內有 1 次寫入
save 300 10     # 300 秒內有 10 次寫入
save 60 10000   # 60 秒內有 10000 次寫入
```

優點：檔案小，適合備份
缺點：可能丟失上次快照後的資料

### AOF（Append Only File）

每次寫入操作追加到日誌：

```bash
appendonly yes
appendfsync everysec  # 每秒同步（預設）
# 或 appendfsync always (每次寫入同步，最安全但最慢)
# 或 appendfsync no (作業系統決定，最快但最不安全)
```

優點：更好的持久性
缺點：檔案較大，寫入效能略低

### 混合持久化（Redis 5.0+）

```bash
aof-use-rdb-preamble yes
```

開啟後，AOF 檔案以 RDB 格式開頭，後續增量用 AOF 格式。

## Redis Cluster

Redis Cluster 提供了分散式能力：

```
┌─────────────────────────────────────────────┐
│              Redis Cluster                   │
│                                              │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐     │
│  │ Master1 │  │ Master2 │  │ Master3 │     │
│  │ (Slot0) │  │ (Slot1) │  │ (Slot2) │     │
│  └────┬────┘  └────┬────┘  └────┬────┘     │
│       │            │            │           │
│  ┌────┴────┐  ┌────┴────┐  ┌────┴────┐     │
│  │ Slave1  │  │ Slave2  │  │ Slave3  │     │
│  └─────────┘  └─────────┘  └─────────┘     │
└─────────────────────────────────────────────┘
```

特點：
- **16384 個槽（slot）**：資料自動分散到 16384 個槽
- **自動分割**：每個 Master 處理一部分槽
- **副本複製**：每個 Master 可以有 N 個副本
- **自動容錯**：Master 故障時副本自動提升

## 記憶體管理

Redis 的記憶體使用優化：

### 記憶體回收

Redis 記憶體滿了後，會根據淘汰策略刪除鍵：

```bash
maxmemory-policy allkeys-lru
```

常見策略：
- `noeviction`：拒絕寫入（預設）
- `allkeys-lru`：刪除最近最少使用的鍵
- `allkeys-random`：隨機刪除
- `volatile-lru`：只刪除有 TTL 的鍵中 LRU 的
- `volatile-ttl`：刪除即將過期的鍵

### 記憶體碎片

Redis 使用 jemalloc 作為預設記憶體分配器，可以減少碎片。

## 典型應用場景

### 1. 快取

```python
def get_user(user_id):
    # 先查快取
    cache_key = f"user:{user_id}"
    cached = redis.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # 快取未命中，查詢資料庫
    user = db.query("SELECT * FROM users WHERE id = ?", user_id)
    
    # 寫入快取
    redis.setex(cache_key, 3600, json.dumps(user))
    return user
```

### 2. 工作階段儲存

```python
session = {
    "user_id": 123,
    "cart": [...],
    "preferences": {...}
}
redis.setex(f"session:{session_id}", 86400, json.dumps(session))
```

### 3. 計數器

```bash
INCR page_views:2024:01:15
INCR article:views:123
```

### 4. 排行榜

```bash
ZADD leaderboard 100 "Tom"
ZADD leaderboard 90 "Alice"
ZADD leaderboard 80 "Bob"

# 前三名
ZREVRANGE leaderboard 0 2 WITHSCORES
```

### 5. 訊息佇列

```bash
# 生產者
LPUSH queue "task:1"
LPUSH queue "task:2"

# 消費者
BRPOP queue 0  # 阻擋直到有新元素
```

### 6. 速率限制

```python
def rate_limit(user_id, max_requests=100, window=60):
    key = f"ratelimit:{user_id}"
    current = redis.get(key)
    
    if current and int(current) >= max_requests:
        return False  # 超過限制
    
    pipe = redis.pipeline()
    pipe.incr(key)
    pipe.expire(key, window)
    pipe.execute()
    return True
```

## 與 db6 的比較

| 特性 | Redis | db6 |
|------|-------|-----|
| 持久化 | 可選（RDB/AOF） | 必需 |
| 資料結構 | 豐富（String, Hash, List, Set, ZSet, Stream） | KV 簡單 |
| 交易 | 不支援 SQL 等級的交易 | 有限支援 |
| 查詢語言 | 指令 | SQL |
| 分散式 | Redis Cluster | 未來規劃 |
| 記憶體 | 完全在記憶體 | 可選磁碟 |

db6 的 MemoryEngine 與 Redis 有些相似，都是基於記憶體的 KV 儲存。但 Redis 有更豐富的資料結構和分散式支援。

## 延伸閱讀

- Redis Documentation: https://redis.io/docs/
- Redis GitHub: https://github.com/redis/redis
- "Redis in Action" by Josiah L. Carlson