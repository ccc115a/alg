# planner/ — 查詢規劃器

## 目的

查詢規劃器 (query planner) 接收 Parser 產生的 AST，將其轉換為**執行計畫 (execution plan)**。執行計畫是一個或多個 `Plan` 節點組成的樹，Executor 根據這個計畫來實際操作資料。

## 設計

Planner 目前相對簡單，主要做兩件事：

1. **AST → Plan 轉換** — 將 Statement 轉為對應的 Plan
2. **引擎限制檢查** — 根據引擎類型判斷是否支援某些操作

## Plan 節點類型

| 節點 | 對應 SQL | 說明 |
|------|----------|------|
| `Scan` | SELECT | 掃描資料表 |
| `Join` | JOIN | 多表連接 |
| `Insert` | INSERT | 插入資料 |
| `Update` | UPDATE | 更新資料 |
| `Delete` | DELETE | 刪除資料 |
| `CreateTable` | CREATE TABLE | 建立表 |
| `CreateFtsTable` | CREATE VIRTUAL TABLE | 建立 FTS 表 |
| `DropTable` | DROP TABLE | 刪除表 |
| `Empty` | 無操作 | 不產生動作 |

## 引擎限制

LSM 引擎由於其高寫入吞吐量的設計取向，不支援 JOIN 操作：

```rust
fn plan_select(&self, s: &SelectStmt, engine_type: &str) -> Result<Plan> {
    if let Some(ref join) = s.joins.first() {
        if engine_type == "lsm" {
            return Err(Error::NotSupported("JOIN not supported with LSM engine"));
        }
    }
}
```

## 相關資源

- `planner/plan.rs` — Plan 節點定義
- `planner/constraints.rs` — 約束驗證 (stub)
- `executor/executor.rs` — Plan 的執行者
