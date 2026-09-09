# planner/plan.rs — 執行計畫節點

## 設計概念

Plan 是 Planner 的輸出、Executor 的輸入。每個 Plan 節點代表一個資料操作步驟。

## Plan 列舉

```rust
pub enum Plan {
    Scan(ScanPlan),       // 掃描資料
    Join(JoinPlan),       // 多表連接
    Insert(InsertPlan),   // 插入
    Update(UpdatePlan),   // 更新
    Delete(DeletePlan),   // 刪除
    CreateTable(...),     // 建立表
    CreateFtsTable(...),  // FTS 表
    DropTable(...),       // 刪除表
    Empty,                // 無操作
}
```

## 重要節點詳解

### ScanPlan

最常用的計畫節點，代表一次資料掃描：

```rust
pub struct ScanPlan {
    pub table: String,
    pub filter: Option<Expr>,       // WHERE 條件
    pub order_by: Vec<OrderItem>,    // ORDER BY
    pub limit: Option<i64>,          // LIMIT
    pub is_fts: bool,                // 是否為 FTS 查詢
    pub fts_query: Option<String>,   // FTS 查詢字串
}
```

### JoinPlan

多表連接：

```rust
pub struct JoinPlan {
    pub left: Box<Plan>,
    pub right: Box<Plan>,
    pub kind: String,         // INNER, LEFT, RIGHT, CROSS
    pub condition: Option<Expr>,
}
```

使用 `Box<Plan>` 實現遞迴結構，左右子節點各自代表一張表的掃描計畫。

## 相關資源

- `planner/planner.md` — 產生 Plan
- `executor/executor.md` — 消費 Plan
