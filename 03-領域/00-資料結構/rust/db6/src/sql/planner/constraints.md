# planner/constraints.rs — 約束驗證 (Stub)

## 背景

資料庫的**約束 (constraint)** 是對資料的規則限制，確保資料完整性：

- `NOT NULL` — 欄位不能為空
- `UNIQUE` — 欄位值必須唯一
- `PRIMARY KEY` — 主鍵，唯一且非空
- `FOREIGN KEY` — 外鍵，引用其他表的欄位
- `CHECK` — 自訂條件檢查

## 目前狀態

`constraints.rs` 目前是 stub，僅定義了 `TableConstraints` 結構，尚未實作完整的約束驗證邏輯。這是 db6 已知的待辦事項之一。

## 相關資源

- `planner/planner.md` — Planner 主體
- `parser/ast.rs` — ColumnDef 中的約束定義
