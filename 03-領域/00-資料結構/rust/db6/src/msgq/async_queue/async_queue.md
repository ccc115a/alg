# msgq/async_queue/ — 非同步訊息佇列

## 概述

`async_queue` 模組經過 v4.11 重構後，從單一檔案拆分為 6 個子模組，各自負責不同的關注點。

## 模組結構

```
async_queue/
├── config.rs    — AsyncQueueConfig, RetryConfig, with_retry
├── queue.rs     — AsyncQueue 主體
├── metrics.rs   — QueueMetrics, QueueHealth, HealthStatus
├── stream.rs    — AsyncQueueStream (tokio Stream)
├── exactly.rs   — ExactlyOnceQueue (恰好一次傳遞)
└── facade.rs    — AsyncMsgq (工廠入口)
```

## AsyncQueue (queue.rs)

核心實現，使用 tokio 的 `Notify` 取代 busy-wait polling。

```rust
let queue = AsyncQueue::new("orders", engine.clone());
queue.enqueue(b"order data".to_vec()).await?;
let msg = queue.dequeue().await?;
queue.ack(&msg.id).await?;
```

## AsyncQueueConfig (config.rs)

```rust
let config = AsyncQueueConfig {
    poll_interval: Duration::from_millis(100),
    max_retries: 3,
    cleanup_interval: Some(Duration::from_secs(3600)),
};
```

`with_retry` 函數提供退避重試：

```rust
with_retry(|| some_fallible_op(), |n| Duration::from_millis(10 * (1 << n))).await?;
```

## QueueMetrics (metrics.rs)

```rust
pub struct QueueMetrics {
    pub enqueued: AtomicU64,
    pub dequeued: AtomicU64,
    pub acked: AtomicU64,
    pub nacked: AtomicU64,
    pub failed: AtomicU64,
}
```

## AsyncQueueStream (stream.rs)

實現 `tokio_stream::Stream` trait，允許消費者用 `while let` 語法消費訊息：

```rust
let mut stream = queue.stream();
while let Some(msg) = stream.next().await {
    process(msg).await;
}
```

## ExactlyOnceQueue (exactly.rs)

使用 **deduplication (去重)** 訊息 ID 來實現恰好一次傳遞：

```rust
let exactly = ExactlyOnceQueue::new("dedup-queue", engine.clone());
exactly.enqueue("order-123", b"data".to_vec()).await?;
// 第二次相同 ID 會被忽略
exactly.enqueue("order-123", b"data".to_vec()).await?;
```

## AsyncMsgq (facade.rs)

工廠入口，同時管理多個佇列：

```rust
let msgq = AsyncMsgq::new(engine);
let q1 = msgq.queue("q1");
let q2 = msgq.queue("q2");
```

## 相關資源

- `msgq/sync_queue.md` — 同步版本
- `msgq/common/common.md` — 共用元件 (ConcurrencyLimiter)
