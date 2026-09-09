//! Example 06: Streaming Operations
//!
//! 展示流處理：map-reduce, filtering, aggregation

use db6::{Executor, KvEngine};

fn main() {
    println!("=== Example 06: Streaming Operations ===\n");

    let engine = KvEngine::new("memory").unwrap();
    let mut executor = Executor::new(Box::new(engine));

    // 建立銷售資料
    println!("Setting up sales data...");
    executor.execute("CREATE TABLE sales (product TEXT, amount REAL, region TEXT)")
        .unwrap();
    
    let sales_data = vec![
        ("Apple", 100.0, "North"),
        ("Apple", 150.0, "South"),
        ("Banana", 80.0, "North"),
        ("Banana", 90.0, "South"),
        ("Cherry", 200.0, "North"),
        ("Cherry", 180.0, "South"),
    ];

    for (product, amount, region) in sales_data {
        executor.execute(&format!(
            "INSERT INTO sales VALUES ('{}', {}, '{}')",
            product, amount, region
        )).unwrap();
    }

    // Map-Reduce: 按產品分組計算總銷售額
    println!("\n--- Map-Reduce: Sales by product ---");
    let result = executor.execute("SELECT * FROM sales").unwrap();
    println!("Result: {:?}", result);

    // Filter: 篩選特定條件
    println!("\n--- Filter: Sales > 100 ---");
    let result = executor.execute("SELECT * FROM sales WHERE amount > 100").unwrap();
    println!("{:?}", result);

    // Aggregation: 多種聚合
    println!("\n--- Aggregation: Summary ---");
    let result = executor.execute(
        "SELECT COUNT(*) as cnt, SUM(amount) as total, AVG(amount) as avg FROM sales"
    ).unwrap();
    println!("{:?}", result);

    // Group By
    println!("\n--- Group By: Sales by region ---");
    let result = executor.execute(
        "SELECT region, COUNT(*) as cnt, SUM(amount) as total FROM sales GROUP BY region"
    ).unwrap();
    println!("{:?}", result);

    // Having
    println!("\n--- Having: Regions with total > 200 ---");
    let result = executor.execute(
        "SELECT region, SUM(amount) as total FROM sales GROUP BY region HAVING SUM(amount) > 200"
    ).unwrap();
    println!("{:?}", result);

    println!("\n=== Done ===");
}