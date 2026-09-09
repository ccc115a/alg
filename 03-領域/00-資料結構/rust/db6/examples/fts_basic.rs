//! FTS 基本操作範例
//! 
//! 展示如何使用 db6 的全文檢索功能

use db6::{FtsIndex, engine::HashMemoryEngine};

fn main() {
    println!("=== FTS Basic Example ===\n");

    // 建立引擎
    let mut engine = HashMemoryEngine::new();

    // 建立 FTS 索引
    let mut fts = FtsIndex::new(&mut engine);

    // 加入文件
    fts.insert(1, "Hello world").unwrap();
    fts.insert(2, "你好世界").unwrap();
    fts.insert(3, "Rust 程式設計").unwrap();
    fts.insert(4, "Database system").unwrap();
    fts.insert(5, "資料庫系統").unwrap();

    println!("Added 5 documents\n");

    // 搜尋
    println!("Search 'world':");
    let results = fts.search("world").unwrap();
    println!("  doc_ids: {:?}", results);

    // 搜尋中文
    println!("\nSearch '資料庫':");
    let results = fts.search("資料庫").unwrap();
    println!("  doc_ids: {:?}", results);

    // BM25 搜尋（返回分數）
    println!("\nBM25 Search 'database':");
    let results = fts.search_bm25("database").unwrap();
    for (doc_id, score) in results {
        println!("  doc_id: {}, score: {}", doc_id, score);
    }

    // 前綴搜尋
    println!("\nPrefix Search 'Da':");
    let results = fts.search_prefix("Da").unwrap();
    println!("  doc_ids: {:?}", results);

    println!("\n=== Done ===");
}