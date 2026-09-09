use thiserror::Error;

#[derive(Debug, Clone, Error)]
pub enum Error {
    #[error("IO error: {0}")]
    Io(String),

    #[error("key not found")]
    KeyNotFound,

    #[error("operation not supported: {0}")]
    NotSupported(String),

    #[error("data corruption: {0}")]
    Corruption(String),

    #[error("transaction error: {0}")]
    TransactionError(String),

    #[error("transaction: {0}")]
    Transaction(String),

    #[error("invalid configuration: {0}")]
    InvalidConfig(String),

    #[error("invalid engine: {0}")]
    InvalidEngine(String),

    #[error("SQL error: {0}")]
    Sql(String),
}

pub type Result<T> = std::result::Result<T, Error>;

impl From<std::io::Error> for Error {
    fn from(e: std::io::Error) -> Self {
        Error::Io(e.to_string())
    }
}