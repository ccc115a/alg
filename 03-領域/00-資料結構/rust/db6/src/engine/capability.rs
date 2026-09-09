//! Capability marker system
//!
//! Because the `StorageEngine` trait uses `where Self: Sized` on factory methods, it cannot be used as `Box<dyn StorageEngine>`.
//! Capability marker traits are used instead to indicate at compile time which features an engine supports.
//!
//! If an engine does not support a feature (e.g., JOIN), the executor returns an error at runtime rather than forbidding it at compile time.

use crate::engine::StorageEngine;

/// Marks that an engine supports ORDER BY sorting
///
/// Requires the engine's scan() to traverse keys in order (BTreeMap, BTree Engine natively support this).
pub trait CanOrderBy: StorageEngine {}

/// Marks that an engine supports JOIN operations
///
/// JOIN requires the engine to perform multiple scans within the same table_id and correlate results.
pub trait CanJoin: StorageEngine {}

/// Marks that an engine supports Full-Text Search (FTS)
///
/// FTS requires the engine to support prefix scans for traversing inverted indices.
pub trait CanFts: StorageEngine {}

/// Marks that an engine supports transactions
///
/// Transactions require begin/commit/rollback semantics.
pub trait CanTransaction: StorageEngine {}

/// Marks that an engine supports range scans
///
/// All engines should support scan(); this marker is used for semantic distinction.
pub trait CanScan: StorageEngine {}

/// Marks that an engine supports batch operations
///
/// Optimized implementations of batch_put and range_delete.
pub trait CanBatch: StorageEngine {}

/// Marks that an engine supports GROUP BY and aggregate functions
///
/// Aggregate functions include COUNT, SUM, AVG, MIN, MAX, etc.
pub trait CanGroupBy: StorageEngine {}

/// Helper macro for quickly implementing capability markers
///
/// Accepts an engine type and one or more capability traits, automatically generating the corresponding impl blocks.
/// For example, `impl_capabilities!(HashMemoryEngine, CanOrderBy, CanScan)` expands to:
/// `impl CanOrderBy for HashMemoryEngine {}` and `impl CanScan for HashMemoryEngine {}`.
#[macro_export]
macro_rules! impl_capabilities {
    ($engine:ident, $( $cap:ident ),*) => {
        $(
            impl $crate::engine::capability::$cap for $engine {}
        )*
    };
}
