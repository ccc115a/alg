//! Sync publish/subscribe implementation
//!
//! Traditional Pub/Sub pattern with channel subscribe, publish, history, and pattern matching.
//! Subscribers poll for new messages (sync version).

use crate::kv::{KvEngine, KvStore};
use crate::msgq::error::{MsgqError, Result};
use serde::{Deserialize, Serialize};
use std::sync::{Arc, RwLock};

/// Pub/Sub message
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SyncPubSubMessage {
    pub id: String,
    pub channel: String,
    pub payload: Vec<u8>,
    pub timestamp: u64,
}

impl SyncPubSubMessage {
    /// Create a new Pub/Sub message
    pub fn new(channel: &str, payload: Vec<u8>) -> Self {
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_millis() as u64;
        let id = format!("{}:{:08x}", now, fastrand::u32(..));

        Self {
            id,
            channel: channel.to_string(),
            payload,
            timestamp: now,
        }
    }

    /// Parse payload as UTF-8 string
    pub fn payload_str(&self) -> Option<String> {
        String::from_utf8(self.payload.clone()).ok()
    }
}

/// Channel message list (for KV storage)
#[derive(Serialize, Deserialize, Default)]
struct ChannelMessages {
    messages: Vec<SyncPubSubMessage>,
}

/// Pub/Sub configuration
///
/// - `max_history`: Maximum history count
/// - `history_enabled`: Whether history is enabled
/// - `pattern_matching`: Whether pattern matching is enabled
/// - `channel_capacity`: Channel capacity
#[derive(Debug, Clone)]
pub struct PubSubConfig {
    pub max_history: usize,
    pub history_enabled: bool,
    pub pattern_matching: bool,
    pub channel_capacity: usize,
}

impl Default for PubSubConfig {
    fn default() -> Self {
        Self {
            max_history: 100,
            history_enabled: true,
            pattern_matching: true,
            channel_capacity: 1024,
        }
    }
}

#[derive(Debug, Clone)]
pub struct TopicMatcher {
    segments: Vec<Option<String>>,
}

impl TopicMatcher {
    pub fn new(pattern: &str) -> Self {
        let segments: Vec<Option<String>> = pattern
            .split('.')
            .map(|s| {
                if s == "*" || s.is_empty() {
                    None
                } else {
                    Some(s.to_string())
                }
            })
            .collect();
        Self { segments }
    }

    pub fn matches(&self, topic: &str) -> bool {
        let parts: Vec<&str> = topic.split('.').collect();
        if parts.len() != self.segments.len() {
            return false;
        }
        for (i, seg) in self.segments.iter().enumerate() {
            if let Some(ref pattern) = seg {
                if parts[i] != pattern {
                    return false;
                }
            }
        }
        true
    }
}

pub struct SyncPubSub {
    name: String,
    engine: Arc<RwLock<KvEngine>>,
    config: PubSubConfig,
}

impl SyncPubSub {
    pub fn new(name: &str, engine: Arc<RwLock<KvEngine>>) -> Self {
        Self {
            name: name.to_string(),
            engine,
            config: PubSubConfig::default(),
        }
    }

    pub fn with_config(name: &str, engine: Arc<RwLock<KvEngine>>, config: PubSubConfig) -> Self {
        Self {
            name: name.to_string(),
            engine,
            config,
        }
    }

    pub fn config(&self) -> &PubSubConfig {
        &self.config
    }

    pub fn set_config(&mut self, config: PubSubConfig) {
        self.config = config;
    }

    pub fn publish(&mut self, channel: &str, payload: Vec<u8>) -> Result<String> {
        let msg = SyncPubSubMessage::new(channel, payload);
        let msg_id = msg.id.clone();

        // Get existing messages
        let mut channel_messages = self.get_channel_messages(channel)?;

        // Append new message
        channel_messages.messages.push(msg);

        // Save
        let key = self.channel_messages_key(channel);
        let json = serde_json::to_vec(&channel_messages)?;
        {
            let mut guard = self.engine.write().map_err(|_| MsgqError::InvalidEngine("lock poisoned".into()))?;
            guard.put(1, key.as_bytes(), &json).map_err(MsgqError::Db)?;
        }

        Ok(msg_id)
    }

    pub fn publish_to_topic(&mut self, topic: &str, payload: Vec<u8>) -> Result<String> {
        self.publish(topic, payload)
    }

    pub fn subscribe_topic(&mut self, topic_pattern: &str, subscriber_id: &str) -> Result<()> {
        if !self.config.pattern_matching {
            return Err(MsgqError::InvalidOperation("pattern matching not enabled".into()));
        }
        self.subscribe(topic_pattern, subscriber_id)
    }

    pub fn subscribe_pattern(&mut self, pattern: &str, subscriber_id: &str) -> Result<()> {
        if !self.config.pattern_matching {
            return Err(MsgqError::InvalidOperation("pattern matching not enabled".into()));
        }

        let mut patterns = self.get_patterns()?;
        if !patterns.contains(&pattern.to_string()) {
            patterns.push(pattern.to_string());
        }

        let key = format!("pubsub:{}:patterns", self.name);
        let json = serde_json::to_vec(&patterns)?;
        {
            let mut guard = self.engine.write().map_err(|_| MsgqError::InvalidEngine("lock poisoned".into()))?;
            guard.put(1, key.as_bytes(), &json).map_err(MsgqError::Db)?;
        }

        let offset_key = format!("pubsub:{}:pattern_offset:{}:{}", self.name, pattern, subscriber_id);
        {
            let mut guard = self.engine.write().map_err(|_| MsgqError::InvalidEngine("lock poisoned".into()))?;
            guard.put(1, offset_key.as_bytes(), b"0").map_err(MsgqError::Db)?;
        }

        Ok(())
    }

    pub fn consume_pattern(&mut self, pattern: &str, subscriber_id: &str) -> Result<Option<SyncPubSubMessage>> {
        if !self.config.pattern_matching {
            return Err(MsgqError::InvalidOperation("pattern matching not enabled".into()));
        }

        let offset_key = format!("pubsub:{}:pattern_offset:{}:{}", self.name, pattern, subscriber_id);
        let offset = {
            let guard = self.engine.read().map_err(|_| MsgqError::InvalidEngine("lock poisoned".into()))?;
            if let Ok(Some(data)) = guard.get(1, offset_key.as_bytes()) {
                let offset_str = String::from_utf8_lossy(&data);
                offset_str.parse().unwrap_or(0)
            } else {
                0
            }
        };

        let channels = self.list_channels()?;

        for channel in channels {
            let matcher = TopicMatcher::new(pattern);
            if !matcher.matches(&channel) {
                continue;
            }

            let channel_messages = self.get_channel_messages(&channel)?;
            if offset < channel_messages.messages.len() {
                let msg = channel_messages.messages[offset].clone();

                let new_offset = offset + 1;
                {
                    let mut guard = self.engine.write().map_err(|_| MsgqError::InvalidEngine("lock poisoned".into()))?;
                    guard.put(1, offset_key.as_bytes(), new_offset.to_string().as_bytes()).map_err(MsgqError::Db)?;
                }

                return Ok(Some(msg));
            }
        }

        Ok(None)
    }

    pub fn list_patterns(&self) -> Result<Vec<String>> {
        self.get_patterns()
    }

    pub fn subscribe_with_history(
        &mut self,
        channel: &str,
        subscriber_id: &str,
        history_count: usize,
    ) -> Result<Vec<SyncPubSubMessage>> {
        self.subscribe(channel, subscriber_id)?;

        if !self.config.history_enabled {
            return Ok(vec![]);
        }

        self.get_history(channel, history_count)
    }

    pub fn get_history(&self, channel: &str, count: usize) -> Result<Vec<SyncPubSubMessage>> {
        if !self.config.history_enabled {
            return Ok(vec![]);
        }

        let channel_messages = self.get_channel_messages(channel)?;
        let max_count = count.min(self.config.max_history);
        let start = channel_messages.messages.len().saturating_sub(max_count);

        Ok(channel_messages.messages[start..].to_vec())
    }

    pub fn set_max_history(&mut self, max: usize) {
        self.config.max_history = max;
    }

    fn get_patterns(&self) -> Result<Vec<String>> {
        let key = format!("pubsub:{}:patterns", self.name);
        {
            let guard = self.engine.read().map_err(|_| MsgqError::InvalidEngine("lock poisoned".into()))?;
            if let Ok(Some(data)) = guard.get(1, key.as_bytes()) {
                return Ok(serde_json::from_slice(&data).unwrap_or_default());
            }
        }
        Ok(vec![])
    }

    pub fn subscribe(&mut self, channel: &str, subscriber_id: &str) -> Result<()> {
        // Get existing subscribers
        let mut subscribers = self.get_subscribers(channel)?;

        // Add if not exists
        if !subscribers.contains(&subscriber_id.to_string()) {
            subscribers.push(subscriber_id.to_string());
        }

        // Save subscribers
        let key = self.channel_subscribers_key(channel);
        let json = serde_json::to_vec(&subscribers)?;
        {
            let mut guard = self.engine.write().map_err(|_| MsgqError::InvalidEngine("lock poisoned".into()))?;
            guard.put(1, key.as_bytes(), &json).map_err(MsgqError::Db)?;
        }

        // Initialize offset to 0
        let offset_key = self.offset_key(channel, subscriber_id);
        {
            let mut guard = self.engine.write().map_err(|_| MsgqError::InvalidEngine("lock poisoned".into()))?;
            guard.put(1, offset_key.as_bytes(), b"0").map_err(MsgqError::Db)?;
        }

        Ok(())
    }

    pub fn unsubscribe(&mut self, channel: &str, subscriber_id: &str) -> Result<()> {
        // Remove from subscribers
        let mut subscribers = self.get_subscribers(channel)?;
        subscribers.retain(|s| s != subscriber_id);

        let key = self.channel_subscribers_key(channel);
        let json = serde_json::to_vec(&subscribers)?;
        {
            let mut guard = self.engine.write().map_err(|_| MsgqError::InvalidEngine("lock poisoned".into()))?;
            guard.put(1, key.as_bytes(), &json).map_err(MsgqError::Db)?;
        }

        // Delete offset
        let offset_key = self.offset_key(channel, subscriber_id);
        {
            let mut guard = self.engine.write().map_err(|_| MsgqError::InvalidEngine("lock poisoned".into()))?;
            guard.delete(1, offset_key.as_bytes()).map_err(MsgqError::Db)?;
        }

        Ok(())
    }

    pub fn consume(&mut self, channel: &str, subscriber_id: &str) -> Result<Option<SyncPubSubMessage>> {
        // Get offset
        let offset = self.get_offset(channel, subscriber_id)?;

        // Get messages
        let channel_messages = self.get_channel_messages(channel)?;

        if offset < channel_messages.messages.len() {
            let msg = channel_messages.messages[offset].clone();

            // Increment offset
            let new_offset = offset + 1;
            let offset_key = self.offset_key(channel, subscriber_id);
            {
                let mut guard = self.engine.write().map_err(|_| MsgqError::InvalidEngine("lock poisoned".into()))?;
                guard.put(1, offset_key.as_bytes(), new_offset.to_string().as_bytes()).map_err(MsgqError::Db)?;
            }

            return Ok(Some(msg));
        }

        Ok(None)
    }

    pub fn list_channels(&self) -> Result<Vec<String>> {
        let start = format!("pubsub:{}:messages:", self.name).as_bytes().to_vec();
        let end = format!("pubsub:{}:messages;", self.name).as_bytes().to_vec();
        let start_sub = format!("pubsub:{}:subscribers:", self.name).as_bytes().to_vec();
        let end_sub = format!("pubsub:{}:subscribers;", self.name).as_bytes().to_vec();

        let mut channels = std::collections::HashSet::new();

        {
            let guard = self.engine.read().map_err(|_| MsgqError::InvalidEngine("lock poisoned".into()))?;
            // Scan for messages keys
            if let Ok(results) = guard.scan(1, &start, &end) {
                for (key, _) in results {
                    let key_str = String::from_utf8_lossy(&key).to_string();
                    if let Some(ch) = key_str.strip_prefix(&format!("pubsub:{}:messages:", self.name)) {
                        channels.insert(ch.to_string());
                    }
                }
            }
            // Also scan for subscribers keys (channels with no messages but with subscribers)
            if let Ok(results) = guard.scan(1, &start_sub, &end_sub) {
                for (key, _) in results {
                    let key_str = String::from_utf8_lossy(&key).to_string();
                    if let Some(ch) = key_str.strip_prefix(&format!("pubsub:{}:subscribers:", self.name)) {
                        channels.insert(ch.to_string());
                    }
                }
            }
        }

        Ok(channels.into_iter().collect())
    }

    pub fn list_subscribers(&self, channel: &str) -> Result<Vec<String>> {
        Ok(self.get_subscribers(channel)?)
    }

    pub fn message_count(&self, channel: &str) -> Result<usize> {
        let channel_messages = self.get_channel_messages(channel)?;
        Ok(channel_messages.messages.len())
    }

    // Internal helpers
    fn channel_messages_key(&self, channel: &str) -> String {
        format!("pubsub:{}:messages:{}", self.name, channel)
    }

    fn channel_subscribers_key(&self, channel: &str) -> String {
        format!("pubsub:{}:subscribers:{}", self.name, channel)
    }

    fn offset_key(&self, channel: &str, subscriber_id: &str) -> String {
        format!("pubsub:{}:offset:{}:{}", self.name, channel, subscriber_id)
    }

    fn get_channel_messages(&self, channel: &str) -> Result<ChannelMessages> {
        let key = self.channel_messages_key(channel);
        {
            let guard = self.engine.read().map_err(|_| MsgqError::InvalidEngine("lock poisoned".into()))?;
            if let Ok(Some(data)) = guard.get(1, key.as_bytes()) {
                return Ok(serde_json::from_slice(&data).unwrap_or_default());
            }
        }
        Ok(ChannelMessages::default())
    }

    fn get_subscribers(&self, channel: &str) -> Result<Vec<String>> {
        let key = self.channel_subscribers_key(channel);
        {
            let guard = self.engine.read().map_err(|_| MsgqError::InvalidEngine("lock poisoned".into()))?;
            if let Ok(Some(data)) = guard.get(1, key.as_bytes()) {
                return Ok(serde_json::from_slice(&data).unwrap_or_default());
            }
        }
        Ok(vec![])
    }

    fn get_offset(&self, channel: &str, subscriber_id: &str) -> Result<usize> {
        let key = self.offset_key(channel, subscriber_id);
        {
            let guard = self.engine.read().map_err(|_| MsgqError::InvalidEngine("lock poisoned".into()))?;
            if let Ok(Some(data)) = guard.get(1, key.as_bytes()) {
                let offset_str = String::from_utf8_lossy(&data);
                return Ok(offset_str.parse().unwrap_or(0));
            }
        }
        Ok(0)
    }
}