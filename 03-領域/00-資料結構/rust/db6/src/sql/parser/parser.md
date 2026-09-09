# parser/parser.rs — 語法分析器

## 理論基礎：遞迴下降解析

**遞迴下降解析 (recursive descent parsing)** 是一種手寫的 top-down 語法分析技術。每個語法規則對應一個函式，函式之間互相遞迴呼叫：

```
parse_select() → parse_from() → parse_where() → ...
```

### 優點

- 實作直觀，每個規則對應一個函式
- 錯誤訊息容易控制
- 支援自訂擴展（如 FTS 的 MATCH 子句）

### 缺點

- 需要手寫，無法自動產生
- 對於複雜語法（如運算子優先級）需要額外處理

## 運算子優先級

db6 parser 透過函式呼叫順序實現優先級：

```
parse_expr()       → 最低優先級 (OR)
  parse_and_expr() → AND
    parse_cmp_expr() → 比較運算子 (=, <, >)
      parse_add_expr() → +, -
        parse_mul_expr() → *, /
          parse_primary() → 最高優先級 (常數、識別符)
```

例如 `1 + 2 * 3` 會被正確解析為 `1 + (2 * 3)`。

## 支援的 SQL 語法

- 基本 CRUD (SELECT/INSERT/UPDATE/DELETE)
- 交易 (BEGIN/COMMIT/ROLLBACK)
- 索引 (CREATE/DROP INDEX)
- JOIN (INNER/LEFT/RIGHT/CROSS)
- GROUP BY / HAVING / ORDER BY / LIMIT
- FTS (CREATE VIRTUAL TABLE, MATCH)
- 子查詢 (Subquery)

## 語法錯誤處理

parser 在遇到無法匹配的 token 時回傳 `Err`，內含字串描述幫助除錯。

## 相關資源

- `parser/lexer.md` — 提供 token 串
- `parser/ast.md` — 輸出 AST
- `planner/planner.md` — 消費 AST
