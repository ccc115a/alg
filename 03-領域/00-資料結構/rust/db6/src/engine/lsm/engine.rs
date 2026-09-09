//! LSM-Tree storage engine implementation
//!
//! LSM-Tree (Log-Structured Merge-Tree) is a data structure optimized for high write throughput.
//! Core concept: writes first go to in-memory MemTable, then are flushed to disk as SSTable when full.
//!
//! Write path:
//!   put → MemTable → (flush) → SSTable
//! Read path:
//!   get → MemTable → Bloom Filter → SSTables (newest to oldest)
//!
//! Limitation: currently only supports `table_id = 1` (single table namespace).

use std::collections::BTreeMap;
use std::path::Path;
use std::sync::RwLock;

use crate::engine::{EngineStats, StorageEngine};
use crate::error::{Error, Result};

use super::memtable::MemTable;
use super::sstable::SSTable;
use super::wal::Wal;
use super::bloom::BloomFilter;

/// LSM-Tree engine main structure
///
/// - `path`: persistence path
/// - `memtable`: in-memory write buffer
/// - `sstables`: on-disk SSTable collection (oldest to newest)
/// - `bloom`: Bloom filter for fast negative lookups
/// - `wal`: write-ahead log for data durability
/// - `in_transaction`: transaction state
/// - `tx_buffer`: transaction buffer
pub struct LsmEngine {
    path: Option<std::path::PathBuf>,
    memtable: RwLock<MemTable>,
    sstables: RwLock<Vec<SSTable>>,
    bloom: RwLock<BloomFilter>,
    wal: RwLock<Option<Wal>>,
    in_transaction: RwLock<bool>,
    tx_buffer: RwLock<Option<BTreeMap<Vec<u8>, Option<Vec<u8>>>>>,
}

impl LsmEngine {
    /// Create a new in-memory LSM engine (no persistence)
    pub fn new() -> Self {
        LsmEngine {
            path: None,
            memtable: RwLock::new(MemTable::new()),
            sstables: RwLock::new(Vec::new()),
            bloom: RwLock::new(BloomFilter::new(1024)),
            wal: RwLock::new(None),
            in_transaction: RwLock::new(false),
            tx_buffer: RwLock::new(None),
        }
    }

    /// Open or create an LSM engine from a disk path
    ///
    /// Startup sequence:
    /// 1. Scan directory for all `.sst` files, load existing SSTables
    /// 2. Try to open `wal.log` and replay unflushed data
    /// 3. Clear the WAL and create a new log
    pub fn open(path: &Path) -> Result<Self> {
        std::fs::create_dir_all(path)?;

        let mut engine = Self::new();
        engine.path = Some(path.to_path_buf());

        // 步驟1：載入現有的 SSTable
        if path.exists() {
            if let Ok(entries) = std::fs::read_dir(path) {
                let mut sstables = engine.sstables.write().unwrap();
                for entry in entries.flatten() {
                    let path = entry.path();
                    if path.extension().map_or(false, |ext| ext == "sst") {
                        if let Ok(ss) = SSTable::open(&path) {
                            sstables.push(ss);
                        }
                    }
                }
            }
        }

        // 步驟2：從 WAL 復原資料
        let wal_path = path.join("wal.log");
        if wal_path.exists() {
            let wal = Wal::open(&wal_path)?;
            let recovered = wal.recover()?;

            if !recovered.is_empty() {
                let mut memtable = engine.memtable.write().unwrap();
                for (k, v) in recovered {
                    memtable.put(k, v);
                }
            }

            // 清空 WAL（資料已復原到 MemTable）
            let _ = wal.clear();

            // 建立新的 WAL
            engine.wal = RwLock::new(Some(Wal::create(&wal_path)?));
        } else {
            // 建立新的 WAL
            engine.wal = RwLock::new(Some(Wal::create(&wal_path)?));
        }

        Ok(engine)
    }

    /// Flush MemTable to disk
    ///
    /// Process:
    /// 1. Read all data from MemTable
    /// 2. Update Bloom Filter
    /// 3. Write to WAL
    /// 4. Create a new SSTable file
    /// 5. Clear MemTable
    fn flush_memtable(&mut self) -> Result<()> {
        let data = {
            let mem = self.memtable.read().unwrap();
            mem.all_data()
        };

        if data.is_empty() {
            return Ok(());
        }

        // 更新 Bloom Filter
        for (k, _) in &data {
            self.bloom.write().unwrap().insert(k);
        }

        // 寫入 WAL
        if let Ok(wal) = self.wal.read() {
            if let Some(w) = wal.as_ref() {
                for (k, v) in &data {
                    w.write(k, v)?;
                }
            }
        }

        // 建立 SSTable（僅在有設定路徑時）
        if let Some(ref path) = self.path {
            let sstable_path = path.join(format!("{}.sst", std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_nanos()));

            let sstable = SSTable::create(&sstable_path, data)?;
            self.sstables.write().unwrap().push(sstable);
        }

        // 清空 MemTable
        self.memtable.write().unwrap().clear();

        Ok(())
    }

    /// Write to WAL only (no SSTable created)
    ///
    /// Used during transaction commit to ensure data durability,
    /// without triggering a MemTable → SSTable flush.
    fn sync_wal_only(&self) -> Result<()> {
        let data = {
            let mem = self.memtable.read().unwrap();
            mem.all_data()
        };

        for (k, _) in &data {
            self.bloom.write().unwrap().insert(k);
        }

        if let Ok(wal) = self.wal.read() {
            if let Some(w) = wal.as_ref() {
                for (k, v) in data {
                    w.write(&k, &v)?;
                }
            }
        }

        Ok(())
    }
}

impl Default for LsmEngine {
    fn default() -> Self {
        Self::new()
    }
}

// ===== StorageEngine trait 實作 =====

impl StorageEngine for LsmEngine {
    fn open(path: &Path) -> Result<Box<dyn StorageEngine>> {
        Ok(Box::new(Self::open(path)?))
    }

    fn open_memory() -> Box<dyn StorageEngine> {
        Box::new(Self::new())
    }

    fn engine_type(&self) -> &'static str {
        "lsm"
    }

    /// Read a single key
    ///
    /// Lookup path (fastest to slowest):
    /// 1. Transaction buffer
    /// 2. MemTable (in-memory)
    /// 3. Bloom Filter (fast exclusion)
    /// 4. SSTable (disk, newest to oldest)
    fn get(&self, table_id: u32, key: &[u8]) -> Result<Option<Vec<u8>>> {
        // 步驟1：查交易緩衝區
        if let Ok(tx) = self.tx_buffer.read() {
            if let Some(buffer) = tx.as_ref() {
                if let Some(value) = buffer.get(key) {
                    return match value {
                        Some(v) => Ok(Some(v.clone())),
                        None => Ok(None),
                    };
                }
            }
        }

        // 步驟2：查 MemTable
        let mem = self.memtable.read().unwrap();
        if let Some(v) = mem.get(key) {
            if v.is_data() {
                return Ok(Some(v.get_data().unwrap().clone()));
            } else {
                return Ok(None);
            }
        }
        drop(mem);

        // 步驟3：Bloom Filter 快速排除
        if !self.bloom.read().unwrap().might_contain(key) {
            return Ok(None);
        }

        // 步驟4：從 SSTable 由新到舊查詢
        let sstables = self.sstables.read().unwrap();
        for ss in sstables.iter().rev() {
            if let Some(v) = ss.get(key) {
                return Ok(Some(v));
            }
        }

        Ok(None)
    }

    /// Write a key-value pair (unlike BTree engine, all table_ids map to table_id=1 in LSM)
    fn put(&mut self, table_id: u32, key: &[u8], value: &[u8]) -> Result<()> {
        if table_id != 1 {
            return Err(Error::NotSupported("LSM engine only supports table_id=1".into()));
        }
        if *self.in_transaction.read().unwrap() {
            let mut tx = self.tx_buffer.write().unwrap();
            if tx.is_none() {
                *tx = Some(BTreeMap::new());
            }
            if let Some(ref mut buffer) = *tx {
                buffer.insert(key.to_vec(), Some(value.to_vec()));
            }
        } else {
            self.memtable.write().unwrap().put(key.to_vec(), value.to_vec());
        }
        Ok(())
    }

    /// Delete a key (using tombstone marker)
    fn delete(&mut self, table_id: u32, key: &[u8]) -> Result<()> {
        if table_id != 1 {
            return Err(Error::NotSupported("LSM engine only supports table_id=1".into()));
        }
        if *self.in_transaction.read().unwrap() {
            let mut tx = self.tx_buffer.write().unwrap();
            if tx.is_none() {
                *tx = Some(BTreeMap::new());
            }
            if let Some(ref mut buffer) = *tx {
                buffer.insert(key.to_vec(), None);
            }
        } else {
            self.memtable.write().unwrap().delete(key.to_vec());
        }
        Ok(())
    }

    /// Range scan (scans MemTable only, not SSTables)
    fn scan(&self, _table_id: u32, start: &[u8], end: &[u8]) -> Result<Vec<(Vec<u8>, Vec<u8>)>> {
        let mut results = self.memtable.read().unwrap().scan(start, end);

        // 套用交易緩衝區的修改
        if let Ok(tx) = self.tx_buffer.read() {
            if let Some(buffer) = tx.as_ref() {
                for (key, value) in buffer.iter() {
                    match value {
                        Some(v) => {
                            results.retain(|(k, _)| k != key);
                            results.push((key.clone(), v.clone()));
                        }
                        None => {
                            results.retain(|(k, _)| k != key);
                        }
                    }
                }
            }
        }
        Ok(results)
    }

    /// Batch write
    fn batch_put(&mut self, table_id: u32, pairs: Vec<(Vec<u8>, Vec<u8>)>) -> Result<()> {
        if table_id != 1 {
            return Err(Error::NotSupported("LSM engine only supports table_id=1".into()));
        }
        if *self.in_transaction.read().unwrap() {
            let mut tx = self.tx_buffer.write().unwrap();
            if tx.is_none() {
                *tx = Some(BTreeMap::new());
            }
            if let Some(ref mut buffer) = *tx {
                for (key, value) in pairs {
                    buffer.insert(key, Some(value));
                }
            }
        } else {
            let mut mem = self.memtable.write().unwrap();
            for (key, value) in pairs {
                mem.put(key, value);
            }
        }
        Ok(())
    }

    /// Range delete
    fn range_delete(&mut self, table_id: u32, start: &[u8], end: &[u8]) -> Result<()> {
        if table_id != 1 {
            return Err(Error::NotSupported("LSM engine only supports table_id=1".into()));
        }
        let keys: Vec<Vec<u8>> = self.memtable.read().unwrap().scan(start, end)
            .into_iter()
            .map(|(k, _)| k)
            .collect();

        if *self.in_transaction.read().unwrap() {
            let mut tx = self.tx_buffer.write().unwrap();
            if tx.is_none() {
                *tx = Some(BTreeMap::new());
            }
            if let Some(ref mut buffer) = *tx {
                for key in keys {
                    buffer.insert(key, None);
                }
            }
        } else {
            let mut mem = self.memtable.write().unwrap();
            for key in keys {
                mem.delete(key);
            }
        }
        Ok(())
    }

    /// Flush MemTable to SSTable
    fn flush(&mut self) -> Result<()> {
        self.flush_memtable()
    }

    /// Same as flush
    fn sync(&mut self) -> Result<()> {
        self.flush_memtable()
    }

    /// Begin transaction
    fn begin_transaction(&mut self) -> Result<()> {
        if *self.in_transaction.read().unwrap() {
            return Err(Error::Transaction("Transaction already active".into()));
        }
        *self.in_transaction.write().unwrap() = true;
        Ok(())
    }

    /// Commit transaction: write buffer to MemTable and sync WAL
    fn commit_transaction(&mut self) -> Result<()> {
        if !*self.in_transaction.read().unwrap() {
            return Err(Error::Transaction("No active transaction".into()));
        }

        if let Some(buffer) = self.tx_buffer.write().unwrap().take() {
            let mut mem = self.memtable.write().unwrap();
            for (key, value) in buffer.into_iter() {
                match value {
                    Some(v) => mem.put(key, v),
                    None => mem.delete(key),
                }
            }
        }

        *self.in_transaction.write().unwrap() = false;
        self.sync_wal_only()
    }

    /// Rollback transaction: discard buffer
    fn rollback_transaction(&mut self) -> Result<()> {
        if !*self.in_transaction.read().unwrap() {
            return Err(Error::Transaction("No active transaction".into()));
        }
        self.tx_buffer.write().unwrap().take();
        *self.in_transaction.write().unwrap() = false;
        Ok(())
    }

    /// Check if transaction is active
    fn has_transaction(&self) -> bool {
        *self.in_transaction.read().unwrap()
    }

    /// Get statistics (key count from MemTable + SSTables)
    fn stats(&self) -> EngineStats {
        let mem_keys = self.memtable.read().unwrap().len() as u64;
        let sstable_keys: u64 = self.sstables.read().unwrap().iter().map(|s| s.len()).sum();
        EngineStats {
            key_count: mem_keys + sstable_keys,
            size_bytes: 0,
            cache_hit_rate: None,
            in_transaction: *self.in_transaction.read().unwrap(),
            engine: "lsm",
        }
    }
}

// ===== 單元測試 =====

#[cfg(test)]
mod tests {
    use super::*;

    /// Test basic put/get operations
    #[test]
    fn test_lsm_basic() {
        let mut engine = LsmEngine::new();
        engine.put(1, b"hello", b"world").unwrap();
        assert_eq!(engine.get(1, b"hello").unwrap(), Some(b"world".to_vec()));
        assert_eq!(engine.get(1, b"missing").unwrap(), None);
    }

    /// Test range scan
    #[test]
    fn test_lsm_scan() {
        let mut engine = LsmEngine::new();
        engine.put(1, b"a", b"1").unwrap();
        engine.put(1, b"b", b"2").unwrap();
        engine.put(1, b"c", b"3").unwrap();

        let results = engine.scan(1, b"a", b"c").unwrap();
        assert!(results.len() >= 2);
    }

    /// Test delete operation
    #[test]
    fn test_lsm_delete() {
        let mut engine = LsmEngine::new();
        engine.put(1, b"key", b"value").unwrap();
        engine.delete(1, b"key").unwrap();
        assert_eq!(engine.get(1, b"key").unwrap(), None);
    }

    /// Test transaction: begin → put → commit
    #[test]
    fn test_lsm_transaction() {
        let mut engine = LsmEngine::new();
        engine.put(1, b"a", b"1").unwrap();

        engine.begin_transaction().unwrap();
        engine.put(1, b"b", b"2").unwrap();
        assert_eq!(engine.get(1, b"b").unwrap(), Some(b"2".to_vec()));

        engine.commit_transaction().unwrap();
        assert_eq!(engine.get(1, b"b").unwrap(), Some(b"2".to_vec()));
    }

    /// Test transaction rollback
    #[test]
    fn test_lsm_transaction_rollback() {
        let mut engine = LsmEngine::new();
        engine.put(1, b"a", b"1").unwrap();

        engine.begin_transaction().unwrap();
        engine.put(1, b"b", b"2").unwrap();
        engine.rollback_transaction().unwrap();

        assert_eq!(engine.get(1, b"b").unwrap(), None);
    }

    /// Test that multiple tables are unsupported
    #[test]
    fn test_lsm_multi_table_unsupported() {
        let mut engine = LsmEngine::new();
        let result = engine.put(2, b"key", b"value");
        assert!(result.is_err());
    }

    /// Test disk persistence
    #[test]
    fn test_lsm_persistence() {
        let temp_dir = std::env::temp_dir().join("db6_lsm_persist_test");
        let _ = std::fs::remove_dir_all(&temp_dir);

        {
            let mut engine = LsmEngine::open(&temp_dir).unwrap();
            engine.put(1, b"key1", b"value1").unwrap();
            engine.put(1, b"key2", b"value2").unwrap();
            engine.flush().unwrap();
        }

        {
            let engine = LsmEngine::open(&temp_dir).unwrap();
            assert_eq!(engine.get(1, b"key1").unwrap(), Some(b"value1".to_vec()));
            assert_eq!(engine.get(1, b"key2").unwrap(), Some(b"value2".to_vec()));
        }

        let _ = std::fs::remove_dir_all(&temp_dir);
    }

    /// Test WAL recovery: write transaction data → reopen → data should be restored from WAL
    #[test]
    fn test_lsm_wal_recovery() {
        let temp_dir = std::env::temp_dir().join("db6_lsm_wal_test");
        let _ = std::fs::remove_dir_all(&temp_dir);

        {
            let mut engine = LsmEngine::open(&temp_dir).unwrap();
            engine.begin_transaction().unwrap();
            engine.put(1, b"key1", b"value1").unwrap();
            engine.put(1, b"key2", b"value2").unwrap();
            engine.commit_transaction().unwrap();
        }

        {
            let engine = LsmEngine::open(&temp_dir).unwrap();
            assert_eq!(engine.get(1, b"key1").unwrap(), Some(b"value1".to_vec()));
            assert_eq!(engine.get(1, b"key2").unwrap(), Some(b"value2".to_vec()));
        }

        let _ = std::fs::remove_dir_all(&temp_dir);
    }
}

// LSM 引擎支援的能力：掃描、批次操作、交易
impl crate::engine::CanScan for LsmEngine {}
impl crate::engine::CanBatch for LsmEngine {}
impl crate::engine::CanTransaction for LsmEngine {}