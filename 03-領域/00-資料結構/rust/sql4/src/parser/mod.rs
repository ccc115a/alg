//! Parser 模組：SQL 字串 → AST
//!
//! 使用方式：
//! ```rust
//! use sql4::parser::parse;
//!
//! let stmts = parse("SELECT * FROM users WHERE id = 1").unwrap();
//! ```

pub mod ast;
pub mod lexer;
pub mod parser;

pub use parser::parse;
