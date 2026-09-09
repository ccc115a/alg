//! SQL parser — Lexer → Parser → Abstract Syntax Tree (AST)
//!
//! Contains three submodules:
//! - `lexer`: Tokenizes SQL strings into a token stream
//! - `ast`: Defines AST nodes for SQL statements
//! - `parser`: Uses recursive descent to parse the token stream into an AST

pub mod lexer;
pub mod ast;
pub mod parser;

pub use parser::parse;