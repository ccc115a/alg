//! B+Tree CLI 互動式測試工具
//!
//! 支援指令：
//!   insert <key> <value>  - 插入資料
//!   search <key>           - 查詢單一 key
//!   range <start> <end>     - 範圍查詢
//!   delete <key>           - 刪除資料
//!   list                   - 列出所有資料
//!   len                    - 顯示資料筆數
//!   flush                  - 將變更寫入磁碟
//!   quit                   - 離開

mod codec;
mod node;
mod storage;
mod tree;
mod wal;

use node::Key;
use storage::{DiskStorage, MemoryStorage, Storage};
use std::io::{self, Write};
use tree::BPlusTree;

type Tree = BPlusTree<MemoryStorage>;

fn parse_key(s: &str) -> Key {
    if let Ok(i) = s.parse::<i64>() {
        Key::Integer(i)
    } else {
        Key::Text(s.to_string())
    }
}

fn key_display(key: &Key) -> String {
    match key {
        Key::Integer(i) => i.to_string(),
        Key::Text(s) => format!("\"{}\"", s),
    }
}

fn value_display(v: &[u8]) -> String {
    String::from_utf8_lossy(v).to_string()
}

fn run_demo() -> io::Result<()> {
    println!("=== B+Tree Demo ===");
    println!("支援指令：insert, search, range, delete, list, len, flush, quit");
    println!();

    let mut tree: Tree = BPlusTree::new(4, MemoryStorage::new());
    let mut disk_tree: Option<BPlusTree<DiskStorage>> = None;
    let mut use_disk = false;

    loop {
        print!("btree> ");
        io::stdout().flush()?;
        
        let mut input = String::new();
        if io::stdin().read_line(&mut input)? == 0 {
            break;
        }
        
        let input = input.trim();
        if input.is_empty() {
            continue;
        }

        let parts: Vec<&str> = input.split_whitespace().collect();
        if parts.is_empty() {
            continue;
        }

        match parts[0].to_lowercase().as_str() {
            "insert" => {
                if parts.len() < 3 {
                    println!("用法：insert <key> <value>");
                    continue;
                }
                let key = parse_key(parts[1]);
                let value = parts[2..].join(" ").as_bytes().to_vec();
                
                if use_disk {
                    if let Some(ref mut t) = disk_tree {
                        t.insert(key, value);
                        println!("已插入 (磁碟模式)");
                    }
                } else {
                    tree.insert(key, value);
                    println!("已插入");
                }
            }
            "search" => {
                if parts.len() < 2 {
                    println!("用法：search <key>");
                    continue;
                }
                let key = parse_key(parts[1]);
                
                let result = if use_disk {
                    disk_tree.as_mut().and_then(|t| t.search(&key))
                } else {
                    tree.search(&key)
                };
                
                match result {
                    Some(v) => println!("找到：{}", value_display(&v)),
                    None => println!("找不到"),
                }
            }
            "range" => {
                if parts.len() < 3 {
                    println!("用法：range <start> <end>");
                    continue;
                }
                let start = parse_key(parts[1]);
                let end = parse_key(parts[2]);
                
                let results = if use_disk {
                    disk_tree.as_mut().map(|t| t.range_search(&start, &end)).unwrap_or_default()
                } else {
                    tree.range_search(&start, &end)
                };
                
                if results.is_empty() {
                    println!("(無結果)");
                } else {
                    for r in results {
                        println!("  {} -> {}", key_display(&r.key), value_display(&r.value));
                    }
                }
            }
            "delete" => {
                if parts.len() < 2 {
                    println!("用法：delete <key>");
                    continue;
                }
                let key = parse_key(parts[1]);
                
                let deleted = if use_disk {
                    disk_tree.as_mut().map(|t| t.delete(&key)).unwrap_or(false)
                } else {
                    tree.delete(&key)
                };
                
                if deleted {
                    println!("已刪除");
                } else {
                    println!("找不到要刪除的 key");
                }
            }
            "list" => {
                let keys: Vec<Key> = if use_disk {
                    vec![] 
                } else {
                    vec![Key::Integer(0)]
                };
                
                if !use_disk {
                    println!("(MemoryStorage：不支援列舉所有鍵，請使用 search 查詢特定 key)");
                    println!("或使用 range 指令進行範圍查詢");
                } else {
                    println!("(DiskStorage：請使用 range 指令查詢)");
                }
            }
            "len" => {
                let len = if use_disk {
                    disk_tree.as_ref().map(|t| t.len()).unwrap_or(0)
                } else {
                    tree.len()
                };
                println!("資料筆數：{}", len);
            }
            "flush" => {
                if use_disk {
                    if let Some(ref mut t) = disk_tree {
                        t.flush();
                        println!("已寫入磁碟");
                    }
                } else {
                    println!("(MemoryStorage 不需要 flush)");
                }
            }
            "disk" => {
                if parts.len() < 2 {
                    println!("用法：disk <on|off> [路徑]");
                    continue;
                }
                match parts[1] {
                    "on" => {
                        let path = parts.get(2).map(|s| s.to_string())
                            .unwrap_or_else(|| "/tmp/btree_demo.db".to_string());
                        match DiskStorage::open(&path) {
                            Ok(storage) => {
                                if storage.page_count() == 0 {
                                    disk_tree = Some(BPlusTree::new(4, storage));
                                    use_disk = true;
                                    println!("已建立新資料庫並切換到磁碟模式：{}", path);
                                } else {
                                    let root = storage.page_count() - 1;
                                    disk_tree = Some(BPlusTree::open(4, storage, root, 0));
                                    use_disk = true;
                                    println!("已開啟現有資料庫並切換到磁碟模式：{}", path);
                                }
                            }
                            Err(e) => println!("無法開啟檔案：{}", e),
                        }
                    }
                    "off" => {
                        disk_tree = None;
                        use_disk = false;
                        tree = BPlusTree::new(4, MemoryStorage::new());
                        println!("已切換到記憶體模式");
                    }
                    _ => println!("用法：disk <on|off> [路徑]"),
                }
            }
            "quit" | "exit" => {
                if use_disk {
                    if let Some(ref mut t) = disk_tree {
                        t.flush();
                    }
                }
                println!("再見！");
                break;
            }
            "help" => {
                println!("支援指令：");
                println!("  insert <key> <value>  - 插入資料");
                println!("  search <key>           - 查詢單一 key");
                println!("  range <start> <end>    - 範圍查詢");
                println!("  delete <key>          - 刪除資料");
                println!("  list                  - 列出所有資料");
                println!("  len                   - 顯示資料筆數");
                println!("  flush                 - 將變更寫入磁碟");
                println!("  disk on [路徑]        - 切換到磁碟模式");
                println!("  disk off              - 切換到記憶體模式");
                println!("  quit                  - 離開");
            }
            _ => println!("未知指令：{}，輸入 help 查看說明", parts[0]),
        }
    }

    Ok(())
}

fn main() {
    if let Err(e) = run_demo() {
        eprintln!("錯誤：{}", e);
    }
}