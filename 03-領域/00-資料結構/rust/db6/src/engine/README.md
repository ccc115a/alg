# engine/ — 儲存引擎層

## 概覽

engine 是 db6 的儲存引擎層，定義了統一的 `StorageEngine` trait，並提供多種實作。每個引擎共用相同的 KV 操作介面，可互換使用。

## 模組列表

| 模組 | 說明 | 實作型別 |
|------|------|---------|
| `mod.rs` | StorageEngine trait、EngineStats | 統一的抽象介面 |
| `capability.rs` | EngineCapability、CapabilityMap | 引擎能力查詢系統 |
| `memory/` | 記憶體引擎 | HashMemoryEngine、BTreeMemoryEngine |
| `btree/` | 磁碟 BTree 引擎 | BTreeEngine |
| `lsm/` | LSM-Tree 引擎 | LsmEngine |

## 設計原則

- **StorageEngine trait** — 所有引擎透過 `put`/`get`/`delete`/`scan` 四個核心方法操作
- **table_id** — 多表隔離透過 `table_id` 參數實現
- **dyn 相容性** — `open`/`open_memory` 使用 `where Self: Sized` 約束

## 相關連結

- `mod.md` — StorageEngine 抽象層詳解
- `capability.md` — 引擎能力查詢系統
- `memory/README.md` — 記憶體引擎
- `btree/README.md` — 磁碟 BTree 引擎
- `lsm/README.md` — LSM-Tree 引擎
