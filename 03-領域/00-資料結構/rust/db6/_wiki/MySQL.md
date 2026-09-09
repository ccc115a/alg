# MySQL

## 概述

MySQL 是全球最流行的開源關聯式資料庫管理系統之一，屬於 Oracle 公司。MySQL 以其穩定性、易用性和效能著稱，是 LAMP（Linux、Apache、MySQL、PHP/Python/Perl）堆疊的核心元件，驅動了世界上大量的網站和應用程式。

## 歷史

- **1995**：MySQL AB 成立，發布 MySQL 1.0
- **2000**：MySQL 3.23，引入 InnoDB
- **2003**：MySQL 4.0，支援子查詢
- **2005**：MySQL 5.0，支援儲存過程、觸發器、視圖
- **2008**：Sun Microsystems 收購 MySQL AB
- **2010**：Oracle 收購 Sun Microsystems，MySQL 進入 Oracle 時代
- **2010**：MariaDB 分叉（由 MySQL 創始人發起）
- **2015**：MySQL 5.7，效能提升
- **2018**：MySQL 8.0，支援 Window Functions、CTE、JSON 增強

## 儲存引擎

MySQL 的架構支援多個儲存引擎，這是其最重要的特性之一：

### InnoDB

預設和最常用的引擎：
- **事務支援**：完整的 ACID 交易支援
- **行級鎖定**：並發效能優秀
- **MVCC**：非阻塞讀取
- **外鍵約束**：完整的參照完整性
- **自動崩潰恢復**：基於 redo log
- **B+Tree 索引**：預設使用聚集索引

```sql
CREATE TABLE users (
    id INT PRIMARY KEY,
    name VARCHAR(100)
) ENGINE=InnoDB;
```

### MyISAM

較舊的引擎，某些場景仍有使用：
- **表級鎖定**：寫入效能受限
- **無事務支援**
- **較小的記憶體佔用**
- **支援全文檢索**

```sql
CREATE TABLE logs (
    id INT PRIMARY KEY,
    message TEXT
) ENGINE=MyISAM;
```

### 其他引擎

| 引擎 | 說明 |
|------|------|
| Memory | 記憶體儲存，極速讀寫 |
| CSV | CSV 檔案格式 |
| Archive | 壓縮儲存，適合歸檔 |
| Blackhole | 垃圾桶，不用實際儲存 |

## InnoDB 的架構

```
┌────────────────────────────────────────────────────┐
│                   MySQL Server                      │
│  ┌──────────────────────────────────────────────┐  │
│  │            SQL Layer                          │  │
│  │  Parser → Rewriter → Optimizer → Executor     │  │
│  └──────────────────────────────────────────────┘  │
│                         │                           │
│  ┌──────────────────────▼──────────────────────┐  │
│  │         Storage Engine API                    │  │
│  └──────────────────────┬──────────────────────┘  │
└──────────────────────────┼──────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────┐
│                    InnoDB Engine                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │ Buffer Pool │  │  Redo Log   │  │  Undo Log   │   │
│  │  (記憶體)   │  │  (磁碟)    │  │  (記憶體)   │   │
│  └─────────────┘  └─────────────┘  └─────────────┘   │
│  ┌────────────────────────────────────────────────┐ │
│  │           Tablespace (磁碟)                    │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐    │ │
│  │  │ Tables   │  │  Indexes  │  │  Temp     │    │ │
│  │  │ (B+Tree) │  │ (B+Tree)  │  │ Tablespace│    │ │
│  │  └──────────┘  └──────────┘  └──────────┘    │ │
│  └────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

### Buffer Pool

InnoDB 的記憶體緩衝區，緩存資料頁和索引頁：

```sql
-- 查看緩衝池大小
SHOW VARIABLES LIKE 'innodb_buffer_pool_size';

-- 設置緩衝池大小
SET GLOBAL innodb_buffer_pool_size = 8589934592;  -- 8GB
```

### Doublewrite Buffer

防止部分寫入損壞：
1. 先寫入 doublewrite buffer
2. 再寫入實際的資料頁

### Redo Log

用於崩潰恢復的日誌：
- 記錄修改後的資料
- 事務提交時強制刷盤
- 恢復時重演未刷入資料頁的修改

## 索引結構

### 聚集索引

InnoDB 使用聚集索引組織表資料：
- 主鍵索引的葉節點包含完整的行資料
- 非主鍵查詢需要「回表」

```sql
CREATE TABLE orders (
    id INT PRIMARY KEY,          -- 聚集索引
    user_id INT,
    total DECIMAL(10,2),
    KEY idx_user (user_id)       -- 二級索引
);

-- 使用 idx_user 查詢
SELECT * FROM orders WHERE user_id = 1;
-- 先在 idx_user 中找到主鍵 id，再回表查詢完整行
```

### 二級索引

二級索引的葉節點儲存：
- 索引列的值
- 對應的主鍵值

## 交易隔離級別

| 隔離級別 | 說明 | 使用的鎖 |
|----------|------|----------|
| READ UNCOMMITTED | 讀取未提交的變更 | 無 |
| READ COMMITTED | 只讀取已提交的變更 | Record Lock |
| REPEATABLE READ | 同一交易中多次讀取結果相同（預設） | Gap Lock |
| SERIALIZABLE | 序列化，類似表鎖 | Next-Key Lock |

### REPEATABLE READ 與幻讀

InnoDB 在 REPEATABLE READ 模式下使用 Next-Key Lock 防止幻讀：

```sql
BEGIN;
SELECT * FROM orders WHERE user_id = 1 FOR UPDATE;
-- 鎖住 user_id = 1 的所有記錄 + 相鄰的 gap
```

## MVCC

InnoDB 使用 MVCC 實現非阻塞讀取：

- **Read View**：交易開始時建立的快照
- **隱藏列**：`DB_TRX_ID`（最後修改的交易）、`DB_ROLL_PTR`（指向 undo log 的指標）
- **undo log**：儲存記錄的歷史版本

## SQL 優化

### EXPLAIN

```sql
EXPLAIN SELECT * FROM users WHERE email = 'test@example.com';
+----+-------------+-------+------+---------------+------+---------+-------+------+-------------+
| id | select_type| table | type |   key        | rows | filtered| Extra |
+----+-------------+-------+------+---------------+------+---------+-------+-------------+
|  1 | SIMPLE     | users | ref  | idx_email    |    1 |   100.00|       |
+----+-------------+-------+------+---------------+------+---------+-------+-------------+
```

### 索引使用原則

- **最左前綴**：複合索引從左邊開始使用
- **覆蓋索引**：查詢的所有欄位都在索引中
- **避免函數**：WHERE YEAR(created_at) = 2024 會使索引失效

## 複製架構

MySQL 支援主從複製：

```
┌────────┐          ┌────────┐          ┌────────┐
│ Master │ ──────▶ │ Slave1 │          │ Slave2 │
│ (寫)   │  binlog │ (讀)   │          │ (讀)   │
└────────┘          └────────┘          └────────┘
```

複製類型：
- **SBR（Statement-Based Replication）**：複製 SQL 語句
- **RBR（Row-Based Replication）**：複製行的變更
- **GBR（Mixed-Based Replication）**：混合模式

## 在 db6 中的比較

| 特性 | MySQL (InnoDB) | db6 (BTreeEngine) |
|------|----------------|-------------------|
| 索引類型 | B+Tree + Hash | B-Tree |
| 交易隔離 | 完整 4 種 | 有限 |
| SQL 標準 | 完整 | 部分 |
| 規模 | 大型 | 中小型 |
| 複製 | 原生支援 | 未來規劃 |

## 延伸閱讀

- MySQL Documentation: https://dev.mysql.com/doc/refman/8.0/en/
- "High Performance MySQL" by Baron Schwartz et al.
- InnoDB Internals: https://github.com/jeremycole/innodb_diagrams