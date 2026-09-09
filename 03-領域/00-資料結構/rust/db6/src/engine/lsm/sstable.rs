//! SSTable — LSM-Tree on-disk Sorted String Table
//!
//! SSTable (Sorted String Table) is the on-disk storage format for LSM-Tree.
//! When the MemTable accumulates enough data, it is sorted and written to an SSTable.
//!
//! Each SSTable is stored in a `.sst` file and serialized with bincode.
//! Lookups search from newest to oldest SSTable.

use std::collections::BTreeMap;
use std::fs::{File, OpenOptions};
use std::io::{Read, Write};
use std::path::Path;

use crate::error::{Error, Result};

/// SSTable structure
///
/// Each SSTable corresponds to a `.sst` file containing an ordered set of key-value pairs.
pub struct SSTable {
    /// File path
    path: std::path::PathBuf,
    /// Sorted key-value data
    data: BTreeMap<Vec<u8>, Vec<u8>>,
}

impl SSTable {
    /// Create a new SSTable and write to disk
    ///
    /// Called when flushing from MemTable.
    /// `data` is already sorted (comes from BTreeMap).
    pub fn create(path: &Path, data: Vec<(Vec<u8>, Vec<u8>)>) -> Result<Self> {
        let mut ss = Self {
            path: path.to_path_buf(),
            data: BTreeMap::new(),
        };

        for (k, v) in data {
            ss.data.insert(k, v);
        }

        ss.write_to_disk()?;
        Ok(ss)
    }

    /// Load an SSTable from disk
    pub fn open(path: &Path) -> Result<Self> {
        if !path.exists() {
            return Ok(Self {
                path: path.to_path_buf(),
                data: BTreeMap::new(),
            });
        }

        let mut file = File::open(path)?;
        let mut contents = Vec::new();
        file.read_to_end(&mut contents)?;

        let data: BTreeMap<Vec<u8>, Vec<u8>> = match bincode::deserialize(&contents) {
            Ok(d) => d,
            Err(_) => BTreeMap::new(),
        };

        Ok(Self {
            path: path.to_path_buf(),
            data,
        })
    }

    /// Serialize BTreeMap and write to `.sst` file
    fn write_to_disk(&self) -> Result<()> {
        let mut file = OpenOptions::new()
            .create(true)
            .write(true)
            .truncate(true)
            .open(&self.path)?;

        let data = bincode::serialize(&self.data)
            .map_err(|e| Error::Sql(format!("bincode: {:?}", e)))?;

        file.write_all(&data)?;
        Ok(())
    }

    /// Read the value for a given key
    pub fn get(&self, key: &[u8]) -> Option<Vec<u8>> {
        self.data.get(key).cloned()
    }

    /// Range scan
    pub fn scan(&self, start: &[u8], end: &[u8]) -> Vec<(Vec<u8>, Vec<u8>)> {
        let start = if start.is_empty() { None } else { Some(start.to_vec()) };
        let end = if end.is_empty() { None } else { Some(end.to_vec()) };

        match (start, end) {
            (None, None) => self.data.iter().map(|(k, v)| (k.clone(), v.clone())).collect(),
            (Some(s), None) => self.data.range(s..).map(|(k, v)| (k.clone(), v.clone())).collect(),
            (None, Some(e)) => self.data.range(..e).map(|(k, v)| (k.clone(), v.clone())).collect(),
            (Some(s), Some(e)) => self.data.range(s..e).map(|(k, v)| (k.clone(), v.clone())).collect(),
        }
    }

    /// Return the key count of this SSTable
    pub fn len(&self) -> u64 {
        self.data.len() as u64
    }
}