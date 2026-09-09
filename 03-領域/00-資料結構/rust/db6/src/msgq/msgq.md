# msgq/mod.rs — 訊息佇列系統入口

## 概述

msgq (Message Queue) 模組是 db6 的訊息佇列與發布/訂閱系統，建構在底層 KV 儲存引擎之上。支援同步與非同步兩種操作模式。

## 模組結構

```
msgq/
├── common/          — 共用元件 (ConcurrencyLimiter, GracefulShutdown)
├── error.rs         — 錯誤型別 (使用 thiserror)
├── message.rs       — SyncQueueMessage 定義
├── sync_queue.rs    — 同步佇列
├── sync_pubsub.rs   — 同步 Pub/Sub
├── async_queue/     — 非同步佇列 (含 config, metrics, queue, stream, exactly)
├── async_pubsub.rs  — 非同步 Pub/Sub
└── sql/             — SQL 執行器 (Async/Sync)
```

## 設計理念

1. **雙模式** — 同步與非同步 API 共享底層資料模型
2. **KV 為基礎** — 使用 `KvEngine` 實現持久化
3. **Tokio 原生** — 非同步版本使用 tokio channel、notify

## 主要元件

| 元件 | 同步 | 非同步 |
|------|------|--------|
| Queue | SyncQueue | AsyncQueue (tokio) |
| Pub/Sub | SyncPubSub | AsyncPubSub (broadcast) |
| SQL | SyncSqlExecutor | AsyncSqlExecutor (tokio) |

## Msgq 入口

提供統一的 `Msgq` 結構，類似工廠模式：

```rust
let msgq = Msgq::new("memory").unwrap();
let queue = msgq.queue("myqueue");        // SyncQueue
let async_q = msgq.async_queue("myqueue"); // AsyncQueue
```

## 相關資源

- `msgq/message.md` — 訊息結構
- `msgq/error.md` — 錯誤處理
- `msgq/common/limiter.md` — 並發限制
- `msgq/common/shutdown.md` — 優雅關閉
