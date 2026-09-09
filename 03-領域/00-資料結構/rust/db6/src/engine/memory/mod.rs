//! In-memory engine module
//!
//! Provides two in-memory engine implementations:
//! - `HashMemoryEngine`: HashMap-based, O(1) operations, does not support ORDER BY/scan
//! - `BTreeMemoryEngine`: BTreeMap-based, O(log n) operations, supports ORDER BY/scan
//!
//! In-memory engines are suitable for testing, caching, or scenarios that do not require persistence.
//! Data is lost when the program exits.

pub mod hash;
pub mod btree;

pub use hash::HashMemoryEngine;
pub use btree::BTreeMemoryEngine;