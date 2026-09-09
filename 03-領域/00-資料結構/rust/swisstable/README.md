# Swisstable

A Rust implementation of the Swiss Table hash table algorithm.

## Overview

Swiss Table is a highly efficient hash table algorithm originally developed by Google. This crate provides `SwisstableMap<K, V>` and `SwisstableSet<T>` implementations based on this algorithm.

## Features

- **Cache-friendly**: Uses contiguous memory blocks for hash slots
- **Open addressing**: All elements stored in a single array  
- **Robin Hood hashing**: Minimizes probe sequence length variance
- **SIMD-friendly**: Design allows for SIMD-accelerated probing
- **No_std compatible**: Can be used in `no_std` environments with `alloc`

## Usage

Add this to your `Cargo.toml`:

```toml
[dependencies]
swisstable = "0.1.0"
```

## Example

```rust
use swisstable::SwisstableMap;

let mut map = SwisstableMap::new();
map.insert("key", 100);
assert_eq!(map.get(&"key"), Some(&100));
```

## SwisstableMap API

```rust
// Create a new map
let mut map = SwisstableMap::new();

// Insert entries
map.insert("key1", 100);
map.insert("key2", 200);

// Get values
assert_eq!(map.get(&"key1"), Some(&100));

// Update values
let old = map.insert("key1", 999);
assert_eq!(old, Some(100));

// Remove values
let removed = map.remove(&"key2");
assert_eq!(removed, Some(200));

// Iterate
for (key, value) in &map {
    println!("{}: {}", key, value);
}

// Check length
assert_eq!(map.len(), 1);
assert!(!map.is_empty());
```

## SwisstableSet API

```rust
use swisstable::SwisstableSet;

let mut set = SwisstableSet::new();
set.insert(1);
set.insert(2);
set.insert(3);

assert!(set.contains(&1));
assert!(!set.contains(&4));

set.remove(&2);
assert_eq!(set.len(), 2);

for val in &set {
    println!("{}", val);
}
```

## Performance

Swiss Table achieves excellent performance through:

1. **Cache locality**: Elements are stored in contiguous memory, reducing cache misses
2. **Robin Hood probing**: Ensures even probe distance distribution
3. **High load factor**: Typically operates efficiently at 87.5%+ load factor
4. **SIMD potential**: Group-based probing can be accelerated with SIMD instructions

## Comparison with std::collections::HashMap

| Feature | HashMap | Swisstable |
|---------|--------|------------|
| Algorithm | Separate chaining | Open addressing |
| Cache locality | Moderate | Excellent |
| Memory overhead | Per-element pointers | Contiguous |
| Maturity | Battle-tested | New implementation |

## Running Examples

```bash
# Basic example
cargo run --example basic

# Word count example
cargo run --example word_count

# Phonebook example
cargo run --example phonebook
```

## Running Tests

```bash
cargo test
```

## License

MIT OR Apache-2.0