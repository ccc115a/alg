# parser/lexer.rs — 詞法分析器

## 理論基礎：詞法分析

**詞法分析 (lexical analysis)** 是編譯過程的第一階段，將原始字串轉換為一連串的 **token (詞彙單元)**。每個 token 代表一個最小的語法單位，如關鍵字、識別符、運算子、字面值等。

### 常見作法

經典的詞法分析器使用**有限狀態機 (finite state machine, FSM)**。lexer 從第一個字元開始讀取，根據當前字元決定下一步狀態：

```
空白 → 跳過
字母 → 讀取完整識別符或關鍵字
數字 → 讀取完整數字
' → 讀取字串字面值
符號 → 單一字元 token
```

## Token 類型

db6 lexer 支援 60 多種 token，分類如下：

- **關鍵字** — SELECT, FROM, WHERE, INSERT, CREATE, JOIN 等
- **識別符** — 表名、欄位名 (Ident(String))
- **字面值** — 整數 (LitInt)、浮點數 (LitFloat)、字串 (LitStr)、NULL
- **運算子** — =, !=, <, >, +, -, *, /, || 等
- **標點** — (, ), ,, ;, .

### FTS5 相關 Token

支援全文搜尋的 `MATCH`、`VIRTUAL` 關鍵字。

## 實作特點

關鍵字比對使用 `HashMap` 預先建立對照表，查詢時間 O(1)：

```rust
fn keyword(s: &str) -> Option<Token> {
    // 轉大寫後比對
    match s.to_uppercase().as_str() {
        "SELECT" => Some(Token::Select),
        // ... 60+ keywords
        _ => None,  // 回傳 None 表示這是識別符
    }
}
```

識別符與關鍵字的區分：如果是關鍵字回傳對應 Token，否則回傳 `Token::Ident(s)`。

## 相關資源

- `parser/ast.rs` — token 被組裝為 AST
- `parser/parser.rs` — 語法分析器使用 token
