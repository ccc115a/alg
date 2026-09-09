//! SQL Executor submodule — wraps SQL execution as a message queue service
//!
//! ```text
//! Client -> [SQL Queue] -> Worker -> Database
//!                     ^
//!                Message Queue (based on tokio)
//! ```
//!
//! Supports both synchronous (SyncSqlExecutor) and asynchronous (AsyncSqlExecutor) modes.

mod types;
mod async_sql;
mod sync_sql;

pub use types::{JobResult, ResultStore, SqlJob, SqlResultStore};
pub use async_sql::AsyncSqlExecutor;
pub use sync_sql::SyncSqlExecutor;

use std::collections::HashMap;