# capability.rs — 引擎能力系統

## 背景：為什麼需要能力標記？

在一個支援多種儲存引擎的資料庫中，不同引擎支援的功能不同。例如：

- HashMemoryEngine 不支援範圍掃描 (scan)，因為 HashMap 的鍵是無序的
- BTreeEngine 支援交易，但 HashMemoryEngine 不支援

傳統作法是在執行期檢查，但這會導致 runtime error。db6 採用 **編譯期能力檢查 (compile-time capability checking)**，利用 Rust 的 trait 系統在編譯期就防止錯誤用法。

## 實作原理

使用 **marker trait** — 沒有方法定義的 trait，只作為標記：

```rust
pub trait CanOrderBy: StorageEngine {}
```

任何實作 `CanOrderBy` 的型別代表它支援排序功能。函式可以這樣約束：

```rust
fn execute_query<E: StorageEngine + CanOrderBy>(engine: &mut E) { ... }
```

## 提供的標記

| Trait | 意義 |
|-------|------|
| `CanOrderBy` | 支援 ORDER BY（需要有序儲存） |
| `CanJoin` | 支援 JOIN 操作 |
| `CanFts` | 支援全文搜尋 |
| `CanTransaction` | 支援交易 (BEGIN/COMMIT/ROLLBACK) |
| `CanScan` | 支援範圍掃描 |
| `CanBatch` | 支援批量操作 |
| `CanGroupBy` | 支援 GROUP BY 與聚合函數 |

## impl_capabilities! 巨集

爲了簡化每個引擎的實作，提供了巨集：

```rust
impl_capabilities!(BTreeMemoryEngine, CanOrderBy, CanScan, CanGroupBy);
```

這會展開為多個 `impl Trait for Type {}` 區塊。

## 相關資源

- `engine/mod.rs` — StorageEngine trait 定義
- `sql/executor/executor.rs` — 使用能力約束的實際範例
