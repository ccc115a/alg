//! ConcurrencyLimiter — Concurrency limiter based on tokio Semaphore
//!
//! Similar to mini-redis design: limits the number of concurrent async tasks
//! to prevent system resource exhaustion. Each task must `acquire()` a permit
//! before starting, and the permit is automatically returned when finished.
//!
//! Differences from using `Arc<Semaphore>` directly:
//! - Uses `acquire_owned()` to get permits, permit lifetime is not tied to borrows
//! - Supports dynamic limit adjustment via `set_limit()`
//! - Can query available permits via `available()`

use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;
use tokio::sync::Semaphore;

/// Concurrency limiter
pub struct ConcurrencyLimiter {
    /// Underlying Semaphore
    semaphore: Arc<Semaphore>,
    /// Limit value (for querying, does not affect Semaphore behavior)
    limit: Arc<AtomicUsize>,
}

impl ConcurrencyLimiter {
    /// Create a new concurrency limiter
    ///
    /// `limit`: Maximum number of concurrent tasks
    pub fn new(limit: usize) -> Self {
        Self {
            semaphore: Arc::new(Semaphore::new(limit)),
            limit: Arc::new(AtomicUsize::new(limit)),
        }
    }

    /// Same as `new()`, alternative naming
    pub fn with_limit(limit: usize) -> Self {
        Self::new(limit)
    }

    /// Asynchronously acquire a permit (may wait)
    ///
    /// Waits when all permits are in use until one is returned.
    /// Uses `acquire_owned()` so the permit lifetime can cross async boundaries.
    pub async fn acquire(&self) -> Result<tokio::sync::OwnedSemaphorePermit, String> {
        self.semaphore.clone().acquire_owned().await.map_err(|e| e.to_string())
    }

    /// Try to acquire a permit (non-blocking)
    ///
    /// Returns None immediately if no permits are available.
    pub fn try_acquire(&self) -> Option<tokio::sync::OwnedSemaphorePermit> {
        self.semaphore.clone().try_acquire_owned().ok()
    }

    /// Query the current number of available permits
    pub fn available(&self) -> usize {
        self.semaphore.available_permits()
    }

    /// Get the currently configured concurrency limit
    pub fn limit(&self) -> usize {
        self.limit.load(Ordering::Relaxed)
    }

    /// Dynamically adjust the concurrency limit
    ///
    /// Note: This only updates the recorded value, does not affect the existing Semaphore.
    pub fn set_limit(&self, new_limit: usize) {
        self.limit.store(new_limit, Ordering::Relaxed);
    }
}

impl Clone for ConcurrencyLimiter {
    fn clone(&self) -> Self {
        Self {
            semaphore: self.semaphore.clone(),
            limit: self.limit.clone(),
        }
    }
}