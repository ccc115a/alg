# executor/transaction.rs — 交易支援 (Stub)

## 背景：資料庫交易

**交易 (transaction)** 是一組不可分割的操作序列，具有 ACID 特性：

- **Atomicity (原子性)** — 全部成功或全部失敗
- **Consistency (一致性)** — 保持資料完整性
- **Isolation (隔離性)** — 併發交易互不干擾
- **Durability (持久性)** — 已提交的交易永久保存

## 目前狀態

`transaction.rs` 目前是 stub，僅定義了 `Transaction` 結構，`commit()` 和 `rollback()` 方法使用 `todo!()` 等待實作。

真正的交易支援在引擎層 (`BTreeEngine` 的 `begin_transaction` / `commit_transaction` / `rollback_transaction`)，SQL 層的交易指令 (`BEGIN` / `COMMIT` / `ROLLBACK`) 目前直接委派給引擎處理。

## 相關資源

- `engine/btree/engine.md` — BTree 引擎的交易實作
- `engine/lsm/engine.md` — LSM 引擎的交易實作
- `executor/executor.md` — SQL 執行器
