# sql/ — SQL 子系統

## 三層架構

db6 的 SQL 子系統移植自 sql6，採用經典的三層設計：

```
SQL 字串 → Parser (解析) → Planner (規劃) → Executor (執行) → 結果
```

## 模組對應

| 目錄 | 功能 | 輸入 | 輸出 |
|------|------|------|------|
| `parser/` | SQL 詞法與語法解析 | SQL 字串 | AST (Statement) |
| `planner/` | 查詢規劃與最佳化 | AST | 執行計畫 |
| `executor/` | 執行 SQL | 執行計畫 | ResultSet |

## 資料流

```
"SELECT * FROM users WHERE id = 1"
        ↓ parser/lexer.rs (詞法分析)
[Token::Select, Token::Star, Token::From, ...]
        ↓ parser/parser.rs (語法分析)
Statement::Select(SelectStmt { ... })
        ↓ planner/planner.rs (規劃)
Plan { table, columns, filter, ... }
        ↓ executor/executor.rs (執行)
ResultSet { columns: [...], rows: [...], affected: 0 }
```

## 設計理念

SQL 子系統完全與儲存引擎解耦，透過 `StorageEngine` trait 與 `KvStore` trait 操作底層資料。

## 相關資源

- `sql/parser/lexer.md` — 詞法分析器
- `sql/parser/ast.md` — 抽象語法樹
- `sql/parser/parser.md` — 語法分析器
- `sql/planner/planner.md` — 查詢規劃器
- `sql/executor/executor.md` — SQL 執行器
