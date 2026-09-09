use redblacktree::RedBlackTree;
use std::env;
use std::process;

fn main() {
    let args: Vec<String> = env::args().collect();

    if args.len() < 2 {
        print_usage();
        process::exit(1);
    }

    match args[1].as_str() {
        "insert" => {
            if args.len() < 4 {
                eprintln!("Usage: {} insert <key> <value>", args[0]);
                process::exit(1);
            }
            let key: i32 = match args[2].parse() {
                Ok(k) => k,
                Err(_) => {
                    eprintln!("Invalid key: {}", args[2]);
                    process::exit(1);
                }
            };
            let value = &args[3];
            let mut tree = RedBlackTree::new();
            tree.insert(key, value.clone());
            println!("Inserted: {} -> {}", key, value);
        }
        "search" => {
            if args.len() < 3 {
                eprintln!("Usage: {} search <key>", args[0]);
                process::exit(1);
            }
            let key: i32 = match args[2].parse() {
                Ok(k) => k,
                Err(_) => {
                    eprintln!("Invalid key: {}", args[2]);
                    process::exit(1);
                }
            };
            let tree: RedBlackTree<i32, String> = RedBlackTree::new();
            match tree.get(&key) {
                Some(v) => println!("Found: {} -> {}", key, v),
                None => println!("Key {} not found", key),
            }
        }
        "delete" => {
            if args.len() < 3 {
                eprintln!("Usage: {} delete <key>", args[0]);
                process::exit(1);
            }
            let key: i32 = match args[2].parse() {
                Ok(k) => k,
                Err(_) => {
                    eprintln!("Invalid key: {}", args[2]);
                    process::exit(1);
                }
            };
            let mut tree: RedBlackTree<i32, String> = RedBlackTree::new();
            if tree.remove(&key) {
                println!("Deleted: {}", key);
            } else {
                println!("Key {} not found", key);
            }
        }
        "list" => {
            let tree: RedBlackTree<i32, String> = RedBlackTree::new();
            println!("Tree size: {}", tree.size());
            println!("Tree height: {}", tree.height());
            println!("Valid RB-Tree: {}", tree.is_valid());
        }
        "min" => {
            let tree: RedBlackTree<i32, String> = RedBlackTree::new();
            match tree.min_key() {
                Some(k) => println!("Min key: {}", k),
                None => println!("Tree is empty"),
            }
        }
        "max" => {
            let tree: RedBlackTree<i32, String> = RedBlackTree::new();
            match tree.max_key() {
                Some(k) => println!("Max key: {}", k),
                None => println!("Tree is empty"),
            }
        }
        "help" => {
            print_usage();
        }
        _ => {
            eprintln!("Unknown command: {}", args[1]);
            print_usage();
            process::exit(1);
        }
    }
}

fn print_usage() {
    println!("Red-Black Tree CLI");
    println!();
    println!("Usage: {} <command> [args]", env::args().next().unwrap_or("redblacktree".to_string()));
    println!();
    println!("Commands:");
    println!("  insert <key> <value>  Insert a key-value pair");
    println!("  search <key>          Search for a key");
    println!("  delete <key>          Delete a key");
    println!("  list                  List tree info");
    println!("  min                   Show minimum key");
    println!("  max                   Show maximum key");
    println!("  help                  Show this help");
}