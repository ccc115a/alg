# parser/ast.rs — 抽象語法樹

## 理論基礎：抽象語法樹

**AST (Abstract Syntax Tree，抽象語法樹)** 是程式碼的樹狀結構表示。與 parse tree (具體語法樹) 不同，AST 省略了不影響語意的細節（如分號、括號），保留關鍵結構資訊。

### 為什麼需要 AST？

1. **多重用途** — AST 可以同時用於語意分析、最佳化、程式碼生成
2. **簡化處理** — 樹狀結構比平面 token 串更容易遍歷與轉換
3. **語意清晰** — 每個節點對應一個語法結構，而非單一字元

## 核心節點

### Statement (語句)

頂層節點，代表一個完整的 SQL 語句：

```rust
pub enum Statement {
    Select(SelectStmt),
    Insert(InsertStmt),
    Update(UpdateStmt),
    Delete(DeleteStmt),
    CreateTable(CreateTableStmt),
    Begin,
    Commit,
    Rollback,
    // ... 20+ 種語句
}
```

### Expr (運算式)

代表有值的表達式，遞迴結構：

```rust
pub enum Expr {
    LitInt(i64),
    LitStr(String),
    Column(String),
    BinOp { left: Box<Expr>, op: BinOp, right: Box<Expr> },
    // ...
}
```

例如 `age + 1 > 18` 會被解析為：
```
BinOp {
    left: BinOp { left: Column("age"), op: Plus, right: LitInt(1) },
    op: Gt,
    right: LitInt(18)
}
```

### SelectStmt

SELECT 查詢的完整結構：

```rust
pub struct SelectStmt {
    pub columns: Vec<SelectItem>,   // SELECT 後的欄位
    pub from: Option<FromItem>,     // FROM 子句
    pub where_: Option<Expr>,       // WHERE 條件
    pub group_by: Option<Vec<Expr>>, // GROUP BY
    pub having: Option<Expr>,       // HAVING 條件
    pub order_by: Vec<OrderItem>,   // ORDER BY
    pub limit: Option<u64>,         // LIMIT
    pub offset: Option<u64>,        // OFFSET
}
```

## Visitor 模式

AST 的遍歷通常使用 visitor 模式。db6 的 planner 就是一個 visitor，它走訪 AST 節點並產生執行計畫。

## 相關資源

- `parser/lexer.md` — token 來源
- `parser/parser.md` — token → AST 的轉換
- `planner/planner.md` — AST → 執行計畫
