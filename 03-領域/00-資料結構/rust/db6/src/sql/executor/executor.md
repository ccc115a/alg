# executor/executor.rs — SQL 執行器

## 功能概述

Executor 是 SQL 子系統的核心，負責實際執行 Planner 產生的 Plan，或直接解析並執行 SQL 字串。

## 執行流程

```
Executor::execute(sql_string)
    → parse(sql_string)           // Parser: String → Statement
    → Planner::plan(statement)    // Planner: Statement → Plan
    → self.execute_plan(plan)     // 執行 Plan → ResultSet
```

## 關鍵實作

### 資料完整性檢查

insert 時透過 `check_key_matches` 確保 Schema 定義與實際資料一致。

### GROUP BY / 聚合

透過 `apply_group_by()` 實作分組與聚合函數：

| 函數 | 實作方式 |
|------|---------|
| COUNT | 計算群組行數 |
| SUM | 浮點數加總 |
| AVG | SUM / COUNT |
| MIN | 遍歷取最小值 |
| MAX | 遍歷取最大值 |

### WHERE 過濾

使用 `eval_expr()` 評估 WHERE 條件，支援：
- 一般比較 (`=`, `<`, `>`, `LIKE`, `IN`)
- JSON Path 查詢 (`@.field > value`)

### JSON Path 支援

值如果儲存為 JSON 字串，可以透過 `@.field` 語法訪問內部欄位：

```sql
SELECT * FROM users WHERE @.age > 18
```

Executor 使用 `serde_json` 解析 JSON 值，根據 Path 取出對應欄位進行比較。

## ResultSet

```rust
pub struct ResultSet {
    pub columns: Vec<String>,   // 欄位名
    pub rows: Vec<Vec<String>>, // 資料行
    pub affected: u64,          // 受影響行數
}
```

## 相關資源

- `executor/json_path.md` — JSON Path 評估
- `executor/transaction.md` — 交易支援
- `planner/plan.md` — Plan 節點定義
