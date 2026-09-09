//! Unified error type system
//!
//! Defines the shared `Error` and `Result` types for the entire db6 project, providing consistent error handling across all modules.
//! Uses the `thiserror` crate to automatically derive Display and Error implementations.

use thiserror::Error;

/// Global error type for db6
///
/// Covers errors from IO, key-value, transactions, configuration, engine, SQL, FTS, and other layers.
/// Each variant defines a human-readable error message via the `#[error("...")]` attribute.
#[derive(Debug, Clone, Error)]
pub enum Error {
    /// IO operation failed, e.g., file read/write error
    #[error("IO error: {0}")]
    Io(String),

    /// The specified key does not exist in the KV store
    #[error("key not found")]
    KeyNotFound,

    /// The requested operation is not supported (e.g., scanning an unsupported engine)
    #[error("operation not supported: {0}")]
    NotSupported(String),

    /// Data corruption detected (e.g., malformed BTree node, LSM SSTable checksum failure)
    #[error("data corruption: {0}")]
    Corruption(String),

    /// Transaction-related error (e.g., transaction not started)
    #[error("transaction error: {0}")]
    TransactionError(String),

    /// Transaction operation failed (e.g., error during commit or rollback)
    #[error("transaction: {0}")]
    Transaction(String),

    /// Invalid engine or system configuration
    #[error("invalid configuration: {0}")]
    InvalidConfig(String),

    /// Unknown storage engine type
    #[error("invalid engine: {0}")]
    InvalidEngine(String),

    /// SQL syntax or execution error
    #[error("SQL error: {0}")]
    Sql(String),

    /// Full-text search operation error
    #[error("FTS error: {0}")]
    Fts(String),
}

/// Unified Result alias for the project
///
/// Shorthand: `Result<T>` is equivalent to `std::result::Result<T, Error>`
pub type Result<T> = std::result::Result<T, Error>;

/// Automatically converts standard IO errors into db6 Error
impl From<std::io::Error> for Error {
    fn from(e: std::io::Error) -> Self {
        Error::Io(e.to_string())
    }
}