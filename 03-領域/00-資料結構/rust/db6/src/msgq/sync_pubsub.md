# msgq/sync_pubsub.md — 同步發布/訂閱

## Pub/Sub 模型

SyncPubSub 實現了傳統的 **發布/訂閱 (Publisher/Subscriber)** 模式。與佇列的不同在於：每條訊息會廣播給所有訂閱者，而不是被單一消費者消費。

```
KV 儲存結構 (table_id = hash("pubsub:{channel}")):
└── 通道列表 (in-memory) → Vec<SyncPubSubMessage>
```

## PubSubConfig

```rust
let config = PubSubConfig {
    max_history: 100,           // 保留歷史訊息數
    history_enabled: true,      // 啟用歷史
    pattern_matching: false,    // 啟用模式匹配
    channel_capacity: 10000,    // 通道容量
};
```

## 核心操作

| 方法 | 說明 |
|------|------|
| `publish` | 發布訊息到指定頻道 |
| `subscribe` | 訂閱頻道 |
| `unsubscribe` | 取消訂閱 |
| `get_history` | 取得頻道歷史 |
| `clear_channel` | 清除頻道 |
| `subscriber_count` | 查詢訂閱者數量 |

## 模式匹配 (Pattern Matching)

當 `pattern_matching = true`，支援萬用字元訂閱：

```
subscribe("news.*")   → 匹配 "news.sports", "news.tech"
subscribe("users.*.profile") → 匹配 "users.123.profile"
```

`TopicMatcher` 結構處理模式匹配邏輯。

## 與 AsyncPubSub 的差異

| 特性 | SyncPubSub | AsyncPubSub |
|------|-----------|-------------|
| 訂閱者通訊 | in-memory Vec | tokio broadcast |
| 持久化 | KV store | KV store + broadcast |
| 傳遞保證 | At-least-once | At-least-once |
| 即時性 | 輪詢 | 即時通知 |

## 相關資源

- `msgq/async_pubsub.md` — 非同步版本
- `msgq/sync_queue.md` — 同步佇列
