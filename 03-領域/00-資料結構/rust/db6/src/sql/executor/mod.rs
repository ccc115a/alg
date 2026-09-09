//! SQL executor — Executes query plans and returns result sets
//!
//! The execution layer is responsible for:
//! - Traversing the PlanNode execution plan tree
//! - Calling StorageEngine for actual data operations
//! - JSON path operations (JSON_EXTRACT, JSON_SET, etc.)
//! - Transaction management (BEGIN/COMMIT/ROLLBACK)
//!
//! Ported from sql6, modified to replace pager with StorageEngine trait.

pub mod executor;
pub mod json_path;
pub mod transaction;

pub use executor::{Executor, ResultSet, SqlExecutor};