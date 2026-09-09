//! B+Tree implementation — uses the Rust standard library's BTreeMap
//!
//! This is a simplified B+Tree implementation that uses `std::collections::BTreeMap` under the hood.
//! A real B+Tree implementation would need to manage node splitting, page allocation, etc.
//! This version leverages Rust's built-in BTreeMap for ordering and range queries,
//! and implements persistence via serialization (bincode).
//!
//! Data is stored in the `btree.dat` file; the entire BTreeMap is serialized at once.

use std::collections::BTreeMap;
use std::fs::{File, OpenOptions};
use std::io::{Read, Write};
use std::path::Path;
use crate::error::Result;

/// BTree data structure
///
/// - `data`: Core data, uses BTreeMap to store all key-value pairs (ordered)
/// - `path`: Optional disk path for persistence
pub struct BTree {
    data: BTreeMap<Vec<u8>, Vec<u8>>,
    path: Option<std::path::PathBuf>,
}

impl BTree {
    /// Create an empty in-memory BTree
    pub fn new() -> Self {
        Self {
            data: BTreeMap::new(),
            path: None,
        }
    }

    /// Load BTree from disk
    ///
    /// Reads serialized data from `path/btree.dat`.
    /// Returns an empty BTree if the file does not exist.
    pub fn load(path: &Path) -> Result<Self> {
        let data_path = path.join("btree.dat");

        if !data_path.exists() {
            return Ok(Self::new());
        }

        let mut file = File::open(&data_path)?;
        let mut contents = Vec::new();
        file.read_to_end(&mut contents)?;

        // If deserialization fails (incompatible format), return empty BTree
        let data: BTreeMap<Vec<u8>, Vec<u8>> = match bincode::deserialize(&contents) {
            Ok(d) => d,
            Err(_) => BTreeMap::new(),
        };

        Ok(Self {
            data,
            path: Some(path.to_path_buf()),
        })
    }

    /// Serialize BTree and write to disk
    pub fn save(&self) -> Result<()> {
        if let Some(ref path) = self.path {
            let data_path = path.join("btree.dat");

            let mut file = OpenOptions::new()
                .create(true)
                .write(true)
                .truncate(true)
                .open(&data_path)?;

            let data = bincode::serialize(&self.data)
                .map_err(|e| std::io::Error::new(std::io::ErrorKind::Other, format!("bincode: {:?}", e)))?;

            file.write_all(&data)?;
        }
        Ok(())
    }

    /// Set the persistence path
    pub fn set_path(&mut self, path: std::path::PathBuf) {
        self.path = Some(path);
    }

    /// Read the value for a given key, O(log n)
    pub fn get(&self, key: &[u8]) -> Option<Vec<u8>> {
        self.data.get(key).cloned()
    }

    /// Insert or update a key-value pair
    pub fn put(&mut self, key: Vec<u8>, value: Vec<u8>) {
        self.data.insert(key, value);
    }

    /// Delete a key-value pair, returns true if the key existed
    pub fn delete(&mut self, key: &[u8]) -> bool {
        self.data.remove(key).is_some()
    }

    /// Range scan [start, end)
    ///
    /// Supports four boundary combinations:
    /// - No boundaries: scan all
    /// - Start only: from start to end
    /// - End only: from beginning to end (exclusive)
    /// - Both: start (inclusive) to end (exclusive)
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

    /// Flush data to disk
    pub fn flush(&mut self) -> Result<()> {
        self.save()
    }
}

impl Default for BTree {
    fn default() -> Self {
        Self::new()
    }
}