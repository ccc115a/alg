//! Async message queue submodule
//!
//! Refactored in v4.11 from a single file into multiple separated concern submodules:
//!
//! - `config.rs`: Queue config and retry strategy
//! - `queue.rs`: Core queue implementation (tokio Notify)
//! - `metrics.rs`: Monitoring metrics and health checks
//! - `stream.rs`: tokio Stream interface
//! - `exactly.rs`: Exactly-Once delivery
//! - `facade.rs`: Factory entry point (AsyncMsgq)

pub mod config;
pub mod metrics;
pub mod queue;
pub mod stream;
pub mod facade;
pub mod exactly;

// Alias SyncQueueMessage as AsyncQueueMessage for backward compatibility
pub use crate::msgq::SyncQueueMessage as AsyncQueueMessage;

pub use config::{AsyncQueueConfig, RetryConfig, with_retry};
pub use metrics::{QueueMetrics, HealthStatus, QueueHealth};
pub use queue::AsyncQueue;
pub use stream::AsyncQueueStream;
pub use facade::AsyncMsgq;
pub use exactly::ExactlyOnceQueue;

#[cfg(test)]
mod tests {
    use super::*;
    use crate::kv::KvEngine;
    use std::sync::Arc;

    fn get_engine() -> Arc<std::sync::RwLock<KvEngine>> {
        Arc::new(std::sync::RwLock::new(KvEngine::new("memory").unwrap()))
    }

    /// Test basic async queue operations: enqueue → dequeue → ack
    #[tokio::test]
    async fn test_async_queue_basic() {
        let engine = get_engine();
        let mut q = AsyncQueue::new("test", engine);

        let id = q.enqueue(b"hello".to_vec(), 30).await.unwrap();
        assert!(!id.is_empty());

        assert_eq!(q.length().await.unwrap(), 1);

        let msg = q.dequeue(0).await.unwrap().unwrap();
        assert_eq!(msg.payload, b"hello");

        q.ack(&msg.id).await.unwrap();
        assert_eq!(q.length().await.unwrap(), 0);
    }

    /// Test Nack makes message visible again with incremented delivery_count
    #[tokio::test]
    async fn test_async_queue_nack() {
        let engine = get_engine();
        let mut q = AsyncQueue::new("test", engine);

        q.enqueue(b"msg".to_vec(), 30).await.unwrap();

        let msg = q.dequeue(0).await.unwrap().unwrap();
        assert_eq!(msg.delivery_count, 1);

        q.nack(&msg.id).await.unwrap();

        let msg2 = q.dequeue(0).await.unwrap().unwrap();
        assert_eq!(msg2.delivery_count, 2);
    }

    /// Test purging the queue
    #[tokio::test]
    async fn test_async_queue_purge() {
        let engine = get_engine();
        let mut q = AsyncQueue::new("test", engine);

        q.enqueue(b"msg1".to_vec(), 30).await.unwrap();
        q.enqueue(b"msg2".to_vec(), 30).await.unwrap();

        q.purge().await.unwrap();

        assert_eq!(q.length().await.unwrap(), 0);
    }
}
