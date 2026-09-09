//! Capability compile-time check example
//! 
//! This shows how SqlExecutor enforces capabilities at compile time.

use db6::{SqlExecutor, engine::{HashMemoryEngine, BTreeMemoryEngine, CanOrderBy, CanFts}};

fn test_order_by_compile_time<E: CanOrderBy>() {
    println!("Engine supports ORDER BY");
}

fn test_fts_compile_time<E: CanFts>() {
    println!("Engine supports FTS");
}

fn main() {
    println!("=== Capability Compile-Time Check Example ===\n");

    // BTreeMemoryEngine supports ORDER BY - this compiles
    let engine_btree = BTreeMemoryEngine::new();
    let mut exec = SqlExecutor::new(engine_btree);
    exec.execute("SELECT * FROM t ORDER BY id").unwrap();
    println!("BTreeMemoryEngine: ORDER BY works!");

    // HashMemoryEngine does NOT support ORDER BY - would need compile_fail
    // Uncommenting the following would cause a compile error:
    // let engine_hash = HashMemoryEngine::new();
    // let mut exec: SqlExecutor<HashMemoryEngine> = SqlExecutor::new(engine_hash);
    // exec.execute("SELECT * FROM t ORDER BY id"); // compile error!

    // Demonstrate capability traits
    println!("\n--- Capability Check ---");
    
    // This works - BTreeMemoryEngine implements CanOrderBy
    test_order_by_compile_time::<BTreeMemoryEngine>();
    
    // This would fail at compile time for HashMemoryEngine:
    // test_order_by_compile_time::<HashMemoryEngine>();
    // Error: the trait bound `HashMemoryEngine: CanOrderBy` is not satisfied

    // But both support FTS
    test_fts_compile_time::<BTreeMemoryEngine>();
    test_fts_compile_time::<HashMemoryEngine>();

    println!("\n=== Done ===");
    println!("\nCapability Matrix:");
    println!("  HashMemoryEngine: CanFts, CanBatch");
    println!("  BTreeMemoryEngine: CanOrderBy, CanScan, CanBatch, CanFts");
    println!("  BTreeEngine:       CanOrderBy, CanScan, CanBatch, CanFts, CanTransaction");
    println!("  LsmEngine:         CanScan, CanBatch, CanTransaction");
}