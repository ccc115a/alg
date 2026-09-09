//! B+Tree 模組
//!
//! 提供 B+Tree 索引結構。
//!
//! # 功能
//! - 插入（insert）/ 查詢（search）/ 範圍查詢（range_search）/ 刪除（delete）
//! - key 支援整數（i64）與字串
//! - 葉節點以雙向有序鏈結串列連接，支援高效範圍掃描
//!
//! # 使用範例
//! ```rust
//! use btree::{BPlusTree, Key, MemoryStorage};
//!
//! let mut tree = BPlusTree::new(4, MemoryStorage::new());
//! tree.insert(Key::Integer(42), b"hello".to_vec());
//! assert_eq!(tree.search(&Key::Integer(42)), Some(b"hello".as_slice().to_vec()));
//! ```

pub mod codec;
pub mod node;
pub mod storage;
pub mod tree;
pub mod wal;

pub use node::{Key, Node, NodeType, Record};
pub use storage::{DiskStorage, MemoryStorage, Storage};
pub use tree::BPlusTree;