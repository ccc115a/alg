//! Hash in-memory engine — similar to Redis, fast KV operations
//!
//! Implemented using `HashMap`, all operations are O(1) time complexity.
//! **Does not support** ORDER BY or range scans because HashMap does not guarantee key ordering.
//!
//! Suitable for scenarios requiring fast random access without sorting.

use std::collections::HashMap;
use std::fs::{File, OpenOptions};
use std::io::{Read, Write};
use std::path::Path;
use crate::engine::{EngineStats, StorageEngine};
use crate::error::Result;

/// Hash in-memory engine
///
/// Internal structure: `HashMap<table_id, HashMap<key, value>>`
/// - Outer HashMap uses table_id to separate different table spaces
/// - Inner HashMap stores the actual key-value pairs
pub struct HashMemoryEngine {
    /// Multi-table map: table_id → HashMap<Vec<u8>, Vec<u8>>
    tables: HashMap<u32, HashMap<Vec<u8>, Vec<u8>>>,
    /// Optional disk path (for persistence)
    path: Option<std::path::PathBuf>,
}

impl HashMemoryEngine {
    /// Create a new in-memory engine without persistence
    pub fn new() -> Self {
        HashMemoryEngine {
            tables: HashMap::new(),
            path: None,
        }
    }

    /// Load from disk or create a persistent engine
    ///
    /// Data is stored in `path/hashtable.dat` using bincode serialization.
    pub fn open(path: &Path) -> Result<Self> {
        std::fs::create_dir_all(path)?;

        let data_path = path.join("hashtable.dat");

        let tables = if data_path.exists() {
            let mut file = File::open(&data_path)?;
            let mut contents = Vec::new();
            file.read_to_end(&mut contents)?;

            // If deserialization fails (format change etc.), use empty HashMap
            match bincode::deserialize(&contents) {
                Ok(t) => t,
                Err(_) => HashMap::new(),
            }
        } else {
            HashMap::new()
        };

        Ok(HashMemoryEngine {
            tables,
            path: Some(path.to_path_buf()),
        })
    }

    /// Write data back to disk (persistence)
    ///
    /// Uses atomic write pattern to prevent data corruption:
    /// 1. First write to a temp file `hashtable.tmp`
    /// 2. Then atomically replace the original file via `rename`
    fn save(&self) -> Result<()> {
        if let Some(ref path) = self.path {
            let temp_path = path.join("hashtable.tmp");
            let data_path = path.join("hashtable.dat");

            // Step 1: Write to temp file
            let mut file = OpenOptions::new()
                .create(true)
                .write(true)
                .truncate(true)
                .open(&temp_path)?;

            let data = bincode::serialize(&self.tables)
                .map_err(|e| std::io::Error::new(std::io::ErrorKind::Other, format!("bincode: {:?}", e)))?;

            file.write_all(&data)?;
            drop(file);

            // Step 2: Atomic rename
            std::fs::rename(&temp_path, &data_path)?;
        }
        Ok(())
    }

    /// Get or create the HashMap for the given table_id
    fn table_mut(&mut self, table_id: u32) -> &mut HashMap<Vec<u8>, Vec<u8>> {
        self.tables.entry(table_id).or_insert_with(HashMap::new)
    }
}

impl Default for HashMemoryEngine {
    fn default() -> Self {
        Self::new()
    }
}

// ===== StorageEngine trait implementation =====

impl StorageEngine for HashMemoryEngine {
    fn open(path: &std::path::Path) -> Result<Box<dyn StorageEngine>> {
        Ok(Box::new(Self::open(path)?))
    }

    fn open_memory() -> Box<dyn StorageEngine> {
        Box::new(Self::new())
    }

    fn engine_type(&self) -> &'static str {
        "memory-hash"
    }

    fn get(&self, table_id: u32, key: &[u8]) -> Result<Option<Vec<u8>>> {
        Ok(self.tables.get(&table_id).and_then(|t| t.get(key).cloned()))
    }

    fn put(&mut self, table_id: u32, key: &[u8], value: &[u8]) -> Result<()> {
        self.table_mut(table_id).insert(key.to_vec(), value.to_vec());
        Ok(())
    }

    fn delete(&mut self, table_id: u32, key: &[u8]) -> Result<()> {
        self.table_mut(table_id).remove(key);
        Ok(())
    }

    fn scan(&self, table_id: u32, _start: &[u8], _end: &[u8]) -> Result<Vec<(Vec<u8>, Vec<u8>)>> {
        Ok(self.tables.get(&table_id)
            .map(|t| t.iter().map(|(k, v)| (k.clone(), v.clone())).collect())
            .unwrap_or_default())
    }

    fn batch_put(&mut self, table_id: u32, pairs: Vec<(Vec<u8>, Vec<u8>)>) -> Result<()> {
        let table = self.table_mut(table_id);
        for (key, value) in pairs {
            table.insert(key, value);
        }
        Ok(())
    }

    fn range_delete(&mut self, table_id: u32, _start: &[u8], _end: &[u8]) -> Result<()> {
        self.tables.remove(&table_id);
        Ok(())
    }

    fn flush(&mut self) -> Result<()> {
        self.save()
    }

    fn sync(&mut self) -> Result<()> {
        self.save()
    }

    fn begin_transaction(&mut self) -> Result<()> {
        Err(crate::error::Error::NotSupported("HashMemoryEngine does not support transactions".into()))
    }

    fn commit_transaction(&mut self) -> Result<()> {
        Err(crate::error::Error::NotSupported("HashMemoryEngine does not support transactions".into()))
    }

    fn rollback_transaction(&mut self) -> Result<()> {
        Err(crate::error::Error::NotSupported("HashMemoryEngine does not support transactions".into()))
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
            engine: "memory-hash",
        }
    }
}

// ===== Unit tests =====

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_hash_basic() {
        let mut engine = HashMemoryEngine::new();
        engine.put(1, b"hello", b"world").unwrap();
        assert_eq!(engine.get(1, b"hello").unwrap(), Some(b"world".to_vec()));
        assert_eq!(engine.get(1, b"missing").unwrap(), None);
    }

    #[test]
    fn test_hash_delete() {
        let mut engine = HashMemoryEngine::new();
        engine.put(1, b"k", b"v").unwrap();
        engine.delete(1, b"k").unwrap();
        assert_eq!(engine.get(1, b"k").unwrap(), None);
    }

    #[test]
    fn test_hash_multi_table() {
        let mut engine = HashMemoryEngine::new();
        engine.put(1, b"key", b"table1").unwrap();
        engine.put(2, b"key", b"table2").unwrap();
        assert_eq!(engine.get(1, b"key").unwrap(), Some(b"table1".to_vec()));
        assert_eq!(engine.get(2, b"key").unwrap(), Some(b"table2".to_vec()));
    }

    #[test]
    fn test_hash_scan_all() {
        let mut engine = HashMemoryEngine::new();
        engine.put(1, b"a", b"1").unwrap();
        engine.put(1, b"b", b"2").unwrap();

        let results = engine.scan(1, b"", b"").unwrap();
        assert_eq!(results.len(), 2);
    }

    #[test]
    fn test_hash_batch_put() {
        let mut engine = HashMemoryEngine::new();
        let pairs = vec![
            (b"k1".to_vec(), b"v1".to_vec()),
            (b"k2".to_vec(), b"v2".to_vec()),
        ];
        engine.batch_put(1, pairs).unwrap();
        assert_eq!(engine.get(1, b"k1").unwrap(), Some(b"v1".to_vec()));
        assert_eq!(engine.get(1, b"k2").unwrap(), Some(b"v2".to_vec()));
    }

    #[test]
    fn test_hash_persistence() {
        let temp_dir = std::env::temp_dir().join("db6_hash_persist_test");
        let _ = std::fs::remove_dir_all(&temp_dir);

        // Phase 1: write data and flush
        {
            let mut engine = HashMemoryEngine::open(Path::new(&temp_dir)).unwrap();
            engine.put(1, b"key1", b"value1").unwrap();
            engine.put(1, b"key2", b"value2").unwrap();
            engine.flush().unwrap();
        }

        // Phase 2: reopen and verify data still exists
        {
            let engine = HashMemoryEngine::open(Path::new(&temp_dir)).unwrap();
            assert_eq!(engine.get(1, b"key1").unwrap(), Some(b"value1".to_vec()));
            assert_eq!(engine.get(1, b"key2").unwrap(), Some(b"value2".to_vec()));
        }

        let _ = std::fs::remove_dir_all(&temp_dir);
    }
}

// Hash engine capability markers: supports batch operations and full-text search
impl crate::engine::CanBatch for HashMemoryEngine {}
impl crate::engine::CanFts for HashMemoryEngine {}