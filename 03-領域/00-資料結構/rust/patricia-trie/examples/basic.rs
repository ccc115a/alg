use patricia_trie::PatriciaTrie;

fn main() {
    // Create a new Patricia trie
    let mut trie = PatriciaTrie::new();

    // Insert key-value pairs
    trie.insert("apple", 1);
    trie.insert("app", 2);
    trie.insert("appetite", 3);
    trie.insert("banana", 4);
    trie.insert("bat", 5);

    println!("=== Basic Operations ===");
    println!("len: {}", trie.len());
    println!("get(\"apple\"): {:?}", trie.get("apple"));
    println!("get(\"app\"): {:?}", trie.get("app"));
    println!("get(\"ap\"): {:?}", trie.get("ap"));
    println!("contains(\"bat\"): {}", trie.contains("bat"));

    // Update existing key
    println!();
    println!("=== Update ===");
    println!("insert(\"app\", 99): old={:?}", trie.insert("app", 99));
    println!("get(\"app\"): {:?}", trie.get("app"));

    // Prefix search
    println!();
    println!("=== Prefix Search ===");
    let results = trie.prefix_search("app");
    println!("prefix(\"app\"):");
    for (key, val) in &results {
        println!("  {} -> {}", key, val);
    }

    // Longest prefix
    println!();
    println!("=== Longest Prefix ===");
    println!("longest(\"appetizer\"): {:?}", trie.longest_prefix("appetizer"));
    println!("longest(\"application\"): {:?}", trie.longest_prefix("application"));
    println!("longest(\"banana_split\"): {:?}", trie.longest_prefix("banana_split"));

    // Delete
    println!();
    println!("=== Delete ===");
    println!("delete(\"banana\"): {:?}", trie.delete("banana"));
    println!("delete(\"banana\"): {:?}", trie.delete("banana")); // again
    println!("contains(\"banana\"): {}", trie.contains("banana"));
    println!("len after delete: {}", trie.len());

    // All keys
    println!();
    println!("=== All Keys ===");
    let mut keys = trie.keys();
    keys.sort();
    println!("{:?}", keys);

    // Demonstrate node splitting: keys with common prefix
    println!();
    println!("=== Node Splitting (car/cat) ===");
    let mut geo = PatriciaTrie::new();
    geo.insert("car", 10);
    geo.insert("cat", 20);
    geo.insert("cap", 30);
    println!("get(\"car\"): {:?}", geo.get("car"));
    println!("get(\"cat\"): {:?}", geo.get("cat"));
    println!("get(\"cap\"): {:?}", geo.get("cap"));

    // Unicode support
    println!();
    println!("=== Unicode ===");
    let mut uni = PatriciaTrie::new();
    uni.insert("café", 1);
    uni.insert("你好", 2);
    uni.insert("世界", 3);
    println!("get(\"café\"): {:?}", uni.get("café"));
    println!("get(\"你好\"): {:?}", uni.get("你好"));

    // Empty string key
    println!();
    println!("=== Empty Key ===");
    uni.insert("", 0);
    println!("get(\"\"): {:?}", uni.get(""));
    println!("longest(\"anything\"): {:?}", uni.longest_prefix("anything"));
}
