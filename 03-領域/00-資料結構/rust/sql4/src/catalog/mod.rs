//! Catalog 模組：資料庫的資料字典
//!
//! 管理所有 Table 的定義（schema、root_page、row_count），
//! 並透過 B+Tree 持久化到系統表。

pub mod catalog;
pub mod meta;

pub use catalog::Catalog;
