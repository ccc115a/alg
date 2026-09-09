# msgq/async_pubsub.md — 非同步發布/訂閱

## 雙層架構

AsyncPubSub 使用 **雙層架構**：

1. **內層** — SyncPubSub (持久化層)，將訊息寫入 KV store
2. **外層** — tokio broadcast channel (即時傳遞層)

這樣既有 KV store 的持久化能力，又有 tokio 的即時性。

## 架構圖

```
Publish("news", data)
  │
  ├── SyncPubSub.publish() → KV store (持久化)
  │
  └── broadcast::Sender.send(data) → 所有訂閱者 (即時)
```

## 訂閱者管理

```rust
let sub = pubsub.subscribe("news").await.unwrap();
while let Ok(msg) = sub.recv().await {
    println!("收到: {}", msg.payload_str().unwrap());
}
```

## 模式訂閱 (Pattern Subscription)

```rust
let pattern_sub = pubsub.psubscribe("news.*").await.unwrap();
```

使用 `TopicMatcher` 結構比對頻道名稱與萬用字元模式。

## AsyncPatternSubscriber

```rust
pub struct AsyncPatternSubscriber {
    pub pattern: String,
    pub receiver: broadcast::Receiver<AsyncPubSubMessage>,
}
```

## 與 SyncPubSub 的比較

- SyncPubSub 使用 in-memory Vec 儲存訂閱者列表，消費者在同一個同步上下文中輪詢
- AsyncPubSub 使用 tokio broadcast channel，消費者通過非同步接收器即時獲取訊息

## 相關資源

- `msgq/sync_pubsub.md` — 同步版本
- `msgq/async_queue/async_queue.md` — 非同步佇列
- `msgq/common/common.md` — 共用元件
