//! KvEngine Factory 範例
//! 
//! 展示如何使用 KvEngine 統一工廠建立 KV store

use db6::kv::{KvStore, KvEngine};

fn main() {
    println!("=== KvEngine Factory Example ===\n");

    // 測試 1: Hash Memory Engine
    println!("--- HashMemoryEngine ---");
    let mut kv = KvEngine::new("memory").unwrap();
    println!("Engine type: {}", kv.engine_type());
    
    kv.put(1, b"key1", b"value1").unwrap();
    kv.put(1, b"key2", b"value2").unwrap();
    kv.put(1, b"key3", b"value3").unwrap();
    
    let val = kv.get(1, b"key1").unwrap();
    println!("get key1: {:?}", val);
    
    let rows = kv.scan(1, b"", b"").unwrap();
    println!("scan all: {} rows", rows.len());

    // 測試 2: BTree Memory Engine
    println!("\n--- BTreeMemoryEngine ---");
    let mut kv = KvEngine::new("btree").unwrap();
    println!("Engine type: {}", kv.engine_type());
    
    kv.put(1, b"key1", b"value1").unwrap();
    kv.put(1, b"key2", b"value2").unwrap();
    
    let val = kv.get(1, b"key1").unwrap();
    println!("get key1: {:?}", val);
    
    // BTree supports range scan
    let rows = kv.scan(1, b"key1", b"key2").unwrap();
    println!("scan key1 to key2: {} rows", rows.len());

    // 測試 3: LSM Engine (memory mode)
    println!("\n--- LsmEngine (memory) ---");
    let mut kv = KvEngine::new("lsm").unwrap();
    println!("Engine type: {}", kv.engine_type());
    
    kv.put(1, b"key1", b"value1").unwrap();
    
    let val = kv.get(1, b"key1").unwrap();
    println!("get key1: {:?}", val);

    // 測試 4: BTree 持久化
    println!("\n--- BTree Persistence ---");
    let temp_dir = std::env::temp_dir().join("db6_kv_factory_test");
    let _ = std::fs::remove_dir_all(&temp_dir);
    std::fs::create_dir_all(&temp_dir).unwrap();

    {
        let mut kv = KvEngine::open("btree", &temp_dir).unwrap();
        kv.put(1, b"name", b"Alice").unwrap();
        kv.put(1, b"age", b"30").unwrap();
        kv.flush().unwrap();
        println!("Wrote data and flushed");
    }

    {
        let kv = KvEngine::open("btree", &temp_dir).unwrap();
        let name = kv.get(1, b"name").unwrap();
        let age = kv.get(1, b"age").unwrap();
        println!("After reopen: name={:?}, age={:?}", name, age);
    }

    let _ = std::fs::remove_dir_all(&temp_dir);

    // 測試 5: LSM 持久化
    println!("\n--- LSM Persistence ---");
    let temp_dir = std::env::temp_dir().join("db6_lsm_kv_test");
    let _ = std::fs::remove_dir_all(&temp_dir);

    {
        let mut kv = KvEngine::open("lsm", &temp_dir).unwrap();
        kv.put(1, b"city", b"Taipei").unwrap();
        kv.flush().unwrap();
        println!("Wrote data and flushed to SSTable");
    }

    {
        let kv = KvEngine::open("lsm", &temp_dir).unwrap();
        let city = kv.get(1, b"city").unwrap();
        println!("After reopen: city={:?}", city);
    }

    let _ = std::fs::remove_dir_all(&temp_dir);

    println!("\n=== Done ===");
}