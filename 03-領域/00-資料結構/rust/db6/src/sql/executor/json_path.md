# executor/json_path.rs — JSON Path 評估

## 背景：JSON 在資料庫中的角色

現代資料庫通常支援 JSON 資料類型。db6 的 KV 儲存模型將值儲存為 `Vec<u8>`，但如果值使用 JSON 格式，就可以透過 JSON Path 語法查詢內部結構。

## JSON Path 語法

db6 支援簡化的 JSON Path 語法，以 `@` 表示當前文件：

```
@.field           → 存取頂層欄位
@.nested.field    → 存取巢狀欄位
@.field > 18      → 比較運算
@.field LIKE 'A%' → 模糊匹配
@.field IN (1,2)  → 列表成員
@.field IS NULL   → 空值判斷
```

## 實作核心

### json_get

根據 Path 一層層深入 JSON 物件：

```rust
pub fn json_get(json: &serde_json::Value, path: &[String]) -> serde_json::Value {
    let mut current = json.clone();
    for key in path {
        if let serde_json::Value::Object(map) = &current {
            if let Some(v) = map.get(key) { current = v.clone(); }
            else { return serde_json::Value::Null; }
        }
    }
    current
}
```

### json_path_compare

取得 JSON 值後與表達式比較，支援 `=`, `!=`, `<`, `>`, `<=`, `>=` 等運算子。

## 效能考量

每次 WHERE 過濾都需要 `serde_json::from_str()` 解析 JSON，在大量資料時可能成為瓶頸。

## 相關資源

- `executor/executor.md` — 在 Executor 中使用 JSON Path
- `parser/ast.rs` — JSON Path 表達式節點
