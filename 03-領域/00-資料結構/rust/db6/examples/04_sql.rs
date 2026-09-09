//! Example 04: SQL Operations
//!
//! 展示 SQL 查詢：SELECT, JOIN, GROUP BY, 聚合函數

use db6::{Executor, KvEngine};

fn main() {
    println!("=== Example 04: SQL Operations ===\n");

    let engine = KvEngine::new("memory").unwrap();
    let mut executor = Executor::new(Box::new(engine));

    // 建立銷售資料表
    println!("Creating tables...");
    executor.execute("CREATE TABLE products (id INTEGER, name TEXT, price REAL, category TEXT)")
        .unwrap();
    executor.execute("CREATE TABLE sales (id INTEGER, product_id INTEGER, quantity INTEGER, date TEXT)")
        .unwrap();

    // 插入產品資料
    println!("\nInserting products...");
    executor.execute("INSERT INTO products VALUES (1, 'Laptop', 999.99, 'Electronics')").unwrap();
    executor.execute("INSERT INTO products VALUES (2, 'Mouse', 29.99, 'Electronics')").unwrap();
    executor.execute("INSERT INTO products VALUES (3, 'Chair', 199.99, 'Furniture')").unwrap();
    executor.execute("INSERT INTO products VALUES (4, 'Desk', 399.99, 'Furniture')").unwrap();

    // 插入銷售資料
    println!("Inserting sales...");
    executor.execute("INSERT INTO sales VALUES (1, 1, 5, '2024-01-15')").unwrap();
    executor.execute("INSERT INTO sales VALUES (2, 1, 3, '2024-01-20')").unwrap();
    executor.execute("INSERT INTO sales VALUES (3, 2, 10, '2024-01-15')").unwrap();
    executor.execute("INSERT INTO sales VALUES (4, 3, 2, '2024-01-18')").unwrap();
    executor.execute("INSERT INTO sales VALUES (5, 4, 1, '2024-01-25')").unwrap();

    // 基本查詢
    println!("\n--- All products ---");
    let result = executor.execute("SELECT * FROM products").unwrap();
    println!("{:?}", result);

    // 條件查詢
    println!("\n--- Electronics products ---");
    let result = executor.execute("SELECT * FROM products WHERE category = 'Electronics'").unwrap();
    println!("{:?}", result);

    // JOIN 查詢
    println!("\n--- Sales with product details ---");
    let sql = r#"
        SELECT s.id, p.name, s.quantity, s.date 
        FROM sales s 
        JOIN products p ON s.product_id = p.id
    "#;
    let result = executor.execute(sql).unwrap();
    println!("{:?}", result);

    // 聚合函數
    println!("\n--- Total sales by product ---");
    let sql = r#"
        SELECT product_id, SUM(quantity) as total_qty 
        FROM sales 
        GROUP BY product_id
    "#;
    let result = executor.execute(sql).unwrap();
    println!("{:?}", result);

    // 子查詢
    println!("\n--- Products with above-average price ---");
    let sql = r#"
        SELECT name, price FROM products 
        WHERE price > (SELECT AVG(price) FROM products)
    "#;
    let result = executor.execute(sql).unwrap();
    println!("{:?}", result);

    // ORDER BY
    println!("\n--- Products sorted by price ---");
    let result = executor.execute("SELECT * FROM products ORDER BY price DESC").unwrap();
    println!("{:?}", result);

    // LIMIT
    println!("\n--- Top 2 expensive products ---");
    let result = executor.execute("SELECT * FROM products ORDER BY price DESC LIMIT 2").unwrap();
    println!("{:?}", result);

    println!("\n=== Done ===");
}