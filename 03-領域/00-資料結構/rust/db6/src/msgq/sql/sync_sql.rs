//! Sync SQL Executor — based on SyncQueue (blocking)
//!
//! Uses SyncQueue as work queue, polling to wait for SQL execution results.

use std::collections::HashMap;
use std::sync::Arc;

use crate::kv::KvEngine;
use crate::msgq::SyncQueue;
use super::types::{JobResult, SqlJob};

pub struct SyncSqlExecutor {
    queue: SyncQueue,
    results: Arc<std::sync::Mutex<HashMap<String, JobResult>>>,
}

impl SyncSqlExecutor {
    pub fn new(engine: Arc<std::sync::RwLock<KvEngine>>) -> Self {
        let results = Arc::new(std::sync::Mutex::new(HashMap::new()));
        let queue = SyncQueue::new("sql", engine);

        Self { queue, results }
    }

    pub fn execute(&mut self, sql: &str) -> Result<JobResult, String> {
        let job = SqlJob::new(sql.to_string());
        let job_id = job.job_id.clone();
        let payload = job.serialize()?;

        self.queue.enqueue(payload, 30).map_err(|e| format!("{:?}", e))?;

        loop {
            std::thread::sleep(std::time::Duration::from_millis(50));

            if let Ok(results) = self.results.lock() {
                if let Some(result) = results.get(&job_id) {
                    return Ok(result.clone());
                }
            }
        }
    }

    pub fn execute_with_timeout(&mut self, sql: &str, timeout_ms: u64) -> Result<JobResult, String> {
        let job = SqlJob::new(sql.to_string());
        let job_id = job.job_id.clone();
        let payload = job.serialize()?;

        self.queue.enqueue(payload, 30).map_err(|e| format!("{:?}", e))?;

        let start = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_millis() as u64;
        let deadline = start + timeout_ms;

        loop {
            let now = std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_millis() as u64;

            if now >= deadline {
                return Err("timeout".to_string());
            }

            std::thread::sleep(std::time::Duration::from_millis(50));

            if let Ok(results) = self.results.lock() {
                if let Some(result) = results.get(&job_id) {
                    return Ok(result.clone());
                }
            }
        }
    }
}