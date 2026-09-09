//! SQL Queue type definitions
//!
//! JobResult: SQL execution result enum
//! ResultStore: result storage abstraction (memory/custom)
//! SqlJob: SQL job description

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::RwLock;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum JobResult {
    Select {
        columns: Vec<String>,
        rows: Vec<Vec<serde_json::Value>>,
    },
    Insert { affected: u64 },
    Update { affected: u64 },
    Delete { affected: u64 },
    Create { table_name: String },
    Drop { table_name: String },
    Error { message: String },
}

impl JobResult {
    pub fn to_json(&self) -> serde_json::Value {
        match self {
            JobResult::Select { columns, rows } => {
                serde_json::json!({
                    "type": "select",
                    "columns": columns,
                    "rows": rows
                })
            }
            JobResult::Insert { affected } => {
                serde_json::json!({
                    "type": "insert",
                    "affected": affected
                })
            }
            JobResult::Update { affected } => {
                serde_json::json!({
                    "type": "update",
                    "affected": affected
                })
            }
            JobResult::Delete { affected } => {
                serde_json::json!({
                    "type": "delete",
                    "affected": affected
                })
            }
            JobResult::Create { table_name } => {
                serde_json::json!({
                    "type": "create",
                    "table": table_name
                })
            }
            JobResult::Drop { table_name } => {
                serde_json::json!({
                    "type": "drop",
                    "table": table_name
                })
            }
            JobResult::Error { message } => {
                serde_json::json!({
                    "type": "error",
                    "message": message
                })
            }
        }
    }

    pub fn is_select(&self) -> bool {
        matches!(self, JobResult::Select { .. })
    }

    pub fn is_error(&self) -> bool {
        matches!(self, JobResult::Error { .. })
    }

    pub fn error_message(&self) -> Option<String> {
        match self {
            JobResult::Error { message } => Some(message.clone()),
            _ => None,
        }
    }
}

pub enum ResultStore {
    Memory(Arc<RwLock<HashMap<String, JobResult>>>),
    Custom(Box<dyn SqlResultStore>),
}

impl Clone for ResultStore {
    fn clone(&self) -> Self {
        match self {
            ResultStore::Memory(arc) => ResultStore::Memory(arc.clone()),
            ResultStore::Custom(_) => ResultStore::Memory(Arc::new(RwLock::new(HashMap::new()))),
        }
    }
}

impl ResultStore {
    pub fn memory() -> Self {
        Self::Memory(Arc::new(RwLock::new(HashMap::new())))
    }

    pub async fn store(&self, job_id: &str, result: JobResult) -> Result<(), String> {
        match self {
            ResultStore::Memory(map) => {
                let mut guard = map.write().await;
                guard.insert(job_id.to_string(), result);
                Ok(())
            }
            ResultStore::Custom(store) => store.store(job_id, result),
        }
    }

    pub async fn get(&self, job_id: &str) -> Result<Option<JobResult>, String> {
        match self {
            ResultStore::Memory(map) => {
                let guard = map.read().await;
                Ok(guard.get(job_id).cloned())
            }
            ResultStore::Custom(store) => store.get(job_id),
        }
    }
}

pub trait SqlResultStore: Send + Sync {
    fn store(&self, job_id: &str, result: JobResult) -> Result<(), String>;
    fn get(&self, job_id: &str) -> Result<Option<JobResult>, String>;
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SqlJob {
    pub job_id: String,
    pub sql: String,
    pub submitted_at: u64,
}

impl SqlJob {
    pub fn new(sql: String) -> Self {
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_millis() as u64;
        let job_id = format!("{}:{:08x}", now, fastrand::u32(..));

        Self {
            job_id,
            sql,
            submitted_at: now,
        }
    }

    pub fn serialize(&self) -> Result<Vec<u8>, String> {
        serde_json::to_vec(self).map_err(|e| e.to_string())
    }

    pub fn deserialize(data: &[u8]) -> Result<Self, String> {
        serde_json::from_slice(data).map_err(|e| e.to_string())
    }
}