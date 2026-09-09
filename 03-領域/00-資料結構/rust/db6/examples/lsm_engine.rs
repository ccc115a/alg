//! LSM Engine 範例
//! 
//! 展示如何使用 LsmEngine

use db6::engine::{StorageEngine, LsmEngine};
use std::path::Path;

fn main() {
    println!("=== LSM Engine Example ===\n");

    // 測試 1: 記憶體模式
    println!("--- Memory Mode ---");
    let mut engine = LsmEngine::new();
    println!("Engine type: {}", engine.engine_type());

    engine.put(1, b"key1", b"value1").unwrap();
    engine.put(1, b"key2", b"value2").unwrap();
    engine.put(1, b"key3", b"value3").unwrap();

    let val = engine.get(1, b"key1").unwrap();
    println!("get key1: {:?}", val);

    // 交易支援
    println!("\n--- Transaction Test ---");
    engine.begin_transaction().unwrap();
    engine.put(1, b"key4", b"value4").unwrap();
    engine.commit_transaction().unwrap();
    let val = engine.get(1, b"key4").unwrap();
    println!("after commit, get key4: {:?}", val);

    // 測試 2: 持久化模式 (SSTable)
    println!("\n--- Persistence Mode (SSTable) ---");
    let temp_dir = std::env::temp_dir().join("db6_lsm_test");
    let _ = std::fs::remove_dir_all(&temp_dir);
    std::fs::create_dir_all(&temp_dir).unwrap();

    // Write and flush to SSTable
    {
        let mut engine = LsmEngine::open(Path::new(&temp_dir)).unwrap();
        engine.put(1, b"name", b"Alice").unwrap();
        engine.put(1, b"age", b"30").unwrap();
        engine.flush().unwrap();
        println!("Wrote data and flushed to SSTable");
    }

    // Reopen and verify
    {
        let engine = LsmEngine::open(Path::new(&temp_dir)).unwrap();
        let name = engine.get(1, b"name").unwrap();
        let age = engine.get(1, b"age").unwrap();
        println!("After reopen: name={:?}, age={:?}", name, age);
        assert!(name.is_some());
        println!("SSTable persistence test PASSED!");
    }

    // 測試 3: WAL recovery
    println!("\n--- WAL Recovery Test ---");
    let temp_dir2 = std::env::temp_dir().join("db6_lsm_wal_test");
    let _ = std::fs::remove_dir_all(&temp_dir2);

    // Write with transaction (writes to WAL)
    {
        let mut engine = LsmEngine::open(Path::new(&temp_dir2)).unwrap();
        engine.begin_transaction().unwrap();
        engine.put(1, b"key1", b"value1").unwrap();
        engine.put(1, b"key2", b"value2").unwrap();
        engine.commit_transaction().unwrap();
    }

    // Reopen - WAL should be recovered
    {
        let engine = LsmEngine::open(Path::new(&temp_dir2)).unwrap();
        let val1 = engine.get(1, b"key1").unwrap();
        let val2 = engine.get(1, b"key2").unwrap();
        println!("After reopen: key1={:?}, key2={:?}", val1, val2);
        assert!(val1.is_some());
        println!("WAL recovery test PASSED!");
    }

    // Cleanup
    let _ = std::fs::remove_dir_all(&temp_dir);
    let _ = std::fs::remove_dir_all(&temp_dir2);

    println!("\n=== Done ===");
}