//! Phonebook example using Swisstable
//!
//! Demonstrates using SwisstableMap as a phonebook with CRUD operations.
//! Run with: cargo run --example phonebook

use swisstable::SwisstableMap;

#[derive(Debug, Clone)]
struct Contact {
    name: String,
    phone: String,
    email: String,
}

fn main() {
    println!("=== Phonebook Example ===\n");

    let mut phonebook: SwisstableMap<String, Contact> = SwisstableMap::new();

    // Add some contacts
    phonebook.insert(
        String::from("Alice"),
        Contact {
            name: "Alice".to_string(),
            phone: "0912-345-678".to_string(),
            email: "alice@example.com".to_string(),
        },
    );

    phonebook.insert(
        String::from("Bob"),
        Contact {
            name: "Bob".to_string(),
            phone: "0987-654-321".to_string(),
            email: "bob@example.com".to_string(),
        },
    );

    phonebook.insert(
        String::from("Charlie"),
        Contact {
            name: "Charlie".to_string(),
            phone: "0955-123-456".to_string(),
            email: "charlie@example.com".to_string(),
        },
    );

    println!("Initial phonebook ({} contacts):", phonebook.len());
    print_phonebook(&phonebook);

    // Update Charlie's phone number
    let old = phonebook.insert(
        String::from("Charlie"),
        Contact {
            name: "Charlie".to_string(),
            phone: "0999-888-777".to_string(),
            email: "charlie@example.com".to_string(),
        },
    );

    if let Some(old_contact) = old {
        println!(
            "\nUpdated Charlie's phone from {} to 0999-888-777",
            old_contact.phone
        );
    }

    // Search for a contact
    let search_name = String::from("Alice");
    if let Some(contact) = phonebook.get(&search_name) {
        println!(
            "\nFound {}: phone={}, email={}",
            search_name, contact.phone, contact.email
        );
    } else {
        println!("\n{} not found in phonebook", search_name);
    }

    // Delete Bob
    let removed = phonebook.remove(&String::from("Bob"));
    if let Some(contact) = removed {
        println!("\nRemoved Bob (phone: {})", contact.phone);
    }

    println!("\nFinal phonebook ({} contacts):", phonebook.len());
    print_phonebook(&phonebook);

    println!("\n=== Done! ===");
}

fn print_phonebook(phonebook: &SwisstableMap<String, Contact>) {
    let mut names: Vec<_> = phonebook.iter().map(|(name, _)| name.clone()).collect();
    names.sort();

    for name in names {
        if let Some(contact) = phonebook.get(&name) {
            println!("  {:10} | {} | {}", name, contact.phone, contact.email);
        }
    }
}
