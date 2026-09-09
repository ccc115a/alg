//! 多引擎切換範例
//! 
//! 展示如何在不同引擎間切換

use db6::engine::{StorageEngine, HashMemoryEngine, BTreeMemoryEngine, BTreeEngine, LsmEngine};

fn test_engine(name: &str, mut engine: Box<dyn StorageEngine>) {
    println!("\n--- Testing {} ---", name);
    
    // 基本操作
    engine.put(1, b"key1", b"value1").unwrap();
    let val = engine.get(1, b"key1").unwrap();
    println!("put/get: {:?}", val);
    
    // 統計
    let stats = engine.stats();
    println!("engine: {}, keys: {}", stats.engine, stats.key_count);
}

fn main() {
    println!("=== Multi Engine Example ===\n");

    // 使用 HashMemoryEngine
    test_engine("HashMemoryEngine", Box::new(HashMemoryEngine::new()));

    // 使用 BTreeMemoryEngine
    test_engine("BTreeMemoryEngine", Box::new(BTreeMemoryEngine::new()));

    // 使用 BTreeEngine
    test_engine("BTreeEngine", Box::new(BTreeEngine::new()));

    // 使用 LSMEngine
    test_engine("LsmEngine", Box::new(LsmEngine::new()));

    println!("\n=== Done ===");
}