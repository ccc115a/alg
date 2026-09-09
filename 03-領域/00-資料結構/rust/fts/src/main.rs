use std::fs;
use std::io::{self, BufRead, Write};

fn main() -> io::Result<()> {
    let corpus_path = "data/corpus.txt";
    let content = fs::read_to_string(corpus_path)
        .map_err(|e| {
            eprintln!("無法讀取 {}: {}", corpus_path, e);
            e
        })?;

    let lines: Vec<String> = content.lines().map(|s| s.to_string()).collect();
    let idx = fts::Index::build(&lines);

    println!("FTS 全文檢索系統 (CJK / English)");
    println!("================================");
    println!("載入 {} 筆文件", idx.doc_count());
    println!("索引 {} 個詞項", idx.term_count());
    println!("輸入關鍵字搜尋 (空白分隔為 AND，或輸入 :or 切換模式)");
    println!("輸入 :quit 離開");
    println!();

    let mut mode = fts::SearchMode::And;
    let stdin = io::stdin();
    loop {
        print!("{}> ", match mode {
            fts::SearchMode::And => "AND",
            fts::SearchMode::Or => "OR",
        });
        io::stdout().flush()?;

        let mut input = String::new();
        stdin.lock().read_line(&mut input)?;
        let input = input.trim();

        match input {
            ":quit" | ":q" => break,
            ":or" => {
                mode = fts::SearchMode::Or;
                println!("切換為 OR 模式");
                continue;
            }
            ":and" => {
                mode = fts::SearchMode::And;
                println!("切換為 AND 模式");
                continue;
            }
            "" => continue,
            _ => {}
        }

        let results = idx.search(input, mode);
        if results.is_empty() {
            println!("  沒有符合結果");
        } else {
            println!("  找到 {} 筆結果:", results.len());
            for r in &results {
                println!("  [{:3}] (score: {:.2}) {}", r.doc_id, r.score, r.line);
            }
        }
        println!();
    }

    Ok(())
}
