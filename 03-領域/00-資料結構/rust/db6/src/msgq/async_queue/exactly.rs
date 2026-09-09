//! Exactly-Once Queue
//!
//! Achieves exactly-once delivery semantics via idempotency key deduplication.
//! Each message has a unique idempotency key; duplicate submissions with the same key are ignored.

use std::sync::Arc;
use tokio::sync::RwLock;
use std::collections::HashSet;

use super::queue::AsyncQueue;
use crate::msgq::SyncQueueMessage as AsyncQueueMessage;

/// Exactly-Once queue
///
/// - `inner`: Underlying AsyncQueue
/// - `processed_keys`: Set of already-processed idempotency keys
/// - `ttl_secs`: Key time-to-live (prevents unbounded memory growth)
pub struct ExactlyOnceQueue {
    inner: AsyncQueue,
    processed_keys: Arc<RwLock<HashSet<String>>>,
    ttl_secs: u64,
}

impl ExactlyOnceQueue {
    /// Create a new Exactly-Once queue
    pub fn new(queue: AsyncQueue, ttl_secs: u64) -> Self {
        Self {
            inner: queue,
            processed_keys: Arc::new(RwLock::new(HashSet::new())),
            ttl_secs,
        }
    }

    /// 冪等入隊：如果 idempotency_key 已存在則忽略
    ///
    /// - 回傳 `Ok(Some(msg_id))`: 首次入隊成功
    /// - 回傳 `Ok(None)`: 重複提交，已忽略
    pub async fn enqueue_once(
        &mut self,
        idempotency_key: String,
        payload: Vec<u8>,
    ) -> Result<Option<String>, String> {
        {
            let keys = self.processed_keys.read().await;
            if keys.contains(&idempotency_key) {
                return Ok(None);
            }
        }

        let msg_id = self.inner.enqueue(payload, 30).await?;

        {
            let mut keys = self.processed_keys.write().await;
            keys.insert(idempotency_key);
        }

        Ok(Some(msg_id))
    }

    pub async fn dequeue(&mut self, wait_secs: u64) -> Result<Option<AsyncQueueMessage>, String> {
        self.inner.dequeue(wait_secs).await
    }

    pub async fn ack(&mut self, msg_id: &str) -> Result<(), String> {
        self.inner.ack(msg_id).await
    }

    pub async fn nack(&mut self, msg_id: &str) -> Result<(), String> {
        self.inner.nack(msg_id).await
    }

    pub async fn cleanup_expired(&mut self) -> Result<usize, String> {
        let mut keys = self.processed_keys.write().await;
        let before = keys.len();
        keys.retain(|k| {
            if let Ok(ts) = k.split(':').next().unwrap_or("0").parse::<u64>() {
                let now = std::time::SystemTime::now()
                    .duration_since(std::time::UNIX_EPOCH)
                    .unwrap()
                    .as_millis() as u64;
                ts * 1000 > now - self.ttl_secs * 1000
            } else {
                true
            }
        });
        let removed = before - keys.len();

        Ok(removed)
    }
}

impl Clone for ExactlyOnceQueue {
    fn clone(&self) -> Self {
        Self {
            inner: self.inner.clone(),
            processed_keys: self.processed_keys.clone(),
            ttl_secs: self.ttl_secs,
        }
    }
}
