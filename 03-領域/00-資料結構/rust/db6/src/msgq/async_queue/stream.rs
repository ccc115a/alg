//! AsyncQueue Stream interface — implements futures::stream::Stream trait
//!
//! Allows consumers to consume messages using `while let` syntax.

use super::queue::AsyncQueue;
use super::AsyncQueueMessage;
use futures::stream::Stream;
use std::collections::VecDeque;
use std::pin::Pin;
use std::task::{Context, Poll};

/// Async queue stream
///
/// Wraps AsyncQueue and implements the Stream trait,
/// allowing consumers to consume messages like an iterator.
pub struct AsyncQueueStream {
    /// Underlying queue
    queue: AsyncQueue,
    /// Internal buffer (for async boundary)
    buffer: VecDeque<AsyncQueueMessage>,
}

impl AsyncQueueStream {
    /// Create stream
    pub fn new(queue: AsyncQueue) -> Self {
        Self {
            queue,
            buffer: VecDeque::new(),
        }
    }
}

impl Stream for AsyncQueueStream {
    type Item = Result<AsyncQueueMessage, String>;

    /// Poll for the next message
    fn poll_next(mut self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Option<Self::Item>> {
        if let Some(msg) = self.buffer.pop_front() {
            return Poll::Ready(Some(Ok(msg)));
        }

        let queue = &mut self.queue;
        match futures::executor::block_on(queue.dequeue(0)) {
            Ok(Some(msg)) => Poll::Ready(Some(Ok(msg))),
            Ok(None) => {
                cx.waker().wake_by_ref();
                Poll::Pending
            }
            Err(e) => Poll::Ready(Some(Err(e))),
        }
    }
}

impl AsyncQueue {
    pub fn stream(self) -> AsyncQueueStream {
        AsyncQueueStream::new(self)
    }
}
