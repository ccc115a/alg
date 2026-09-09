//! FtsTable：全文檢索虛擬資料表
//!
//! 模擬 SQLite FTS5 的使用介面：
//!
//! ```sql
//! -- 建立
//! CREATE VIRTUAL TABLE articles USING fts5(title, body);
//!
//! -- 插入
//! INSERT INTO articles VALUES (1, 'Rust lang', 'Fast and safe');
//!
//! -- 查詢（MATCH 語法）
//! SELECT * FROM articles WHERE articles MATCH 'rust';
//! SELECT * FROM articles WHERE articles MATCH '"rust language"';  -- 短語
//! SELECT * FROM articles WHERE articles MATCH 'rust AND safe';
//! SELECT * FROM articles WHERE articles MATCH 'rust OR python';
//! ```
//!
//! 內部結構：
//!   - 原始資料：`HashMap<u64, Vec<String>>` (rowid → column values)
//!   - 全文索引：每個 column 共用同一個 `InvertedIndex`
//!     （column 欄位名加前綴 "col:name:" 作為 term 前綴以區分欄位搜尋）

use std::collections::HashMap;

use super::index::InvertedIndex;
use super::tokenizer::Tokenizer;

/// 查詢語法解析結果
#[derive(Debug, Clone, PartialEq)]
pub enum MatchQuery {
    Term(String),
    Phrase(Vec<String>),
    And(Vec<MatchQuery>),
    Or(Vec<MatchQuery>),
    ColumnFilter { column: String, query: Box<MatchQuery> },
}

/// 解析 MATCH 字串 → MatchQuery
pub fn parse_match_query(q: &str) -> MatchQuery {
    let q = q.trim();

    // OR
    if let Some(pos) = find_keyword(q, " OR ") {
        let left  = parse_match_query(&q[..pos]);
        let right = parse_match_query(&q[pos+4..]);
        return flatten_or(left, right);
    }

    // AND
    if let Some(pos) = find_keyword(q, " AND ") {
        let left  = parse_match_query(&q[..pos]);
        let right = parse_match_query(&q[pos+5..]);
        return flatten_and(left, right);
    }

    // 短語 "..."
    if q.starts_with('"') && q.ends_with('"') {
        let inner = &q[1..q.len()-1];
        let tok = Tokenizer::new();
        let terms: Vec<String> = tok.tokenize(inner).into_iter().map(|t| t.term).collect();
        return MatchQuery::Phrase(terms);
    }

    // 欄位限定 col:term
    if let Some((colon_byte, _)) = q.char_indices().find(|(_, c)| *c == ':') {
        let col = q[..colon_byte].to_string();
        let rest = parse_match_query(&q[colon_byte+1..]);
        return MatchQuery::ColumnFilter { column: col, query: Box::new(rest) };
    }

    // 單一 term
    MatchQuery::Term(q.to_lowercase())
}

fn find_keyword(s: &str, kw: &str) -> Option<usize> {
    let mut depth = 0i32;
    for (byte_pos, ch) in s.char_indices() {
        if ch == '"' { depth = 1 - depth; }
        if depth == 0 && s[byte_pos..].starts_with(kw) { return Some(byte_pos); }
    }
    None
}

fn flatten_or(l: MatchQuery, r: MatchQuery) -> MatchQuery {
    match (l, r) {
        (MatchQuery::Or(mut lv), MatchQuery::Or(rv)) => { lv.extend(rv); MatchQuery::Or(lv) }
        (MatchQuery::Or(mut lv), r) => { lv.push(r); MatchQuery::Or(lv) }
        (l, r) => MatchQuery::Or(vec![l, r]),
    }
}

fn flatten_and(l: MatchQuery, r: MatchQuery) -> MatchQuery {
    match (l, r) {
        (MatchQuery::And(mut lv), MatchQuery::And(rv)) => { lv.extend(rv); MatchQuery::And(lv) }
        (MatchQuery::And(mut lv), r) => { lv.push(r); MatchQuery::And(lv) }
        (l, r) => MatchQuery::And(vec![l, r]),
    }
}

// ── FtsTable ──────────────────────────────────────────────────────────────

pub struct FtsTable {
    pub name:    String,
    pub columns: Vec<String>,
    tokenizer:   Tokenizer,
    index:       InvertedIndex,
    /// rowid → column values（原始資料）
    storage:     HashMap<u64, Vec<String>>,
    next_rowid:  u64,
}

impl FtsTable {
    pub fn new(name: &str, columns: Vec<String>) -> Self {
        FtsTable {
            name:       name.to_string(),
            columns,
            tokenizer:  Tokenizer::new(),
            index:      InvertedIndex::new(),
            storage:    HashMap::new(),
            next_rowid: 1,
        }
    }

    // ── 資料操作 ──────────────────────────────────────────────────────────

    /// 插入一列；`values` 對應 columns 順序
    pub fn insert(&mut self, values: Vec<String>) -> u64 {
        let rowid = self.next_rowid;
        self.next_rowid += 1;
        self.index_row(rowid, &values);
        self.storage.insert(rowid, values);
        rowid
    }

    /// 以 rowid 插入（與主表 rowid 對齊）
    pub fn insert_with_id(&mut self, rowid: u64, values: Vec<String>) {
        self.index_row(rowid, &values);
        self.storage.insert(rowid, values);
        if rowid >= self.next_rowid { self.next_rowid = rowid + 1; }
    }

    /// 更新一列
    pub fn update(&mut self, rowid: u64, values: Vec<String>) {
        self.index.remove_document(rowid);
        self.index_row(rowid, &values);
        self.storage.insert(rowid, values);
    }

    /// 刪除一列
    pub fn delete(&mut self, rowid: u64) {
        self.index.remove_document(rowid);
        self.storage.remove(&rowid);
    }

    /// 以 MATCH 查詢，回傳 (rowid, score, column_values) 依分數降序
    pub fn search(&mut self, query: &str) -> Vec<(u64, f64, Vec<String>)> {
        let q = parse_match_query(query);
        let scores = self.execute_query(&q);
        let mut result: Vec<(u64, f64, Vec<String>)> = scores.into_iter()
            .filter_map(|(rowid, score)| {
                self.storage.get(&rowid).map(|vals| (rowid, score, vals.clone()))
            })
            .collect();
        result.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));
        result
    }

    pub fn row_count(&self) -> usize { self.storage.len() }

    // ── 內部輔助 ──────────────────────────────────────────────────────────

    fn index_row(&mut self, rowid: u64, values: &[String]) {
        // 使用循序 token index 作為 position（確保短語搜尋正確）
        let mut all_tokens = Vec::new();
        let mut seq: u32 = 0;
        for (col_idx, val) in values.iter().enumerate() {
            let col_name = self.columns.get(col_idx).cloned().unwrap_or_default();
            let tokens = self.tokenizer.tokenize(val);
            for tok in &tokens {
                // 欄位前綴版本
                all_tokens.push(super::tokenizer::Token {
                    term:   format!("{}:{}", col_name, tok.term),
                    offset: seq as usize,
                });
                // 無前綴版本
                all_tokens.push(super::tokenizer::Token {
                    term:   tok.term.clone(),
                    offset: seq as usize,
                });
                seq += 1;
            }
        }
        self.index.index_document(rowid, &all_tokens);
    }

    fn execute_query(&mut self, q: &MatchQuery) -> HashMap<u64, f64> {
        match q {
            MatchQuery::Term(t) => {
                self.index.search_term(t).into_iter().collect()
            }
            MatchQuery::Phrase(terms) => {
                let refs: Vec<&str> = terms.iter().map(|s| s.as_str()).collect();
                self.index.search_phrase(&refs).into_iter().collect()
            }
            MatchQuery::And(parts) => {
                let mut acc: Option<HashMap<u64, f64>> = None;
                for part in parts {
                    let scores = self.execute_query(part);
                    acc = Some(match acc {
                        None => scores,
                        Some(existing) => existing.into_iter()
                            .filter_map(|(id, s)| scores.get(&id).map(|ts| (id, s + ts)))
                            .collect(),
                    });
                }
                acc.unwrap_or_default()
            }
            MatchQuery::Or(parts) => {
                let mut combined: HashMap<u64, f64> = HashMap::new();
                for part in parts {
                    for (id, score) in self.execute_query(part) {
                        *combined.entry(id).or_insert(0.0) += score;
                    }
                }
                combined
            }
            MatchQuery::ColumnFilter { column, query } => {
                // 把 query 中的 term 加上欄位前綴
                let prefixed = prefix_query(query, column);
                self.execute_query(&prefixed)
            }
        }
    }
}

fn prefix_query(q: &MatchQuery, col: &str) -> MatchQuery {
    match q {
        MatchQuery::Term(t)    => MatchQuery::Term(format!("{}:{}", col, t)),
        MatchQuery::Phrase(ts) => MatchQuery::Phrase(ts.iter().map(|t| format!("{}:{}", col, t)).collect()),
        MatchQuery::And(parts) => MatchQuery::And(parts.iter().map(|p| prefix_query(p, col)).collect()),
        MatchQuery::Or(parts)  => MatchQuery::Or(parts.iter().map(|p| prefix_query(p, col)).collect()),
        MatchQuery::ColumnFilter { column: c, query: q } => MatchQuery::ColumnFilter { column: c.clone(), query: Box::new(prefix_query(q, col)) },
    }
}

// ── 測試 ─────────────────────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;

    fn make_table() -> FtsTable {
        let mut t = FtsTable::new("articles", vec!["title".into(), "body".into()]);
        t.insert(vec!["Rust Programming".into(), "Rust is fast and memory safe".into()]);
        t.insert(vec!["Python Basics".into(),    "Python is easy to learn".into()]);
        t.insert(vec!["資料庫設計".into(),        "介紹關聯式資料庫的基本概念".into()]);
        t.insert(vec!["Rust 與資料庫".into(),     "使用 Rust 操作 SQL 資料庫".into()]);
        t
    }

    #[test]
    fn search_single_term() {
        let mut t = make_table();
        let r = t.search("rust");
        assert_eq!(r.len(), 2);
    }

    #[test]
    fn search_cjk() {
        let mut t = make_table();
        let r = t.search("資料");
        assert!(r.len() >= 2);
    }

    #[test]
    fn search_and() {
        let mut t = make_table();
        let r = t.search("rust AND memory");
        assert_eq!(r.len(), 1);
        assert_eq!(r[0].2[0], "Rust Programming");
    }

    #[test]
    fn search_or() {
        let mut t = make_table();
        let r = t.search("rust OR python");
        assert_eq!(r.len(), 3);
    }

    #[test]
    fn search_phrase() {
        let mut t = make_table();
        let r = t.search("\"memory safe\"");
        assert_eq!(r.len(), 1);
    }

    #[test]
    fn search_no_result() {
        let mut t = make_table();
        let r = t.search("javascript");
        assert!(r.is_empty());
    }

    #[test]
    fn update_then_search() {
        let mut t = make_table();
        t.update(1, vec!["Python Guide".into(), "Python not Rust".into()]);
        // doc 1 已不含 "fast"
        let r = t.search("fast");
        assert!(r.iter().all(|(id, _, _)| *id != 1));
    }

    #[test]
    fn delete_then_search() {
        let mut t = make_table();
        t.delete(2); // 刪除 Python 文件
        let r = t.search("python");
        assert!(r.is_empty());
    }

    #[test]
    fn score_ordering() {
        let mut t = make_table();
        let r = t.search("rust");
        // 分數應遞減
        for i in 1..r.len() { assert!(r[i-1].1 >= r[i].1); }
    }

    #[test]
    fn parse_query_and() {
        let q = parse_match_query("rust AND safe");
        assert!(matches!(q, MatchQuery::And(_)));
    }

    #[test]
    fn parse_query_or() {
        let q = parse_match_query("rust OR python");
        assert!(matches!(q, MatchQuery::Or(_)));
    }

    #[test]
    fn parse_query_phrase() {
        let q = parse_match_query("\"memory safe\"");
        assert!(matches!(q, MatchQuery::Phrase(_)));
    }

    #[test]
    fn column_filter() {
        let mut t = make_table();
        // 只搜 title 欄位
        let r = t.search("title:rust");
        assert!(r.len() >= 1);
    }
}
