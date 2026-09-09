# sql/ — SQL 子系統

## 概覽

SQL 子系統包含解析器 (Parser)、規劃器 (Planner) 與執行器 (Executor) 三個階段，將 SQL 字串轉換為資料庫操作。

## 模組列表

| 模組 | 說明 | 主要型別 |
|------|------|---------|
| `parser/` | SQL 解析 | Lexer → Token → Parser → AST |
| `planner/` | 查詢規劃 | Planner → PlanNode (SQL → 執行計劃) |
| `executor/` | 執行引擎 | Executor (Engine + SQL → ResultSet) |

## 處理管線

```
SQL 字串 → Parser → AST → Planner → PlanNode → Executor → ResultSet
```

## parser/

將 SQL 文字解析為抽象語法樹 (AST)：

| 檔案 | 說明 |
|------|------|
| `lexer.rs` | 詞法分析器：Token 定義 |
| `ast.rs` | 語法樹節點：Statement, Select, Insert, CreateTable 等 |
| `parser.rs` | 語法分析器：SQL → Statement 遞迴下降解析 |

支援的語法：SELECT (JOIN/GROUP BY/ORDER BY/LIMIT)、INSERT、UPDATE、DELETE、CREATE TABLE、BEGIN/COMMIT/ROLLBACK、CREATE INDEX。

## planner/

將 AST 轉換為可執行的計劃：

| 檔案 | 說明 |
|------|------|
| `planner.rs` | 規劃器：AST → PlanNode 轉換，檢查表/欄位存在性 |
| `plan.rs` | 執行計劃節點定義 |
| `constraints.rs` | 約束檢查 (NOT NULL、UNIQUE、CHECK) |

規劃層負責語意檢查、約束驗證、最佳化 (如謂詞下推)。

## executor/

實際執行查詢計劃：

| 檔案 | 說明 |
|------|------|
| `executor.rs` | 核心執行器，遍歷 PlanNode |
| `json_path.rs` | JSON 路徑運算 (JSON_EXTract、JSON_SET 等) |
| `transaction.rs` | 交易管理 (BEGIN/COMMIT/ROLLBACK) |

## 相關連結

- `sql.md` — SQL 架構概述
- `parser/lexer.md` — 詞法分析
- `parser/ast.md` — 語法樹節點
- `parser/parser.md` — 語法分析
- `planner/planner.md` — 規劃器
- `planner/plan.md` — 執行計劃
- `planner/constraints.md` — 約束檢查
- `executor/executor.md` — 執行器
- `executor/json_path.md` — JSON 路徑
- `executor/transaction.md` — 交易管理
- `engine/README.md` — 底層儲存引擎
