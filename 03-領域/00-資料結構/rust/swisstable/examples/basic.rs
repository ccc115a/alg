//! Basic usage example for Swisstable
//!
//! Run with: cargo run --example basic

use swisstable::SwisstableMap;
use swisstable::SwisstableSet;

fn main() {
    println!("=== Swisstable Basic Example ===\n");

    // Create a new map with String keys and i32 values
    let mut map = SwisstableMap::new();

    // Insert some key-value pairs
    map.insert(String::from("name"), 100);
    map.insert(String::from("age"), 30);
    map.insert(String::from("score"), 85);

    println!("After inserting 3 entries:");
    println!("  Map length: {}", map.len());
    println!("  Capacity: {}", map.capacity());

    // Get values using the get method
    println!("\n  name = {:?}", map.get(&String::from("name")));
    println!("  age = {:?}", map.get(&String::from("age")));

    // Update a value
    let old_score = map.insert(String::from("age"), 31);
    println!("\nUpdated age from {:?} to 31", old_score);

    // Iterate over the map
    println!("\nIterating over all entries:");
    for (key, value) in &map {
        println!("  {}: {}", key, value);
    }

    // Using Index trait (requires Debug trait on key)
    println!("\nUsing Index trait: age = {}", map[&String::from("age")]);

    // Create a set
    let mut set = SwisstableSet::new();
    set.insert(String::from("apple"));
    set.insert(String::from("banana"));
    set.insert(String::from("cherry"));

    println!("\n=== SwisstableSet Example ===");
    println!("Set contains {} fruits:", set.len());
    for fruit in &set {
        println!("  - {}", fruit);
    }

    // Check membership
    println!(
        "\n  Contains 'banana': {}",
        set.contains(&String::from("banana"))
    );
    println!(
        "  Contains 'grape': {}",
        set.contains(&String::from("grape"))
    );

    // Remove an element
    let removed = set.remove(&String::from("banana"));
    println!("\nRemoved 'banana': {:?}", removed);
    println!("Set now contains {} fruits", set.len());

    println!("\n=== Done! ===");
}
