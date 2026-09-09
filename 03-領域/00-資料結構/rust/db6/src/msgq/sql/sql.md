# msgq/sql/ — SQL 執行器

## 設計目的

`sql` 子模組將 SQL 執行整合到訊息佇列系統中，支援同步 (`SyncSqlExecutor`) 與非同步 (`AsyncSqlExecutor`) 兩種執行模式。

## SqlJob 範本

```rust
pub struct SqlJob {
    pub id: String,
    pub sql: String,
    pub params: Vec<String>,
    pub scheduled_at: Option<u64>,
}
```

## JobResult 與 ResultStore

```rust
pub struct JobResult {
    pub id: String,
    pub success: bool,
    pub result: Option<ResultSet>,
    pub error: Option<String>,
    pub executed_at: u64,
    pub duration_ms: u64,
}

pub struct ResultStore {
    store: HashMap<String, JobResult>,
    limit: usize,
}
```

## SyncSqlExecutor

同步執行 SQL 作業：

```rust
let mut executor = SyncSqlExecutor::new(engine.clone(), None, None);
executor.submit(SqlJob {
    id: "job1".into(),
    sql: "SELECT * FROM users".into(),
    params: vec![],
    scheduled_at: None,
}).unwrap();
```

## AsyncSqlExecutor

非同步版本，支援並發限制與優雅關閉：

```rust
let executor = AsyncSqlExecutor::new(
    engine,
    ConcurrencyLimiter::new(4),     // 最多 4 個並發
    GracefulShutdown::new(),
);

executor.submit(SqlJob {
    id: "job1".into(),
    sql: "INSERT INTO users VALUES ($1, $2)".into(),
    params: vec!["Alice".into(), "30".into()],
    scheduled_at: None,
}).await.unwrap();
```

## 排程執行

當 `scheduled_at` 設為未來時間時，作業會等待到指定時間才執行：

```rust
SqlJob {
    scheduled_at: Some(now + 5000),  // 5 秒後執行
    ..
}
```

## 內部實作

### SyncSqlExecutor

- 使用 `VecDeque` 作為作業佇列
- 在 `process_pending()` 方法中逐一處理
- 無並發限制或優雅關閉

### AsyncSqlExecutor

- 使用 `tokio::sync::mpsc` channel 傳遞作業
- 使用 `ConcurrencyLimiter` 限制並發
- 使用 `GracefulShutdown` 響應關閉訊號
- 在 `run_worker()` 內部迴圈中等待作業並執行

## 相關資源

- `msgq/common/limiter.md` — 並發限制
- `msgq/common/shutdown.md` — 優雅關閉
- `sql/sql.md` — SQL 執行器概述
