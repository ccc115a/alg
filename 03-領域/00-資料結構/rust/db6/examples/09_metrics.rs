//! Example 09: Monitoring and Metrics
//!
//! 展示監控功能：AsyncSqlExecutor Metrics

#[tokio::main]
async fn main() {
    println!("=== Example 09: Monitoring and Metrics ===\n");

    // AsyncSqlExecutor Metrics
    println!("--- AsyncSqlExecutor Metrics ---");
    let results = db6::msgq::ResultStore::memory();
    let executor = db6::msgq::AsyncSqlExecutor::new(results);
    
    println!("  Available concurrency: {}", executor.available_concurrency());
    println!("  Concurrency limit: {}", executor.concurrency_limit());

    // 並發限制測試
    println!("\n--- Testing concurrency limit ---");
    let limited_executor = db6::msgq::AsyncSqlExecutor::with_concurrency_limit(
        db6::msgq::ResultStore::memory(),
        2
    );
    println!("  Limited executor: {} permits", limited_executor.concurrency_limit());

    println!("\n=== Done ===");
}