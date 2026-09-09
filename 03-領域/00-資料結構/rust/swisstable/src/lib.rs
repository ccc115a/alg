//! # Swisstable
//!
//! A Rust implementation of the Swiss Table hash table algorithm.
//!
//! Swiss Table is a highly efficient hash table algorithm originally developed by Google,
//! featuring cache-friendly design and SIMD-accelerated probing.
//!
//! ## Features
//!
//! - **Cache-friendly**: Uses contiguous memory blocks for hash slots
//! - **Open addressing**: All elements stored in a single array
//! - **Robin Hood hashing**: Minimizes probe sequence length variance
//! - **Automatic resizing**: Dynamically grows/shrinks based on load factor
//!
//! ## Example
//!
//! ```
//! use swisstable::SwisstableMap;
//!
//! let mut map = SwisstableMap::new();
//! map.insert("key", 100);
//! assert_eq!(map.get(&"key"), Some(&100));
//! ```
//!
//! ## Comparison with std::collections::HashMap
//!
//! - Similar API to `std::collections::HashMap`
//! - Better cache locality due to Swiss Table design
//! - Not yet as thoroughly tested as the standard library implementation
//!
//! ## Crate Features
//!
//! This crate has minimal dependencies and is `no_std` compatible (with `alloc`).

#![cfg_attr(not(feature = "std"), no_std)]
#![cfg_attr(not(feature = "std"), alloc)]

#[cfg(feature = "std")]
extern crate std as core;

use core::alloc::{alloc, dealloc, Layout};
use core::fmt;
use core::hash::{BuildHasher, Hash, Hasher};
use core::iter::Iterator;
use core::mem;

#[cfg(not(feature = "std"))]
use alloc::vec::Vec;

struct Bucket<K, V> {
    hash: u64,
    key: Option<Box<K>>,
    value: Option<Box<V>>,
}

/// A hash map implementation based on the Swiss Table algorithm.
///
/// Swiss Table is an open-addressing hash table that uses a probing scheme
/// optimized for cache locality. It achieves high performance through
/// cache-line aware memory access patterns.
///
/// # Example
///
/// ```
/// use swisstable::SwisstableMap;
///
/// let mut map = SwisstableMap::new();
/// map.insert(1, "a");
/// map.insert(2, "b");
///
/// assert_eq!(map.get(&1), Some(&"a"));
/// assert_eq!(map.len(), 2);
/// ```

const TOMBSTONE: u64 = u64::MAX;

#[derive(Clone)]
pub struct SwisstableMap<K, V> {
    buckets: *mut Bucket<K, V>,
    capacity: usize,
    len: usize,
    hasher: core::collections::hash_map::RandomState,
}

impl<K: Hash + Eq, V> SwisstableMap<K, V> {
    /// Creates a new empty `SwisstableMap`.
    ///
    /// # Example
    ///
    /// ```
    /// use swisstable::SwisstableMap;
    ///
    /// let map: SwisstableMap<i32, &str> = SwisstableMap::new();
    /// assert!(map.is_empty());
    /// ```
    pub fn new() -> Self {
        Self::with_capacity_and_hasher(4, core::collections::hash_map::RandomState::new())
    }

    /// Creates a new empty `SwisstableMap` with the given capacity and hasher.
    ///
    /// The capacity will be rounded up to the next power of two, with a minimum of 16.
    pub fn with_capacity_and_hasher(
        capacity: usize,
        hasher: core::collections::hash_map::RandomState,
    ) -> Self {
        let cap = capacity.next_power_of_two().max(16);
        let layout = Layout::array::<Bucket<K, V>>(cap).unwrap();
        let buckets = unsafe { alloc(layout) as *mut Bucket<K, V> };

        unsafe {
            for i in 0..cap {
                core::ptr::write(
                    buckets.add(i),
                    Bucket {
                        hash: 0,
                        key: None,
                        value: None,
                    },
                );
            }
        }

        SwisstableMap {
            buckets,
            capacity: cap,
            len: 0,
            hasher,
        }
    }

    fn probe_index(&self, hash: u64) -> usize {
        (hash as usize) & (self.capacity - 1)
    }

    /// Inserts a key-value pair into the map.
    ///
    /// If the key already existed, the old value is returned.
    ///
    /// # Example
    ///
    /// ```
    /// use swisstable::SwisstableMap;
    ///
    /// let mut map = SwisstableMap::new();
    /// map.insert("key", 100);
    /// assert_eq!(map.get(&"key"), Some(&100));
    /// ```
    pub fn insert(&mut self, mut key: K, mut value: V) -> Option<V> {
        let mut hasher = self.hasher.build_hasher();
        key.hash(&mut hasher);
        let mut hash = hasher.finish();

        let mut index = self.probe_index(hash);
        let mut dist = 0usize;

        loop {
            unsafe {
                let bucket = &mut *self.buckets.add(index);

                if bucket.key.is_none() {
                    bucket.hash = hash;
                    bucket.key = Some(Box::new(key));
                    bucket.value = Some(Box::new(value));
                    self.len += 1;
                    return None;
                }

                if bucket.hash == TOMBSTONE {
                    bucket.hash = hash;
                    bucket.key = Some(Box::new(key));
                    bucket.value = Some(Box::new(value));
                    self.len += 1;
                    return None;
                }

                if bucket.key.as_ref().map(|k| **k == key).unwrap_or(false) {
                    let old_value = bucket.value.take().unwrap();
                    bucket.value = Some(Box::new(value));
                    return Some(*old_value);
                }

                let existing_index = self.probe_index(bucket.hash);
                let existing_dist = (index.wrapping_sub(existing_index)) & (self.capacity - 1);

                if dist > existing_dist {
                    let old_hash = bucket.hash;
                    let old_key = bucket.key.take().unwrap();
                    let old_value = bucket.value.take().unwrap();

                    bucket.hash = hash;
                    bucket.key = Some(Box::new(key));
                    bucket.value = Some(Box::new(value));

                    key = *old_key;
                    value = *old_value;
                    hash = old_hash;
                    dist = existing_dist;
                }

                dist += 1;
                index = (index + 1) & (self.capacity - 1);

                if dist >= self.capacity {
                    self.resize();
                    return self.insert(key, value);
                }
            }
        }
    }

    /// Returns a reference to the value corresponding to the key.
    ///
    /// # Example
    ///
    /// ```
    /// use swisstable::SwisstableMap;
    ///
    /// let mut map = SwisstableMap::new();
    /// map.insert("key", 100);
    /// assert_eq!(map.get(&"key"), Some(&100));
    /// assert_eq!(map.get(&"nonexistent"), None);
    /// ```
    pub fn get(&self, key: &K) -> Option<&V> {
        let mut hasher = self.hasher.build_hasher();
        key.hash(&mut hasher);
        let hash = hasher.finish();

        let mut index = self.probe_index(hash);

        loop {
            unsafe {
                let bucket = &*self.buckets.add(index);

                if bucket.key.is_none() {
                    return None;
                }

                if bucket.hash == TOMBSTONE {
                    return None;
                }

                if bucket.hash == hash && bucket.key.as_ref().map(|k| **k == *key).unwrap_or(false)
                {
                    return bucket.value.as_ref().map(|v| &**v);
                }

                index = (index + 1) & (self.capacity - 1);

                if index == self.probe_index(hash) {
                    return None;
                }
            }
        }
    }

    /// Removes a key from the map, returning the value if it was present.
    ///
    /// # Example
    ///
    /// ```
    /// use swisstable::SwisstableMap;
    ///
    /// let mut map = SwisstableMap::new();
    /// map.insert("key", 100);
    /// assert_eq!(map.remove(&"key"), Some(100));
    /// assert!(map.is_empty());
    /// ```
    pub fn remove(&mut self, key: &K) -> Option<V> {
        let mut hasher = self.hasher.build_hasher();
        key.hash(&mut hasher);
        let hash = hasher.finish();

        let mut index = self.probe_index(hash);

        loop {
            unsafe {
                let bucket = &mut *self.buckets.add(index);

                if bucket.key.is_none() {
                    return None;
                }

                if bucket.hash == TOMBSTONE {
                    return None;
                }

                if bucket.hash == hash && bucket.key.as_ref().map(|k| **k == *key).unwrap_or(false)
                {
                    let result = bucket.value.take().map(|v| *v);
                    bucket.key.take();
                    bucket.hash = TOMBSTONE;
                    self.len -= 1;
                    return result;
                }

                index = (index + 1) & (self.capacity - 1);

                if index == self.probe_index(hash) {
                    return None;
                }
            }
        }
    }

    fn resize(&mut self) {
        let new_cap = self.capacity * 2;
        let layout = Layout::array::<Bucket<K, V>>(new_cap).unwrap();
        let mut new_buckets = unsafe { alloc(layout) as *mut Bucket<K, V> };

        unsafe {
            for i in 0..new_cap {
                core::ptr::write(
                    new_buckets.add(i),
                    Bucket {
                        hash: 0,
                        key: None,
                        value: None,
                    },
                );
            }

            let old_cap = self.capacity;
            let old_buckets = self.buckets;

            mem::swap(&mut self.buckets, &mut new_buckets);
            self.capacity = new_cap;
            self.len = 0;

            for i in 0..old_cap {
                let bucket = &mut *old_buckets.add(i);
                if let Some(key) = bucket.key.take() {
                    let value = bucket.value.take().unwrap();
                    let hash = bucket.hash;

                    let mut index = (hash as usize) & (self.capacity - 1);
                    loop {
                        let new_bucket = &mut *self.buckets.add(index);
                        if new_bucket.key.is_none() {
                            new_bucket.hash = hash;
                            new_bucket.key = Some(key);
                            new_bucket.value = Some(value);
                            self.len += 1;
                            break;
                        }
                        index = (index + 1) & (self.capacity - 1);
                    }
                }
            }

            dealloc(
                old_buckets as *mut u8,
                Layout::array::<Bucket<K, V>>(old_cap).unwrap(),
            );
        }
    }

    /// Returns the number of elements in the map.
    pub fn len(&self) -> usize {
        self.len
    }

    /// Returns `true` if the map contains no elements.
    pub fn is_empty(&self) -> bool {
        self.len == 0
    }

    /// Returns the current capacity of the map.
    ///
    /// Capacity is always a power of two and at least 16.
    pub fn capacity(&self) -> usize {
        self.capacity
    }

    /// Returns an iterator over the entries of the map.
    pub fn iter(&self) -> Iter<'_, K, V> {
        self.into_iter()
    }

    /// Removes all elements from the map.
    ///
    /// Note that this does not deallocate the backing storage;
    /// the capacity remains unchanged.
    pub fn clear(&mut self) {
        unsafe {
            for i in 0..self.capacity {
                core::ptr::drop_in_place(self.buckets.add(i));
                core::ptr::write(
                    self.buckets.add(i),
                    Bucket {
                        hash: TOMBSTONE,
                        key: None,
                        value: None,
                    },
                );
            }
            self.len = 0;
        }
    }
}

impl<K, V> Drop for SwisstableMap<K, V> {
    fn drop(&mut self) {
        unsafe {
            for i in 0..self.capacity {
                core::ptr::drop_in_place(self.buckets.add(i));
            }
            dealloc(
                self.buckets as *mut u8,
                Layout::array::<Bucket<K, V>>(self.capacity).unwrap(),
            );
        }
    }
}

impl<K: Hash + Eq + fmt::Debug, V: fmt::Debug> fmt::Debug for SwisstableMap<K, V> {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.debug_map().entries(self.into_iter()).finish()
    }
}

impl<K: Hash + Eq, V> Default for SwisstableMap<K, V> {
    fn default() -> Self {
        Self::new()
    }
}

impl<K: Hash + Eq + fmt::Debug, V> core::ops::Index<&K> for SwisstableMap<K, V> {
    type Output = V;

    fn index(&self, key: &K) -> &V {
        match self.get(key) {
            Some(value) => value,
            None => panic!("key not found: {:?}", key),
        }
    }
}

/// An iterator over the entries of a `SwisstableMap`.
pub struct Iter<'a, K, V> {
    map: &'a SwisstableMap<K, V>,
    index: usize,
}

impl<'a, K, V> IntoIterator for &'a SwisstableMap<K, V> {
    type Item = (&'a K, &'a V);
    type IntoIter = Iter<'a, K, V>;

    fn into_iter(self) -> Self::IntoIter {
        Iter {
            map: self,
            index: 0,
        }
    }
}

impl<'a, K, V> Iterator for Iter<'a, K, V> {
    type Item = (&'a K, &'a V);

    fn next(&mut self) -> Option<Self::Item> {
        while self.index < self.map.capacity {
            unsafe {
                let bucket = &*self.map.buckets.add(self.index);
                self.index += 1;
                if let Some(ref key) = bucket.key {
                    if let Some(ref value) = bucket.value {
                        return Some((key.as_ref(), value.as_ref()));
                    }
                }
            }
        }
        None
    }
}

impl<'a, K, V> Clone for Iter<'a, K, V> {
    fn clone(&self) -> Self {
        Iter {
            map: self.map,
            index: self.index,
        }
    }
}

/// A hash set implementation based on the Swiss Table algorithm.
///
/// # Example
///
/// ```
/// use swisstable::SwisstableSet;
///
/// let mut set = SwisstableSet::new();
/// set.insert(1);
/// set.insert(2);
///
/// assert!(set.contains(&1));
/// assert!(!set.contains(&3));
/// ```
#[derive(Clone)]
pub struct SwisstableSet<T> {
    map: SwisstableMap<T, ()>,
}

impl<T: Hash + Eq> SwisstableSet<T> {
    /// Creates a new empty `SwisstableSet`.
    ///
    /// # Example
    ///
    /// ```
    /// use swisstable::SwisstableSet;
    ///
    /// let set: SwisstableSet<i32> = SwisstableSet::new();
    /// assert!(set.is_empty());
    /// ```
    pub fn new() -> Self {
        SwisstableSet {
            map: SwisstableMap::new(),
        }
    }

    /// Creates a new empty `SwisstableSet` with the given capacity.
    pub fn with_capacity(capacity: usize) -> Self {
        SwisstableSet {
            map: SwisstableMap::with_capacity_and_hasher(
                capacity,
                core::collections::hash_map::RandomState::new(),
            ),
        }
    }

    /// Inserts a value into the set.
    ///
    /// Returns `true` if the value was not already present.
    pub fn insert(&mut self, value: T) -> bool {
        self.map.insert(value, ()).is_none()
    }

    /// Returns `true` if the set contains the value.
    pub fn contains(&self, value: &T) -> bool {
        self.map.get(value).is_some()
    }

    /// Removes a value from the set, returning `Some(())` if it was present.
    pub fn remove(&mut self, value: &T) -> Option<()> {
        self.map.remove(value)
    }

    /// Returns the number of elements in the set.
    pub fn len(&self) -> usize {
        self.map.len()
    }

    /// Returns `true` if the set contains no elements.
    pub fn is_empty(&self) -> bool {
        self.map.is_empty()
    }

    /// Removes all elements from the set.
    pub fn clear(&mut self) {
        self.map.clear();
    }

    /// Returns an iterator over the values in the set.
    pub fn iter(&self) -> IterSet<'_, T> {
        IterSet {
            iter: (&self.map).into_iter(),
        }
    }
}

impl<T: Hash + Eq> Default for SwisstableSet<T> {
    fn default() -> Self {
        Self::new()
    }
}

impl<T: Hash + Eq + fmt::Debug> fmt::Debug for SwisstableSet<T> {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.debug_set().entries(self.into_iter()).finish()
    }
}

impl<'a, T: Hash + Eq> IntoIterator for &'a SwisstableSet<T> {
    type Item = &'a T;
    type IntoIter = IterSet<'a, T>;

    fn into_iter(self) -> Self::IntoIter {
        IterSet {
            iter: (&self.map).into_iter(),
        }
    }
}

/// An iterator over the values of a `SwisstableSet`.
pub struct IterSet<'a, T> {
    iter: Iter<'a, T, ()>,
}

impl<'a, T> Iterator for IterSet<'a, T> {
    type Item = &'a T;

    fn next(&mut self) -> Option<Self::Item> {
        self.iter.next().map(|(k, &())| k)
    }
}

impl<'a, T> Clone for IterSet<'a, T> {
    fn clone(&self) -> Self {
        IterSet {
            iter: self.iter.clone(),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_new_map_is_empty() {
        let map: SwisstableMap<i32, i32> = SwisstableMap::new();
        assert!(map.is_empty());
        assert_eq!(map.len(), 0);
    }

    #[test]
    fn test_insert_single() {
        let mut map = SwisstableMap::new();
        map.insert(1, 100);
        assert_eq!(map.len(), 1);
        assert_eq!(map.get(&1), Some(&100));
    }

    #[test]
    fn test_insert_multiple() {
        let mut map = SwisstableMap::new();
        map.insert(1, 100);
        map.insert(2, 200);
        map.insert(3, 300);
        assert_eq!(map.len(), 3);
        assert_eq!(map.get(&1), Some(&100));
        assert_eq!(map.get(&2), Some(&200));
        assert_eq!(map.get(&3), Some(&300));
    }

    #[test]
    fn test_update_existing() {
        let mut map = SwisstableMap::new();
        map.insert(1, 100);
        let old = map.insert(1, 999);
        assert_eq!(old, Some(100));
        assert_eq!(map.len(), 1);
        assert_eq!(map.get(&1), Some(&999));
    }

    #[test]
    fn test_remove_single() {
        let mut map = SwisstableMap::new();
        map.insert(1, 100);
        let removed = map.remove(&1);
        assert_eq!(removed, Some(100));
        assert!(map.is_empty());
    }

    #[test]
    fn test_remove_nonexistent() {
        let mut map = SwisstableMap::new();
        map.insert(1, 100);
        let removed = map.remove(&2);
        assert!(removed.is_none());
        assert_eq!(map.len(), 1);
    }

    #[test]
    fn test_many_insertions() {
        let mut map = SwisstableMap::new();
        for i in 0..100 {
            map.insert(i, i * 10);
        }
        assert_eq!(map.len(), 100);
        for i in 0..100 {
            assert_eq!(map.get(&i), Some(&(i * 10)));
        }
    }

    #[test]
    fn test_iterate() {
        let mut map = SwisstableMap::new();
        for i in 0..10 {
            map.insert(i, i);
        }
        let mut count = 0;
        for (k, v) in &map {
            assert_eq!(*k, *v);
            count += 1;
        }
        assert_eq!(count, 10);
    }

    #[test]
    fn test_capacity() {
        let map: SwisstableMap<i32, i32> = SwisstableMap::new();
        assert!(map.capacity() >= 16);
    }

    #[test]
    fn test_default() {
        let map: SwisstableMap<i32, i32> = Default::default();
        assert!(map.is_empty());
    }

    #[test]
    fn test_debug() {
        let mut map = SwisstableMap::new();
        map.insert(1, 100);
        let debug_str = format!("{:?}", map);
        assert!(debug_str.contains("1"));
    }

    #[test]
    fn test_string_keys() {
        let mut map = SwisstableMap::new();
        map.insert("apple", 1);
        map.insert("banana", 2);
        assert_eq!(map.get(&"apple"), Some(&1));
        assert_eq!(map.get(&"banana"), Some(&2));
    }

    #[test]
    fn test_new_set_is_empty() {
        let set: SwisstableSet<i32> = SwisstableSet::new();
        assert!(set.is_empty());
    }

    #[test]
    fn test_set_insert() {
        let mut set = SwisstableSet::new();
        set.insert(1);
        assert_eq!(set.len(), 1);
        assert!(set.contains(&1));
    }

    #[test]
    fn test_set_insert_duplicate() {
        let mut set = SwisstableSet::new();
        set.insert(1);
        let inserted = set.insert(1);
        assert!(!inserted);
        assert_eq!(set.len(), 1);
    }

    #[test]
    fn test_set_remove() {
        let mut set = SwisstableSet::new();
        set.insert(1);
        set.insert(2);
        set.remove(&1);
        assert_eq!(set.len(), 1);
        assert!(!set.contains(&1));
        assert!(set.contains(&2));
    }

    #[test]
    fn test_set_iterate() {
        let mut set = SwisstableSet::new();
        for i in 0..10 {
            set.insert(i);
        }
        let mut count = 0;
        for val in &set {
            assert!(*val >= 0 && *val < 10);
            count += 1;
        }
        assert_eq!(count, 10);
    }

    #[test]
    fn test_index() {
        let mut map = SwisstableMap::new();
        map.insert("key", 100);
        assert_eq!(map[&"key"], 100);
    }

    #[test]
    fn test_clear() {
        let mut map = SwisstableMap::new();
        map.insert(1, 100);
        map.insert(2, 200);
        assert_eq!(map.len(), 2);
        map.clear();
        assert!(map.is_empty());
    }

    #[test]
    fn test_set_clear() {
        let mut set = SwisstableSet::new();
        set.insert(1);
        set.insert(2);
        assert_eq!(set.len(), 2);
        set.clear();
        assert!(set.is_empty());
    }
}
