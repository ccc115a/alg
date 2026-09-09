# msgq 發展規劃

## v4.2 - Queue 強化

### Dead Letter Queue (DLQ)

當訊息 delivery_count 超過閾值，自動移至 DLQ。

```rust
// Config
pub struct QueueConfig {
    pub max_delivery_count: u32,  // 預設 3
    pub dlq_name: Option<String>,   // DLQ 佇列名稱
}

// 修改 dequeue 邏輯
impl AsyncQueue {
    pub async fn dequeue(&mut self) -> Result<Option<AsyncQueueMessage>> {
        let msg = self.do_dequeue().await?;
        if let Some(msg) = msg {
            if msg.delivery_count >= self.config.max_delivery_count {
                // 移至 DLQ
                self.dlq.enqueue(msg.payload, 0).await?;
                self.ack(&msg.id).await?;
                return self.dequeue().await;
            }
        }
        Ok(msg)
    }
}
```

### Delayed Messages

支援延遲 delivery，訊息在指定時間後才可取用。

```rust
impl SyncQueue {
    pub fn enqueue_at(
        &mut self,
        payload: Vec<u8>,
        deliver_at: u64,  // Unix timestamp
    ) -> Result<String> {
        let mut msg = SyncQueueMessage::new(payload, 0);
        msg.visible_after = deliver_at;  // 設為未來時間
        // ... 儲存
    }

    pub fn enqueue_delay(
        &mut self,
        payload: Vec<u8>,
        delay_secs: u64,
    ) -> Result<String> {
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_millis() as u64;
        self.enqueue_at(payload, now + delay_secs * 1000)
    }
}
```

### Message TTL

訊息過期自動刪除。

```rust
pub struct QueueConfig {
    pub message_ttl_secs: Option<u64>,  // None = 無限
}

impl SyncQueue {
    fn maybe_delete_expired(&mut self) -> Result<()> {
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_millis() as u64;
        
        if let Some(ttl) = self.config.message_ttl_secs {
            self.messages.retain(|m| {
                now - m.enqueued_at < ttl * 1000
            });
        }
    }
}
```

### Priority Queue

優先級訊息先處理。

```rust
pub struct PriorityMessage {
    pub priority: u8,    // 0 = 最高優先級
    pub message: SyncQueueMessage,
}

impl SyncQueue {
    pub fn enqueue_priority(
        &mut self,
        payload: Vec<u8>,
        priority: u8,
    ) -> Result<String> {
        let mut msg = SyncQueueMessage::new(payload, 0);
        let priority_msg = PriorityMessage { priority, message: msg };
        self.priority_queue.push(priority_msg);
        // 維持 max-heap 順序
    }
}
```

### Batch Enqueue

一次 enqueue 多個訊息。

```rust
impl SyncQueue {
    pub fn batch_enqueue(
        &mut self,
        payloads: Vec<Vec<u8>>,
    ) -> Result<Vec<String>> {
        let mut ids = Vec::new();
        for payload in payloads {
            let id = self.enqueue(payload, 0)?;
            ids.push(id);
        }
        Ok(ids)
    }
}
```

---

## v4.3 - PubSub 強化

### Pattern Subscription

Glob 風格的主題匹配。

```rust
pub struct PatternSubscriber {
    pub pattern: String,  // e.g., "news.*", "sports.football.*"
    pub receiver: broadcast::Receiver<AsyncPubSubMessage>,
}

impl AsyncPubSub {
    pub async fn subscribe_pattern(
        &self,
        pattern: &str,
    ) -> Result<PatternSubscriber> {
        // 訂閱所有匹配的主题
    }

    async fn match_and_publish(&self, channel: &str, msg: AsyncPubSubMessage) {
        // 檢查所有 pattern 訂閱者
    }
}
```

### Message History

新訂閱者可取得歷史訊息。

```rust
pub struct AsyncPubSub {
    // 保留最近 N 則訊息
    max_history: usize,
    history: Arc<RwLock<Vec<(String, AsyncPubSubMessage)>>>, // (channel, msg)
}

impl AsyncPubSub {
    pub async fn subscribe_with_history(
        &self,
        channel: &str,
        history_count: usize,
    ) -> Result<(broadcast::Receiver<AsyncPubSubMessage>, Vec<AsyncPubSubMessage>)> {
        let receiver = self.subscribe(channel).await?;
        let history = self.get_history(channel, history_count).await;
        Ok((receiver, history))
    }
}
```

### Wildcard Topics

複雜主題階層。

```rust
// Topic 格式: category.action.object
// 例如: user.created.admin, order.completed.customer

pub struct TopicMatcher {
    segments: Vec<Option<String>>,  // None = wildcard
}

impl TopicMatcher {
    pub fn matches(&self, topic: &str) -> bool {
        let parts: Vec<&str> = topic.split('.').collect();
        if parts.len() != self.segments.len() {
            return false;
        }
        for (i, seg) in self.segments.iter().enumerate() {
            if let Some(pattern) = seg {
                if parts[i] != pattern {
                    return false;
                }
            }
        }
        true
    }
}
```

---

## v4.4 - Async 強化

### Channel-based Queue

使用 tokio channel 實現高效 AsyncQueue。

```rust
pub struct AsyncChannelQueue {
    name: String,
    sender: mpsc::Sender<AsyncQueueMessage>,
    receiver: mpsc::Receiver<AsyncQueueMessage>,
    inflight: Arc<RwLock<HashSet<String>>>,
}

impl AsyncChannelQueue {
    pub fn new(name: &str, cap: usize) -> Self {
        let (tx, rx) = mpsc::channel(cap);
        Self {
            name: name.to_string(),
            sender: tx,
            receiver: rx,
            inflight: Arc::new(RwLock::new(HashSet::new())),
        }
    }

    pub async fn enqueue(&mut self, payload: Vec<u8>) -> Result<String> {
        let msg = AsyncQueueMessage::new(payload, 0);
        let id = msg.id.clone();
        self.sender.send(msg).await.map_err(|e| e.to_string())?;
        Ok(id)
    }

    pub async fn dequeue(&mut self) -> Result<Option<AsyncQueueMessage>> {
        match self.receiver.try_recv() {
            Ok(msg) => Ok(Some(msg)),
            Err(TryRecvError::Empty) => Ok(None),
            Err(TryRecvError::Closed) => Err("queue closed".into()),
        }
    }
}
```

### Async Iterator

`for await` 語法支援。

```rust
pub struct AsyncQueueIter {
    queue: AsyncQueue,
}

impl AsyncQueueIter {
    pub fn new(queue: AsyncQueue) -> Self {
        Self { queue }
    }
}

impl Stream for AsyncQueueIter {
    type Item = Result<AsyncQueueMessage, String>;

    fn poll_next(mut self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Option<Self::Item>> {
        let queue = &mut *self.queue;
        match futures::executor::block_on(queue.dequeue()) {
            Ok(Some(msg)) => Poll::Ready(Some(Ok(msg))),
            Ok(None) => {
                // 等待後重試
                cx.waker().wake_by_ref();
                Poll::Pending
            }
            Err(e) => Poll::Ready(Some(Err(e))),
        }
    }
}

// 使用
let mut iter = AsyncQueueIter::new(queue);
while let Some(msg) = iter.next().await {
    println!("{:?}", msg);
}
```

---

## v4.6 - Reliability

### Exactly-Once

Idempotency key 防重複處理。

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExactlyOnceMessage {
    pub idempotency_key: String,
    pub payload: Vec<u8>,
    pub processed: bool,
}

pub struct ExactlyOnceQueue {
    inner: AsyncQueue,
    processed_keys: Arc<RwLock<HashSet<String>>>,
    ttl_secs: u64,
}

impl ExactlyOnceQueue {
    pub async fn enqueue_once(
        &mut self,
        idempotency_key: String,
        payload: Vec<u8>,
    ) -> Result<Option<String>, String> {
        let mut keys = self.processed_keys.write().await;
        
        if keys.contains(&idempotency_key) {
            return Ok(None);  // 已經處理過
        }
        drop(keys);

        let msg_id = self.inner.enqueue(payload, 0).await?;
        
        // 標記為已處理
        let mut keys = self.processed_keys.write().await;
        keys.insert(idempotency_key);
        
        Ok(Some(msg_id))
    }
}
```

### Retry Backoff

指數退避重試。

```rust
pub struct RetryConfig {
    pub max_retries: u32,
    pub initial_delay_ms: u64,
    pub max_delay_ms: u64,
    pub backoff_multiplier: f64,
}

pub async fn with_retry<T, F, E>(
    config: RetryConfig,
    mut operation: F,
) -> Result<T, E>
where
    F: FnMut() -> Result<T, E>,
{
    let mut delay = config.initial_delay_ms;
    let mut attempts = 0;

    loop {
        match operation() {
            Ok(result) => return Ok(result),
            Err(e) => {
                attempts += 1;
                if attempts >= config.max_retries {
                    return Err(e);
                }
                tokio::time::sleep(Duration::from_millis(delay)).await;
                delay = (delay as f64 * config.backoff_multiplier) as u64;
                delay = delay.min(config.max_delay_ms);
            }
        }
    }
}
```

---

## v4.7 - Monitoring

### Prometheus Metrics

```rust
use prometheus::{Counter, Histogram, Gauge};

pub struct QueueMetrics {
    // Queue metrics
    pub enqueued_total: Counter,
    pub dequeued_total: Counter,
    pub acked_total: Counter,
    pub nacked_total: Counter,
    pub in_flight: Gauge,
    pub queue_depth: Gauge,
    
    // PubSub metrics  
    pub published_total: Counter,
    pub subscribers: Gauge,
    
    // Latency
    pub enqueue_latency: Histogram,
    pub dequeue_latency: Histogram,
}

impl QueueMetrics {
    pub fn new(namespace: &str) -> Self {
        let opts = |name: &str| {
            opts!(name, "queue metrics").namespace(namespace)
        };
        
        Self {
            enqueued_total: counter!(opts("enqueued_total")),
            dequeued_total: counter!(opts("dequeued_total")),
            acked_total: counter!(opts("acked_total")),
            nacked_total: counter!(opts("nacked_total")),
            in_flight: gauge!(opts("in_flight")),
            queue_depth: gauge!(opts("queue_depth")),
            published_total: counter!(opts("published_total")),
            subscribers: gauge!(opts("subscribers")),
            enqueue_latency: histogram!(opts("enqueue_latency"), [0.001, 0.01, 0.1, 1.0]),
            dequeue_latency: histogram!(opts("dequeue_latency"), [0.001, 0.01, 0.1, 1.0]),
        }
    }
}

// 使用
impl AsyncQueue {
    pub fn with_metrics(self, metrics: QueueMetrics) -> Self {
        // 包裝方法記錄 metrics
    }
}
```

### Health Check

```rust
pub enum HealthStatus {
    Healthy,
    Degraded(String),
    Unhealthy(String),
}

pub struct QueueHealth {
    pub status: HealthStatus,
    pub details: HashMap<String, String>,
}

impl AsyncQueue {
    pub async fn health(&self) -> QueueHealth {
        let depth = self.length().await.unwrap_or(0);
        
        if depth > 10000 {
            HealthStatus::Degraded("queue depth high".into())
        } else {
            HealthStatus::Healthy
        }
    }
}
```

---

## 版本規劃總覽

| 版本 | 主題 | 功能 |
|------|------|------|
| v4.2 | Queue 強化 | DLQ, Delayed Messages, TTL, Priority, Batch |
| v4.3 | PubSub 強化 | Pattern Subscription, History, Wildcard |
| v4.4 | Async 強化 | Channel Queue, Async Iterator |
| v4.6 | Reliability | Exactly-Once, Retry Backoff |
| v4.7 | Monitoring | Prometheus Metrics, Health Check |

---

## 實作順序建議

1. **v4.2** - 最實用，Queue 是核心功能
2. **v4.4** - Async 改進提升效能
3. **v4.6** - Reliability，生產環境需要
4. **v4.3** - PubSub 增強
5. **v4.7** - 監控，最後加入