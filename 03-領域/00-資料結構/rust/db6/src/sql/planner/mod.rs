//! SQL planner — Converts AST into executable query plans
//!
//! The planning layer is responsible for:
//! - Semantic checks (table existence, column existence)
//! - Constraint validation (NOT NULL, UNIQUE, CHECK)
//! - Query optimization (predicate pushdown, etc.)
//! - Generating PlanNode execution plans

pub mod plan;
pub mod planner;
pub mod constraints;

pub use planner::Planner;
pub use plan::{Plan, ScanPlan, FtsPlan};