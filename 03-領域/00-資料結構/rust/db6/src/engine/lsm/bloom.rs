//! Bloom Filter — probabilistic data structure
//!
//! Bloom Filter is used to quickly check whether an element **might be in a set**.
//!
//! ## Characteristics
//!
//! - If it returns `false`: the element is **definitely not** in the set
//! - If it returns `true`: the element **might be** in the set (may have false positives)
//! - Cannot delete elements (standard Bloom Filter does not support deletion)
//!
//! ## Usage in LSM-Tree
//!
//! When querying the LSM engine, check the Bloom Filter first:
//! - If `might_contain(key)` = false, return None immediately, avoiding expensive SSTable disk reads
//! - If = true, search in SSTables
//!
//! ## Implementation details
//!
//! Uses 3 hash functions and a bit array. On insert, each element is hashed 3 times,
//! setting the corresponding bits to 1. On lookup, check if all corresponding bits are 1.
//!
//! The bit array is stored in `Vec<u64>`, each u64 holds 64 bits.

use std::collections::hash_map::DefaultHasher;
use std::hash::{Hash, Hasher};

/// Bloom Filter
///
/// - `bits`: bit array (in u64 units)
/// - `capacity`: expected number of elements
/// - `hashes`: number of hash functions (fixed at 3)
pub struct BloomFilter {
    bits: Vec<u64>,
    capacity: usize,
    hashes: usize,
}

impl BloomFilter {
    /// Create a new Bloom Filter
    ///
    /// `capacity`: expected number of elements to store
    pub fn new(capacity: usize) -> Self {
        let bits = (capacity + 63) / 64;
        Self {
            bits: vec![0; bits],
            capacity,
            hashes: 3,
        }
    }

    /// Compute hash of a key using a seed
    ///
    /// Using different seeds produces multiple (approximately) independent hash functions.
    /// First hash the key content, then hash the seed, and finally take modulo.
    fn hash(&self, key: &[u8], seed: usize) -> usize {
        let mut hasher = DefaultHasher::new();
        key.hash(&mut hasher);
        seed.hash(&mut hasher);
        (hasher.finish() as usize) % self.capacity
    }

    /// Insert a key into the Bloom Filter
    ///
    /// Compute positions with 3 hash functions and set the corresponding bits to 1.
    pub fn insert(&mut self, key: &[u8]) {
        for i in 0..self.hashes {
            let h = self.hash(key, i);
            let idx = h / 64;
            let bit = h % 64;
            if idx < self.bits.len() {
                self.bits[idx] |= 1 << bit;
            }
        }
    }

    /// Check if a key might be in the set
    ///
    /// - `false`: definitely not in the set
    /// - `true`: might be in the set (may have false positives)
    pub fn might_contain(&self, key: &[u8]) -> bool {
        for i in 0..self.hashes {
            let h = self.hash(key, i);
            let idx = h / 64;
            let bit = h % 64;
            if idx >= self.bits.len() {
                return false;
            }
            if self.bits[idx] & (1 << bit) == 0 {
                return false;
            }
        }
        true
    }
}

impl Default for BloomFilter {
    fn default() -> Self {
        Self::new(1024)
    }
}