//! Queue monitoring metrics and health checks

use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::Arc;

/// Queue monitoring metrics
///
/// All metrics use AtomicU64 for thread safety.
/// - `enqueued_total`: Cumulative enqueue count
/// - `dequeued_total`: Cumulative dequeue count
/// - `acked_total`: Cumulative ack count
/// - `nacked_total`: Cumulative nack count
/// - `in_flight`: Number of messages being processed
/// - `queue_depth`: Queue depth
#[derive(Debug, Clone)]
pub struct QueueMetrics {
    pub enqueued_total: Arc<AtomicU64>,
    pub dequeued_total: Arc<AtomicU64>,
    pub acked_total: Arc<AtomicU64>,
    pub nacked_total: Arc<AtomicU64>,
    pub in_flight: Arc<AtomicU64>,
    pub queue_depth: Arc<AtomicU64>,
}

impl QueueMetrics {
    /// Create a new metrics instance
    pub fn new() -> Self {
        Self {
            enqueued_total: Arc::new(AtomicU64::new(0)),
            dequeued_total: Arc::new(AtomicU64::new(0)),
            acked_total: Arc::new(AtomicU64::new(0)),
            nacked_total: Arc::new(AtomicU64::new(0)),
            in_flight: Arc::new(AtomicU64::new(0)),
            queue_depth: Arc::new(AtomicU64::new(0)),
        }
    }

    /// Increment enqueue count
    pub fn enqueued_inc(&self) {
        self.enqueued_total.fetch_add(1, Ordering::Relaxed);
    }

    /// Increment dequeue count
    pub fn dequeued_inc(&self) {
        self.dequeued_total.fetch_add(1, Ordering::Relaxed);
    }

    /// Increment ack count
    pub fn acked_inc(&self) {
        self.acked_total.fetch_add(1, Ordering::Relaxed);
    }

    /// Increment nack count
    pub fn nacked_inc(&self) {
        self.nacked_total.fetch_add(1, Ordering::Relaxed);
    }

    /// Set in-flight message count
    pub fn in_flight_set(&self, count: u64) {
        self.in_flight.store(count, Ordering::Relaxed);
    }

    /// Set queue depth
    pub fn queue_depth_set(&self, depth: u64) {
        self.queue_depth.store(depth, Ordering::Relaxed);
    }
}

impl Default for QueueMetrics {
    fn default() -> Self {
        Self::new()
    }
}

/// Health status enum
#[derive(Debug, Clone)]
pub enum HealthStatus {
    Healthy,
    Degraded(String),
    Unhealthy(String),
}

pub struct QueueHealth {
    pub status: HealthStatus,
    pub details: std::collections::HashMap<String, String>,
}

impl QueueHealth {
    pub fn healthy() -> Self {
        Self {
            status: HealthStatus::Healthy,
            details: std::collections::HashMap::new(),
        }
    }

    pub fn degraded(reason: &str) -> Self {
        let mut details = std::collections::HashMap::new();
        details.insert("reason".to_string(), reason.to_string());
        Self {
            status: HealthStatus::Degraded(reason.to_string()),
            details,
        }
    }

    pub fn unhealthy(reason: &str) -> Self {
        let mut details = std::collections::HashMap::new();
        details.insert("reason".to_string(), reason.to_string());
        Self {
            status: HealthStatus::Unhealthy(reason.to_string()),
            details,
        }
    }
}
