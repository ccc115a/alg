# Transaction（資料庫交易）

## 概述

資料庫交易（Transaction）是一組原子性的資料庫操作，這些操作要么全部成功執行，要么全部不執行。交易是實現資料一致性和完整性的基礎機制，廣泛應用於金融轉帳、庫存管理、訂單處理等需要確保資料正確性的場景。

## ACID 特性

交易必須滿足 ACID 四大特性：

- **Atomicity（原子性）**：交易是不可分割的執行單位
- **Consistency（一致性）**：交易執行後，資料庫必須處於一致狀態
- **Isolation（隔離性）**：並發交易的執行互不干擾
- **Durability（持久性）**：交易完成後，結果永久保存

詳細說明請參閱 [ACID.md](ACID.md)。

## 交易的語法

### SQL 標準語法

```sql
-- 開始交易
BEGIN TRANSACTION;

-- 或者
BEGIN;

-- 或者（Implicit transaction）
START TRANSACTION;

-- 執行操作
UPDATE accounts SET balance = balance - 1000 WHERE id = 1;
UPDATE accounts SET balance = balance + 1000 WHERE id = 2;

-- 提交
COMMIT;

-- 或回滾
ROLLBACK;
```

### Savepoint（儲存點）

```sql
BEGIN;
INSERT INTO orders (product_id, quantity) VALUES (1, 10);

SAVEPOINT sp1;
INSERT INTO orders (product_id, quantity) VALUES (2, 20);

-- 假設此時發現第一筆訂單有問題，回滾到儲存點
ROLLBACK TO SAVEPOINT sp1;

-- 繼續處理
INSERT INTO orders (product_id, quantity) VALUES (3, 30);

COMMIT;  -- 只會提交第三筆
```

## 並發控制

### 鎖（Locking）

**共享鎖（S Lock）**：
```sql
-- 讀取時加共享鎖
SELECT * FROM accounts WHERE id = 1 LOCK IN SHARE MODE;
```

**排他鎖（X Lock）**：
```sql
-- 寫入時加排他鎖
SELECT * FROM accounts WHERE id = 1 FOR UPDATE;
```

**鎖的相容矩陣**：

|  | S Lock | X Lock |
|--|--------|--------|
| S Lock | ✓ | ✗ |
| X Lock | ✗ | ✗ |

### 悲觀鎖 vs 樂觀鎖

**悲觀鎖（Pessimistic Locking）**：
- 假設衝突經常發生
- 在讀取時就加鎖
- 適合寫入密集場景

```sql
BEGIN;
SELECT * FROM accounts WHERE id = 1 FOR UPDATE;
-- 處理業務邏輯
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
COMMIT;
```

**樂觀鎖（Optimistic Locking）**：
- 假設衝突較少
- 在提交時才檢查衝突
- 適合讀取密集場景

```sql
-- 讀取時不鎖定
SELECT id, balance, version FROM accounts WHERE id = 1;

-- 更新時檢查 version
UPDATE accounts
SET balance = balance - 100, version = version + 1
WHERE id = 1 AND version = :old_version;
-- 如果 version 已改變，則更新 0 行，需要重試
```

### MVCC（Multi-Version Concurrency Control）

MVCC 是一種不使用鎖的並發控制機制：

```sql
-- Session A
BEGIN;
SELECT balance FROM accounts WHERE id = 1;  -- 讀到 balance=1000

-- Session B（在 Session A 事務中）
BEGIN;
UPDATE accounts SET balance = 800 WHERE id = 1;
COMMIT;

-- Session A 繼續（REPEATABLE READ 隔離級別下）
SELECT balance FROM accounts WHERE id = 1;  -- 仍讀到 1000
-- 因為 Session A 開始時的快照仍然有效
```

## 交易的實現機制

### 日誌系統

**Write-Ahead Log (WAL)**：
1. 修改資料前，先寫日誌
2. 日誌必須刷到磁碟
3. 然後才修改資料頁

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   修改記憶體   │ ──▶ │   寫 WAL     │ ──▶ │   修改完成   │
└─────────────┘     └─────────────┘     └─────────────┘
                          │
                          ▼
                    ┌───────────┐
                    │ 刷到磁碟   │
                    └───────────┘
```

**Undo Log**（用於回滾）：
```
| Before Image | After Image | Transaction ID |
|--------------|-------------|----------------|
| balance=1000 | balance=900 | 42             |
```

### 兩階段提交（Two-Phase Commit）

用於分散式交易的協定：

```
Phase 1: Prepare
┌─────────┐         ┌─────────┐         ┌─────────┐
│ Coordinator │ ──▶ │ Node A │         │
│             │ ──▶ │ Node B │         │
└─────────┘         └─────────┘         └─────────┘
                    
Phase 2: Commit
┌─────────┐         ┌─────────┐         ┌─────────┐
│ Coordinator │ ◀── │ Node A │ OK       │
│             │ ◀── │ Node B │ OK       │
│             │ ──▶ │ Node A │ COMMIT   │
│             │ ──▶ │ Node B │ COMMIT   │
└─────────┘         └─────────┘         └─────────┘
```

## 交易隔離級別

| 隔離級別 | Dirty Read | Non-repeatable Read | Phantom Read |
|----------|------------|---------------------|--------------|
| READ UNCOMMITTED | ✓ | ✓ | ✓ |
| READ COMMITTED | ✗ | ✓ | ✓ |
| REPEATABLE READ | ✗ | ✗ | ✓ |
| SERIALIZABLE | ✗ | ✗ | ✗ |

### PostgreSQL 的實現

PostgreSQL 使用 SSI（SERIALIZABLE SNAPSHOT ISOLATION），是 SERIALIZABLE 隔離級別的實作，比標準的鎖實現效能更好。

### MySQL (InnoDB) 的實現

MySQL InnoDB 使用：
- **REPEATABLE READ**：預設隔離級別
- **Next-Key Lock**：防止幻讀
- **Gap Lock**：鎖定範圍

## 在 db6 中的實現

db6 的 StorageEngine trait 定義了交易相關的方法：

```rust
pub trait StorageEngine: Send + Sync {
    fn begin_transaction(&mut self) -> Result<()>;
    fn commit_transaction(&mut self) -> Result<()>;
    fn rollback_transaction(&mut self) -> Result<()>;
    fn has_transaction(&self) -> bool;
}
```

各引擎的實現：

| 引擎 | 交易支援 |
|------|----------|
| MemoryEngine | 無（操作是 no-op） |
| BTreeEngine | 完整（Write-Ahead Log） |
| LsmEngine | 有限（單層次） |

## 交易的常見問題

### 死結（Deadlock）

```sql
-- Session A
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;  -- 鎖住 id=1
UPDATE orders SET status = 'paid' WHERE id = 1;              -- 嘗試鎖住 id=1 (在 orders 表)

-- Session B（並發執行）
BEGIN;
UPDATE orders SET status = 'paid' WHERE id = 1;  -- 鎖住 id=1 (在 orders 表)
UPDATE accounts SET balance = balance - 100 WHERE id = 1;  -- 嘗試鎖住 id=1 (在 accounts 表)
-- 死結！
```

**解決方案**：總是以相同順序訪問資源。

### 長交易

長時間執行的事務會：
- 持有過多的鎖
- 阻礙其他並發交易
- 佔用過多記憶體

**建議**：保持交易簡短，及時提交或回滾。

## 分散式交易

在分散式環境中，交易變得更複雜。

### XA 交易

X/Open XA 標準定義了分散式交易的介面：

```c
// 開始分散式交易
xid = xa_open("oracle_db", ...);
xa_begin(xid);

// 在多個資料庫執行操作
xa_commit(xid);  // 或 xa_rollback(xid);
```

### Saga 模式

Saga 是一種不使用兩階段提交的分散式交易模式：

```
┌──────┐  ┌──────┐  ┌──────┐
│ step1 │─▶│ step2 │─▶│ step3 │
└──┬───┘  └──┬───┘  └──┬───┘
   │         │         │
   ▼         ▼         ▼
comp1     comp2     comp3 (補償操作)
```

補償操作用於在失敗時回滾已執行的步驟。

## 延伸閱讀

- Gray, J., & Reuter, A. (1993). Transaction Processing: Concepts and Techniques. Morgan Kaufmann.
- Bernstein, P. A., & Newcomer, E. (2009). Principles of Transaction Processing (2nd Edition). Morgan Kaufmann.