//! MemTable — LSM-Tree in-memory write buffer
//!
//! MemTable (Memory Table) is the first layer of LSM-Tree; all writes enter here first.
//! Internally uses `BTreeMap` to maintain sorted order and support range scans.
//!
//! When the MemTable reaches a certain size, it is flushed to disk as an SSTable.
//!
//! ## Value enum
//!
//! - `Data(Vec<u8>)`: normal data
//! - `Tombstone`: deletion marker indicating the key has been deleted

use std::collections::BTreeMap;

/// Value type: normal data or tombstone deletion marker
#[derive(Clone, Debug)]
pub enum Value {
    /// Normal data
    Data(Vec<u8>),
    /// Deletion marker (tombstone) indicating this key has been deleted
    Tombstone,
}

impl Value {
    /// Returns true if this is normal data (not Tombstone)
    pub fn is_data(&self) -> bool {
        matches!(self, Value::Data(_))
    }

    /// Get the data content (returns None for Tombstone)
    pub fn get_data(&self) -> Option<&Vec<u8>> {
        match self {
            Value::Data(v) => Some(v),
            Value::Tombstone => None,
        }
    }
}

/// MemTable structure
///
/// Uses `BTreeMap` to store ordered key-value pairs, keys are `Vec<u8>`, values are `Value`.
pub struct MemTable {
    map: BTreeMap<Vec<u8>, Value>,
}

impl MemTable {
    /// Create an empty MemTable
    pub fn new() -> Self {
        Self { map: BTreeMap::new() }
    }

    /// Insert or update a key-value pair
    pub fn put(&mut self, key: Vec<u8>, value: Vec<u8>) {
        self.map.insert(key, Value::Data(value));
    }

    /// Delete a key (insert a Tombstone marker)
    pub fn delete(&mut self, key: Vec<u8>) {
        self.map.insert(key, Value::Tombstone);
    }

    /// Get a value by key
    pub fn get(&self, key: &[u8]) -> Option<&Value> {
        self.map.get(key)
    }

    /// Range scan [start, end), returns only normal data (skips Tombstones)
    pub fn scan(&self, start: &[u8], end: &[u8]) -> Vec<(Vec<u8>, Vec<u8>)> {
        let start = if start.is_empty() { None } else { Some(start.to_vec()) };
        let end = if end.is_empty() { None } else { Some(end.to_vec()) };

        match (start, end) {
            (None, None) => self.map.iter()
                .filter(|(_, v)| v.is_data())
                .map(|(k, v)| (k.clone(), v.get_data().unwrap().clone()))
                .collect(),
            (Some(s), None) => self.map.range(s..)
                .filter(|(_, v)| v.is_data())
                .map(|(k, v)| (k.clone(), v.get_data().unwrap().clone()))
                .collect(),
            (None, Some(e)) => self.map.range(..e)
                .filter(|(_, v)| v.is_data())
                .map(|(k, v)| (k.clone(), v.get_data().unwrap().clone()))
                .collect(),
            (Some(s), Some(e)) => self.map.range(s..e)
                .filter(|(_, v)| v.is_data())
                .map(|(k, v)| (k.clone(), v.get_data().unwrap().clone()))
                .collect(),
        }
    }

    /// Return the number of keys (including Tombstones)
    pub fn len(&self) -> usize {
        self.map.len()
    }

    /// Return all normal data (for flushing to SSTable)
    pub fn all_data(&self) -> Vec<(Vec<u8>, Vec<u8>)> {
        self.map.iter()
            .filter(|(_, v)| v.is_data())
            .map(|(k, v)| (k.clone(), v.get_data().unwrap().clone()))
            .collect()
    }

    /// Clear the MemTable
    pub fn clear(&mut self) {
        self.map.clear();
    }
}

impl Default for MemTable {
    fn default() -> Self {
        Self::new()
    }
}