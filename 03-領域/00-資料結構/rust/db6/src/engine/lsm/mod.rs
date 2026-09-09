//! LSM-Tree storage engine module
//!
//! Implementation of a persistent storage engine based on LSM-Tree (Log-Structured Merge-Tree),
//! especially suited for high write throughput workloads.
//!
//! Architecture:
//! - MemTable: in-memory write buffer (active/read-only)
//! - SSTable: on-disk Sorted String Table
//! - WAL: write-ahead log for data recovery
//! - Bloom Filter: probabilistic filter to accelerate negative key lookups

pub mod engine;
pub mod memtable;
pub mod sstable;
pub mod wal;
pub mod bloom;

pub use engine::LsmEngine;