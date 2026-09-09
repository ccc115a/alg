# main.rs — 互動式 SQL REPL

## 什麼是 REPL？

REPL 是 Read-Eval-Print-Loop 的縮寫，一種互動式命令列環境。使用者輸入一行指令，系統立即執行並顯示結果，然後等待下一行輸入。這是資料庫領域常見的操作介面，類似 MySQL 的 `mysql>` prompt 或 PostgreSQL 的 `psql`。

## 引擎切換機制

db6 REPL 支援執行期間動態切換儲存引擎：

```
db6> .engine btree
Switched to btree engine
```

背後的運作原理是透過 `create_engine()` 工廠函式 (factory function)，根據使用者指定的名稱建立對應的引擎實例。由於所有引擎都實作 `StorageEngine` trait，因此可以透過**特徵物件 (trait object)** `Box<dyn StorageEngine>` 統一管理。

支援的引擎類型：

| 名稱 | 實際型別 | 特性 |
|------|---------|------|
| `memory-hash` | HashMemoryEngine | 快速 KV，不支援 ORDER BY |
| `memory-btree` | BTreeMemoryEngine | 支援 SQL 排序 |
| `btree` | BTreeEngine | 磁碟持久化，交易 |
| `lsm` | LsmEngine | 高寫入吞吐量 |

## 點命令 (Dot Commands)

以 `.` 開頭的特殊指令，非 SQL 語法：

- `.engine` — 檢視或切換引擎
- `.read <file>` — 從檔案讀取並執行 SQL
- `.help` — 顯示說明
- `.quit` / `.exit` — 離開

## SQL 執行流程

使用者輸入 SQL → `Executor::execute()` → Parser 解析 → Planner 規劃 → Executor 執行 → 回傳 `ResultSet`

## 相關資源

- `lib.rs` — crate 入口
- `sql/executor/executor.rs` — SQL 執行器
- `engine/mod.rs` — 儲存引擎系統
