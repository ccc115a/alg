//! Message queue system — Queue and publish/subscribe based on KV storage engine
//!
//! Provides synchronous (Sync) and asynchronous (Async) operation modes:
//!
//! ## Sync Components
//! - `SyncQueue`: FIFO message queue with priority, DLQ, visibility timeout
//! - `SyncPubSub`: Publish/subscribe with pattern matching
//! - `SyncSqlExecutor`: SQL executor
//!
//! ## Async Components (tokio)
//! - `AsyncQueue`: Async queue based on tokio Notify
//! - `AsyncPubSub`: Async publish/subscribe based on broadcast channel
//! - `AsyncSqlExecutor`: Async SQL executor with concurrency limiting
//!
//! ## Shared Components
//! - `ConcurrencyLimiter`: tokio Semaphore wrapper to limit concurrent tasks
//! - `GracefulShutdown`: tokio Notify wrapper for graceful shutdown

mod common;
mod error;
mod message;
mod sync_queue;
mod sync_pubsub;
mod async_queue;
mod async_pubsub;
mod sql;

pub use common::{ConcurrencyLimiter, GracefulShutdown, DEFAULT_CONCURRENCY_LIMIT};
pub use error::{MsgqError, Result};
pub use message::SyncQueueMessage;
pub use sync_queue::{SyncQueue, QueueMeta, QueueConfig};
pub use sync_pubsub::{SyncPubSub, SyncPubSubMessage, PubSubConfig, TopicMatcher};
pub use async_queue::{AsyncQueue, AsyncQueueMessage, AsyncMsgq, AsyncQueueConfig, AsyncQueueStream, RetryConfig, with_retry, ExactlyOnceQueue, QueueMetrics, QueueHealth, HealthStatus};
pub use async_pubsub::{AsyncPubSub, AsyncPubSubMessage, AsyncPatternSubscriber};
pub use sql::{AsyncSqlExecutor, SyncSqlExecutor, JobResult, ResultStore, SqlJob};

use crate::kv::{KvEngine, KvStore};
use std::path::Path;
use std::sync::{Arc, RwLock};

pub struct Msgq {
    engine: Arc<RwLock<KvEngine>>,
}

impl Msgq {
    pub fn new(engine_type: &str) -> Result<Self> {
        let engine = KvEngine::new(engine_type)
            .map_err(|e| MsgqError::InvalidEngine(e.to_string()))?;
        Ok(Self {
            engine: Arc::new(RwLock::new(engine)),
        })
    }

    pub fn open(engine_type: &str, path: &Path) -> Result<Self> {
        let engine = KvEngine::open(engine_type, path)
            .map_err(|e| MsgqError::InvalidEngine(e.to_string()))?;
        Ok(Self {
            engine: Arc::new(RwLock::new(engine)),
        })
    }

    pub fn queue(&self, name: &str) -> SyncQueue {
        SyncQueue::new(name, self.engine.clone())
    }

    // Note: To share Tokio Notify events between producers and consumers,
    // they must clone() the same AsyncQueue instance, or use AsyncMsgq::queue()
    pub fn async_queue(&self, name: &str) -> AsyncQueue {
        AsyncQueue::new(name, self.engine.clone())
    }

    pub fn pubsub(&self) -> SyncPubSub {
        SyncPubSub::new("default", self.engine.clone())
    }

    pub fn async_pubsub(&self) -> AsyncPubSub {
        AsyncPubSub::new(self.engine.clone())
    }

    pub fn list_queues(&self) -> Result<Vec<String>> {
        let start = b"queue:";
        let end = b"queue;";

        let results = self.engine.read().unwrap().scan(1, start, end)?;
        let mut queues = std::collections::HashSet::new();

        for (key, _) in results {
            let key_str = String::from_utf8_lossy(&key);
            if let Some(name) = key_str.strip_prefix("queue:") {
                if let Some(queue_name) = name.split(':').next() {
                    if !queue_name.is_empty() {
                        queues.insert(queue_name.to_string());
                    }
                }
            }
        }

        Ok(queues.into_iter().collect())
    }

    pub fn delete_queue(&mut self, name: &str) -> Result<()> {
        let mut queue = self.queue(name);
        queue.purge()?;
        Ok(())
    }

    pub fn stats(&self, name: &str) -> Result<QueueStats> {
        let queue = self.queue(name);
        let meta_key = format!("queue:{}:meta", name);

        if let Some(data) = self.engine.read().unwrap().get(1, meta_key.as_bytes())? {
            #[derive(serde::Deserialize)]
            struct QueueMeta {
                total_enqueued: u64,
                completed: u64,
                nacked: u64,
            }
            let meta: QueueMeta = serde_json::from_slice(&data)?;

            Ok(QueueStats {
                name: name.to_string(),
                length: queue.length()?,
                total_enqueued: meta.total_enqueued,
                completed: meta.completed,
                nacked: meta.nacked,
            })
        } else {
            Ok(QueueStats {
                name: name.to_string(),
                length: 0,
                total_enqueued: 0,
                completed: 0,
                nacked: 0,
            })
        }
    }
}

#[derive(Debug, serde::Serialize)]
pub struct QueueStats {
    pub name: String,
    pub length: usize,
    pub total_enqueued: u64,
    pub completed: u64,
    pub nacked: u64,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_msgq_basic() {
        let msgq = Msgq::new("memory").unwrap();
        let mut queue = msgq.queue("test");

        let id1 = queue.enqueue(b"msg1".to_vec(), 30).unwrap();
        let id2 = queue.enqueue(b"msg2".to_vec(), 30).unwrap();

        assert!(!id1.is_empty());
        assert!(!id2.is_empty());
        assert_eq!(queue.length().unwrap(), 2);

        let msg = queue.dequeue(0).unwrap().unwrap();
        assert!(msg.payload == b"msg1" || msg.payload == b"msg2");

        queue.ack(&msg.id).unwrap();
        assert_eq!(queue.length().unwrap(), 1);
    }

    #[test]
    fn test_msgq_visibility_timeout() {
        let msgq = Msgq::new("memory").unwrap();
        let mut queue = msgq.queue("test");

        queue.enqueue(b"msg".to_vec(), 1).unwrap();

        let msg = queue.dequeue(0).unwrap().unwrap();

        let msg2 = queue.dequeue(0).unwrap();
        assert!(msg2.is_none() || msg2.unwrap().id != msg.id);

        std::thread::sleep(std::time::Duration::from_secs(2));

        let msg3 = queue.dequeue(0).unwrap().unwrap();
        assert_eq!(msg3.id, msg.id);
    }

    #[test]
    fn test_msgq_nack() {
        let msgq = Msgq::new("memory").unwrap();
        let mut queue = msgq.queue("test");

        let _id = queue.enqueue(b"msg".to_vec(), 30).unwrap();

        let msg = queue.dequeue(0).unwrap().unwrap();
        assert_eq!(msg.delivery_count, 1);

        queue.nack(&msg.id).unwrap();

        let msg2 = queue.dequeue(0).unwrap().unwrap();
        assert_eq!(msg2.delivery_count, 2);
    }

    #[test]
    fn test_msgq_stats() {
        let msgq = Msgq::new("memory").unwrap();
        let mut queue = msgq.queue("test");

        queue.enqueue(b"msg1".to_vec(), 30).unwrap();
        queue.enqueue(b"msg2".to_vec(), 30).unwrap();

        let stats = msgq.stats("test").unwrap();
        assert_eq!(stats.total_enqueued, 2);
        assert_eq!(stats.length, 2);
    }

    #[test]
    fn test_msgq_purge() {
        let msgq = Msgq::new("memory").unwrap();
        let mut queue = msgq.queue("test");

        queue.enqueue(b"msg1".to_vec(), 30).unwrap();
        queue.enqueue(b"msg2".to_vec(), 30).unwrap();

        assert_eq!(queue.length().unwrap(), 2);

        queue.purge().unwrap();

        assert_eq!(queue.length().unwrap(), 0);
    }

    #[test]
    fn test_msgq_peek() {
        let msgq = Msgq::new("memory").unwrap();
        let mut queue = msgq.queue("test");

        queue.enqueue(b"msg1".to_vec(), 30).unwrap();
        queue.enqueue(b"msg2".to_vec(), 30).unwrap();

        let peeked = queue.peek().unwrap().unwrap();
        assert_eq!(peeked.payload, b"msg1");

        assert_eq!(queue.length().unwrap(), 2);
    }
}

#[cfg(test)]
mod pubsub_tests {
    use super::*;

    #[test]
    fn test_pubsub_basic() {
        let msgq = Msgq::new("memory").unwrap();
        let mut ps = msgq.pubsub();

        ps.subscribe("news", "reader1").unwrap();
        ps.subscribe("news", "reader2").unwrap();

        let id = ps.publish("news", b"Breaking news!".to_vec()).unwrap();
        assert!(!id.is_empty());

        let msg1 = ps.consume("news", "reader1").unwrap().unwrap();
        let msg2 = ps.consume("news", "reader2").unwrap().unwrap();

        assert_eq!(msg1.payload, b"Breaking news!");
        assert_eq!(msg2.payload, b"Breaking news!");
        assert_eq!(msg1.id, msg2.id);
    }

    #[test]
    fn test_pubsub_offset_tracking() {
        let msgq = Msgq::new("memory").unwrap();
        let mut ps = msgq.pubsub();

        ps.subscribe("ch", "sub").unwrap();

        ps.publish("ch", b"msg1".to_vec()).unwrap();
        ps.publish("ch", b"msg2".to_vec()).unwrap();

        let m1 = ps.consume("ch", "sub").unwrap().unwrap();
        assert_eq!(m1.payload, b"msg1");

        let m2 = ps.consume("ch", "sub").unwrap().unwrap();
        assert_eq!(m2.payload, b"msg2");

        let m3 = ps.consume("ch", "sub").unwrap();
        assert!(m3.is_none());
    }

    #[test]
    fn test_pubsub_unsubscribe() {
        let msgq = Msgq::new("memory").unwrap();
        let mut ps = msgq.pubsub();

        ps.subscribe("ch", "sub").unwrap();
        ps.publish("ch", b"msg".to_vec()).unwrap();

        assert!(ps.consume("ch", "sub").unwrap().is_some());

        ps.unsubscribe("ch", "sub").unwrap();

        ps.subscribe("ch", "sub").unwrap();
        let msg = ps.consume("ch", "sub").unwrap().unwrap();
        assert_eq!(msg.payload, b"msg");
    }

    #[test]
    fn test_pubsub_list_channels() {
        let msgq = Msgq::new("memory").unwrap();
        let mut ps = msgq.pubsub();

        ps.subscribe("ch1", "sub").unwrap();
        ps.publish("ch2", b"msg".to_vec()).unwrap();

        let channels = ps.list_channels().unwrap();
        assert!(channels.iter().any(|c| c == "ch1"));
        assert!(channels.iter().any(|c| c == "ch2"));
    }

    #[test]
    fn test_pubsub_message_count() {
        let msgq = Msgq::new("memory").unwrap();
        let mut ps = msgq.pubsub();

        ps.publish("ch", b"msg1".to_vec()).unwrap();
        ps.publish("ch", b"msg2".to_vec()).unwrap();

        assert_eq!(ps.message_count("ch").unwrap(), 2);
    }

    #[test]
    fn test_pubsub_multiple_channels() {
        let msgq = Msgq::new("memory").unwrap();
        let mut ps = msgq.pubsub();

        ps.subscribe("channel_a", "sub1").unwrap();
        ps.subscribe("channel_b", "sub1").unwrap();

        ps.publish("channel_a", b"msg for a".to_vec()).unwrap();
        ps.publish("channel_b", b"msg for b".to_vec()).unwrap();

        let msg_a = ps.consume("channel_a", "sub1").unwrap().unwrap();
        let msg_b = ps.consume("channel_b", "sub1").unwrap().unwrap();

        assert_eq!(msg_a.payload, b"msg for a");
        assert_eq!(msg_b.payload, b"msg for b");
    }
}