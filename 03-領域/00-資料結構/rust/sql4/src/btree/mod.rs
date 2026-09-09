//! B+Tree 模組
//!
//! 提供 sql4 資料庫的核心索引結構。
//!
//! # 功能
//! - 插入（insert）/ 查詢（search）/ 範圍查詢（range_search）/ 刪除（delete）
//! - key 支援整數（i64）與字串
//! - 葉節點以雙向有序鏈結串列連接，支援高效範圍掃描
//!
//! # 使用範例
//! ```rust
//! use sql4::btree::{BPlusTree, Key};
//!
//! let mut tree = BPlusTree::new(4);
//! tree.insert(Key::Integer(42), b"hello".to_vec());
//! assert_eq!(tree.search(&Key::Integer(42)), Some(b"hello".as_slice()));
//! ```

pub mod node;
pub mod tree;

