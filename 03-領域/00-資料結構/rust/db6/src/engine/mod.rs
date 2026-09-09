//! Storage engine abstraction layer
//!
//! Defines two interface layers:
//! - [`StorageEngine`] — Low-level interface providing table_id isolation, flush/sync/transaction, etc.
//! - [`KvStore`] — Lightweight interface directly invoked by the SQL layer; the executor uses this to operate the engine
//!
//! All engines (Memory/BTree/LSM) implement both `StorageEngine` + `KvStore`.
//! Engines are interchangeable; users can dynamically select one by name.

pub mod memory;
pub mod btree;
pub mod lsm;
pub mod capability;

pub use memory::{HashMemoryEngine, BTreeMemoryEngine};
pub use btree::BTreeEngine;
pub use lsm::LsmEngine;
pub use capability::{CanOrderBy, CanJoin, CanFts, CanTransaction, CanScan, CanBatch, CanGroupBy};

use crate::error::Result;

/// Engine statistics for monitoring and debugging
///
/// - `key_count`: Current number of stored keys
/// - `size_bytes`: Estimated storage size
/// - `cache_hit_rate`: Cache hit rate (only supported by some engines)
/// - `in_transaction`: Whether a transaction is active
/// - `engine`: Engine type name string
#[derive(Debug, Clone, Default)]
pub struct EngineStats {
    pub key_count: u64,
    pub size_bytes: u64,
    pub cache_hit_rate: Option<f64>,
    pub in_transaction: bool,
    pub engine: &'static str,
}

/// Low-level storage engine interface
///
/// Defines the operations that all storage engines must implement, including:
/// - Basic KV operations (get/put/delete/scan)
/// - Batch operations (batch_put/range_delete)
/// - Persistence (flush/sync)
/// - Transaction support (begin/commit/rollback)
/// - Observability (stats)
///
/// The `table_id` parameter enables multi-table isolation; different tables share the same engine without interference.
pub trait StorageEngine: Send + Sync {
    // ── Factory methods ────────────────────────────────────────────────────────

    /// Open or create a disk-based database (BTree/LSM only)
    fn open(path: &std::path::Path) -> Result<Box<dyn StorageEngine>>
    where
        Self: Sized;

    /// Create an in-memory database
    fn open_memory() -> Box<dyn StorageEngine>
    where
        Self: Sized;

    /// Return the engine type name string
    fn engine_type(&self) -> &'static str;

    // ── Basic KV operations ─────────────────────────────────────────────────

    /// Read a key-value entry from the specified table
    fn get(&self, table_id: u32, key: &[u8]) -> Result<Option<Vec<u8>>>;

    /// Write or update a key-value entry in the specified table
    fn put(&mut self, table_id: u32, key: &[u8], value: &[u8]) -> Result<()>;

    /// Delete a key-value entry from the specified table (uses tombstone marker)
    fn delete(&mut self, table_id: u32, key: &[u8]) -> Result<()>;

    /// Range scan [start, end), return all key-value pairs in the range
    fn scan(&self, table_id: u32, start: &[u8], end: &[u8]) -> Result<Vec<(Vec<u8>, Vec<u8>)>>;

    /// Batch write multiple key-value pairs (performance optimization, reduces locking/log overhead)
    fn batch_put(&mut self, table_id: u32, pairs: Vec<(Vec<u8>, Vec<u8>)>) -> Result<()>;

    /// Range delete [start, end), delete all keys in the range
    fn range_delete(&mut self, table_id: u32, start: &[u8], end: &[u8]) -> Result<()>;

    // ── FTS (Full-Text Search) note ───────────────────────────────────────────
    // FTS is not accessed through StorageEngine directly but via FtsIndex:
    //   let mut fts = FtsIndex::new(engine);
    //   fts.insert(doc_id, text)?;
    //   let results = fts.search(query)?;

    // ── Persistence operations ──────────────────────────────────────────────

    /// Flush dirty data from memory to disk
    fn flush(&mut self) -> Result<()>;

    /// Execute fsync to ensure data is persisted (no data loss)
    fn sync(&mut self) -> Result<()>;

    // ── Transaction support ──────────────────────────────────────────────────

    /// Begin a new transaction
    fn begin_transaction(&mut self) -> Result<()>;

    /// Commit the current transaction, making all changes permanent
    fn commit_transaction(&mut self) -> Result<()>;

    /// Rollback the current transaction, discarding all uncommitted changes
    fn rollback_transaction(&mut self) -> Result<()>;

    /// Check whether a transaction is currently active
    fn has_transaction(&self) -> bool;

    // ── Observability ────────────────────────────────────────────────────────

    /// Get current engine statistics
    fn stats(&self) -> EngineStats;
}

/// Lightweight KV interface directly used by the SQL executor
///
/// Unlike StorageEngine, this trait does not require flush/sync/transaction,
/// as those operations are managed at a higher level by the SQL Executor.
///
/// All engines (Memory/BTree/LSM) implement `impl KvStore for XxxEngine`.
pub trait KvStore: Send + Sync {
    /// Return the engine type name (defaults to "unknown")
    fn engine_type(&self) -> &'static str { "unknown" }

    /// Write a key-value entry
    fn put(&mut self, table_id: u32, key: &[u8], value: &[u8]) -> Result<()>;

    /// Read a key-value entry
    fn get(&mut self, table_id: u32, key: &[u8]) -> Result<Option<Vec<u8>>>;

    /// Delete a key-value entry
    fn delete(&mut self, table_id: u32, key: &[u8]) -> Result<()>;

    /// Range scan
    fn scan(&self, table_id: u32, start: &[u8], end: &[u8]) -> Result<Vec<(Vec<u8>, Vec<u8>)>>;
}