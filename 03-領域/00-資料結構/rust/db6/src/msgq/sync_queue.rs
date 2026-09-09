//! Sync message queue implementation
//!
//! FIFO message queue with priority, visibility timeout, and dead letter queue.
//! Uses KvEngine for data storage, with table_id for queue isolation.

use crate::kv::{KvEngine, KvStore};
use crate::msgq::{error::*, message::SyncQueueMessage};
use std::sync::{Arc, RwLock};

/// Queue configuration
///
/// - `max_delivery_count`: Max delivery count (excess goes to DLQ, default 3)
/// - `dlq_name`: Dead letter queue name (None disables DLQ)
/// - `message_ttl_secs`: Message time-to-live (seconds)
/// - `priority_enabled`: Whether priority ordering is enabled
#[derive(Debug, Clone)]
pub struct QueueConfig {
    pub max_delivery_count: u32,
    pub dlq_name: Option<String>,
    pub message_ttl_secs: Option<u64>,
    pub priority_enabled: bool,
}

impl Default for QueueConfig {
    fn default() -> Self {
        Self {
            max_delivery_count: 3,
            dlq_name: None,
            message_ttl_secs: None,
            priority_enabled: false,
        }
    }
}

/// Sync queue: wraps KvEngine to provide FIFO message queue functionality
pub struct SyncQueue {
    name: String,
    engine: Arc<RwLock<KvEngine>>,
    config: QueueConfig,
}

/// Queue metadata
#[derive(serde::Serialize, serde::Deserialize, Default)]
pub struct QueueMeta {
    pub total_enqueued: u64,
    pub completed: u64,
    pub nacked: u64,
}

impl SyncQueue {
    /// Create a new sync queue
    pub fn new(name: &str, engine: Arc<RwLock<KvEngine>>) -> Self {
        Self {
            name: name.to_string(),
            engine,
            config: QueueConfig::default(),
        }
    }

    /// Create a sync queue with custom configuration
    pub fn with_config(name: &str, engine: Arc<RwLock<KvEngine>>, config: QueueConfig) -> Self {
        Self {
            name: name.to_string(),
            engine,
            config,
        }
    }

    pub fn config(&self) -> &QueueConfig {
        &self.config
    }

    pub fn set_config(&mut self, config: QueueConfig) {
        self.config = config;
    }

    fn now_millis() -> u64 {
        std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_millis() as u64
    }

    pub fn enqueue(&mut self, payload: Vec<u8>, visibility_timeout: u64) -> Result<String> {
        let mut msg = SyncQueueMessage::new(payload, visibility_timeout);
        let msg_id = msg.id.clone();

        let msg_json = serde_json::to_vec(&msg)?;
        let msg_key = format!("queue:{}:msg:{}", self.name, msg_id);
        {
            let mut guard = self.engine.write().map_err(|_| MsgqError::InvalidEngine("lock poisoned".into()))?;
            guard.put(1, msg_key.as_bytes(), &msg_json).map_err(MsgqError::Db)?;
        }

        let mut index = self.read_index()?;
        index.push(msg_id.clone());
        let index_key = format!("queue:{}:index", self.name);
        let index_json = serde_json::to_vec(&index)?;
        {
            let mut guard = self.engine.write().map_err(|_| MsgqError::InvalidEngine("lock poisoned".into()))?;
            guard.put(1, index_key.as_bytes(), &index_json).map_err(MsgqError::Db)?;
        }

        self.update_meta(|m| m.total_enqueued += 1)?;

        Ok(msg_id)
    }

    pub fn enqueue_at(&mut self, payload: Vec<u8>, visibility_timeout: u64, deliver_at: u64) -> Result<String> {
        let mut msg = SyncQueueMessage::new(payload, visibility_timeout);
        msg.visible_after = deliver_at;
        let msg_id = msg.id.clone();

        let msg_json = serde_json::to_vec(&msg)?;
        let msg_key = format!("queue:{}:msg:{}", self.name, msg_id);
        {
            let mut guard = self.engine.write().map_err(|_| MsgqError::InvalidEngine("lock poisoned".into()))?;
            guard.put(1, msg_key.as_bytes(), &msg_json).map_err(MsgqError::Db)?;
        }

        let mut index = self.read_index()?;
        index.push(msg_id.clone());
        let index_key = format!("queue:{}:index", self.name);
        let index_json = serde_json::to_vec(&index)?;
        {
            let mut guard = self.engine.write().map_err(|_| MsgqError::InvalidEngine("lock poisoned".into()))?;
            guard.put(1, index_key.as_bytes(), &index_json).map_err(MsgqError::Db)?;
        }

        self.update_meta(|m| m.total_enqueued += 1)?;

        Ok(msg_id)
    }

    pub fn enqueue_delay(&mut self, payload: Vec<u8>, visibility_timeout: u64, delay_secs: u64) -> Result<String> {
        let deliver_at = Self::now_millis() + delay_secs * 1000;
        self.enqueue_at(payload, visibility_timeout, deliver_at)
    }

    pub fn enqueue_priority(&mut self, payload: Vec<u8>, priority: u8) -> Result<String> {
        if !self.config.priority_enabled {
            return Err(MsgqError::InvalidOperation("priority queue not enabled".into()));
        }

        let mut msg = SyncQueueMessage::new(payload, 0);
        msg.priority = priority;
        let msg_id = msg.id.clone();

        let msg_json = serde_json::to_vec(&msg)?;
        let msg_key = format!("queue:{}:msg:{}", self.name, msg_id);
        {
            let mut guard = self.engine.write().map_err(|_| MsgqError::InvalidEngine("lock poisoned".into()))?;
            guard.put(1, msg_key.as_bytes(), &msg_json).map_err(MsgqError::Db)?;
        }

        let mut pindex = self.read_priority_index()?;
        pindex.push((priority, msg_id.clone()));
        pindex.sort_by(|a, b| b.0.cmp(&a.0));
        let pindex_key = format!("queue:{}:pindex", self.name);
        let pindex_json = serde_json::to_vec(&pindex)?;
        {
            let mut guard = self.engine.write().map_err(|_| MsgqError::InvalidEngine("lock poisoned".into()))?;
            guard.put(1, pindex_key.as_bytes(), &pindex_json).map_err(MsgqError::Db)?;
        }

        self.update_meta(|m| m.total_enqueued += 1)?;

        Ok(msg_id)
    }

    pub fn batch_enqueue(&mut self, payloads: Vec<Vec<u8>>, visibility_timeout: u64) -> Result<Vec<String>> {
        let mut ids = Vec::new();
        for payload in payloads {
            let id = self.enqueue(payload, visibility_timeout)?;
            ids.push(id);
        }
        Ok(ids)
    }

    pub fn dequeue(&mut self, wait_timeout_secs: u64) -> Result<Option<SyncQueueMessage>> {
        if self.config.priority_enabled {
            if let Some(msg) = self.dequeue_priority()? {
                return Ok(Some(msg));
            }
        }

        let index = self.read_index()?;
        let now = Self::now_millis();

        for msg_id in &index {
            let msg_key = format!("queue:{}:msg:{}", self.name, msg_id);
            let data_opt = {
                let guard = self.engine.read().map_err(|_| MsgqError::InvalidEngine("lock poisoned".into()))?;
                guard.get(1, msg_key.as_bytes()).map_err(MsgqError::Db)?
            };

            if let Some(data) = data_opt {
                if let Ok(mut msg) = serde_json::from_slice::<SyncQueueMessage>(&data) {
                    if msg.is_visible() {
                        let in_flight = self.is_inflight(msg_id)?;
                        if in_flight {
                            let now = Self::now_millis();
                            if msg.visible_after > now {
                                continue;
                            }
                            self.remove_inflight(msg_id)?;
                        }

                        if self.config.dlq_name.is_some() 
                            && msg.delivery_count >= self.config.max_delivery_count {
                            self.move_to_dlq(msg.clone())?;
                            self.remove_from_index(msg_id)?;
                            self.remove_inflight(msg_id)?;
                            continue;
                        }

                        self.add_inflight(msg_id)?;

                        msg.delivery_count += 1;
                        msg.visible_after = now + msg.visibility_timeout * 1000;

                        let updated_json = serde_json::to_vec(&msg)?;
                        let mut guard = self.engine.write().map_err(|_| MsgqError::InvalidEngine("lock poisoned".into()))?;
                        guard.put(1, msg_key.as_bytes(), &updated_json).map_err(MsgqError::Db)?;

                        return Ok(Some(msg));
                    }
                }
            }
        }

        if wait_timeout_secs > 0 {
            std::thread::sleep(std::time::Duration::from_secs(1));
            return self.dequeue(wait_timeout_secs - 1);
        }

        Ok(None)
    }

    fn dequeue_priority(&mut self) -> Result<Option<SyncQueueMessage>> {
        let pindex = self.read_priority_index()?;
        let now = Self::now_millis();

        for (_, msg_id) in &pindex {
            let msg_key = format!("queue:{}:msg:{}", self.name, msg_id);
            let data_opt = {
                let guard = self.engine.read().map_err(|_| MsgqError::InvalidEngine("lock poisoned".into()))?;
                guard.get(1, msg_key.as_bytes()).map_err(MsgqError::Db)?
            };

            if let Some(data) = data_opt {
                if let Ok(mut msg) = serde_json::from_slice::<SyncQueueMessage>(&data) {
                    if msg.is_visible() {
                        let in_flight = self.is_inflight(msg_id)?;
                        if in_flight {
                            let now = Self::now_millis();
                            if msg.visible_after > now {
                                continue;
                            }
                            self.remove_inflight(msg_id)?;
                        }

                        self.add_inflight(msg_id)?;

                        msg.visible_after = now + msg.visibility_timeout * 1000;

                        let updated_json = serde_json::to_vec(&msg)?;
                        let mut guard = self.engine.write().map_err(|_| MsgqError::InvalidEngine("lock poisoned".into()))?;
                        guard.put(1, msg_key.as_bytes(), &updated_json).map_err(MsgqError::Db)?;

                        return Ok(Some(msg));
                    }
                }
            }
        }

        Ok(None)
    }

    pub fn ack(&mut self, msg_id: &str) -> Result<()> {
        let msg_key = format!("queue:{}:msg:{}", self.name, msg_id);

        {
            let guard = self.engine.read().map_err(|_| MsgqError::InvalidEngine("lock poisoned".into()))?;
            if guard.get(1, msg_key.as_bytes()).map_err(MsgqError::Db)?.is_none() {
                return Err(MsgqError::MessageNotFound(msg_id.to_string()));
            }
        }

        self.remove_from_index(msg_id)?;
        self.remove_from_priority_index(msg_id)?;
        self.remove_inflight(msg_id)?;
        {
            let mut guard = self.engine.write().map_err(|_| MsgqError::InvalidEngine("lock poisoned".into()))?;
            guard.delete(1, msg_key.as_bytes()).map_err(MsgqError::Db)?;
        }
        self.update_meta(|m| m.completed += 1)?;

        Ok(())
    }

    pub fn nack(&mut self, msg_id: &str) -> Result<()> {
        let msg_key = format!("queue:{}:msg:{}", self.name, msg_id);

        let data = {
            let guard = self.engine.read().map_err(|_| MsgqError::InvalidEngine("lock poisoned".into()))?;
            guard.get(1, msg_key.as_bytes()).map_err(MsgqError::Db)?
                .ok_or_else(|| MsgqError::MessageNotFound(msg_id.to_string()))?
        };

        let mut msg: SyncQueueMessage = serde_json::from_slice(&data)?;

        self.remove_inflight(msg_id)?;

        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_millis() as u64;
        msg.visible_after = now;

        let updated_json = serde_json::to_vec(&msg)?;
        {
            let mut guard = self.engine.write().map_err(|_| MsgqError::InvalidEngine("lock poisoned".into()))?;
            guard.put(1, msg_key.as_bytes(), &updated_json).map_err(MsgqError::Db)?;
        }
        self.update_meta(|m| m.nacked += 1)?;

        Ok(())
    }

    pub fn peek(&self) -> Result<Option<SyncQueueMessage>> {
        let index = self.read_index()?;

        for msg_id in &index {
            let msg_key = format!("queue:{}:msg:{}", self.name, msg_id);
            let data_opt = {
                let guard = self.engine.read().map_err(|_| MsgqError::InvalidEngine("lock poisoned".into()))?;
                guard.get(1, msg_key.as_bytes()).map_err(MsgqError::Db)?
            };
            if let Some(data) = data_opt {
                if let Ok(msg) = serde_json::from_slice::<SyncQueueMessage>(&data) {
                    if msg.is_visible() {
                        return Ok(Some(msg));
                    }
                }
            }
        }

        Ok(None)
    }

    pub fn length(&self) -> Result<usize> {
        let index = self.read_index()?;
        Ok(index.len())
    }

    pub fn priority_length(&self) -> Result<usize> {
        let pindex = self.read_priority_index()?;
        Ok(pindex.len())
    }

    pub fn cleanup_expired(&mut self) -> Result<usize> {
        let ttl = match self.config.message_ttl_secs {
            Some(ttl) => ttl * 1000,
            None => return Ok(0),
        };

        let now = Self::now_millis();
        let mut removed = 0;

        let index = self.read_index()?;
        let mut updated_index = index.clone();

        for msg_id in &index {
            let msg_key = format!("queue:{}:msg:{}", self.name, msg_id);
            let data_opt = {
                let guard = self.engine.read().map_err(|_| MsgqError::InvalidEngine("lock poisoned".into()))?;
                guard.get(1, msg_key.as_bytes()).map_err(MsgqError::Db)?
            };

            if let Some(data) = data_opt {
                if let Ok(msg) = serde_json::from_slice::<SyncQueueMessage>(&data) {
                    if now - msg.enqueued_at > ttl {
                        {
                            let mut guard = self.engine.write().map_err(|_| MsgqError::InvalidEngine("lock poisoned".into()))?;
                            guard.delete(1, msg_key.as_bytes()).map_err(MsgqError::Db)?;
                        }
                        updated_index.retain(|id| id != msg_id);
                        removed += 1;
                    }
                }
            }
        }

        if removed > 0 {
            let index_key = format!("queue:{}:index", self.name);
            let index_json = serde_json::to_vec(&updated_index)?;
            {
                let mut guard = self.engine.write().map_err(|_| MsgqError::InvalidEngine("lock poisoned".into()))?;
                guard.put(1, index_key.as_bytes(), &index_json).map_err(MsgqError::Db)?;
            }
        }

        Ok(removed)
    }

    pub fn dlq_length(&self) -> Result<usize> {
        let dlq_name = match &self.config.dlq_name {
            Some(name) => name,
            None => return Ok(0),
        };

        let start_key = format!("queue:{}:dlq:", dlq_name);
        let end_key = format!("queue:{}:dlq;", dlq_name);

        let guard = self.engine.read().map_err(|_| MsgqError::InvalidEngine("lock poisoned".into()))?;
        let results = guard.scan(1, start_key.as_bytes(), end_key.as_bytes()).map_err(MsgqError::Db)?;
        Ok(results.len())
    }

    pub fn purge_dlq(&mut self) -> Result<usize> {
        let dlq_name = match &self.config.dlq_name {
            Some(name) => name,
            None => return Err(MsgqError::InvalidOperation("DLQ not configured".into())),
        };

        let start_key = format!("queue:{}:dlq:", dlq_name);
        let end_key = format!("queue:{}:dlq;", dlq_name);

        let results = {
            let guard = self.engine.read().map_err(|_| MsgqError::InvalidEngine("lock poisoned".into()))?;
            guard.scan(1, start_key.as_bytes(), end_key.as_bytes()).map_err(MsgqError::Db)?
        };

        let mut removed = 0;
        {
            let mut guard = self.engine.write().map_err(|_| MsgqError::InvalidEngine("lock poisoned".into()))?;
            for (key, _) in results {
                guard.delete(1, &key).map_err(MsgqError::Db)?;
                removed += 1;
            }
        }

        Ok(removed)
    }

    pub fn purge(&mut self) -> Result<()> {
        let index = self.read_index()?;

        {
            let mut guard = self.engine.write().map_err(|_| MsgqError::InvalidEngine("lock poisoned".into()))?;
            for msg_id in &index {
                let msg_key = format!("queue:{}:msg:{}", self.name, msg_id);
                guard.delete(1, msg_key.as_bytes()).map_err(MsgqError::Db)?;
            }

            let index_key = format!("queue:{}:index", self.name);
            guard.delete(1, index_key.as_bytes()).map_err(MsgqError::Db)?;

            let inflight_key = format!("queue:{}:inflight", self.name);
            guard.delete(1, inflight_key.as_bytes()).map_err(MsgqError::Db)?;
        }

        self.reset_meta()?;

        Ok(())
    }

    fn read_index(&self) -> Result<Vec<String>> {
        let index_key = format!("queue:{}:index", self.name);
        {
            let guard = self.engine.read().map_err(|_| MsgqError::InvalidEngine("lock poisoned".into()))?;
            if let Ok(Some(data)) = guard.get(1, index_key.as_bytes()) {
                return Ok(serde_json::from_slice(&data)?);
            }
        }
        Ok(vec![])
    }

    fn read_priority_index(&self) -> Result<Vec<(u8, String)>> {
        let pindex_key = format!("queue:{}:pindex", self.name);
        {
            let guard = self.engine.read().map_err(|_| MsgqError::InvalidEngine("lock poisoned".into()))?;
            if let Ok(Some(data)) = guard.get(1, pindex_key.as_bytes()) {
                return Ok(serde_json::from_slice(&data)?);
            }
        }
        Ok(vec![])
    }

    fn remove_from_priority_index(&mut self, msg_id: &str) -> Result<()> {
        let pindex_key = format!("queue:{}:pindex", self.name);
        let mut pindex = self.read_priority_index()?;
        pindex.retain(|(_, id)| id != msg_id);
        let pindex_json = serde_json::to_vec(&pindex)?;
        {
            let mut guard = self.engine.write().map_err(|_| MsgqError::InvalidEngine("lock poisoned".into()))?;
            guard.put(1, pindex_key.as_bytes(), &pindex_json).map_err(MsgqError::Db)?;
        }
        Ok(())
    }

    fn move_to_dlq(&mut self, msg: SyncQueueMessage) -> Result<()> {
        let dlq_name = self.config.dlq_name.as_ref()
            .ok_or_else(|| MsgqError::InvalidOperation("DLQ not configured".into()))?;

        let dlq_key = format!("queue:{}:dlq:{}", dlq_name, msg.id);
        let msg_json = serde_json::to_vec(&msg)?;
        {
            let mut guard = self.engine.write().map_err(|_| MsgqError::InvalidEngine("lock poisoned".into()))?;
            guard.put(1, dlq_key.as_bytes(), &msg_json).map_err(MsgqError::Db)?;
        }

        Ok(())
    }

    fn remove_from_index(&mut self, msg_id: &str) -> Result<()> {
        let index_key = format!("queue:{}:index", self.name);
        let mut index = self.read_index()?;
        index.retain(|id| id != msg_id);
        let index_json = serde_json::to_vec(&index)?;
        {
            let mut guard = self.engine.write().map_err(|_| MsgqError::InvalidEngine("lock poisoned".into()))?;
            guard.put(1, index_key.as_bytes(), &index_json).map_err(MsgqError::Db)?;
        }
        Ok(())
    }

    fn is_inflight(&self, msg_id: &str) -> Result<bool> {
        let inflight_key = format!("queue:{}:inflight", self.name);
        {
            let guard = self.engine.read().map_err(|_| MsgqError::InvalidEngine("lock poisoned".into()))?;
            if let Ok(Some(data)) = guard.get(1, inflight_key.as_bytes()) {
                let inflight: Vec<String> = serde_json::from_slice(&data)?;
                return Ok(inflight.iter().any(|id| id == msg_id));
            }
        }
        Ok(false)
    }

    fn add_inflight(&mut self, msg_id: &str) -> Result<()> {
        let inflight_key = format!("queue:{}:inflight", self.name);
        let mut inflight: Vec<String> = {
            let guard = self.engine.read().map_err(|_| MsgqError::InvalidEngine("lock poisoned".into()))?;
            if let Ok(Some(data)) = guard.get(1, inflight_key.as_bytes()) {
                serde_json::from_slice(&data).unwrap_or_default()
            } else {
                vec![]
            }
        };
        inflight.push(msg_id.to_string());
        let inflight_json = serde_json::to_vec(&inflight)?;
        {
            let mut guard = self.engine.write().map_err(|_| MsgqError::InvalidEngine("lock poisoned".into()))?;
            guard.put(1, inflight_key.as_bytes(), &inflight_json).map_err(MsgqError::Db)?;
        }
        Ok(())
    }

    fn remove_inflight(&mut self, msg_id: &str) -> Result<()> {
        let inflight_key = format!("queue:{}:inflight", self.name);
        let mut inflight: Vec<String> = {
            let guard = self.engine.read().map_err(|_| MsgqError::InvalidEngine("lock poisoned".into()))?;
            if let Ok(Some(data)) = guard.get(1, inflight_key.as_bytes()) {
                serde_json::from_slice(&data).unwrap_or_default()
            } else {
                vec![]
            }
        };
        inflight.retain(|id| id != msg_id);
        let inflight_json = serde_json::to_vec(&inflight)?;
        {
            let mut guard = self.engine.write().map_err(|_| MsgqError::InvalidEngine("lock poisoned".into()))?;
            guard.put(1, inflight_key.as_bytes(), &inflight_json).map_err(MsgqError::Db)?;
        }
        Ok(())
    }

    fn update_meta<F: FnOnce(&mut QueueMeta)>(&mut self, f: F) -> Result<()> {
        let meta_key = format!("queue:{}:meta", self.name);
        let mut meta: QueueMeta = {
            let guard = self.engine.read().map_err(|_| MsgqError::InvalidEngine("lock poisoned".into()))?;
            if let Ok(Some(data)) = guard.get(1, meta_key.as_bytes()) {
                serde_json::from_slice(&data).unwrap_or_default()
            } else {
                QueueMeta::default()
            }
        };
        f(&mut meta);
        let meta_json = serde_json::to_vec(&meta)?;
        {
            let mut guard = self.engine.write().map_err(|_| MsgqError::InvalidEngine("lock poisoned".into()))?;
            guard.put(1, meta_key.as_bytes(), &meta_json).map_err(MsgqError::Db)?;
        }
        Ok(())
    }

    fn reset_meta(&mut self) -> Result<()> {
        let meta_key = format!("queue:{}:meta", self.name);
        let meta = QueueMeta::default();
        let meta_json = serde_json::to_vec(&meta)?;
        {
            let mut guard = self.engine.write().map_err(|_| MsgqError::InvalidEngine("lock poisoned".into()))?;
            guard.put(1, meta_key.as_bytes(), &meta_json).map_err(MsgqError::Db)?;
        }
        Ok(())
    }
}