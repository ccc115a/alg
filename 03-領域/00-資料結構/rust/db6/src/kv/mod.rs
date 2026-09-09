//! KV API unified interface — factory pattern + unified KvStore abstraction layer
//!
//! Provides the `KvEngine` enum as a factory interface, allowing users to select
//! a storage engine by string name without dealing with concrete engine types directly.
//!
//! KvEngine uses `Arc<RwLock<...>>` for thread-safe shared access.

use std::path::Path;
use std::sync::{Arc, RwLock};
use crate::error::{Error, Result};
use crate::engine::{EngineStats, StorageEngine};

/// KV Store unified interface
///
/// Defines all basic KV operations. Unlike StorageEngine,
/// this trait directly serves the upper SQL executor layer.
pub trait KvStore {
    /// Write a key-value pair
    fn put(&mut self, table_id: u32, key: &[u8], value: &[u8]) -> Result<()>;
    /// Read a key-value pair
    fn get(&self, table_id: u32, key: &[u8]) -> Result<Option<Vec<u8>>>;
    /// Delete a key-value pair
    fn delete(&mut self, table_id: u32, key: &[u8]) -> Result<()>;
    /// Range scan [start, end)
    fn scan(&self, table_id: u32, start: &[u8], end: &[u8]) -> Result<Vec<(Vec<u8>, Vec<u8>)>>;
    /// Batch write
    fn batch_put(&mut self, table_id: u32, pairs: Vec<(Vec<u8>, Vec<u8>)>) -> Result<()>;
    /// Range delete
    fn range_delete(&mut self, table_id: u32, start: &[u8], end: &[u8]) -> Result<()>;
    /// Flush data to disk
    fn flush(&mut self) -> Result<()>;
    /// Get engine type name
    fn engine_type(&self) -> &'static str;
}

/// KV Engine enum
///
/// Wraps four different storage engine implementations, created via `new()` or `open()` factory methods.
///
/// | Variant | new() Name | open() Support | Features |
/// |------|-----------|------------|------|
/// | Hash | "memory"/"hash" | no | O(1) random access |
/// | BTreeMem | "btree"/"btree-mem" | no | Ordered, range scan |
/// | BTree | not directly | "btree" | Disk persistence, transactions |
/// | Lsm | "lsm" | "lsm" | High write throughput |
pub enum KvEngine {
    /// HashMap memory engine (O(1), does not support ORDER BY)
    Hash(Arc<RwLock<crate::engine::HashMemoryEngine>>),
    /// BTreeMap memory engine (O(log n), supports ORDER BY)
    BTreeMem(Arc<RwLock<crate::engine::BTreeMemoryEngine>>),
    /// Disk BTree engine (supports transactions)
    BTree(Arc<RwLock<crate::engine::BTreeEngine>>),
    /// LSM-Tree engine (high write throughput)
    Lsm(Arc<RwLock<crate::engine::LsmEngine>>),
}

impl KvEngine {
    /// Create an in-memory engine
    ///
    /// - `"memory"` or `"hash"`: HashMap engine
    /// - `"btree"` or `"btree-mem"`: BTreeMap engine
    /// - `"lsm"`: LSM engine (in-memory mode)
    pub fn new(engine_type: &str) -> Result<Self> {
        match engine_type.to_lowercase().as_str() {
            "memory" | "hash" => Ok(KvEngine::Hash(Arc::new(RwLock::new(crate::engine::HashMemoryEngine::new())))),
            "btree" | "btree-mem" => Ok(KvEngine::BTreeMem(Arc::new(RwLock::new(crate::engine::BTreeMemoryEngine::new())))),
            "lsm" => Ok(KvEngine::Lsm(Arc::new(RwLock::new(crate::engine::LsmEngine::new())))),
            _ => Err(crate::error::Error::InvalidEngine(engine_type.to_string())),
        }
    }

    /// Create a persistent (on-disk) engine
    ///
    /// - `"btree"`: Open BTree engine from path
    /// - `"lsm"`: Open LSM engine from path
    pub fn open(engine_type: &str, path: &Path) -> Result<Self> {
        match engine_type.to_lowercase().as_str() {
            "btree" => Ok(KvEngine::BTree(Arc::new(RwLock::new(crate::engine::BTreeEngine::open(path)?)))),
            "lsm" => Ok(KvEngine::Lsm(Arc::new(RwLock::new(crate::engine::LsmEngine::open(path)?)))),
            _ => Err(crate::error::Error::InvalidEngine(format!("{} does not support open(path)", engine_type))),
        }
    }
}

// ===== KvStore trait 實作：委派給具體引擎 =====
// 透過 match 委派給內部的具體引擎實作。

impl KvStore for KvEngine {
    fn put(&mut self, table_id: u32, key: &[u8], value: &[u8]) -> Result<()> {
        match self {
            KvEngine::Hash(e) => e.write().unwrap().put(table_id, key, value),
            KvEngine::BTreeMem(e) => e.write().unwrap().put(table_id, key, value),
            KvEngine::BTree(e) => e.write().unwrap().put(table_id, key, value),
            KvEngine::Lsm(e) => e.write().unwrap().put(table_id, key, value),
        }
    }

    fn get(&self, table_id: u32, key: &[u8]) -> Result<Option<Vec<u8>>> {
        match self {
            KvEngine::Hash(e) => e.read().unwrap().get(table_id, key),
            KvEngine::BTreeMem(e) => e.read().unwrap().get(table_id, key),
            KvEngine::BTree(e) => e.read().unwrap().get(table_id, key),
            KvEngine::Lsm(e) => e.read().unwrap().get(table_id, key),
        }
    }

    fn delete(&mut self, table_id: u32, key: &[u8]) -> Result<()> {
        match self {
            KvEngine::Hash(e) => e.write().unwrap().delete(table_id, key),
            KvEngine::BTreeMem(e) => e.write().unwrap().delete(table_id, key),
            KvEngine::BTree(e) => e.write().unwrap().delete(table_id, key),
            KvEngine::Lsm(e) => e.write().unwrap().delete(table_id, key),
        }
    }

    fn scan(&self, table_id: u32, start: &[u8], end: &[u8]) -> Result<Vec<(Vec<u8>, Vec<u8>)>> {
        match self {
            KvEngine::Hash(e) => e.read().unwrap().scan(table_id, start, end),
            KvEngine::BTreeMem(e) => e.read().unwrap().scan(table_id, start, end),
            KvEngine::BTree(e) => e.read().unwrap().scan(table_id, start, end),
            KvEngine::Lsm(e) => e.read().unwrap().scan(table_id, start, end),
        }
    }

    fn batch_put(&mut self, table_id: u32, pairs: Vec<(Vec<u8>, Vec<u8>)>) -> Result<()> {
        match self {
            KvEngine::Hash(e) => e.write().unwrap().batch_put(table_id, pairs),
            KvEngine::BTreeMem(e) => e.write().unwrap().batch_put(table_id, pairs),
            KvEngine::BTree(e) => e.write().unwrap().batch_put(table_id, pairs),
            KvEngine::Lsm(e) => e.write().unwrap().batch_put(table_id, pairs),
        }
    }

    fn range_delete(&mut self, table_id: u32, start: &[u8], end: &[u8]) -> Result<()> {
        match self {
            KvEngine::Hash(e) => e.write().unwrap().range_delete(table_id, start, end),
            KvEngine::BTreeMem(e) => e.write().unwrap().range_delete(table_id, start, end),
            KvEngine::BTree(e) => e.write().unwrap().range_delete(table_id, start, end),
            KvEngine::Lsm(e) => e.write().unwrap().range_delete(table_id, start, end),
        }
    }

    fn flush(&mut self) -> Result<()> {
        match self {
            KvEngine::Hash(e) => e.write().unwrap().flush(),
            KvEngine::BTreeMem(e) => e.write().unwrap().flush(),
            KvEngine::BTree(e) => e.write().unwrap().flush(),
            KvEngine::Lsm(e) => e.write().unwrap().flush(),
        }
    }

    fn engine_type(&self) -> &'static str {
        match self {
            KvEngine::Hash(e) => e.read().unwrap().engine_type(),
            KvEngine::BTreeMem(e) => e.read().unwrap().engine_type(),
            KvEngine::BTree(e) => e.read().unwrap().engine_type(),
            KvEngine::Lsm(e) => e.read().unwrap().engine_type(),
        }
    }
}

// ===== StorageEngine trait 實作 =====

impl StorageEngine for KvEngine {
    fn open(path: &std::path::Path) -> Result<Box<dyn StorageEngine>>
    where
        Self: Sized,
    {
        Ok(Box::new(KvEngine::open("btree", path)?))
    }

    fn open_memory() -> Box<dyn StorageEngine>
    where
        Self: Sized,
    {
        Box::new(KvEngine::new("memory").unwrap())
    }

    fn engine_type(&self) -> &'static str {
        <Self as KvStore>::engine_type(self)
    }

    fn get(&self, table_id: u32, key: &[u8]) -> Result<Option<Vec<u8>>> {
        KvStore::get(self, table_id, key)
    }

    fn put(&mut self, table_id: u32, key: &[u8], value: &[u8]) -> Result<()> {
        KvStore::put(self, table_id, key, value)
    }

    fn delete(&mut self, table_id: u32, key: &[u8]) -> Result<()> {
        KvStore::delete(self, table_id, key)
    }

    fn scan(&self, table_id: u32, start: &[u8], end: &[u8]) -> Result<Vec<(Vec<u8>, Vec<u8>)>> {
        KvStore::scan(self, table_id, start, end)
    }

    fn batch_put(&mut self, table_id: u32, pairs: Vec<(Vec<u8>, Vec<u8>)>) -> Result<()> {
        KvStore::batch_put(self, table_id, pairs)
    }

    fn range_delete(&mut self, table_id: u32, start: &[u8], end: &[u8]) -> Result<()> {
        KvStore::range_delete(self, table_id, start, end)
    }

    fn flush(&mut self) -> Result<()> {
        KvStore::flush(self)
    }

    fn sync(&mut self) -> Result<()> {
        match self {
            KvEngine::Hash(e) => e.write().unwrap().sync(),
            KvEngine::BTreeMem(e) => e.write().unwrap().sync(),
            KvEngine::BTree(e) => e.write().unwrap().sync(),
            KvEngine::Lsm(e) => e.write().unwrap().sync(),
        }
    }

    fn begin_transaction(&mut self) -> Result<()> {
        match self {
            KvEngine::Hash(e) => e.write().unwrap().begin_transaction(),
            KvEngine::BTreeMem(e) => e.write().unwrap().begin_transaction(),
            KvEngine::BTree(e) => e.write().unwrap().begin_transaction(),
            KvEngine::Lsm(e) => e.write().unwrap().begin_transaction(),
        }
    }

    fn commit_transaction(&mut self) -> Result<()> {
        match self {
            KvEngine::Hash(e) => e.write().unwrap().commit_transaction(),
            KvEngine::BTreeMem(e) => e.write().unwrap().commit_transaction(),
            KvEngine::BTree(e) => e.write().unwrap().commit_transaction(),
            KvEngine::Lsm(e) => e.write().unwrap().commit_transaction(),
        }
    }

    fn rollback_transaction(&mut self) -> Result<()> {
        match self {
            KvEngine::Hash(e) => e.write().unwrap().rollback_transaction(),
            KvEngine::BTreeMem(e) => e.write().unwrap().rollback_transaction(),
            KvEngine::BTree(e) => e.write().unwrap().rollback_transaction(),
            KvEngine::Lsm(e) => e.write().unwrap().rollback_transaction(),
        }
    }

    fn has_transaction(&self) -> bool {
        match self {
            KvEngine::Hash(e) => e.read().unwrap().has_transaction(),
            KvEngine::BTreeMem(e) => e.read().unwrap().has_transaction(),
            KvEngine::BTree(e) => e.read().unwrap().has_transaction(),
            KvEngine::Lsm(e) => e.read().unwrap().has_transaction(),
        }
    }

    fn stats(&self) -> EngineStats {
        match self {
            KvEngine::Hash(e) => e.read().unwrap().stats(),
            KvEngine::BTreeMem(e) => e.read().unwrap().stats(),
            KvEngine::BTree(e) => e.read().unwrap().stats(),
            KvEngine::Lsm(e) => e.read().unwrap().stats(),
        }
    }
}

// ===== 單元測試 =====

#[cfg(test)]
mod tests {
    use super::*;

    /// Test creating an engine via KvEngine::new("memory") and performing operations
    #[test]
    fn test_kv_engine_new() {
        let mut kv = KvEngine::new("memory").unwrap();
        KvStore::put(&mut kv, 1, b"key", b"value").unwrap();
        assert_eq!(KvStore::get(&kv, 1, b"key").unwrap(), Some(b"value".to_vec()));
    }

    /// Test BTree memory engine
    #[test]
    fn test_kv_engine_btree_mem() {
        let mut kv = KvEngine::new("btree").unwrap();
        KvStore::put(&mut kv, 1, b"key", b"value").unwrap();
        assert_eq!(KvStore::get(&kv, 1, b"key").unwrap(), Some(b"value".to_vec()));
    }

    /// Test LSM engine
    #[test]
    fn test_kv_engine_lsm() {
        let mut kv = KvEngine::new("lsm").unwrap();
        KvStore::put(&mut kv, 1, b"key", b"value").unwrap();
        assert_eq!(KvStore::get(&kv, 1, b"key").unwrap(), Some(b"value".to_vec()));
    }

    /// Test disk persistence
    #[test]
    fn test_kv_engine_persistence() {
        let temp_dir = std::env::temp_dir().join("db6_kv_test");
        let _ = std::fs::remove_dir_all(&temp_dir);

        {
            let mut kv = KvEngine::open("btree", &temp_dir).unwrap();
            KvStore::put(&mut kv, 1, b"key1", b"value1").unwrap();
            KvStore::flush(&mut kv).unwrap();
        }

        {
            let kv = KvEngine::open("btree", &temp_dir).unwrap();
            assert_eq!(KvStore::get(&kv, 1, b"key1").unwrap(), Some(b"value1".to_vec()));
        }

        let _ = std::fs::remove_dir_all(&temp_dir);
    }
}