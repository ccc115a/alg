# Query Planner（查詢規劃器）

## 概述

查詢規劃器（Query Planner，也稱為 Query Optimizer）是 SQL 資料庫系統的核心元件之一。它負責將 SQL 語句轉換為高效的執行計畫。在關聯式資料庫中，同一個 SQL 查詢可能有多種執行方式，查詢規劃器的任務是選擇成本最低的執行方式。

## 為什麼需要查詢規劃器？

SQL 是一種宣告式語言，使用者描述「要什麼」而不是「如何取得」：

```sql
-- 使用者只描述需求
SELECT u.name, o.total
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE u.age > 18
ORDER BY o.total DESC;
```

這個查詢有多種執行方式：
1. 先掃描 users 表，用 age > 18 過濾，再與 orders JOIN
2. 先 JOIN，再過濾年齡條件，最後排序
3. 先建立臨時索引，進行 NESTED LOOP JOIN
4. 使用 HASH JOIN 替代

查詢規劃器需要評估並選擇最優的執行方式。

## 查詢處理流程

```
SQL Query
    │
    ▼
┌───────────────┐
│     Parser     │  語法分析 → 語法樹
└───────┬───────┘
        │
        ▼
┌───────────────┐
│   Analyzer    │  語義分析 → 語法樹（含型別檢查）
└───────┬───────┘
        │
        ▼
┌───────────────┐
│    Rewriter   │  規則重寫（如視圖展開）
└───────┬───────┘
        │
        ▼
┌───────────────┐
│    Planner    │  生成執行計畫（最優化）
└───────┬───────┘
        │
        ▼
┌───────────────┐
│   Executor    │  執行計畫
└───────────────┘
```

## 代價模型

查詢規劃器使用「代價模型」來評估執行計畫的成本：

```python
# 代價估算公式（簡化版）
cost = 
    cpu_cost * num_rows_processed +
    io_cost * pages_read +
    memory_cost * buffers_used
```

### 統計資訊

代價模型依賴於準確的統計資訊：

| 統計資訊 | 說明 |
|----------|------|
| 表行數 | 資料量大小 |
| 欄位基數 | 不同值的數量 |
| 直方圖 | 值的分佈 |
| NULL 比例 | 空值的比例 |
| 頁面數 | 資料佔用的儲存頁 |

```sql
-- 查看統計資訊
ANALYZE users;  -- 更新統計資訊

-- PostgreSQL
SELECT * FROM pg_stat_user_tables WHERE relname = 'users';
SELECT * FROM pg_stats WHERE tablename = 'users';
```

## 常見的執行計畫運算元

### 掃描（Scan）

**全表掃描（Sequential Scan）**：
```
┌─────────────────────────┐
│   Seq Scan on orders     │
│   Filter: total > 1000   │
└─────────────────────────┘
```

**索引掃描（Index Scan）**：
```
┌─────────────────────────┐
│   Index Scan on users    │
│   Index: idx_users_email │
└─────────────────────────┘
```

**索引僅掃描（Index Only Scan）**：
```
┌─────────────────────────────┐
│   Index Only Scan on users   │
│   Index: idx_users_email     │
└─────────────────────────────┘
```

### 連接（Join）

**巢狀迴圈連接（Nested Loop Join）**：

適用於小表或已有索引的情況：

```
for row_a in table_a:
    for row_b in table_b:
        if row_a.id == row_b.user_id:
            emit row_a + row_b
```

**雜湊連接（Hash Join）**：

適用於大表的等值連接：

```
# 建立階段
hash_table = {}
for row_a in table_a:
    key = row_a.user_id
    hash_table[key].append(row_a)

# 探測階段
for row_b in table_b:
    key = row_b.user_id
    for row_a in hash_table.get(key, []):
        emit row_a + row_b
```

**排序合併連接（Sort-Merge Join）**：

適用於已排序或有索引的輸入：

```
table_a = sort_by_key(table_a)
table_b = sort_by_key(table_b)

a_cursor = table_a.first()
b_cursor = table_b.first()

while a_cursor and b_cursor:
    if a_cursor.key < b_cursor.key:
        a_cursor.next()
    elif a_cursor.key > b_cursor.key:
        b_cursor.next()
    else:
        emit a_cursor.row + b_cursor.row
        a_cursor.next()
        b_cursor.next()
```

### 聚合（Aggregate）

**Hash Aggregate**：
```
┌──────────────────────────────┐
│    Hash Aggregate            │
│    Group Key: department     │
│    -> Hash Left Join         │
└──────────────────────────────┘
```

**Sort Aggregate**：
```
┌──────────────────────────────┐
│    Sort                      │
│    Sort Key: department      │
│    -> Hash Aggregate         │
└──────────────────────────────┘
```

## EXPLAIN 分析

### PostgreSQL

```sql
EXPLAIN SELECT * FROM users WHERE age > 18;

Result:
                               QUERY PLAN
─────────────────────────────────────────────────────────────
Seq Scan on users  (cost=0.00..35.50 rows=1000 width=100)
  Filter: (age > 18)
```

- `cost=0.00..35.50`：起始代價..總代價
- `rows=1000`：估計返回行數
- `width=100`：每行估計位元組數

```sql
EXPLAIN ANALYZE SELECT * FROM users WHERE age > 18;

-- 顯示實際執行時間和計劃
```

### MySQL

```sql
EXPLAIN SELECT * FROM users WHERE age > 18;

+----+-------------+-------+------+---------------+------+---------+------+----------+-------------+
| id | select_type| table | type |   key        | rows | filtered|extra |
+----+-------------+-------+------+---------------+------+---------+------+----------+-------------+
|  1 | SIMPLE     | users | ALL  | NULL         | 1000 |    10.00|Using |
|    |            |       |      |              |      |         |where |
+----+-------------+-------+------+---------------+------+---------+------+----------+-------------+
```

### SQLite

```sql
EXPLAIN QUERY PLAN SELECT * FROM users WHERE age > 18;

Result:
SCAN TABLE users USING COVERING INDEX idx_users_age
```

## 最佳化策略

### 啟發式規則

早期的查詢最佳化器使用簡單的啟發式規則：
1. 尽早過濾（Early filtering）
2. 避免交叉連接
3. 優先使用索引

### 代價基準優化

現代查詢最佳化器使用代價基準優化：
1. 列舉可能的執行計畫
2. 估算每個計畫的成本
3. 選擇成本最低的計畫

### 語法改寫

查詢可以被改寫為更高效的形式：

```sql
-- 原始
SELECT * FROM a, b WHERE a.id = b.id AND b.value > 100

-- 改寫後（將過濾條件提前）
SELECT * FROM (SELECT * FROM b WHERE value > 100) AS b_filtered
JOIN a ON a.id = b_filtered.id
```

## 在 db6 中的 Planner

db6 的 [SQL 層](../src/sql/) 包含查詢規劃功能：

```rust
pub struct Planner {
    // 儲存統計資訊
    stats: HashMap<u32, TableStats>,
}

impl Planner {
    pub fn plan(&self, query: &SQLStatement) -> Result<Plan> {
        // 1. 解析 SQL
        let ast = parse(query)?;
        
        // 2. 生成邏輯計畫
        let logical = self.logical_plan(ast)?;
        
        // 3. 成本估算
        let cost = self.estimate_cost(&logical)?;
        
        // 4. 生成執行計畫
        self.physical_plan(logical, cost)
    }
}
```

db6 的 planner 目前支援：
- SELECT 語句
- 簡單的 WHERE 條件
- JOIN（通過 Nested Loop）
- ORDER BY

未來規劃：
- 代價模型完善
- 更多 JOIN 類型（HASH JOIN、MERGE JOIN）
- 統計資訊收集

## 延伸閱讀

- "Database System Concepts" by Silberschatz, Korth, Sudarshan
- "Architecture of a Database System" - https://db.cs.berkeley.edu/papers/fntdb07-architecture.pdf
- PostgreSQL Query Planner: https://www.postgresql.org/docs/current//planner-optimizer.html