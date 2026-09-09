//! REPL：互動式 SQL 命令列介面
//!
//! 功能：
//!   - 多行輸入（以 ; 結尾才送出）
//!   - 點指令（.help / .tables / .schema / .quit / .fts）
//!   - 結果以對齊表格輸出
//!   - 執行時間顯示
//!   - 錯誤訊息友善顯示

use std::io::{self, BufRead, Write};
use std::time::Instant;
use std::collections::HashMap;

use crate::fts::FtsTable;
use crate::parser::parse;
use crate::planner::planner::Planner;
use crate::planner::{Executor, ResultSet};
use crate::table::row::Value;

// ── REPL ─────────────────────────────────────────────────────────────────

pub struct Repl {
    executor: Executor,
    fts_tables: HashMap<String, FtsTable>,
    prompt:  &'static str,
    history: Vec<String>,
}

impl Repl {
    pub fn new() -> Self {
        Repl {
            executor:   Executor::new(),
            fts_tables: HashMap::new(),
            prompt:     "sql4> ",
            history:    Vec::new(),
        }
    }

    /// 啟動互動式 REPL（從 stdin 讀取）
    pub fn run(&mut self) {
        self.print_banner();
        let stdin  = io::stdin();
        let mut buf = String::new();

        loop {
            // 顯示提示符
            if buf.trim().is_empty() {
                print!("{}", self.prompt);
            } else {
                print!("   ...> ");
            }
            io::stdout().flush().unwrap();

            let mut line = String::new();
            match stdin.lock().read_line(&mut line) {
                Ok(0) => break,          // EOF
                Ok(_) => {}
                Err(e) => { eprintln!("read error: {}", e); break; }
            }

            let trimmed = line.trim_end().to_string();

            // 點指令（立即執行，不需要 ;）
            if trimmed.starts_with('.') {
                self.handle_dot_command(&trimmed);
                buf.clear();
                continue;
            }

            buf.push_str(&trimmed);
            buf.push(' ');

            // 以 ; 判斷語句結束
            if trimmed.ends_with(';') || is_complete(&buf) {
                let sql = buf.trim().to_string();
                if !sql.is_empty() {
                    self.history.push(sql.clone());
                    self.execute_sql(&sql);
                }
                buf.clear();
            }
        }
        println!("\nBye!");
    }

    /// 執行單一 SQL 字串（非互動式，用於腳本 / 測試）
    pub fn execute_sql(&mut self, sql: &str) {
        let start = Instant::now();
        self.history.push(sql.trim_end_matches(';').trim().to_string());
        // 先嘗試攔截 FTS 特殊語法
        if let Some(result) = self.try_handle_fts(sql) {
            match result {
                Ok(rs)  => { print_result_set(&rs); println!("({:.3}s)", start.elapsed().as_secs_f64()); }
                Err(e)  => eprintln!("Error: {}", e),
            }
            return;
        }

        let stmts = match parse(sql) {
            Ok(s)  => s,
            Err(e) => { eprintln!("Parse error: {}", e); return; }
        };

        for stmt in stmts {
            let plan = match Planner::new(self.executor.catalog()).plan(stmt) {
                Ok(p)  => p,
                Err(e) => { eprintln!("Plan error: {}", e); return; }
            };
            match self.executor.execute(plan) {
                Ok(rs) => {
                    print_result_set(&rs);
                    println!("({:.3}s)", start.elapsed().as_secs_f64());
                }
                Err(e) => eprintln!("Error: {}", e),
            }
        }
    }

    // ── 點指令 ────────────────────────────────────────────────────────────

    fn handle_dot_command(&mut self, cmd: &str) {
        let parts: Vec<&str> = cmd.splitn(2, ' ').collect();
        match parts[0] {
            ".quit" | ".exit" | ".q" => {
                println!("Bye!");
                std::process::exit(0);
            }
            ".help" | ".h" => self.print_help(),
            ".tables"      => self.cmd_tables(),
            ".schema"      => self.cmd_schema(parts.get(1).copied()),
            ".fts"         => self.cmd_fts(parts.get(1).copied()),
            ".history"     => self.cmd_history(),
            ".timing"      => println!("(timing always on)"),
            _ => eprintln!("Unknown command: {}  (type .help for help)", parts[0]),
        }
    }

    fn cmd_tables(&self) {
        let mut names = self.executor.catalog().table_names();
        names.sort();
        if names.is_empty() {
            println!("(no tables)");
        } else {
            for n in names { println!("{}", n); }
        }
        // 也列出 FTS 虛擬表
        for name in self.fts_tables.keys() {
            println!("{} (fts)", name);
        }
    }

    fn cmd_schema(&self, table: Option<&str>) {
        let catalog = self.executor.catalog();
        let names: Vec<&str> = match table {
            Some(t) => vec![t],
            None    => catalog.table_names(),
        };
        for name in names {
            if let Some(meta) = catalog.get_table(name) {
                println!("CREATE TABLE {} (", meta.name);
                let cols = &meta.schema.columns;
                for (i, col) in cols.iter().enumerate() {
                    let comma = if i + 1 < cols.len() { "," } else { "" };
                    println!("  {} {}{}", col.name, col.data_type, comma);
                }
                println!(");");
            } else {
                eprintln!("table '{}' not found", name);
            }
        }
        // FTS 虛擬表
        if let Some(t) = table.and_then(|n| self.fts_tables.get(n)) {
            println!("CREATE VIRTUAL TABLE {} USING fts5({});",
                t.name, t.columns.join(", "));
        }
    }

    fn cmd_fts(&mut self, arg: Option<&str>) {
        // .fts <table> <query>
        let arg = match arg {
            Some(a) => a,
            None    => { eprintln!("Usage: .fts <table> <query>"); return; }
        };
        let (table_name, query) = match arg.splitn(2, ' ').collect::<Vec<_>>()[..] {
            [t, q] => (t, q),
            _      => { eprintln!("Usage: .fts <table> <query>"); return; }
        };
        let tbl = match self.fts_tables.get_mut(table_name) {
            Some(t) => t,
            None    => { eprintln!("FTS table '{}' not found", table_name); return; }
        };
        let results = tbl.search(query);
        if results.is_empty() {
            println!("(no results)");
            return;
        }
        // 顯示結果
        let header = format!("{:<8} {:<10} {}", "rowid", "score", tbl.columns.join(" | "));
        println!("{}", header);
        println!("{}", "-".repeat(header.len()));
        for (rowid, score, vals) in &results {
            println!("{:<8} {:<10.4} {}", rowid, score, vals.join(" | "));
        }
        println!("({} result{})", results.len(), if results.len() == 1 { "" } else { "s" });
    }

    fn cmd_history(&self) {
        for (i, h) in self.history.iter().enumerate() {
            println!("{:>3}  {}", i + 1, h);
        }
    }

    // ── FTS SQL 攔截 ──────────────────────────────────────────────────────
    // 處理 SQLite FTS5 相容語法：
    //   CREATE VIRTUAL TABLE t USING fts5(col1, col2)
    //   INSERT INTO t VALUES (...)
    //   SELECT * FROM t WHERE t MATCH 'query'

    fn try_handle_fts(&mut self, sql: &str) -> Option<Result<ResultSet, String>> {
        let upper = sql.trim().to_uppercase();

        // CREATE VIRTUAL TABLE ... USING fts5(...)
        if upper.starts_with("CREATE VIRTUAL TABLE") {
            return Some(self.fts_create(sql));
        }

        // INSERT INTO <fts_table> ...
        if upper.starts_with("INSERT INTO") {
            let table_name = extract_table_name_from_insert(sql)?;
            if self.fts_tables.contains_key(&table_name) {
                return Some(self.fts_insert(sql, &table_name));
            }
        }

        // SELECT ... FROM <fts_table> WHERE <table> MATCH '...'
        if upper.contains("MATCH") {
            if let Some((table_name, query)) = extract_match_query(sql) {
                if self.fts_tables.contains_key(&table_name) {
                    return Some(self.fts_select(&table_name, &query));
                }
            }
        }

        None
    }

    fn fts_create(&mut self, sql: &str) -> Result<ResultSet, String> {
        // 解析：CREATE VIRTUAL TABLE <name> USING fts5(<col1>, <col2>, ...)
        let lower = sql.to_lowercase();
        let after_table = lower.find("table").ok_or("parse error")? + 5;
        let after_using = lower.find("using").ok_or("parse error")?;
        let name = sql[after_table..after_using].trim().to_string();

        let after_fts5 = lower.find("fts5").ok_or("parse error")? + 4;
        let lparen = sql[after_fts5..].find('(').ok_or("parse error")? + after_fts5;
        let rparen = sql.rfind(')').ok_or("parse error")?;
        let cols_str = &sql[lparen+1..rparen];
        let columns: Vec<String> = cols_str.split(',')
            .map(|c| c.trim().to_string())
            .filter(|c| !c.is_empty())
            .collect();

        if self.fts_tables.contains_key(&name) {
            return Err(format!("FTS table '{}' already exists", name));
        }
        self.fts_tables.insert(name.clone(), FtsTable::new(&name, columns));
        Ok(ResultSet::ok_msg("fts5 virtual table created"))
    }

    fn fts_insert(&mut self, sql: &str, table_name: &str) -> Result<ResultSet, String> {
        // 簡單解析 INSERT INTO t VALUES ('v1', 'v2', ...)
        let lower = sql.to_lowercase();
        let after_values = lower.find("values").ok_or("parse error")? + 6;
        let lparen = sql[after_values..].find('(').ok_or("parse error")? + after_values;
        let rparen = sql.rfind(')').ok_or("parse error")?;
        let vals_str = &sql[lparen+1..rparen];

        // 解析以逗號分隔的值（簡單版，不處理值內有逗號）
        let values: Vec<String> = split_sql_values(vals_str);
        let tbl = self.fts_tables.get_mut(table_name).ok_or("table not found")?;
        tbl.insert(values);
        Ok(ResultSet::ok_msg("1 row(s) inserted"))
    }

    fn fts_select(&mut self, table_name: &str, query: &str) -> Result<ResultSet, String> {
        let tbl = self.fts_tables.get_mut(table_name).ok_or("table not found")?;
        let results = tbl.search(query);
        let col_names = tbl.columns.clone();

        let mut out_cols = vec!["rowid".to_string(), "score".to_string()];
        out_cols.extend(col_names);

        let rows: Vec<Vec<Value>> = results.into_iter().map(|(rowid, score, vals)| {
            let mut row = vec![Value::Integer(rowid as i64), Value::Float(score)];
            row.extend(vals.into_iter().map(Value::Text));
            row
        }).collect();

        Ok(ResultSet { columns: out_cols, rows })
    }

    // ── Banner & Help ────────────────────────────────────────────────────

    fn print_banner(&self) {
        println!("sql4 v0.1.0 — SQLite-compatible database with FTS");
        println!("Type .help for help, .quit to exit");
        println!();
    }

    fn print_help(&self) {
        println!("Commands:");
        println!("  .help            Show this help");
        println!("  .tables          List all tables");
        println!("  .schema [TABLE]  Show CREATE statement");
        println!("  .fts TABLE QUERY Full-text search");
        println!("  .history         Show command history");
        println!("  .quit            Exit");
        println!();
        println!("SQL Examples:");
        println!("  CREATE TABLE users (id INTEGER, name TEXT, age INTEGER);");
        println!("  INSERT INTO users VALUES (1, 'Alice', 30);");
        println!("  SELECT * FROM users WHERE age > 25 ORDER BY name;");
        println!("  UPDATE users SET age = 31 WHERE id = 1;");
        println!("  DELETE FROM users WHERE id = 1;");
        println!();
        println!("FTS Examples:");
        println!("  CREATE VIRTUAL TABLE articles USING fts5(title, body);");
        println!("  INSERT INTO articles VALUES ('Rust lang', 'Fast systems');");
        println!("  SELECT * FROM articles WHERE articles MATCH 'rust';");
        println!("  SELECT * FROM articles WHERE articles MATCH '\"rust lang\"';");
        println!("  SELECT * FROM articles WHERE articles MATCH 'rust AND fast';");
    }
}

impl Default for Repl {
    fn default() -> Self { Self::new() }
}

// ── 結果輸出（對齊表格） ──────────────────────────────────────────────────

fn print_result_set(rs: &ResultSet) {
    if rs.columns.is_empty() { return; }

    // 計算每欄最大寬度
    let mut widths: Vec<usize> = rs.columns.iter().map(|c| c.len()).collect();
    for row in &rs.rows {
        for (i, val) in row.iter().enumerate() {
            if i < widths.len() {
                widths[i] = widths[i].max(val.to_string().len());
            }
        }
    }

    // 表頭
    let header: Vec<String> = rs.columns.iter().enumerate()
        .map(|(i, c)| format!("{:<width$}", c, width = widths[i]))
        .collect();
    println!("{}", header.join(" | "));

    // 分隔線
    let sep: Vec<String> = widths.iter().map(|&w| "-".repeat(w)).collect();
    println!("{}", sep.join("-+-"));

    // 資料列
    for row in &rs.rows {
        let cells: Vec<String> = row.iter().enumerate()
            .map(|(i, v)| {
                let w = widths.get(i).copied().unwrap_or(0);
                format!("{:<width$}", v.to_string(), width = w)
            })
            .collect();
        println!("{}", cells.join(" | "));
    }

    println!("({} row{})", rs.rows.len(), if rs.rows.len() == 1 { "" } else { "s" });
}

// ── 輔助解析函式 ──────────────────────────────────────────────────────────

/// 判斷輸入是否已完整（簡單版：包含 ; 或為點指令）
fn is_complete(buf: &str) -> bool {
    let t = buf.trim();
    t.ends_with(';') || t.starts_with('.')
}

fn extract_table_name_from_insert(sql: &str) -> Option<String> {
    let lower = sql.to_lowercase();
    let after_into = lower.find("into")? + 4;
    let rest = sql[after_into..].trim();
    let name: String = rest.chars().take_while(|c| c.is_alphanumeric() || *c == '_').collect();
    if name.is_empty() { None } else { Some(name) }
}

fn extract_match_query(sql: &str) -> Option<(String, String)> {
    // SELECT * FROM t WHERE t MATCH 'query'
    let lower = sql.to_lowercase();
    let match_pos = lower.find("match")?;
    let after_match = sql[match_pos + 5..].trim();

    // 取得 MATCH 前的表名
    let where_pos = lower.find("where")?;
    let between = sql[where_pos + 5..match_pos].trim();
    let table_name: String = between.chars()
        .take_while(|c| c.is_alphanumeric() || *c == '_')
        .collect();

    // 取出 query（去掉外層引號）
    let query = after_match.trim_matches(|c| c == '\'' || c == '"' || c == ';').to_string();
    if table_name.is_empty() || query.is_empty() { return None; }
    Some((table_name, query))
}

/// 簡單解析 SQL VALUES 內的逗號分隔值（去引號）
fn split_sql_values(s: &str) -> Vec<String> {
    let mut result = Vec::new();
    let mut current = String::new();
    let mut in_quote = false;
    let mut quote_char = ' ';

    for c in s.chars() {
        match c {
            '\'' | '"' if !in_quote => { in_quote = true; quote_char = c; }
            c if in_quote && c == quote_char => { in_quote = false; }
            ',' if !in_quote => {
                result.push(current.trim().to_string());
                current.clear();
            }
            _ => current.push(c),
        }
    }
    if !current.trim().is_empty() {
        result.push(current.trim().to_string());
    }
    result
}

// ── 測試 ─────────────────────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;

    fn repl() -> Repl { Repl::new() }

    #[test]
    fn create_and_select() {
        let mut r = repl();
        r.execute_sql("CREATE TABLE users (id INTEGER, name TEXT, age INTEGER);");
        r.execute_sql("INSERT INTO users VALUES (1, 'Alice', 30);");
        r.execute_sql("INSERT INTO users VALUES (2, 'Bob', 25);");
        // 確認沒有 panic，且 executor 有正確執行
        let catalog = r.executor.catalog();
        assert!(catalog.table_exists("users"));
    }

    #[test]
    fn multi_statement() {
        let mut r = repl();
        r.execute_sql("CREATE TABLE t (id INTEGER, val TEXT); INSERT INTO t VALUES (1, 'a');");
        assert!(r.executor.catalog().table_exists("t"));
    }

    #[test]
    fn dot_tables_empty() {
        let r = repl();
        // 不 panic 即可
        r.cmd_tables();
    }

    #[test]
    fn dot_schema() {
        let mut r = repl();
        r.execute_sql("CREATE TABLE products (id INTEGER, name TEXT, price REAL);");
        r.cmd_schema(Some("products"));
    }

    #[test]
    fn fts_create_and_search() {
        let mut r = repl();
        r.execute_sql("CREATE VIRTUAL TABLE docs USING fts5(title, body);");
        assert!(r.fts_tables.contains_key("docs"));

        r.execute_sql("INSERT INTO docs VALUES ('Rust lang', 'Fast safe systems');");
        r.execute_sql("INSERT INTO docs VALUES ('Python intro', 'Easy to learn');");

        // 搜尋
        let result = r.fts_select("docs", "rust").unwrap();
        assert_eq!(result.row_count(), 1);
    }

    #[test]
    fn fts_match_cjk() {
        let mut r = repl();
        r.execute_sql("CREATE VIRTUAL TABLE articles USING fts5(title, body);");
        r.execute_sql("INSERT INTO articles VALUES ('資料庫', '關聯式資料庫設計');");
        r.execute_sql("INSERT INTO articles VALUES ('程式語言', 'Rust 程式語言');");

        let result = r.fts_select("articles", "資料").unwrap();
        assert_eq!(result.row_count(), 1);
    }

    #[test]
    fn fts_and_query() {
        let mut r = repl();
        r.execute_sql("CREATE VIRTUAL TABLE docs USING fts5(title, body);");
        r.execute_sql("INSERT INTO docs VALUES ('Rust Programming', 'Fast and memory safe');");
        r.execute_sql("INSERT INTO docs VALUES ('Python', 'Easy language');");

        let result = r.fts_select("docs", "rust AND safe").unwrap();
        assert_eq!(result.row_count(), 1);
    }

    #[test]
    fn fts_or_query() {
        let mut r = repl();
        r.execute_sql("CREATE VIRTUAL TABLE docs USING fts5(title, body);");
        r.execute_sql("INSERT INTO docs VALUES ('Rust', 'systems language');");
        r.execute_sql("INSERT INTO docs VALUES ('Python', 'scripting language');");
        r.execute_sql("INSERT INTO docs VALUES ('Go', 'concurrent language');");

        let result = r.fts_select("docs", "rust OR python").unwrap();
        assert_eq!(result.row_count(), 2);
    }

    #[test]
    fn extract_match_query_test() {
        let sql = "SELECT * FROM articles WHERE articles MATCH 'rust'";
        let r = extract_match_query(sql).unwrap();
        assert_eq!(r.0, "articles");
        assert_eq!(r.1, "rust");
    }

    #[test]
    fn split_values_test() {
        let vals = split_sql_values("'hello world', 'foo bar'");
        assert_eq!(vals, vec!["hello world", "foo bar"]);
    }

    #[test]
    fn history_tracking() {
        let mut r = repl();
        r.execute_sql("CREATE TABLE t (id INTEGER);");
        r.execute_sql("INSERT INTO t VALUES (1);");
        assert_eq!(r.history.len(), 2);
    }

    #[test]
    fn aligned_output() {
        // print_result_set 不 panic
        let rs = ResultSet {
            columns: vec!["id".into(), "name".into()],
            rows:    vec![
                vec![Value::Integer(1), Value::Text("Alice".into())],
                vec![Value::Integer(2), Value::Text("Bob".into())],
            ],
        };
        print_result_set(&rs);
    }
}
