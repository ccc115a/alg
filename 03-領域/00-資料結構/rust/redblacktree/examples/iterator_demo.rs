use redblacktree::RedBlackTree;

fn main() {
    println!("=== Iterator Demo ===\n");

    let mut tree = RedBlackTree::new();
    tree.insert(3, "three");
    tree.insert(1, "one");
    tree.insert(4, "four");
    tree.insert(1, "ONE");
    tree.insert(5, "five");
    tree.insert(9, "nine");
    tree.insert(2, "two");
    tree.insert(7, "seven");

    println!("Tree: {:?}", tree);

    println!("\nUsing iter():");
    let mut iter = tree.iter();
    while let Some((k, v)) = iter.next() {
        println!("  Key: {}, Value: {}", k, v);
    }

    println!("\nUsing into_iter():");
    let mut tree2 = RedBlackTree::new();
    tree2.insert(100, "hundred");
    tree2.insert(50, "fifty");
    tree2.insert(150, "one-fifty");
    for (k, v) in tree2 {
        println!("  Key: {}, Value: {}", k, v);
    }

    println!("\nUsing for loop:");
    for (key, value) in &tree {
        println!("  {} -> {}", key, value);
    }
}