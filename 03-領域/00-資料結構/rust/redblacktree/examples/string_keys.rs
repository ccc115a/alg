use redblacktree::RedBlackTree;
use std::collections::BTreeMap;

fn main() {
    println!("=== String Keys Demo ===\n");

    let mut tree = RedBlackTree::new();

    tree.insert(String::from("apple"), 1);
    tree.insert(String::from("banana"), 2);
    tree.insert(String::from("cherry"), 3);
    tree.insert(String::from("date"), 4);
    tree.insert(String::from("elderberry"), 5);

    println!("Tree with string keys:");
    for (k, v) in tree.inorder() {
        println!("  {} -> {}", k, v);
    }

    println!("\nSearch results:");
    println!("  banana -> {:?}", tree.get(&String::from("banana")));
    println!("  grape -> {:?}", tree.get(&String::from("grape")));

    println!("\nKeys: {:?}", tree.keys());
    println!("Values: {:?}", tree.values());

    println!("\nComparison with BTreeMap:");
    let mut btree = BTreeMap::new();
    btree.insert(String::from("apple"), 1);
    btree.insert(String::from("banana"), 2);
    btree.insert(String::from("cherry"), 3);

    for (k, v) in &btree {
        println!("  {} -> {}", k, v);
    }

    println!("\nTree is valid RB-Tree: {}", tree.is_valid());
}