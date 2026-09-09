//! Shared components — foundational tools for async programming
//!
//! Provides foundational components shared across multiple msgq components:
//! - ConcurrencyLimiter: Concurrency control based on tokio Semaphore
//! - GracefulShutdown: Graceful shutdown mechanism based on tokio Notify
//!
//! Design inspiration from the mini-redis project.

mod limiter;
mod shutdown;

pub use limiter::ConcurrencyLimiter;
pub use shutdown::GracefulShutdown;

use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;

/// Default concurrency limit
pub const DEFAULT_CONCURRENCY_LIMIT: usize = 100;

/// Create a new AtomicUsize for tracking concurrency limit
pub fn new_atomic_usize(value: usize) -> Arc<AtomicUsize> {
    Arc::new(AtomicUsize::new(value))
}