# query/ — 高階查詢系統 (Db)

## 概覽

提供 Method Chaining (方法鏈) 風格的 Fluent API 查詢介面，使操作更接近程式語言表達式。

## 模組列表

| 檔案 | 說明 |
|------|------|
| `mod.rs` | Db 主結構：表管理、索引、CRUD、交易 |

## Db 使用流程

```rust
let mut db = Db::new("memory")?;

db.create_table("users", &["id", "name", "age"])?;
db.table("users").insert(json!({"id": 1, "name": "Alice"}))?;

let rows = db.table("users")
    .select(&["name"])
    .filter("age", ">", 18)
    .run()?;
```

## 核心功能

- **表管理** — create_table、table 映射、自動 table_id 分配
- **CRUD** — insert、select、update、delete (Method Chaining)
- **索引** — create_index (JSON path 索引)
- **交易** — begin_transaction、commit、rollback
- **JSON 查詢** — json_extract、json_set 等路徑操作

## 相關連結

- `query.md` — 查詢介面詳解
- `kv/README.md` — 底層 KvEngine
- `sql/README.md` — SQL 執行層
