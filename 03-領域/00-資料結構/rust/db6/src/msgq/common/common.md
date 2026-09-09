# msgq/common/ — 共用元件

## 設計目的

`msgq/common` 模組提供非同步程式設計中常用的基礎元件，在多個 msgq 元件間共享。

## 模組結構

```
common/
├── mod.rs        — 匯出
├── limiter.rs    — ConcurrencyLimiter (並發限制)
└── shutdown.rs   — GracefulShutdown (優雅關閉)
```

## ConcurrencyLimiter

限制系統中同時執行的非同步任務數量，防止資源耗盡。

```rust
let limiter = ConcurrencyLimiter::new(16); // 最多 16 個並發任務
let permit = limiter.acquire().await;      // 取得許可（可能等待）
// ... 執行工作 ...
drop(permit);                              // 自動歸還許可
```

內部使用 tokio::sync::Semaphore 實現。

## GracefulShutdown

提供一個可觸發、可監聽的優雅關閉機制。

```rust
let shutdown = GracefulShutdown::new();
let handle = shutdown.handle();

// 工作執行緒
tokio::spawn(async move {
    loop {
        tokio::select! {
            _ = handle.cancelled() => break,  // 收到關閉訊號
            _ = do_work() => continue,
        }
    }
});

// 觸發關閉
shutdown.shutdown().await;
```

內部使用 tokio::sync::Notify 實現。

## 實際應用

- `AsyncSqlExecutor` — 限制 SQL 執行緒數量
- `AsyncQueue` — 限制訊息處理並發數
- `AsyncPubSub` — 限制發布/訂閱並發數

## 參考設計

靈感來自 mini-redis 專案的 `Connection` 與 `Shutdown` 模式。Tokio 官方建議使用 `watch` 或 `Notify` 來實現優雅關閉，本實作選擇 `Notify` 以求輕量。

## 相關資源

- `msgq/async_queue/queue.md` — ConcurrencyLimiter 在佇列中的應用
- `msgq/sql/executor.md` — 並發控制
