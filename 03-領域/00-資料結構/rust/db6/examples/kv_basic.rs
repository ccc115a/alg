//! KV 基本操作範例
//! 
//! 展示如何使用 db6 的 KV API

use db6::engine::{StorageEngine, HashMemoryEngine};

fn main() {
    println!("=== KV Basic Example (Hash) ===\n");

    // 建立 Hash 記憶體引擎 (O(1) 操作)
    let mut engine = HashMemoryEngine::new();

    // 基本寫入讀取
    engine.put(1, b"key1", b"value1").unwrap();
    engine.put(1, b"key2", b"value2").unwrap();
    engine.put(1, b"key3", b"value3").unwrap();

    // 讀取單一 key
    let val = engine.get(1, b"key1").unwrap();
    println!("get key1: {:?}", val);

    // 範圍掃描
    let rows = engine.scan(1, b"key1", b"key3").unwrap();
    println!("\nscan key1 to key3:");
    for (k, v) in rows {
        println!("  {} -> {}", String::from_utf8_lossy(&k), String::from_utf8_lossy(&v));
    }

    // 刪除
    engine.delete(1, b"key2").unwrap();
    let val = engine.get(1, b"key2").unwrap();
    println!("\ndelete key2, get key2: {:?}", val);

    // 批量寫入
    let pairs = vec![
        (b"a".to_vec(), b"1".to_vec()),
        (b"b".to_vec(), b"2".to_vec()),
        (b"c".to_vec(), b"3".to_vec()),
    ];
    engine.batch_put(2, pairs).unwrap();
    let rows = engine.scan(2, b"", b"").unwrap();
    println!("\nbatch_put table 2:");
    for (k, v) in rows {
        println!("  {} -> {}", String::from_utf8_lossy(&k), String::from_utf8_lossy(&v));
    }

    // 範圍刪除
    engine.range_delete(2, b"a", b"c").unwrap();
    let rows = engine.scan(2, b"", b"").unwrap();
    println!("\nrange_delete a-c, remaining:");
    for (k, v) in rows {
        println!("  {} -> {}", String::from_utf8_lossy(&k), String::from_utf8_lossy(&v));
    }

    println!("\n=== Done ===");
}