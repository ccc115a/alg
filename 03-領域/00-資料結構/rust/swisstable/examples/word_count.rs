//! Word count example using Swisstable
//!
//! This example demonstrates using SwisstableMap to count word occurrences.
//! Run with: cargo run --example word_count

use swisstable::SwisstableMap;

fn main() {
    println!("=== Word Count Example ===\n");

    let text = "the quick brown fox jumps over the lazy dog the fox was quick and the dog was lazy but the fox was smarter than the dog";

    let mut word_counts: SwisstableMap<String, usize> = SwisstableMap::new();

    // Count words
    for word in text.split_whitespace() {
        let key = word.to_string();
        let count = word_counts.get(&key).copied().unwrap_or(0);
        word_counts.insert(key, count + 1);
    }

    println!("Text: \"{}...\"", &text[..50.min(text.len())]);
    println!("\nWord counts (sorted by frequency):");

    let mut words: Vec<_> = word_counts.iter().collect();
    words.sort_by(|a, b| b.1.cmp(a.1)); // Sort by count descending

    for (word, count) in words {
        println!("  {:15} : {:3}", word, count);
    }

    // Find most common word
    if let Some((word, count)) = word_counts.iter().max_by_key(|(_, &count)| count) {
        println!("\nMost common word: '{}' (appeared {} times)", word, count);
    }

    // Find words that appear only once
    println!("\nWords appearing only once:");
    for (word, &count) in &word_counts {
        if count == 1 {
            println!("  - {}", word);
        }
    }

    println!("\n=== Done! ===");
}
