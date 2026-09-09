# ACID（交易的四大特性）

## 概述

ACID 是資料庫交易（Transaction）的四個關鍵特性的縮寫：
- **A**tomicity（原子性）
- **C**onsistency（一一致性）
- **I**solation（隔離性）
- **D**urability（持久性）

這些特性確保了資料庫交易的可靠性，是關聯式資料庫能夠安全處理並發操作的基礎。Ted Codd 在其關聯式模型中將交易支援列為關聯式資料庫的 12 條規則之一。

## 原子性（Atomicity）

原子性確保交易是一個不可分割的執行單位：交易中的所有操作要么全部執行，要么全部不執行。

### 現實比喻

想像從 ATM 轉帳：
1. 從帳戶 A 扣除 1000 元
2. 向帳戶 B 添加 1000 元

如果第一步成功但第二步失敗（系統崩潰），原子性確保整個交易被回滾，帳戶 A 不會無故減少 1000 元。

### 實作機制

原子性通常通過以下機制實現：

**Undo Log（回滾日誌）**：
- 記錄每次修改前的狀態
- 交易失敗時，根據 Undo Log 恢復原狀態

**Shadow Paging**：
- 修改前先拷貝頁面
- 修改在拷貝上進行
- 提交後替換原頁面

```sql
BEGIN TRANSACTION;

UPDATE accounts SET balance = balance - 1000 WHERE id = 1;
-- 如果這裡系統崩潰，原子性確保回滾

UPDATE accounts SET balance = balance + 1000 WHERE id = 2;

COMMIT;  -- 或者 ROLLBACK;
```

## 一致性（Consistency）

一致性確保交易執行後，資料庫始終處於一個有效的狀態。

### 約束的作用

資料庫約束是確保一致性的主要機制：

```sql
CREATE TABLE accounts (
    id INTEGER PRIMARY KEY,
    balance DECIMAL(10,2) CHECK (balance >= 0),  -- 餘額非負約束
    user_id INTEGER REFERENCES users(id)          -- 外鍵約束
);
```

### 一致性的層次

1. **語意一致**：應用程式定義的業務規則（如餘額不能為負）
2. **結構一致**：資料庫結構的有效性（如主鍵唯一、外鍵有效）
3. **參照一致**：跨表引用的一致性（如訂單引用的客戶必須存在）

### 原子性與一致性的區別

- **原子性**：交易的執行特性（要么全做，要么全不做）
- **一致性**：交易的結果特性（必須達到有效的資料庫狀態）

一個交易可能是原子的（要么全做，要么全不做），但如果業務規則被破壞（如餘額變成負數），它仍然是不一致的。

## 隔離性（Isolation）

隔離性確保並發執行的交易相互隔離，互不干擾。隔離性通過並發控制機制實現。

### 問題場景

在並發環境下，不正確的隔離會導致以下問題：

**Dirty Read（髒讀）**：
```
交易 A：讀取帳戶 X，餘額為 100
交易 B：修改帳戶 X，餘額改為 50（尚未提交）
交易 A：讀取帳戶 X，餘額為 50（髒讀）
交易 B：回滾，帳戶 X 恢復為 100
交易 A：以為帳戶 X 是 50，但實際是 100
```

**Non-repeatable Read（不可重複讀）**：
```
交易 A：讀取帳戶 X，餘額為 100
交易 B：修改帳戶 X，餘額改為 50 並提交
交易 A：再次讀取帳戶 X，餘額為 50（與第一次不同）
```

**Phantom Read（幻讀）**：
```
交易 A：SELECT COUNT(*) FROM users，結果為 100
交易 B：INSERT INTO users ...（新增一筆）
交易 A：SELECT COUNT(*) FROM users，結果為 101
```

### SQL 標準的隔離級別

| 隔離級別 | Dirty Read | Non-repeatable Read | Phantom Read |
|----------|------------|---------------------|--------------|
| READ UNCOMMITTED | 可能 | 可能 | 可能 |
| READ COMMITTED | 不可能 | 可能 | 可能 |
| REPEATABLE READ | 不可能 | 不可能 | 可能 |
| SERIALIZABLE | 不可能 | 不可能 | 不可能 |

### 實作機制

**鎖（Locking）**：
- **共享鎖（S Lock）**：讀取時加鎖，多個交易可以同時持有
- **互斥鎖（X Lock）**：寫入時加鎖，排他性

**MVCC（多版本並發控制）**：
- 每次修改產生新版本，不覆蓋舊版本
- 讀取時選擇適當的版本
- 大多數現代資料庫（PostgreSQL、MySQL InnoDB）使用 MVCC

## 持久性（Durability）

持久性確保一旦交易提交，其所做的修改將永久保存在資料庫中，即使系統崩潰也不會丟失。

### 實作機制

**Write-Ahead Log（WAL，提前寫入日誌）**：
1. 修改資料前，先將操作記錄寫入日誌
2. 日誌必須成功寫入磁碟後，才能修改資料頁
3. 系統崩潰後，根據日誌恢復

```rust
// WAL 的典型流程
fn put(key: &[u8], value: &[u8]) {
    // 1. 先寫 WAL
    wal.append((key, value));
    wal.sync();  // 確保刷到磁碟

    // 2. 然後修改記憶體
    memtable.insert(key.to_vec(), value.to_vec());
}
```

**資料頁刷新策略**：
- **Checkpoints**：定期將記憶體中的修改刷到磁碟
- **系統崩潰恢復**：重演日誌中的操作

### 持久性與效能的權衡

持久性越強，效能越低：
- **同步寫入**：每次提交都等待資料寫入磁碟，最安全但最慢
- **非同步寫入**：提交後後台寫入，可能丟失少量資料
- **電池備援**：UPS 可以保護記憶體資料

## ACID 在不同資料庫中的實作

### PostgreSQL

- **完整 ACID**：嚴格遵循 ACID 特性
- **MVCC**：使用 SSI（Serializable Snapshot Isolation）
- **WAL**：強大的日誌系統
- **預設隔離級別**：READ COMMITTED

### MySQL (InnoDB)

- **完整 ACID**：支援
- **MVCC**：使用 Redo Log 和 Undo Log
- **預設隔離級別**：REPEATABLE READ（比標準的 READ COMMITTED更嚴格）

### SQLite

- **ACID**：通過 WAL 模式實現
- **預設模式**：DELETE journal mode，較弱
- **建議模式**：WAL mode，支援並發讀

### NoSQL 資料庫

很多 NoSQL 資料庫只提供最終一致性：
- **Cassandra**：可調一致性，可以選擇犧牲一致性換取效能
- **DynamoDB**：最終一致性，預設
- **MongoDB**：有限交易支援（直到 4.0 版本才支援多重文件交易）

## 在 db6 中的 ACID

db6 的 [BTreeEngine](../src/engine/btree/) 支援完整的交易機制：

```rust
pub trait StorageEngine: Send + Sync {
    fn begin_transaction(&mut self) -> Result<()>;
    fn commit_transaction(&mut self) -> Result<()>;
    fn rollback_transaction(&mut self) -> Result<()>;
    fn has_transaction(&self) -> bool;
}
```

- **MemoryEngine**：不支援交易（交易操作是 no-op）
- **BTreeEngine**：支援完整交易
- **LsmEngine**：有限交易支援

## 延伸閱讀

- Gray, J., & Reuter, A. (1993). Transaction Processing: Concepts and Techniques. Morgan Kaufmann.
- Bernstein, P. A., & Newcomer, E. (2009). Principles of Transaction Processing (2nd Edition). Morgan Kaufmann.