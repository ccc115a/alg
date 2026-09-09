//! db6 — Unified database with pluggable storage engines (Memory/BTree/LSM) + KV + SQL + FTS + Msgq
//!
//! # Architecture
//!
//! - **KV API**: Unified key-value interface (implemented by all engines)
//! - **SQL API**: Parser → Planner → Executor (depends on KV layer)
//! - **Storage Engines**: Memory, BTree, LSM (implement StorageEngine trait)
//! - **FTS**: Full-text search via inverted index on KV layer
//! - **Msgq**: Message queue system on KV layer

#![allow(dead_code, unused)]

pub mod engine;
pub mod error;
pub mod sql;
pub mod fts;
pub mod kv;
pub mod query;
pub mod msgq;
pub mod server;

pub use engine::{EngineStats, StorageEngine, KvStore, CanOrderBy, CanJoin, CanFts, CanTransaction, CanScan, CanBatch};
pub use kv::{KvStore as KvApi, KvEngine};
pub use query::Db;
pub use error::{Error, Result};
pub use fts::{FtsIndex, FtsTokenizer, CjkTokenizer, EnglishTokenizer};
pub use sql::{parse, Executor, ResultSet, SqlExecutor};
pub use msgq::{Msgq, SyncQueue, QueueMeta, SyncQueueMessage, QueueStats, SyncPubSub, SyncPubSubMessage, AsyncQueue, AsyncQueueMessage, AsyncMsgq, AsyncPubSub, AsyncPubSubMessage};
