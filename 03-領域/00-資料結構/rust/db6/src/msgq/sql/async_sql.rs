//! Async SQL Executor — based on tokio + mini-redis pattern
//!
//! Design principles:
//! - Each SQL spawns an independent task (not worker pool), achieving true concurrency
//! - Semaphore limits concurrency to prevent resource exhaustion
//! - Supports graceful shutdown via broadcast channel to notify all tasks
//! - Uses tokio::select! to listen for shutdown signal and SQL execution simultaneously

use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;
use tokio::sync::{Semaphore, broadcast};

use super::types::{JobResult, ResultStore, SqlJob};

const DEFAULT_CONCURRENCY_LIMIT: usize = 100;

pub struct AsyncSqlExecutor {
    results: ResultStore,
    semaphore: Arc<Semaphore>,
    concurrency_limit: Arc<AtomicUsize>,
    shutdown: broadcast::Sender<()>,
}

impl AsyncSqlExecutor {
    pub fn new(result_store: ResultStore) -> Self {
        Self::with_concurrency_limit(result_store, DEFAULT_CONCURRENCY_LIMIT)
    }

    pub fn with_concurrency_limit(result_store: ResultStore, limit: usize) -> Self {
        let (shutdown, _) = broadcast::channel(1);

        Self {
            results: result_store,
            semaphore: Arc::new(Semaphore::new(limit)),
            concurrency_limit: Arc::new(AtomicUsize::new(limit)),
            shutdown,
        }
    }

    /// Execute SQL — each SQL immediately spawns an independent task (true concurrency)
    ///
    /// 1. Create SqlJob and get job_id
    /// 2. Spawn a tokio task
    /// 3. Acquire semaphore inside task (ensures permit lifetime is correct)
    /// 4. Use tokio::select! to listen for shutdown and SQL execution
    /// 5. Store result in ResultStore
    pub async fn execute(&self, sql: &str) -> Result<String, String> {
        let job = SqlJob::new(sql.to_string());
        let job_id = job.job_id.clone();
        let results = self.results.clone();
        let semaphore = self.semaphore.clone();
        let mut shutdown_rx = self.shutdown.subscribe();

        tokio::spawn(async move {
            let permit = semaphore.acquire_owned().await.ok();

            let result = tokio::select! {
                res = execute_sql(&job.sql) => res,
                _ = shutdown_rx.recv() => {
                    JobResult::Error { message: "server shutting down".to_string() }
                }
            };

            if let Err(e) = results.store(&job.job_id, result).await {
                eprintln!("Failed to store result: {}", e);
            }

            drop(permit);
        });

        Ok(job_id)
    }

    pub async fn poll(&self, job_id: &str) -> Result<JobResult, String> {
        match self.results.get(job_id).await {
            Ok(Some(result)) => Ok(result),
            Ok(None) => Err("pending".to_string()),
            Err(e) => Err(e),
        }
    }

    pub async fn execute_and_wait(
        &self,
        sql: &str,
        timeout_ms: u64,
    ) -> Result<JobResult, String> {
        let job_id = self.execute(sql).await?;

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

            match self.poll(&job_id).await {
                Ok(result) => return Ok(result),
                Err(e) if e == "pending" => {
                    tokio::time::sleep(std::time::Duration::from_millis(50)).await;
                }
                Err(e) => return Err(e),
            }
        }
    }

    pub fn shutdown(&self) {
        let _ = self.shutdown.send(());
    }

    pub fn available_concurrency(&self) -> usize {
        self.semaphore.available_permits()
    }

    pub fn concurrency_limit(&self) -> usize {
        self.concurrency_limit.load(Ordering::Relaxed)
    }
}

impl Clone for AsyncSqlExecutor {
    fn clone(&self) -> Self {
        Self {
            results: self.results.clone(),
            semaphore: self.semaphore.clone(),
            concurrency_limit: self.concurrency_limit.clone(),
            shutdown: self.shutdown.clone(),
        }
    }
}

/// Mock SQL execution (not yet integrated with real SQL executor)
///
/// Returns mock results based on SQL prefix (SELECT/INSERT/UPDATE/DELETE/CREATE/DROP).
async fn execute_sql(sql: &str) -> JobResult {
    tokio::time::sleep(std::time::Duration::from_millis(50)).await;

    let sql_lower = sql.trim().to_lowercase();

    if sql_lower.starts_with("select") {
        JobResult::Select {
            columns: vec!["id".to_string(), "name".to_string(), "email".to_string()],
            rows: vec![
                vec![serde_json::json!(1), serde_json::json!("Alice"), serde_json::json!("alice@example.com")],
                vec![serde_json::json!(2), serde_json::json!("Bob"), serde_json::json!("bob@example.com")],
                vec![serde_json::json!(3), serde_json::json!("Charlie"), serde_json::json!("charlie@example.com")],
            ],
        }
    } else if sql_lower.starts_with("insert") {
        JobResult::Insert { affected: 1 }
    } else if sql_lower.starts_with("update") {
        JobResult::Update { affected: 1 }
    } else if sql_lower.starts_with("delete") {
        JobResult::Delete { affected: 1 }
    } else if sql_lower.starts_with("create") {
        let table = sql_lower
            .split_whitespace()
            .nth(2)
            .unwrap_or("unknown")
            .trim_end_matches(';');
        JobResult::Create { table_name: table.to_string() }
    } else if sql_lower.starts_with("drop") {
        let table = sql_lower
            .split_whitespace()
            .nth(2)
            .unwrap_or("unknown")
            .trim_end_matches(';');
        JobResult::Drop { table_name: table.to_string() }
    } else {
        JobResult::Error {
            message: format!("Unknown SQL type: {}", sql),
        }
    }
}