//! Example 05: Full-Text Search
//!
//! 展示 FTS 功能：建立索引、搜尋、 Boolean 搜尋

use db6::{Executor, KvEngine};

fn main() {
    println!("=== Example 05: Full-Text Search ===\n");

    let engine = KvEngine::new("memory").unwrap();
    let mut executor = Executor::new(Box::new(engine));

    // 建立虛擬表（支援 FTS）
    println!("Creating FTS table...");
    executor.execute(
        "CREATE VIRTUAL TABLE articles USING fts5(title, content, tokenize='english')"
    ).unwrap();

    // 插入文章
    println!("\nInserting articles...");
    executor.execute(
        "INSERT INTO articles (title, content) VALUES ('Rust Programming', 'Rust is a systems programming language that focuses on safety and performance')"
    ).unwrap();
    executor.execute(
        "INSERT INTO articles (title, content) VALUES ('Database Systems', 'Database systems store and retrieve data efficiently using various indexing techniques')"
    ).unwrap();
    executor.execute(
        "INSERT INTO articles (title, content) VALUES ('Async Programming', 'Async programming allows non-blocking operations in Rust using futures and tokio')"
    ).unwrap();
    executor.execute(
        "INSERT INTO articles (title, content) VALUES ('Memory Safety', 'Rust guarantees memory safety without garbage collection through ownership and borrowing')"
    ).unwrap();

    // 基本搜尋
    println!("\n--- Search for 'Rust' ---");
    let result = executor.execute("SELECT * FROM articles WHERE articles MATCH 'Rust'").unwrap();
    println!("{:?}", result);

    // 多詞搜尋（AND）
    println!("\n--- Search for 'Rust AND safety' ---");
    let result = executor.execute("SELECT * FROM articles WHERE articles MATCH 'Rust AND safety'").unwrap();
    println!("{:?}", result);

    // OR 搜尋
    println!("\n--- Search for 'database OR async' ---");
    let result = executor.execute("SELECT * FROM articles WHERE articles MATCH 'database OR async'").unwrap();
    println!("{:?}", result);

    // NOT 搜尋
    println!("\n--- Search for 'programming NOT database' ---");
    let result = executor.execute("SELECT * FROM articles WHERE articles MATCH 'programming NOT database'").unwrap();
    println!("{:?}", result);

    // 前綴搜尋
    println!("\n--- Prefix search for 'mem*' ---");
    let result = executor.execute("SELECT * FROM articles WHERE articles MATCH 'mem*'").unwrap();
    println!("{:?}", result);

    // 模糊搜尋
    println!("\n--- Search for similar to 'program' ---");
    let result = executor.execute("SELECT * FROM articles WHERE articles MATCH 'program~'").unwrap();
    println!("{:?}", result);

    println!("\n=== Done ===");
}