//! FTS（Full-Text Search）全文檢索模組
//!
//! 支援英語與 CJK（中日韓）的全文搜尋，相容 SQLite FTS5 語法。
//!
//! # 使用範例
//!
//! ```rust
//! use sql4::fts::fts_table::FtsTable;
//!
//! let mut table = FtsTable::new("articles", vec!["title".into(), "body".into()]);
//! table.insert(vec!["Rust Programming".into(), "Fast and safe systems language".into()]);
//! table.insert(vec!["資料庫設計".into(), "關聯式資料庫基本概念".into()]);
//!
//! // 英文搜尋
//! let results = table.search("rust AND safe");
//! assert_eq!(results.len(), 1);
//!
//! // 中文搜尋
//! let results = table.search("資料");
//! assert_eq!(results.len(), 1);
//!
//! // 短語搜尋
//! let results = table.search("\"fast and safe\"");
//! assert_eq!(results.len(), 1);
//! ```

pub mod fts_table;
pub mod index;
pub mod tokenizer;

pub use fts_table::FtsTable;
