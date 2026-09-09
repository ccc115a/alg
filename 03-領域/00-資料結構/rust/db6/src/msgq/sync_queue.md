# msgq/sync_queue.md — 同步訊息佇列

## 佇列模型

SyncQueue 提供 **FIFO (先進先出)** 的訊息佇列支援，建構在底層 KV 儲存引擎之上：

```
KV 儲存結構 (table_id = hash("queue:{name}")):
├── QM:{msg_id} → SyncQueueMessage          // 訊息內容
├── QV:{vis_order} → msg_id                 // 可見性索引 (依可見時間排序)
├── QP:{priority}:{msg_id} → ""             // 優先級索引
└── meta → QueueMeta                        // 佇列中繼資料
```

## QueueConfig 設定

```rust
let config = QueueConfig {
    max_delivery_count: 3,      // 最大傳遞次數（超過進 DLQ）
    dlq_name: Some("dlq"),     // 死信佇列名稱
    message_ttl_secs: Some(86400), // 訊息 TTL
    priority_enabled: true,     // 啟用優先級
};
```

## 核心操作

| 方法    | 說明 |
|---------|------|
| `enqueue` | 將訊息加入佇列 |
| `dequeue` | 取得下一條可見訊息 |
| `ack` | 確認訊息已處理 |
| `nack` | 拒絕處理（重新可見） |
| `peek` | 查看訊息但不消費 |
| `release` | 主動釋放訊息（類似 Nack） |

## 可見性超時 (Visibility Timeout)

消費者 Dequeue 後，訊息進入「不可見」狀態。若在 `visibility_timeout` 毫秒內未 Ack，訊息自動變回可見。這是分散式系統中常用的 **At-least-once** 傳遞保證。

## 死信佇列 (DLQ)

當訊息傳遞次數超過 `max_delivery_count` 時，自動移至 DLQ：

```rust
queue.enqueue_dlq(broken_msg)?;
```

## 優先級支援

當 `priority_enabled = true` 時，Dequeue 優先傳回優先級較高的訊息（數字越小優先級越高）。

## 相關資源

- `msgq/message.md` — SyncQueueMessage
- `msgq/sync_pubsub.md` — 同步 Pub/Sub
- `msgq/async_queue/queue.md` — 非同步版本
