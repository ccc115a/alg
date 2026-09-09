//! Message queue error types
//!
//! Defines MsgqError, the message queue specific error type using thiserror.
//! Separated from the underlying db6 Error for clearer error semantics.

use thiserror::Error;
use crate::error::Error as DbError;

/// Message queue error
#[derive(Error, Debug)]
pub enum MsgqError {
    /// Queue not found
    #[error("Queue not found: {0}")]
    QueueNotFound(String),

    /// Queue is empty
    #[error("Queue is empty")]
    QueueEmpty,

    /// Message not found
    #[error("Message not found: {0}")]
    MessageNotFound(String),

    /// Message is being processed
    #[error("Message in flight, please wait")]
    MessageInFlight,

    /// Invalid message format
    #[error("Invalid message format: {0}")]
    InvalidFormat(String),

    /// Invalid engine type
    #[error("Invalid engine type: {0}")]
    InvalidEngine(String),

    /// Invalid operation
    #[error("Invalid operation: {0}")]
    InvalidOperation(String),

    /// IO error
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),

    /// Serialization error
    #[error("Serialization error: {0}")]
    Serde(#[from] serde_json::Error),

    /// Database error
    #[error("Database error: {0}")]
    Db(#[from] DbError),
}

/// Result alias
pub type Result<T> = std::result::Result<T, MsgqError>;
