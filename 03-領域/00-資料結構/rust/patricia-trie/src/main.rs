use std::io::{self, BufRead, Write};
use patricia_trie::PatriciaTrie;

fn main() {
    let mut trie: PatriciaTrie<String> = PatriciaTrie::new();

    println!("Patricia Trie REPL");
    println!("Commands: insert <key> <value> | get <key> | delete <key> | contains <key>");
    println!("          prefix <key> | longest <key> | keys | len | exit");
    println!();

    let stdin = io::stdin();
    for line in stdin.lock().lines().map_while(Result::ok) {
        let line = line.trim().to_string();
        if line.is_empty() {
            continue;
        }

        let parts: Vec<&str> = line.splitn(3, ' ').collect();
        let cmd = parts[0];

        match cmd {
            "exit" | "quit" => break,
            "keys" => {
                let mut keys = trie.keys();
                keys.sort();
                println!("{} entries: {:?}", keys.len(), keys);
            }
            "len" => println!("{}", trie.len()),
            "insert" if parts.len() >= 3 => {
                let key = parts[1];
                let value = parts[2..].join(" ");
                match trie.insert(key, value.clone()) {
                    Some(old) => println!("updated: {} -> {} (was: {})", key, value, old),
                    None => println!("inserted: {} -> {}", key, value),
                }
            }
            "get" if parts.len() >= 2 => {
                match trie.get(parts[1]) {
                    Some(v) => println!("{}", v),
                    None => println!("(not found)"),
                }
            }
            "delete" if parts.len() >= 2 => {
                match trie.delete(parts[1]) {
                    Some(v) => println!("deleted: {} -> {}", parts[1], v),
                    None => println!("(not found)"),
                }
            }
            "contains" if parts.len() >= 2 => {
                println!("{}", trie.contains(parts[1]));
            }
            "prefix" if parts.len() >= 2 => {
                let results = trie.prefix_search(parts[1]);
                println!("{} matches:", results.len());
                for (k, v) in &results {
                    println!("  {} -> {}", k, v);
                }
            }
            "longest" if parts.len() >= 2 => {
                match trie.longest_prefix(parts[1]) {
                    Some((k, v)) => println!("{} -> {}", k, v),
                    None => println!("(none)"),
                }
            }
            _ => {
                println!("unknown command or missing arguments");
                println!("Commands: insert <key> <val> | get <key> | delete <key> | contains <key>");
                println!("          prefix <key> | longest <key> | keys | len | exit");
            }
        }
        print!("> ");
        io::stdout().flush().unwrap();
    }
}
