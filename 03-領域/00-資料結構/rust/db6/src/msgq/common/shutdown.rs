//! GracefulShutdown — Graceful shutdown mechanism based on tokio broadcast
//!
//! Similar to mini-redis design: coordinates shutdown timing for multiple async tasks.
//! When a shutdown signal is sent, all subscribed tasks receive the notification.

use std::sync::Arc;
use tokio::sync::broadcast;

/// Graceful shutdown coordinator
pub struct GracefulShutdown {
    /// broadcast channel sender
    shutdown_tx: broadcast::Sender<()>,
}

impl GracefulShutdown {
    /// Create a new shutdown coordinator
    pub fn new() -> Self {
        let (tx, _) = broadcast::channel(1);
        Self { shutdown_tx: tx }
    }

    /// Subscribe to the shutdown signal
    ///
    /// Each thread/task needs its own Receiver.
    pub fn subscribe(&self) -> broadcast::Receiver<()> {
        self.shutdown_tx.subscribe()
    }

    /// Trigger shutdown: send signal to all subscribers
    pub fn shutdown(&self) {
        let _ = self.shutdown_tx.send(());
    }

    /// Check if shutdown signal has been received
    ///
    /// Note: This method currently returns false (needs additional state tracking).
    pub fn is_shutdown(&self) -> bool {
        false
    }
}

impl Default for GracefulShutdown {
    fn default() -> Self {
        Self::new()
    }
}

impl Clone for GracefulShutdown {
    fn clone(&self) -> Self {
        Self {
            shutdown_tx: self.shutdown_tx.clone(),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    /// Test shutdown signal send and receive
    #[tokio::test]
    async fn test_shutdown_signal() {
        let gs = GracefulShutdown::new();

        let mut rx1 = gs.subscribe();
        let mut rx2 = gs.subscribe();

        gs.shutdown();

        rx1.recv().await.unwrap();
        rx2.recv().await.unwrap();
    }

    /// Test multiple subscribers receiving shutdown signal simultaneously
    #[tokio::test]
    async fn test_multiple_subscribers() {
        let gs = GracefulShutdown::new();

        let mut receivers = Vec::new();
        for _ in 0..5 {
            receivers.push(gs.subscribe());
        }

        gs.shutdown();

        for rx in receivers.iter_mut() {
            rx.recv().await.unwrap();
        }
    }
}