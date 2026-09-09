use redblacktree::RedBlackTree;

fn main() {
    println!("=== Basic Red-Black Tree Demo ===\n");

    let mut tree = RedBlackTree::new();

    println!("Inserting elements: 10, 5, 15, 3, 7, 12, 20");
    tree.insert(10, "ten");
    tree.insert(5, "five");
    tree.insert(15, "fifteen");
    tree.insert(3, "three");
    tree.insert(7, "seven");
    tree.insert(12, "twelve");
    tree.insert(20, "twenty");

    println!("\nTree size: {}", tree.size());
    println!("Tree height: {}", tree.height());
    println!("Is valid RB-Tree: {}", tree.is_valid());
    println!("Min key: {:?}", tree.min_key());
    println!("Max key: {:?}", tree.max_key());

    println!("\nInorder traversal:");
    for (k, v) in tree.inorder() {
        println!("  {} -> {}", k, v);
    }

    println!("\nSearching for key 7: {:?}", tree.get(&7));
    println!("Searching for key 99: {:?}", tree.get(&99));
    println!("Contains 15: {}", tree.contains(&15));
    println!("Contains 99: {}", tree.contains(&99));

    println!("\nKeys: {:?}", tree.keys());
    println!("Values: {:?}", tree.values());

    println!("\nRemoving key 5...");
    tree.remove(&5);
    println!("Tree size after removal: {}", tree.size());
    println!("Is valid after removal: {}", tree.is_valid());

    println!("\nFinal inorder:");
    for (k, v) in tree.inorder() {
        println!("  {} -> {}", k, v);
    }
}