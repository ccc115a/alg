# memory/ — 記憶體引擎模組

## 目錄結構

- `mod.rs` — 模組入口，匯出兩種引擎
- `hash.rs` — HashMemoryEngine：HashMap 實作，O(1) 查詢
- `btree.rs` — BTreeMemoryEngine：BTreeMap 實作，支援排序

## 選用指南

- 需要快速 KV 查詢，不需排序 → `HashMemoryEngine`
- 需要 SQL 功能 (ORDER BY、範圍查詢) → `BTreeMemoryEngine`
- 需要持久化與交易 → 請使用 `btree/engine.rs` 或 `lsm/engine.rs`

## 使用範例

```rust
use db6::engine::BTreeMemoryEngine;
use db6::engine::StorageEngine;

let mut engine = BTreeMemoryEngine::new();
engine.put(1, b"key", b"value").unwrap();
let val = engine.get(1, b"key").unwrap();
```

## 相關資源

- `engine/mod.md` — 儲存引擎架構總覽
- `engine/capability.md` — 能力標記系統
