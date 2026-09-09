use redblacktree::RedBlackTree;
use std::time::Instant;

fn main() {
    println!("=== Stress Test Demo ===\n");

    println!("Test 1: Insert 10,000 sequential integers");
    let start = Instant::now();
    let mut tree = RedBlackTree::new();
    for i in 0..10_000 {
        tree.insert(i, i * 2);
    }
    println!("  Time: {:?}", start.elapsed());
    println!("  Tree size: {}", tree.size());
    println!("  Height: {}", tree.height());
    println!("  Is valid: {}", tree.is_valid());

    println!("\nTest 2: Search for 5,000 random keys");
    let start = Instant::now();
    let mut found = 0;
    for i in 0..5_000 {
        if tree.get(&(i * 2 % 10_000)).is_some() {
            found += 1;
        }
    }
    println!("  Time: {:?}", start.elapsed());
    println!("  Found: {}/5000", found);

    println!("\nTest 3: Delete 5,000 elements");
    let start = Instant::now();
    for i in 0..5_000 {
        tree.remove(&i);
    }
    println!("  Time: {:?}", start.elapsed());
    println!("  Tree size: {}", tree.size());
    println!("  Is valid: {}", tree.is_valid());

    println!("\nTest 4: Insert 10,000 random integers");
    let start = Instant::now();
    let mut tree2 = RedBlackTree::new();
    let mut rng = SimpleRng::new(12345);
    for _ in 0..10_000 {
        let val = rng.next() % 100_000;
        tree2.insert(val, val);
    }
    println!("  Time: {:?}", start.elapsed());
    println!("  Tree size: {}", tree2.size());
    println!("  Height: {}", tree2.height());
    println!("  Is valid: {}", tree2.is_valid());

    println!("\nTest 5: Complex operations (insert, delete, search interleaved)");
    let start = Instant::now();
    let mut tree3 = RedBlackTree::new();
    for i in 0..1_000 {
        tree3.insert(i, i);
    }
    for i in 0..500 {
        tree3.remove(&i);
        tree3.insert(1000 + i, 1000 + i);
    }
    for i in 500..1500 {
        let _ = tree3.get(&i);
    }
    println!("  Time: {:?}", start.elapsed());
    println!("  Tree size: {}", tree3.size());
    println!("  Is valid: {}", tree3.is_valid());
}

struct SimpleRng {
    state: u64,
}

impl SimpleRng {
    fn new(seed: u64) -> Self {
        SimpleRng { state: seed }
    }

    fn next(&mut self) -> u64 {
        self.state = self.state.wrapping_mul(6364136223846793005).wrapping_add(1);
        self.state
    }
}