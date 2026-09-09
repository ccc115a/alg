//! Sync queue message structure
//!
//! Defines SyncQueueMessage, the basic unit in the message queue system,
//! containing message ID, payload, metadata, and delivery control info.

use serde::{Deserialize, Serialize};

/// Sync queue message
///
/// - `id`: Unique identifier (timestamp + random)
/// - `payload`: Message content (serialized via serde_bytes)
/// - `enqueued_at`: Enqueue timestamp (milliseconds)
/// - `delivery_count`: Number of deliveries
/// - `visibility_timeout`: Visibility timeout (seconds)
/// - `visible_after`: Message is invisible before this time
/// - `priority`: Priority (0-255, higher is more urgent)
/// - `metadata`: Metadata
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SyncQueueMessage {
    pub id: String,
    #[serde(with = "serde_bytes")]
    pub payload: Vec<u8>,
    pub enqueued_at: u64,
    pub delivery_count: u32,
    pub visibility_timeout: u64,
    pub visible_after: u64,
    pub priority: u8,
    pub metadata: Option<String>,
}

impl SyncQueueMessage {
    /// Create a new queue message
    ///
    /// Automatically generates a unique message ID (timestamp + random).
    pub fn new(payload: Vec<u8>, visibility_timeout: u64) -> Self {
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_millis() as u64;

        let id = format!("{}:{:08x}", now, fastrand::u32(..));

        Self {
            id,
            payload,
            enqueued_at: now,
            delivery_count: 0,
            visibility_timeout,
            visible_after: 0,
            priority: 0,
            metadata: None,
        }
    }

    /// Set metadata (builder pattern)
    pub fn with_metadata(mut self, metadata: String) -> Self {
        self.metadata = Some(metadata);
        self
    }

    /// Check if message is visible
    ///
    /// Compares `visible_after` against the current time.
    pub fn is_visible(&self) -> bool {
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_millis() as u64;
        now >= self.visible_after
    }

    /// Parse payload as UTF-8 string
    pub fn payload_str(&self) -> Option<String> {
        String::from_utf8(self.payload.clone()).ok()
    }
}
