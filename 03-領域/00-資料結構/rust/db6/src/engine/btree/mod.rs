//! Disk-based BTree engine module
//!
//! Implements a persistent storage engine based on the BTree structure, with transaction support.
//!
//! Module structure:
//! - `tree.rs`: BTree data structure (based on BTreeMap)
//! - `storage.rs`: File storage and page management
//! - `engine.rs`: StorageEngine trait implementation

mod storage;
mod tree;
mod engine;

pub use storage::{FileStorage, MemoryStorage, Page, Storage, PAGE_SIZE};
pub use tree::BTree;
pub use engine::BTreeEngine;