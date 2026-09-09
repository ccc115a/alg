# PostgreSQL

## 概述

PostgreSQL 是一個功能強大的開源物件關聯式資料庫系統，以其穩定性、資料完整性、擴展性和標準合規性著稱。PostgreSQL 通常被稱為「世界上最先進的開源資料庫」，在許多大型企業和組織中得到廣泛應用。

## 歷史

- **1977**：Ingres 專案啟動，POSTQUEL 查詢語言的祖先
- **1986**：POSTQUEL 改為 SQL，更名為 Postgres
- **1995**：Postgres95 開源，成為 PostgreSQL 的前身
- **1996**：PostgreSQL 6.0 發布
- **2000s**：MVCC、分割區表、觸發器等進階功能加入
- **2010s**：JSON 支援、邏輯複製、並行查詢
- **2020s**：向量搜尋（pgvector）、多型索引、JSONpath

## 核心特性

### 完整的 ACID 支援

PostgreSQL 提供完整的交易支援，預設使用 READ COMMITTED 隔離級別，可配置為：
- READ COMMITTED
- REPEATABLE READ（使用 SSI）
- SERIALIZABLE

### MVCC

PostgreSQL 使用 MVCC（Multi-Version Concurrency Control）實現非阻塞讀取：

```sql
-- 讀取不會封鎖寫入
BEGIN;
SELECT * FROM users WHERE id = 1;  -- 即使其他交易正在修改這筆記錄
COMMIT;
```

### MVCC 的原理

每筆記錄有多個版本：
- `xmin`：建立這筆記錄的交易 ID
- `xmax`：刪除這筆記錄的交易 ID
- `t_xmax`：刪除標記

讀取時根據交易的可見性規則選擇正確的版本。

### 儲存結構

```
┌─────────────────────────────────────────────┐
│             PostgreSQL Cluster              │
│  ┌───────────────────────────────────────┐  │
│  │              Database 1                │  │
│  │  ┌─────────────────────────────────┐  │  │
│  │  │         Table (heap)             │  │  │
│  │  │  ┌─────────────────────────────┐│  │  │
│  │  │  │       B-Tree Index          ││  │  │
│  │  │  │    (on table's columns)     ││  │  │
│  │  │  └─────────────────────────────┘│  │  │
│  │  └─────────────────────────────────┘  │  │
│  └───────────────────────────────────────┘  │
│  ┌───────────────────────────────────────┐  │
│  │              Database 2                │  │
│  └───────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

### 索引類型

PostgreSQL 支援多種索引類型：

```sql
-- B-Tree（預設）
CREATE INDEX idx1 ON users(email);

-- Hash
CREATE INDEX idx2 ON users USING hash(email);

-- GIN（Generalized Inverted Index）- 適合 JSON、陣列、全文檢索
CREATE INDEX idx3 ON documents USING gin(content);

-- GiST（Generalized Search Tree）- 幾何資料、範圍
CREATE INDEX idx4 ON ranges USING gist(value);

-- SP-GiST - 分割空間
-- BRIN - 區塊範圍索引，適合時序資料
```

### JSON 支援

PostgreSQL 對 JSON 的支援非常完善：

```sql
-- JSON 欄位
CREATE TABLE api_logs (
    id SERIAL PRIMARY KEY,
    data JSONB
);

-- JSON 查詢
SELECT * FROM api_logs
WHERE data->>'action' = 'login';

-- JSON 路徑
SELECT * FROM api_logs
WHERE data @? '$.user.id ? (@ > 1000)';
```

### 分割區表

```sql
CREATE TABLE orders (
    id SERIAL,
    created_at DATE,
    total DECIMAL(10,2)
) PARTITION BY RANGE (created_at);

CREATE TABLE orders_2024 PARTITION OF orders
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

CREATE TABLE orders_2025 PARTITION OF orders
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
```

### 擴展生態

PostgreSQL 的擴展生態非常豐富：

| 擴展 | 功能 |
|------|------|
| PostGIS | 地理資訊系統 |
| pgvector | 向量搜尋（AI/ML） |
| TimescaleDB | 時序資料庫 |
| Citus | 分散式查詢 |
| pg_partman | 自動分割區管理 |
| pg_repack | 線上重建索引 |

## 查詢處理流程

PostgreSQL 的查詢處理分為以下階段：

```
SQL Query
    ↓
Parser (語法樹)
    ↓
Analyzer (語義分析)
    ↓
Rewriter (規則重寫)
    ↓
Planner (生成執行計畫)
    ↓
Executor (執行計畫)
    ↓
結果
```

### Planner 的優化

Planner 會評估多種執行計畫，選擇成本最低的：

```sql
EXPLAIN SELECT * FROM users WHERE age > 18;

Result:
Seq Scan on users  (cost=0.00..35.50 rows=1000 width=100)
  Filter: (age > 18)
```

可以使用 `EXPLAIN ANALYZE` 查看實際執行時間。

## MVCC 與 VACUUM

因為 MVCC 的設計，刪除的資料不會立即回收。VACUUM 負責清理：

```sql
-- 手動執行 VACUUM
VACUUM users;

-- 分析（更新統計資訊）
ANALYZE users;

-- 完整 vacuum（可回收更多空間但較慢）
VACUUM FULL users;
```

PostgreSQL 12+ 支援「並行 VACUUM」。

## 複製與高可用

### 流複製（Streaming Replication）

主庫產生的 WAL 日誌持續傳送到備庫：

```
Primary ──WAL──▶ Standby1
         └──WAL──▶ Standby2
```

### 邏輯複製

基於 WAL 的邏輯解碼，支援：
- 部分表複製
- 不同 PostgreSQL 版本間複製
- 訂閱-發布模式

```sql
-- 發布端
CREATE PUBLICATION mypub FOR TABLE users, orders;

-- 訂閱端
CREATE SUBSCRIPTION mysub CONNECTION 'host=primary' PUBLICATION mypub;
```

## 在 db6 中的比較

| 特性 | PostgreSQL | db6 (BTreeEngine) |
|------|------------|-------------------|
| 儲存引擎 | 堆疊 + B-Tree | 純 B-Tree |
| 索引類型 | 多種 | 僅 B-Tree |
| MVCC | 完全支援 | 有限支援 |
| SQL 標準 | 完全遵循 | 部分支援 |
| 擴展性 | 強大 | 受限 |
| 規模 | EB 級 | 中小型 |

db6 可以視為 PostgreSQL 的簡化版本，專注於 KV 儲存和簡單的 SQL 查詢。

## 延伸閱讀

- PostgreSQL Documentation: https://www.postgresql.org/docs/
- "The Internals of PostgreSQL" - https://www.postgresql.org/docs/current/internal.html
- "PostgreSQL 14 internals" - https://pginternals.org/