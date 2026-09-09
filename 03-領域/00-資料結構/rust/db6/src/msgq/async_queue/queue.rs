//! Async queue core implementation
//!
//! AsyncQueue wraps SyncQueue and provides real-time notification via tokio::sync::Notify.
//! When a new message is enqueued, Notify wakes waiting consumers
//! to avoid busy-wait polling.

use std::sync::Arc;
use tokio::sync::{RwLock, Notify};

use super::config::AsyncQueueConfig;
use crate::msgq::{SyncQueue, SyncQueueMessage, QueueConfig};
use crate::kv::KvEngine;

/// Convert MsgqError to String
fn map_err(e: crate::msgq::MsgqError) -> String {
    e.to_string()
}

/// Async message queue
///
/// Wraps the sync SyncQueue with async notification.
pub struct AsyncQueue {
    /// Inner sync queue (uses tokio RwLock for async support)
    inner: Arc<RwLock<SyncQueue>>,
    /// Notifies consumers of new messages
    notify: Arc<Notify>,
}

impl AsyncQueue {
    /// Create a new async queue
    pub fn new(name: &str, engine: Arc<std::sync::RwLock<KvEngine>>) -> Self {
        Self {
            inner: Arc::new(RwLock::new(SyncQueue::new(name, engine))),
            notify: Arc::new(Notify::new()),
        }
    }

    /// Create an async queue with custom configuration
    pub fn with_config(name: &str, engine: Arc<std::sync::RwLock<KvEngine>>, config: AsyncQueueConfig) -> Self {
        let q_config = QueueConfig {
            max_delivery_count: config.max_delivery_count,
            dlq_name: config.dlq_name.clone(),
            message_ttl_secs: config.message_ttl_secs,
            priority_enabled: config.priority_enabled,
        };
        Self {
            inner: Arc::new(RwLock::new(SyncQueue::with_config(name, engine, q_config))),
            notify: Arc::new(Notify::new()),
        }
    }

    /// Get the current queue config
    pub async fn config(&self) -> AsyncQueueConfig {
        let guard = self.inner.read().await;
        let c = guard.config();
        AsyncQueueConfig {
            max_delivery_count: c.max_delivery_count,
            dlq_name: c.dlq_name.clone(),
            message_ttl_secs: c.message_ttl_secs,
            priority_enabled: c.priority_enabled,
        }
    }

    /// Enqueue a message (notifies waiting consumers)
    pub async fn enqueue(&mut self, payload: Vec<u8>, visibility_timeout: u64) -> Result<String, String> {
        let res = {
            let mut guard = self.inner.write().await;
            guard.enqueue(payload, visibility_timeout).map_err(map_err)
        };
        self.notify.notify_waiters();
        res
    }

    /// Enqueue a message at a specific time (delayed delivery)
    pub async fn enqueue_at(&mut self, payload: Vec<u8>, visibility_timeout: u64, deliver_at: u64) -> Result<String, String> {
        let res = {
            let mut guard = self.inner.write().await;
            guard.enqueue_at(payload, visibility_timeout, deliver_at).map_err(map_err)
        };
        self.notify.notify_waiters();
        res
    }

    pub async fn enqueue_delay(&mut self, payload: Vec<u8>, visibility_timeout: u64, delay_secs: u64) -> Result<String, String> {
        let res = {
            let mut guard = self.inner.write().await;
            guard.enqueue_delay(payload, visibility_timeout, delay_secs).map_err(map_err)
        };
        self.notify.notify_waiters();
        res
    }

    pub async fn enqueue_priority(&mut self, payload: Vec<u8>, priority: u8) -> Result<String, String> {
        let res = {
            let mut guard = self.inner.write().await;
            guard.enqueue_priority(payload, priority).map_err(map_err)
        };
        self.notify.notify_waiters();
        res
    }

    pub async fn batch_enqueue(&mut self, payloads: Vec<Vec<u8>>, visibility_timeout: u64) -> Result<Vec<String>, String> {
        let res = {
            let mut guard = self.inner.write().await;
            guard.batch_enqueue(payloads, visibility_timeout).map_err(map_err)
        };
        self.notify.notify_waiters();
        res
    }

    pub async fn dequeue(&mut self, wait_secs: u64) -> Result<Option<SyncQueueMessage>, String> {
        let deadline = if wait_secs == 0 {
            tokio::time::Instant::now()
        } else {
            tokio::time::Instant::now() + tokio::time::Duration::from_secs(wait_secs)
        };

        loop {
            // Fast path / Try first
            {
                let mut guard = self.inner.write().await;
                if let Some(msg) = guard.dequeue(0).map_err(map_err)? {
                    return Ok(Some(msg));
                }
            }

            if wait_secs == 0 || tokio::time::Instant::now() >= deadline {
                return Ok(None);
            }

            tokio::select! {
                _ = self.notify.notified() => {}
                _ = tokio::time::sleep_until(deadline) => {
                    return Ok(None);
                }
            }
        }
    }

    pub async fn ack(&mut self, msg_id: &str) -> Result<(), String> {
        let mut guard = self.inner.write().await;
        guard.ack(msg_id).map_err(map_err)
    }

    pub async fn nack(&mut self, msg_id: &str) -> Result<(), String> {
        let res = {
            let mut guard = self.inner.write().await;
            guard.nack(msg_id).map_err(map_err)
        };
        self.notify.notify_waiters();
        res
    }

    pub async fn peek(&self) -> Result<Option<SyncQueueMessage>, String> {
        let guard = self.inner.read().await;
        guard.peek().map_err(map_err)
    }

    pub async fn length(&self) -> Result<usize, String> {
        let guard = self.inner.read().await;
        guard.length().map_err(map_err)
    }

    pub async fn priority_length(&self) -> Result<usize, String> {
        let guard = self.inner.read().await;
        guard.priority_length().map_err(map_err)
    }

    pub async fn dlq_length(&self) -> Result<usize, String> {
        let guard = self.inner.read().await;
        guard.dlq_length().map_err(map_err)
    }

    pub async fn cleanup_expired(&mut self) -> Result<usize, String> {
        let mut guard = self.inner.write().await;
        guard.cleanup_expired().map_err(map_err)
    }

    pub async fn purge_dlq(&mut self) -> Result<usize, String> {
        let mut guard = self.inner.write().await;
        guard.purge_dlq().map_err(map_err)
    }

    pub async fn purge(&mut self) -> Result<(), String> {
        let mut guard = self.inner.write().await;
        guard.purge().map_err(map_err)
    }
}

impl Clone for AsyncQueue {
    fn clone(&self) -> Self {
        Self {
            inner: self.inner.clone(),
            notify: self.notify.clone(),
        }
    }
}
