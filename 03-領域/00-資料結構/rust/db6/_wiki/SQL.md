# SQL（Structured Query Language，結構化查詢語言）

## 概述

SQL（Structured Query Language，結構化查詢語言）是用于管理關聯式資料庫的標準程式語言。SQL 最初在 1970 年代由 IBM 的 Donald D. Chamberlin 和 Raymond F. Boyce 開發，經過 ANSI 和 ISO 的標準化，成為處理關聯式資料庫的事实標準。

SQL 之所以重要，是因為它提供了一種宣告式（declarative）的資料處理方式：使用者描述「要什麼」（what），而不需要指定「如何取得」（how）。資料庫系統的查詢最佳化器會自動決定最有效的執行計畫。

## SQL 的歷史

### 1970 年代：起源

- **1970**：Edgar F. Codd 發表關聯式資料模型的論文，為 SQL 奠定理論基礎
- **1974**：IBM 開發 System R，首次使用 SEQUEL（SQL 的前身）
- **1979**：Oracle 推出第一個商業 SQL 資料庫

### 1980 年代：標準化

- **1986**：ANSI 發布 SQL-86（SQL1）
- **1989**：ISO 發布 SQL-89，增加了完整性約束

### 1990 年代：擴展

- **1992**：SQL-92（SQL2），增加了進階功能如交易控制、視圖、臨時表
- **1999**：SQL:1999，引入了正規表達式、遞迴查詢、觸發器

### 2000 年代：現代化

- **2003**：SQL:2003，引入了 XML 相關功能、窗口函數
- **2006**：SQL:2006，擴展了 XQuery 支援
- **2008**：SQL:2008，引入了 TRUNCATE、表空間
- **2011**：SQL:2011，增強了時序資料處理
- **2016-2023**：持續更新，包含 JSON、圖形資料等新功能

## SQL 的組成部分

SQL 通常分為幾個子語言：

### 1. DDL（Data Definition Language，資料定義語言）

用於定義和管理資料庫物件：

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE
);

ALTER TABLE users ADD COLUMN age INTEGER;

DROP TABLE users;
```

主要命令：
- **CREATE**：建立資料庫物件（表、索引、視圖等）
- **ALTER**：修改現有資料庫物件
- **DROP**：刪除資料庫物件
- **TRUNCATE**：清空表（快速刪除所有資料）

### 2. DML（Data Manipulation Language，資料操縱語言）

用於查詢和修改資料：

```sql
-- 查詢
SELECT name, email FROM users WHERE age > 18;

-- 插入
INSERT INTO users (name, email, age) VALUES ('張三', 'zhang@example.com', 25);

-- 更新
UPDATE users SET age = 26 WHERE id = 1;

-- 刪除
DELETE FROM users WHERE id = 1;
```

主要命令：
- **SELECT**：查詢資料
- **INSERT**：新增資料
- **UPDATE**：更新資料
- **DELETE**：刪除資料

### 3. DCL（Data Control Language，資料控制語言）

用於控制存取權限：

```sql
GRANT SELECT ON users TO public;
REVOKE DELETE ON users FROM admin;
```

主要命令：
- **GRANT**：授予權限
- **REVOKE**：撤銷權限

### 4. TCL（Transaction Control Language，交易控制語言）

用於管理交易：

```sql
BEGIN TRANSACTION;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;
```

主要命令：
- **BEGIN TRANSACTION**：開始交易
- **COMMIT**：提交交易
- **ROLLBACK**：回滾交易
- **SAVEPOINT**：設定儲存點

## 進階 SQL 功能

### 子查詢（Subquery）

```sql
SELECT name FROM users WHERE id IN (
    SELECT user_id FROM orders WHERE total > 1000
);
```

### JOIN（連接）

```sql
SELECT users.name, orders.total
FROM users
JOIN orders ON users.id = orders.user_id
WHERE orders.date > '2024-01-01';
```

JOIN 的類型：
- **INNER JOIN**：只返回匹配的記錄
- **LEFT JOIN**：返回左表所有記錄，無匹配時以 NULL 填充
- **RIGHT JOIN**：返回右表所有記錄
- **FULL OUTER JOIN**：返回兩個表的所有記錄
- **CROSS JOIN**：笛卡爾積

### 聚合函數（Aggregate Functions）

```sql
SELECT 
    category,
    COUNT(*) as count,
    AVG(price) as avg_price,
    SUM(quantity) as total_quantity
FROM products
GROUP BY category
HAVING COUNT(*) > 10;
```

常用聚合函數：
- **COUNT()**：計算數量
- **SUM()**：求和
- **AVG()**：平均值
- **MIN()**：最小值
- **MAX()**：最大值

### 窗口函數（Window Functions）

窗口函數在不需要 GROUP BY 的情況下進行聚合計算：

```sql
SELECT 
    name,
    department,
    salary,
    AVG(salary) OVER (PARTITION BY department) as dept_avg,
    RANK() OVER (ORDER BY salary DESC) as salary_rank
FROM employees;
```

常用窗口函數：
- **ROW_NUMBER()**：為每一行分配序號
- **RANK()**：計算排名（有間距）
- **DENSE_RANK()**：計算排名（無間距）
- **LEAD() / LAG()**：取得前一行/後一行的值

### 通用表表達式（CTE，Common Table Expression）

```sql
WITH RECURSIVE employee_hierarchy AS (
    SELECT id, name, manager_id, 1 as level
    FROM employees WHERE manager_id IS NULL
    UNION ALL
    SELECT e.id, e.name, e.manager_id, h.level + 1
    FROM employees e
    JOIN employee_hierarchy h ON e.manager_id = h.id
)
SELECT * FROM employee_hierarchy;
```

## SQL 的實作

不同資料庫對 SQL 的支援程度不同：

### 完全遵循 ANSI SQL 的資料庫

- **PostgreSQL**：被譽為最嚴格遵循 SQL 標準的開源資料庫
- **Firebird**：繼承自 Borland 的 InterBase

### 有自己的 SQL 方言

- **MySQL**：有 MySQL 特有的語法和功能
- **SQL Server**：使用 T-SQL，有獨特的擴展
- **Oracle**：使用 PL/SQL，有豐富的擴展

### SQLite

SQLlite 是一個嵌入式資料庫，支援大部分 ANSI SQL:92 的功能，但有一些限制：
- 沒有儲存過程
- 有限的觸發器支援
- 沒有窗口函數（直到版本 3.25.0）

## SQL 注入攻擊

SQL 注入是 Web 應用程式最常見的安全漏洞之一：

```java
// 不安全：直接拼接使用者輸入
String query = "SELECT * FROM users WHERE name = '" + userInput + "'";

// 安全：使用參數化查詢
PreparedStatement ps = connection.prepareStatement(
    "SELECT * FROM users WHERE name = ?"
);
ps.setString(1, userInput);
```

防範 SQL 注入的最佳實踐：
1. 始終使用參數化查詢
2. 使用 ORM 框架（如 Hibernate、Entity Framework）
3. 輸入驗證和淨化
4. 最小權限原則

## ORM 與 SQL

物件關聯對映（ORM）框架將物件導向語言與 SQL 橋接：

| ORM | 語言 | 範例 |
|-----|------|------|
| Hibernate | Java | session.createQuery("from User").list() |
| Entity Framework | C# | context.Users.Where(u => u.Name == name) |
| SQLAlchemy | Python | session.query(User).filter_by(name=name) |
| GORM | Go | db.Where("name = ?", name).Find(&users) |

## 在 db6 中的應用

db6 專案的 [SQL 層](../src/sql/) 移植自 sql6，提供 SQL parser、planner 和 executor。通過統一的 StorageEngine trait，db6 可以讓同一條 SQL 查詢在三個不同的儲存引擎（Memory、BTree、LSM）上執行。

SQL 層的核心元件：
- **Parser**：將 SQL 字串解析為語法樹
- **Planner**：將語法樹轉換為執行計畫
- **Executor**：根據執行計畫操作儲存引擎

詳細說明請參閱 [Query-planner.md](Query-planner.md)。

## 延伸閱讀

- Codd, E. F. (1970). A Relational Model of Data for Large Shared Data Banks. Communications of the ACM.
- Chamberlin, D. D., & Boyce, R. F. (1974). SEQUEL: A Structured English Query Language.
- Date, C. J. (2004). SQL and Relational Theory. O'Reilly Media.