//! SQL + JSON Path Example
//!
//! 展示如何使用 SQL 進行 JSON Path 查詢
//!
//! # 對照 query/ API 的語法
//!
//! | query/ API | SQL API |
//! |------------|---------|
//! | `.filter("$.age > 25")` | `WHERE @.age > 25` |
//! | `.filter("$.name = 'Alice'")` | `WHERE @.name = 'Alice'` |
//! | `.filter("$.city IN ('台北','台中')")` | `WHERE @.city IN ('台北','台中')` |
//!
//! 注意：本範例使用 `Executor` 進行 SQL 查詢

use db6::{Executor, engine::BTreeMemoryEngine};

fn main() {
    println!("=== SQL + JSON Path Example ===\n");

    // 建立 BTree 引擎
    let engine = BTreeMemoryEngine::new();
    let mut executor = Executor::new(Box::new(engine));

    // 測試 1: SQL INSERT + SELECT with JSON Path
    println!("--- SQL INSERT + SELECT with JSON Path ---");

    // 插入 JSON 資料
    executor.execute("INSERT INTO users VALUES ('1', '{\"name\":\"Alice\",\"age\":30,\"city\":\"Taipei\"}')").unwrap();
    executor.execute("INSERT INTO users VALUES ('2', '{\"name\":\"Bob\",\"age\":25,\"city\":\"Kaohsiung\"}')").unwrap();
    executor.execute("INSERT INTO users VALUES ('3', '{\"name\":\"Charlie\",\"age\":35,\"city\":\"Taipei\"}')").unwrap();
    executor.execute("INSERT INTO users VALUES ('4', '{\"name\":\"Diana\",\"age\":28,\"city\":\"Taichung\"}')").unwrap();

    println!("Inserted 4 users");

    // 查詢全部
    let result = executor.execute("SELECT * FROM users").unwrap();
    println!("\nSELECT * FROM users:");
    for row in &result.rows {
        println!("  key={}, value={}", row[0], row[1]);
    }

    // JSON Path 查詢：@.age > 27
    println!("\n// SQL: WHERE @.age > 27");
    let result = executor.execute("SELECT * FROM users WHERE @.age > 27").unwrap();
    println!("Users with age > 27:");
    for row in &result.rows {
        println!("  key={}, value={}", row[0], row[1]);
    }

    // JSON Path 查詢：@.city = 'Taipei'
    println!("\n// SQL: WHERE @.city = 'Taipei'");
    let result = executor.execute("SELECT * FROM users WHERE @.city = 'Taipei'").unwrap();
    println!("Users in Taipei:");
    for row in &result.rows {
        println!("  key={}, value={}", row[0], row[1]);
    }

    // JSON Path 查詢：LIKE
    println!("\n// SQL: WHERE @.name LIKE 'C%'");
    let result = executor.execute("SELECT * FROM users WHERE @.name LIKE 'C%'").unwrap();
    println!("Users with name starting with C:");
    for row in &result.rows {
        println!("  key={}, value={}", row[0], row[1]);
    }

    // JSON Path 查詢：AND 複合條件
    println!("\n// SQL: WHERE @.city = 'Taipei' AND @.age > 27");
    let result = executor.execute("SELECT * FROM users WHERE @.city = 'Taipei' AND @.age > 27").unwrap();
    println!("Users in Taipei with age > 27:");
    for row in &result.rows {
        println!("  key={}, value={}", row[0], row[1]);
    }

    // JSON Path 查詢：OR 複合條件
    println!("\n// SQL: WHERE @.age < 25 OR @.name LIKE 'D%'");
    let result = executor.execute("SELECT * FROM users WHERE @.age < 25 OR @.name LIKE 'D%'").unwrap();
    println!("Users with age < 25 OR name starting with D:");
    for row in &result.rows {
        println!("  key={}, value={}", row[0], row[1]);
    }

    // JSON Path 查詢：IS NULL
    println!("\n// SQL: WHERE @.phone IS NULL");
    executor.execute("INSERT INTO users VALUES ('5', '{\"name\":\"Eve\",\"age\":32}')").unwrap();
    let result = executor.execute("SELECT * FROM users WHERE @.phone IS NULL").unwrap();
    println!("Users without phone (IS NULL):");
    for row in &result.rows {
        println!("  key={}, value={}", row[0], row[1]);
    }

    println!("\n=== SQL + JSON Path Example Done ===");
}