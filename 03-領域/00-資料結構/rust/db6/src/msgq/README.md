# msgq/ — 訊息佇列系統

## 概覽

基於 KV 儲存引擎的訊息佇列與發布/訂閱系統，支援同步與非同步兩種操作模式。

## 模組列表

| 模組/檔案 | 說明 |
|-----------|------|
| `mod.rs` | Msgq 入口，同步/非同步元件匯出 |
| `message.rs` | SyncQueueMessage 資料結構 |
| `error.rs` | MsgqError 型別 (thiserror) |
| `sync_queue.rs` | 同步訊息佇列 (FIFO + 優先級 + DLQ) |
| `sync_pubsub.rs` | 同步發布/訂閱 (Pattern matching) |
| `common/` | 共用元件 (ConcurrencyLimiter, GracefulShutdown) |
| `async_queue/` | 非同步佇列 (tokio Stream, ExactlyOnce, Metrics) |
| `async_pubsub.rs` | 非同步發布/訂閱 (broadcast + KV 持久化) |
| `sql/` | SQL 執行器 (AsyncSqlExecutor, SyncSqlExecutor) |

## 儲存結構

所有 msgq 資料儲存在 KV store 中，以 `queue:{name}` 或 `pubsub:{channel}` 格式的 table_id 隔離。

## 同步 vs 非同步

| 特性 | 同步 | 非同步 |
|------|------|--------|
| Queue | SyncQueue | AsyncQueue (tokio Notify/Stream) |
| Pub/Sub | SyncPubSub (輪詢) | AsyncPubSub (broadcast channel) |
| 執行器 | SyncSqlExecutor | AsyncSqlExecutor (tokio mpsc) |

## 相關連結

- `msgq.md` — 入口概述
- `message.md` — 訊息結構
- `error.md` — 錯誤型別
- `sync_queue.md` — 同步佇列
- `sync_pubsub.md` — 同步 Pub/Sub
- `common/common.md` — ConcurrencyLimiter、GracefulShutdown
- `async_queue/async_queue.md` — 非同步佇列
- `async_pubsub.md` — 非同步 Pub/Sub
- `sql/sql.md` — SQL 執行器
