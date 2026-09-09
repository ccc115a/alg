use lsm::{LsmEngine, StorageEngine};
use std::io::{self, Write};

fn main() {
    println!("=== LSM-Tree CLI ===");
    println!("支援指令：put, get, delete, scan, flush, begin, commit, rollback, stats, quit");
    println!();

    let mut engine: Box<dyn StorageEngine> = Box::new(LsmEngine::new());
    let mut in_memory = true;
    let mut path_prefix = String::new();

    loop {
        print!("lsm> ");
        io::stdout().flush().unwrap();

        let mut input = String::new();
        if io::stdin().read_line(&mut input).unwrap() == 0 {
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
            "put" => {
                if parts.len() < 3 {
                    println!("用法：put <key> <value>");
                    continue;
                }
                let key = parts[1].as_bytes();
                let value = parts[2..].join(" ");
                match engine.put(1, key, value.as_bytes()) {
                    Ok(_) => println!("已寫入"),
                    Err(e) => println!("錯誤：{}", e),
                }
            }

            "get" => {
                if parts.len() < 2 {
                    println!("用法：get <key>");
                    continue;
                }
                let key = parts[1].as_bytes();
                match engine.get(1, key) {
                    Ok(Some(v)) => println!("找到：{}", String::from_utf8_lossy(&v)),
                    Ok(None) => println!("找不到"),
                    Err(e) => println!("錯誤：{}", e),
                }
            }

            "delete" => {
                if parts.len() < 2 {
                    println!("用法：delete <key>");
                    continue;
                }
                let key = parts[1].as_bytes();
                match engine.delete(1, key) {
                    Ok(_) => println!("已刪除"),
                    Err(e) => println!("錯誤：{}", e),
                }
            }

            "scan" => {
                if parts.len() < 3 {
                    println!("用法：scan <start> <end>");
                    continue;
                }
                let start = parts[1].as_bytes();
                let end = parts[2].as_bytes();
                match engine.scan(1, start, end) {
                    Ok(results) => {
                        if results.is_empty() {
                            println!("(無結果)");
                        } else {
                            for (k, v) in results {
                                println!("  {} -> {}", String::from_utf8_lossy(&k), String::from_utf8_lossy(&v));
                            }
                        }
                    }
                    Err(e) => println!("錯誤：{}", e),
                }
            }

            "flush" => {
                match engine.flush() {
                    Ok(_) => println!("已flush到磁碟"),
                    Err(e) => println!("錯誤：{}", e),
                }
            }

            "sync" => {
                match engine.sync() {
                    Ok(_) => println!("已sync"),
                    Err(e) => println!("錯誤：{}", e),
                }
            }

            "begin" => {
                match engine.begin_transaction() {
                    Ok(_) => println!("交易已開始"),
                    Err(e) => println!("錯誤：{}", e),
                }
            }

            "commit" => {
                match engine.commit_transaction() {
                    Ok(_) => println!("交易已提交"),
                    Err(e) => println!("錯誤：{}", e),
                }
            }

            "rollback" => {
                match engine.rollback_transaction() {
                    Ok(_) => println!("交易已rollback"),
                    Err(e) => println!("錯誤：{}", e),
                }
            }

            "stats" => {
                let s = engine.stats();
                println!("引擎：{}", s.engine);
                println!("key數量：{}", s.key_count);
                println!("交易中：{}", s.in_transaction);
            }

            "disk" => {
                if parts.len() < 2 {
                    println!("用法：disk <路徑>");
                    continue;
                }
                let path = std::path::Path::new(parts[1]);
                match LsmEngine::open(path) {
                    Ok(e) => {
                        engine = Box::new(e);
                        in_memory = false;
                        path_prefix = parts[1].to_string();
                        println!("已切換到磁碟模式：{}", path_prefix);
                    }
                    Err(e) => println!("錯誤：{}", e),
                }
            }

            "memory" => {
                engine = Box::new(LsmEngine::new());
                in_memory = true;
                path_prefix.clear();
                println!("已切換到記憶體模式");
            }

            "batch" => {
                if parts.len() < 2 {
                    println!("用法：batch <key1> <val1> <key2> <val2> ...");
                    continue;
                }
                let mut pairs = Vec::new();
                let args: Vec<&str> = parts[1..].to_vec();
                for chunk in args.chunks(2) {
                    if chunk.len() == 2 {
                        pairs.push((chunk[0].as_bytes().to_vec(), chunk[1].as_bytes().to_vec()));
                    }
                }
                match engine.batch_put(1, pairs) {
                    Ok(_) => println!("批次寫入完成"),
                    Err(e) => println!("錯誤：{}", e),
                }
            }

            "range_delete" => {
                if parts.len() < 3 {
                    println!("用法：range_delete <start> <end>");
                    continue;
                }
                let start = parts[1].as_bytes();
                let end = parts[2].as_bytes();
                match engine.range_delete(1, start, end) {
                    Ok(_) => println!("範圍刪除完成"),
                    Err(e) => println!("錯誤：{}", e),
                }
            }

            "help" => {
                println!("支援指令：");
                println!("  put <key> <value>           - 寫入資料");
                println!("  get <key>                   - 讀取資料");
                println!("  delete <key>                - 刪除資料");
                println!("  scan <start> <end>         - 範圍查詢");
                println!("  batch <k1> <v1> ...        - 批次寫入");
                println!("  range_delete <start> <end>  - 範圍刪除");
                println!("  flush                       - 將memtable flush到sstable");
                println!("  sync                        - 同步到磁碟");
                println!("  begin                       - 開始交易");
                println!("  commit                      - 提交交易");
                println!("  rollback                    - 回滾交易");
                println!("  stats                       - 顯示統計資訊");
                println!("  disk <路徑>                 - 切換到磁碟模式");
                println!("  memory                      - 切換到記憶體模式");
                println!("  quit                        - 離開");
            }

            "quit" | "exit" => {
                println!("再見！");
                break;
            }

            _ => {
                println!("未知指令：{}，輸入 help 查看說明", parts[0]);
            }
        }
    }
}