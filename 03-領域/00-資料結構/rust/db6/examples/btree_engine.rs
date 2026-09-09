//! BTree Engine 範例
//! 
//! 展示如何使用 BTreeEngine

use db6::engine::{StorageEngine, BTreeEngine};
use std::path::Path;

fn main() {
    println!("=== BTree Engine Example ===\n");

    // 測試 1: 記憶體模式
    println!("--- Memory Mode ---");
    let mut engine = BTreeEngine::new();
    println!("Engine type: {}", engine.engine_type());

    engine.put(1, b"key1", b"value1").unwrap();
    engine.put(1, b"key2", b"value2").unwrap();
    engine.put(1, b"key3", b"value3").unwrap();

    let val = engine.get(1, b"key1").unwrap();
    println!("get key1: {:?}", val);

    // 掃描
    let rows = engine.scan(1, b"key1", b"key3").unwrap();
    println!("\nscan key1 to key3:");
    for (k, v) in rows {
        println!("  {} -> {}", String::from_utf8_lossy(&k), String::from_utf8_lossy(&v));
    }

    // 交易支援
    println!("\n--- Transaction Test ---");
    engine.begin_transaction().unwrap();
    engine.put(1, b"key4", b"value4").unwrap();
    engine.commit_transaction().unwrap();
    let val = engine.get(1, b"key4").unwrap();
    println!("after commit, get key4: {:?}", val);

    // 測試 2: 持久化模式
    println!("\n--- Persistence Mode ---");
    let temp_dir = std::env::temp_dir().join("db6_btree_test");
    let _ = std::fs::remove_dir_all(&temp_dir);
    std::fs::create_dir_all(&temp_dir).unwrap();

    // 寫入資料
    {
        let mut engine = BTreeEngine::open(Path::new(&temp_dir)).unwrap();
        engine.put(1, b"name", b"Alice").unwrap();
        engine.put(1, b"age", b"30").unwrap();
        engine.flush().unwrap();
        println!("Wrote data and flushed");
    }

    // 重新開啟並讀取
    {
        let engine = BTreeEngine::open(Path::new(&temp_dir)).unwrap();
        let name = engine.get(1, b"name").unwrap();
        let age = engine.get(1, b"age").unwrap();
        println!("After reopen: name={:?}, age={:?}", name, age);
        
        // 驗證
        assert!(name.is_some());
        assert!(age.is_some());
        println!("Persistence test PASSED!");
    }

    // 清理
    let _ = std::fs::remove_dir_all(&temp_dir);

    println!("\n=== Done ===");
}