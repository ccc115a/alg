use crate::error::Result;
use std::path::Path;

#[derive(Debug, Clone, Default)]
pub struct EngineStats {
    pub key_count: u64,
    pub size_bytes: u64,
    pub cache_hit_rate: Option<f64>,
    pub in_transaction: bool,
    pub engine: &'static str,
}

pub trait StorageEngine: Send + Sync {
    fn open(path: &Path) -> Result<Box<dyn StorageEngine>>
    where
        Self: Sized;

    fn open_memory() -> Box<dyn StorageEngine>
    where
        Self: Sized;

    fn engine_type(&self) -> &'static str;

    fn get(&self, table_id: u32, key: &[u8]) -> Result<Option<Vec<u8>>>;

    fn put(&mut self, table_id: u32, key: &[u8], value: &[u8]) -> Result<()>;

    fn delete(&mut self, table_id: u32, key: &[u8]) -> Result<()>;

    fn scan(&self, table_id: u32, start: &[u8], end: &[u8]) -> Result<Vec<(Vec<u8>, Vec<u8>)>>;

    fn batch_put(&mut self, table_id: u32, pairs: Vec<(Vec<u8>, Vec<u8>)>) -> Result<()>;

    fn range_delete(&mut self, table_id: u32, start: &[u8], end: &[u8]) -> Result<()>;

    fn flush(&mut self) -> Result<()>;

    fn sync(&mut self) -> Result<()>;

    fn begin_transaction(&mut self) -> Result<()>;

    fn commit_transaction(&mut self) -> Result<()>;

    fn rollback_transaction(&mut self) -> Result<()>;

    fn has_transaction(&self) -> bool;

    fn stats(&self) -> EngineStats;
}

pub trait KvStore: Send + Sync {
    fn engine_type(&self) -> &'static str {
        "unknown"
    }
    fn put(&mut self, table_id: u32, key: &[u8], value: &[u8]) -> Result<()>;
    fn get(&mut self, table_id: u32, key: &[u8]) -> Result<Option<Vec<u8>>>;
    fn delete(&mut self, table_id: u32, key: &[u8]) -> Result<()>;
    fn scan(&self, table_id: u32, start: &[u8], end: &[u8]) -> Result<Vec<(Vec<u8>, Vec<u8>)>>;
}

pub trait CanScan {}
pub trait CanBatch {}
pub trait CanTransaction {}
pub trait CanOrderBy {}
pub trait CanJoin {}
pub trait CanFts {}
pub trait CanGroupBy {}