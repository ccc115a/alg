//! Memory Engine 範例
//! 
//! 展示兩種 Memory Engine 的差異

use db6::engine::{StorageEngine, HashMemoryEngine, BTreeMemoryEngine};
use std::path::Path;

fn test_hash_engine() {
    println!("\n--- HashMemoryEngine (O(1) ops, no ORDER BY) ---");
    let mut engine = HashMemoryEngine::new();

    println!("Engine type: {}", engine.engine_type());

    engine.put(1, b"key1", b"value1").unwrap();
    engine.put(1, b"key2", b"value2").unwrap();

    let val = engine.get(1, b"key1").unwrap();
    println!("get key1: {:?}", val);

    // scan returns all keys (no range support)
    let rows = engine.scan(1, b"", b"").unwrap();
    println!("scan all: {} rows", rows.len());

    // Note: ORDER BY not supported
    println!("begin_transaction: {:?}", engine.begin_transaction());
}

fn test_btree_engine() {
    println!("\n--- BTreeMemoryEngine (O(log n), supports ORDER BY) ---");
    let mut engine = BTreeMemoryEngine::new();

    println!("Engine type: {}", engine.engine_type());

    engine.put(1, b"key1", b"value1").unwrap();
    engine.put(1, b"key2", b"value2").unwrap();
    engine.put(1, b"key3", b"value3").unwrap();

    let val = engine.get(1, b"key1").unwrap();
    println!("get key1: {:?}", val);

    // scan with range
    let rows = engine.scan(1, b"key1", b"key3").unwrap();
    println!("scan key1 to key3: {} rows", rows.len());

    // ORDER BY is automatic (BTreeMap is sorted)
    let all = engine.scan(1, b"", b"").unwrap();
    println!("scan all (ordered): {:?}", all.iter().map(|(k,_)| String::from_utf8_lossy(k)).collect::<Vec<_>>());

    // Note: No transaction support
    println!("begin_transaction: {:?}", engine.begin_transaction());
}

fn test_hash_persistence() {
    println!("\n--- HashMemoryEngine Persistence ---");
    let temp_dir = std::env::temp_dir().join("db6_hash_test");
    let _ = std::fs::remove_dir_all(&temp_dir);
    std::fs::create_dir_all(&temp_dir).unwrap();

    // Write and flush
    {
        let mut engine = HashMemoryEngine::open(Path::new(&temp_dir)).unwrap();
        engine.put(1, b"name", b"Alice").unwrap();
        engine.put(1, b"age", b"30").unwrap();
        engine.flush().unwrap();
        println!("Wrote data and flushed");
    }

    // Reopen and verify
    {
        let engine = HashMemoryEngine::open(Path::new(&temp_dir)).unwrap();
        let name = engine.get(1, b"name").unwrap();
        let age = engine.get(1, b"age").unwrap();
        println!("After reopen: name={:?}, age={:?}", name, age);
        assert!(name.is_some());
        println!("Hash persistence test PASSED!");
    }

    let _ = std::fs::remove_dir_all(&temp_dir);
}

fn test_btree_persistence() {
    println!("\n--- BTreeMemoryEngine Persistence ---");
    let temp_dir = std::env::temp_dir().join("db6_btree_mem_test");
    let _ = std::fs::remove_dir_all(&temp_dir);
    std::fs::create_dir_all(&temp_dir).unwrap();

    // Write and flush
    {
        let mut engine = BTreeMemoryEngine::open(Path::new(&temp_dir)).unwrap();
        engine.put(1, b"name", b"Bob").unwrap();
        engine.put(1, b"age", b"25").unwrap();
        engine.flush().unwrap();
        println!("Wrote data and flushed");
    }

    // Reopen and verify
    {
        let engine = BTreeMemoryEngine::open(Path::new(&temp_dir)).unwrap();
        let name = engine.get(1, b"name").unwrap();
        let age = engine.get(1, b"age").unwrap();
        println!("After reopen: name={:?}, age={:?}", name, age);
        assert!(name.is_some());
        println!("BTree persistence test PASSED!");
    }

    let _ = std::fs::remove_dir_all(&temp_dir);
}

fn main() {
    println!("=== Memory Engine Example ===\n");
    println!("Two implementations:");
    println!("  - HashMemoryEngine: Redis-like, fast O(1), no ORDER BY/scan");
    println!("  - BTreeMemoryEngine: SQLite-like, supports SQL operations");
    println!("  - Both support open(path) + flush() for persistence\n");

    test_hash_engine();
    test_btree_engine();
    test_hash_persistence();
    test_btree_persistence();

    println!("\n=== Done ===");
}