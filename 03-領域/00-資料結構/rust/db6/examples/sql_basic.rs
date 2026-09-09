//! SQL 基本操作範例
//! 
//! 展示如何使用 db6 的 SQL 解析與執行

use db6::{Executor, engine::BTreeMemoryEngine};

fn main() {
    println!("=== SQL Basic Example ===\n");

    // 建立 BTree 引擎（支援 ORDER BY/scan）
    let engine = BTreeMemoryEngine::new();
    let mut executor = Executor::new(Box::new(engine));

    // INSERT
    println!("INSERT:");
    executor.execute("INSERT INTO users VALUES ('Alice')").unwrap();
    executor.execute("INSERT INTO users VALUES ('Bob')").unwrap();
    executor.execute("INSERT INTO users VALUES ('Charlie')").unwrap();

    // SELECT
    println!("\nSELECT *:");
    let result = executor.execute("SELECT * FROM users").unwrap();
    for row in result.rows {
        println!("  {:?}", row);
    }

    // SELECT
    println!("\nSELECT * again:");
    let result = executor.execute("SELECT * FROM users").unwrap();
    for row in result.rows {
        println!("  {:?}", row);
    }

    // SELECT with LIMIT
    println!("\nSELECT with LIMIT 2:");
    let result = executor.execute("SELECT * FROM users LIMIT 2").unwrap();
    for row in result.rows {
        println!("  {:?}", row);
    }

    // UPDATE
    println!("\nUPDATE:");
    let result = executor.execute("UPDATE users SET value = 'newvalue'").unwrap();
    println!("  affected: {}", result.affected);

    // DELETE
    println!("\nDELETE:");
    let result = executor.execute("DELETE FROM users").unwrap();
    println!("  affected: {}", result.affected);

    // Verify empty
    let result = executor.execute("SELECT * FROM users").unwrap();
    println!("\nAfter DELETE, rows: {}", result.rows.len());

    println!("\n=== Done ===");
}