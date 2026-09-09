//! SQL subsystem — Parser → Planner → Executor
//!
//! This module is ported from the sql6 project and handles the full lifecycle of SQL:
//!
//! 1. **Parser**: Parses SQL strings into an abstract syntax tree (AST)
//! 2. **Planner**: Converts the AST into an executable query plan (PlanNode)
//! 3. **Executor**: Executes the query plan and returns a result set (ResultSet)

pub mod parser;
pub mod planner;
pub mod executor;

pub use parser::parse;
pub use executor::{Executor, ResultSet, SqlExecutor};