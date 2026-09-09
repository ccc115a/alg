//! BTree in-memory engine — similar to SQLite, supports SQL operations
//!
//! Implemented using `BTreeMap`, all operations are O(log n) time complexity.
//! BTreeMap keys are ordered, so it supports ORDER BY and range scans.
//!
//! Suitable for scenarios requiring sorting and range queries.

use std::collections::BTreeMap;
use std::fs::{File, OpenOptions};
use std::io::{Read, Write};
use std::path::Path;
use crate::engine::{EngineStats, StorageEngine};
use crate::error::Result;

/// BTree in-memory engine
///
/// Internal structure: `HashMap<table_id, BTreeMap<key, value>>`
/// - Outer HashMap uses table_id to separate different table spaces
/// - Inner BTreeMap stores key-value pairs in order, supporting range scans
pub struct BTreeMemoryEngine {
    /// Multi-table map: table_id → BTreeMap<Vec<u8>, Vec<u8>>
    tables: std::collections::HashMap<u32, BTreeMap<Vec<u8>, Vec<u8>>>,
    /// Optional disk path (for persistence)
    path: Option<std::path::PathBuf>,
}

impl BTreeMemoryEngine {
    /// Create a new in-memory engine without persistence
    pub fn new() -> Self {
        BTreeMemoryEngine {
            tables: std::collections::HashMap::new(),
            path: None,
        }
    }

    /// Load from disk or create a persistent engine
    ///
    /// Data is stored in `path/btree.dat` using bincode serialization.
    pub fn open(path: &Path) -> Result<Self> {
        std::fs::create_dir_all(path)?;

        let data_path = path.join("btree.dat");

        let tables = if data_path.exists() {
            let mut file = File::open(&data_path)?;
            let mut contents = Vec::new();
            file.read_to_end(&mut contents)?;

            match bincode::deserialize(&contents) {
                Ok(t) => t,
                Err(_) => std::collections::HashMap::new(),
            }
        } else {
            std::collections::HashMap::new()
        };

        Ok(BTreeMemoryEngine {
            tables,
            path: Some(path.to_path_buf()),
        })
    }

    /// Write data back to disk (persistence)
    ///
    /// Uses atomic write pattern to prevent data corruption:
    /// 1. First write to a temp file `btree.tmp`
    /// 2. Then atomically replace the original file via `rename`
    fn save(&self) -> Result<()> {
        if let Some(ref path) = self.path {
            let temp_path = path.join("btree.tmp");
            let data_path = path.join("btree.dat");

            let mut file = OpenOptions::new()
                .create(true)
                .write(true)
                .truncate(true)
                .open(&temp_path)?;

            let data = bincode::serialize(&self.tables)
                .map_err(|e| std::io::Error::new(std::io::ErrorKind::Other, format!("bincode: {:?}", e)))?;

            file.write_all(&data)?;
            drop(file);

            std::fs::rename(&temp_path, &data_path)?;
        }
        Ok(())
    }

    /// Get a read-only reference to the BTreeMap for the given table_id
    fn table(&self, table_id: u32) -> Option<&BTreeMap<Vec<u8>, Vec<u8>>> {
        self.tables.get(&table_id)
    }

    /// Get or create a mutable reference to the BTreeMap for the given table_id
    fn table_mut(&mut self, table_id: u32) -> &mut BTreeMap<Vec<u8>, Vec<u8>> {
        if !self.tables.contains_key(&table_id) {
            self.tables.insert(table_id, BTreeMap::new());
        }
        self.tables.get_mut(&table_id).unwrap()
    }
}

impl Default for BTreeMemoryEngine {
    fn default() -> Self {
        Self::new()
    }
}

// ===== StorageEngine trait implementation =====

impl StorageEngine for BTreeMemoryEngine {
    fn open(path: &std::path::Path) -> Result<Box<dyn StorageEngine>> {
        Ok(Box::new(Self::open(path)?))
    }

    fn open_memory() -> Box<dyn StorageEngine> {
        Box::new(Self::new())
    }

    fn engine_type(&self) -> &'static str {
        "memory-btree"
    }

    fn get(&self, table_id: u32, key: &[u8]) -> Result<Option<Vec<u8>>> {
        Ok(self.table(table_id).and_then(|t| t.get(key).cloned()))
    }

    fn put(&mut self, table_id: u32, key: &[u8], value: &[u8]) -> Result<()> {
        self.table_mut(table_id).insert(key.to_vec(), value.to_vec());
        Ok(())
    }

    fn delete(&mut self, table_id: u32, key: &[u8]) -> Result<()> {
        self.table_mut(table_id).remove(key);
        Ok(())
    }

    fn scan(&self, table_id: u32, start: &[u8], end: &[u8]) -> Result<Vec<(Vec<u8>, Vec<u8>)>> {
        use std::collections::Bound;
        let table = match self.table(table_id) {
            Some(t) => t,
            None => return Ok(Vec::new()),
        };

        let start_bound = if start.is_empty() {
            Bound::Unbounded
        } else {
            Bound::Included(start.to_vec())
        };
        let end_bound = if end.is_empty() {
            Bound::Unbounded
        } else {
            Bound::Excluded(end.to_vec())
        };

        let iter = table.range((start_bound, end_bound));
        Ok(iter.map(|(k, v)| (k.clone(), v.clone())).collect())
    }

    fn batch_put(&mut self, table_id: u32, pairs: Vec<(Vec<u8>, Vec<u8>)>) -> Result<()> {
        let table = self.table_mut(table_id);
        for (key, value) in pairs {
            table.insert(key, value);
        }
        Ok(())
    }

    fn range_delete(&mut self, table_id: u32, start: &[u8], end: &[u8]) -> Result<()> {
        use std::collections::Bound;
        let table = self.table_mut(table_id);

        let start_bound = if start.is_empty() {
            Bound::Unbounded
        } else {
            Bound::Included(start.to_vec())
        };
        let end_bound = if end.is_empty() {
            Bound::Unbounded
        } else {
            Bound::Excluded(end.to_vec())
        };

        let keys: Vec<Vec<u8>> = table.range((start_bound, end_bound)).map(|(k, _)| k.clone()).collect();
        for key in keys {
            table.remove(&key);
        }
        Ok(())
    }

    fn flush(&mut self) -> Result<()> {
        self.save()
    }

    fn sync(&mut self) -> Result<()> {
        self.save()
    }

    fn begin_transaction(&mut self) -> Result<()> {
        Err(crate::error::Error::NotSupported("Memory engine does not support transactions".into()))
    }

    fn commit_transaction(&mut self) -> Result<()> {
        Err(crate::error::Error::NotSupported("Memory engine does not support transactions".into()))
    }

    fn rollback_transaction(&mut self) -> Result<()> {
        Err(crate::error::Error::NotSupported("Memory engine does not support transactions".into()))
    }

    fn has_transaction(&self) -> bool {
        false
    }

    fn stats(&self) -> EngineStats {
        let total_keys: u64 = self.tables.values().map(|t| t.len() as u64).sum();
        EngineStats {
            key_count: total_keys,
            size_bytes: 0,
            cache_hit_rate: None,
            in_transaction: false,
            engine: "memory-btree",
        }
    }
}

// ===== Unit tests =====

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_btree_basic() {
        let mut engine = BTreeMemoryEngine::new();
        engine.put(1, b"hello", b"world").unwrap();
        assert_eq!(engine.get(1, b"hello").unwrap(), Some(b"world".to_vec()));
        assert_eq!(engine.get(1, b"missing").unwrap(), None);
    }

    #[test]
    fn test_btree_scan() {
        let mut engine = BTreeMemoryEngine::new();
        engine.put(1, b"a", b"1").unwrap();
        engine.put(1, b"b", b"2").unwrap();
        engine.put(1, b"c", b"3").unwrap();

        let results = engine.scan(1, b"a", b"c").unwrap();
        assert_eq!(results.len(), 2);
    }

    #[test]
    fn test_btree_delete() {
        let mut engine = BTreeMemoryEngine::new();
        engine.put(1, b"k", b"v").unwrap();
        engine.delete(1, b"k").unwrap();
        assert_eq!(engine.get(1, b"k").unwrap(), None);
    }

    #[test]
    fn test_btree_multi_table() {
        let mut engine = BTreeMemoryEngine::new();
        engine.put(1, b"key", b"table1").unwrap();
        engine.put(2, b"key", b"table2").unwrap();
        assert_eq!(engine.get(1, b"key").unwrap(), Some(b"table1".to_vec()));
        assert_eq!(engine.get(2, b"key").unwrap(), Some(b"table2".to_vec()));
    }

    #[test]
    fn test_btree_order() {
        let mut engine = BTreeMemoryEngine::new();
        engine.put(1, b"c", b"3").unwrap();
        engine.put(1, b"a", b"1").unwrap();
        engine.put(1, b"b", b"2").unwrap();

        let results = engine.scan(1, b"", b"").unwrap();
        let keys: Vec<_> = results.iter().map(|(k, _)| k.clone()).collect();
        assert_eq!(keys, vec![b"a".to_vec(), b"b".to_vec(), b"c".to_vec()]);
    }

    #[test]
    fn test_btree_persistence() {
        let temp_dir = std::env::temp_dir().join("db6_btree_mem_persist_test");
        let _ = std::fs::remove_dir_all(&temp_dir);

        // Phase 1: write data and flush
        {
            let mut engine = BTreeMemoryEngine::open(Path::new(&temp_dir)).unwrap();
            engine.put(1, b"key1", b"value1").unwrap();
            engine.put(1, b"key2", b"value2").unwrap();
            engine.flush().unwrap();
        }

        // Phase 2: reopen and verify
        {
            let engine = BTreeMemoryEngine::open(Path::new(&temp_dir)).unwrap();
            assert_eq!(engine.get(1, b"key1").unwrap(), Some(b"value1".to_vec()));
            assert_eq!(engine.get(1, b"key2").unwrap(), Some(b"value2".to_vec()));
        }

        let _ = std::fs::remove_dir_all(&temp_dir);
    }
}

// BTree memory engine capabilities:
// - CanOrderBy: supports ORDER BY (BTreeMap is ordered)
// - CanScan: supports range scan
// - CanBatch: supports batch operations
// - CanFts: supports full-text search
// - CanGroupBy: supports GROUP BY aggregation
impl crate::engine::CanOrderBy for BTreeMemoryEngine {}
impl crate::engine::CanScan for BTreeMemoryEngine {}
impl crate::engine::CanBatch for BTreeMemoryEngine {}
impl crate::engine::CanFts for BTreeMemoryEngine {}
impl crate::engine::CanGroupBy for BTreeMemoryEngine {}