# query/mod.rs — 高階查詢介面 (Db)

## 設計理念：Fluent API

Db 提供一種 **Method Chaining (方法鏈)** 風格的 API，讓使用者可以串聯方法呼叫來建構查詢。這種風格比直接寫 SQL 更接近程式語言的表達方式。

## 與底層引擎的關係

Db 建立在 `KvEngine` 之上，自動管理 `table_id` 的分配與表名映射。

## 表管理

```rust
let mut db = Db::new("memory").unwrap();

// Method chaining 風格
let rows = db.table("users")
    .select(&["name", "email"])
    .filter("age", ">", 18)
    .run()
    .unwrap();

// 或寫入
db.table("users")
    .insert(json!({"name": "Alice", "age": 30}))
    .unwrap();
```

## 索引支援

支援對 JSON 欄位建立索引，加速查詢：

```rust
db.create_index("users", "$.age").unwrap();
```

## 交易支援

```rust
db.begin_transaction().unwrap();
// ... 多個操作 ...
db.commit_transaction().unwrap();
```

## 限制

- 僅支援 Memory 引擎 (Hash/BTree) 的部分操作
- 部分功能（如 GROUP BY）在 Hash engine 上不支援

## 相關資源

- `kv/mod.rs` — KvEngine 底層
- `sql/executor/executor.md` — SQL 執行器
