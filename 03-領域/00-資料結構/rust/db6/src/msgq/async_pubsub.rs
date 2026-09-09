//! Async publish/subscribe implementation — using tokio::sync::broadcast
//!
//! Two-layer architecture:
//! 1. Inner SyncPubSub handles KV store persistence
//! 2. Outer tokio broadcast handles real-time message delivery
//!
//! This provides both persistence (crash-recoverable history)
//! and broadcast channel real-time delivery.

use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::broadcast;
use tokio::sync::RwLock;

use crate::msgq::sync_pubsub::{PubSubConfig, SyncPubSub};
use crate::kv::KvEngine;

// Alias SyncPubSubMessage as AsyncPubSubMessage for seamless compatibility
pub use crate::msgq::SyncPubSubMessage as AsyncPubSubMessage;
pub use crate::msgq::sync_pubsub::TopicMatcher;

/// Convert MsgqError to String
fn map_err(e: crate::msgq::MsgqError) -> String {
    e.to_string()
}

/// Async pattern subscriber
///
/// Contains a pattern string and a corresponding broadcast receiver.
pub struct AsyncPatternSubscriber {
    pub pattern: String,
    pub receiver: broadcast::Receiver<AsyncPubSubMessage>,
}

/// Async Pub/Sub server
///
/// - `inner`: SyncPubSub handles persistence
/// - `channels`: broadcast channel handles real-time delivery
/// - `config`: Pub/Sub configuration
pub struct AsyncPubSub {
    inner: Arc<RwLock<SyncPubSub>>,
    channels: Arc<RwLock<HashMap<String, broadcast::Sender<AsyncPubSubMessage>>>>,
    config: PubSubConfig,
}

impl AsyncPubSub {
    /// Create a new async Pub/Sub server
    pub fn new(engine: Arc<std::sync::RwLock<KvEngine>>) -> Self {
        Self {
            inner: Arc::new(RwLock::new(SyncPubSub::new("default", engine))),
            channels: Arc::new(RwLock::new(HashMap::new())),
            config: PubSubConfig::default(),
        }
    }

    pub fn with_config(engine: Arc<std::sync::RwLock<KvEngine>>, config: PubSubConfig) -> Self {
        let q_config = config.clone();
        Self {
            inner: Arc::new(RwLock::new(SyncPubSub::with_config("default", engine, q_config))),
            channels: Arc::new(RwLock::new(HashMap::new())),
            config,
        }
    }

    pub fn config(&self) -> &PubSubConfig {
        &self.config
    }

    pub async fn set_config(&mut self, config: PubSubConfig) {
        self.config = config.clone();
        let mut guard = self.inner.write().await;
        guard.set_config(config);
    }

    /// Publish message to channel - persists to DB and all connected subscribers receive it instantly in memory
    pub async fn publish(&self, channel: &str, payload: Vec<u8>) -> Result<String, String> {
        let msg_id = {
            let mut guard = self.inner.write().await;
            guard.publish(channel, payload).map_err(map_err)?
        };

        // We fetch the message we just persisted to get the full struct (with timestamp etc.)
        let channel_history = {
            let guard = self.inner.read().await;
            guard.get_history(channel, 1).unwrap_or_default()
        };

        if let Some(msg) = channel_history.into_iter().last() {
            let mut channels = self.channels.write().await;
            if let Some(sender) = channels.get(channel) {
                let _ = sender.send(msg.clone());
            } else {
                let (tx, _rx) = broadcast::channel(self.config.channel_capacity);
                let _ = tx.send(msg.clone());
                channels.insert(channel.to_string(), tx);
            }
        }

        Ok(msg_id)
    }

    pub async fn publish_to_topic(&self, topic: &str, payload: Vec<u8>) -> Result<String, String> {
        self.publish(topic, payload).await
    }

    /// Subscribe to a channel - returns a receiver
    pub async fn subscribe(&self, channel: &str) -> Result<broadcast::Receiver<AsyncPubSubMessage>, String> {
        let mut channels = self.channels.write().await;

        let sender = if let Some(existing) = channels.get(channel) {
            existing.clone()
        } else {
            let (tx, _rx) = broadcast::channel(self.config.channel_capacity);
            channels.insert(channel.to_string(), tx.clone());
            tx
        };

        Ok(sender.subscribe())
    }

    pub async fn subscribe_topic(&self, topic_pattern: &str) -> Result<broadcast::Receiver<AsyncPubSubMessage>, String> {
        self.subscribe(topic_pattern).await
    }

    pub async fn subscribe_pattern(&self, pattern: &str) -> Result<AsyncPatternSubscriber, String> {
        if !self.config.pattern_matching {
            return Err("pattern matching not enabled".to_string());
        }

        let receiver = self.subscribe(pattern).await?;

        Ok(AsyncPatternSubscriber {
            pattern: pattern.to_string(),
            receiver,
        })
    }

    pub async fn subscribe_with_history(
        &self,
        channel: &str,
        history_count: usize,
    ) -> Result<(broadcast::Receiver<AsyncPubSubMessage>, Vec<AsyncPubSubMessage>), String> {
        let receiver = self.subscribe(channel).await?;

        let history = if self.config.history_enabled {
            let guard = self.inner.read().await;
            guard.get_history(channel, history_count).map_err(map_err)?
        } else {
            vec![]
        };

        Ok((receiver, history))
    }

    pub async fn get_history(&self, channel: &str, count: usize) -> Result<Vec<AsyncPubSubMessage>, String> {
        if !self.config.history_enabled {
            return Ok(vec![]);
        }

        let guard = self.inner.read().await;
        guard.get_history(channel, count).map_err(map_err)
    }

    /// Unsubscribe - just drop the receiver. For DB persistence, the client handles their subscriber IDs if using SyncPubSub manually.
    pub async fn unsubscribe(&self, _channel: &str) -> Result<(), String> {
        // Broadcast receivers unsubscribe automatically on drop
        Ok(())
    }

    /// List all channels
    pub async fn list_channels(&self) -> Vec<String> {
        let guard = self.inner.read().await;
        guard.list_channels().unwrap_or_default()
    }

    /// Get subscriber count
    pub async fn subscriber_count(&self, channel: &str) -> usize {
        let channels = self.channels.read().await;
        if let Some(sender) = channels.get(channel) {
            sender.receiver_count()
        } else {
            0
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::Arc;

    fn get_engine() -> Arc<std::sync::RwLock<KvEngine>> {
        Arc::new(std::sync::RwLock::new(KvEngine::new("memory").unwrap()))
    }

    #[tokio::test]
    async fn test_async_pubsub_basic() {
        let ps = AsyncPubSub::new(get_engine());

        // Subscribe to get receivers
        let mut sub1 = ps.subscribe("news").await.unwrap();
        let mut sub2 = ps.subscribe("news").await.unwrap();

        // Publish
        let id = ps.publish("news", b"Hello".to_vec()).await.unwrap();
        assert!(!id.is_empty());

        // Both subscribers should receive
        let msg1 = sub1.recv().await.unwrap();
        let msg2 = sub2.recv().await.unwrap();

        assert_eq!(msg1.payload, b"Hello");
        assert_eq!(msg2.payload, b"Hello");
    }

    #[tokio::test]
    async fn test_async_pubsub_list_channels() {
        let ps = AsyncPubSub::new(get_engine());

        ps.subscribe("ch1").await.unwrap();
        ps.publish("ch2", b"msg".to_vec()).await.unwrap();

        let channels = ps.list_channels().await;
        
        // Wait, subscribe doesn't trigger channel creation in SyncPubSub
        // unless it's explicitly publishing. Let's make sure it handles it:
        // Actually, broadcast merely holds it in memory, publish pushes it to DB.
        
        assert!(channels.iter().any(|c| c == "ch2")); // ch2 definitely has message
    }
}