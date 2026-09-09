//! Example 01: Basic CRUD Operations
//!
//! 展示基本的資料庫操作：建立表、插入、查詢、更新、刪除

use db6::{Executor, KvEngine};

fn main() {
    println!("=== Example 01: Basic CRUD ===\n");

    // 建立記憶體引擎
    let engine = KvEngine::new("memory").unwrap();
    let mut executor = Executor::new(Box::new(engine));

    // 建立表
    let sql = r#"
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT
        )
    "#;
    match executor.execute(sql) {
        Ok(result) => println!("Created table: {:?}", result),
        Err(e) => println!("Error: {}", e),
    }

    // 插入資料
    let sql = "INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com')";
    match executor.execute(sql) {
        Ok(result) => println!("Inserted: {:?}", result),
        Err(e) => println!("Error: {}", e),
    }

    // 插入多筆
    let sql = "INSERT INTO users (name, email) VALUES ('Bob', 'bob@example.com'), ('Charlie', 'charlie@example.com')";
    match executor.execute(sql) {
        Ok(result) => println!("Inserted multiple: {:?}", result),
        Err(e) => println!("Error: {}", e),
    }

    // 查詢所有
    let sql = "SELECT * FROM users";
    match executor.execute(sql) {
        Ok(result) => {
            println!("\nQuery results:");
            println!("{:?}", result);
        }
        Err(e) => println!("Error: {}", e),
    }

    // 條件查詢
    let sql = "SELECT * FROM users WHERE id = 1";
    match executor.execute(sql) {
        Ok(result) => println!("\nUser with id=1: {:?}", result),
        Err(e) => println!("Error: {}", e),
    }

    // 更新資料
    let sql = "UPDATE users SET email = 'alice.new@example.com' WHERE name = 'Alice'";
    match executor.execute(sql) {
        Ok(result) => println!("\nUpdated: {:?}", result),
        Err(e) => println!("Error: {}", e),
    }

    // 刪除資料
    let sql = "DELETE FROM users WHERE name = 'Bob'";
    match executor.execute(sql) {
        Ok(result) => println!("Deleted: {:?}", result),
        Err(e) => println!("Error: {}", e),
    }

    // 最終查詢
    let sql = "SELECT * FROM users";
    match executor.execute(sql) {
        Ok(result) => println!("\nFinal state: {:?}", result),
        Err(e) => println!("Error: {}", e),
    }

    println!("\n=== Done ===");
}