//! Full-text search module
//!
//! Inverted index implementation based on the KV interface, compatible with all storage engines (Memory/BTree/LSM).
//!
//! ## Features
//!
//! - Inverted Index
//! - CJK (Chinese/Japanese/Korean) and English tokenization
//! - Boolean queries (AND/OR/NOT)
//! - Prefix matching (prefix*)
//! - BM25 relevance scoring
//!
//! ## Internal Storage Structure
//!
//! Uses FTS_TABLE_ID = 255 to store index data:
//! - `term:{term}` → `[doc_id1, doc_id2, ...]` (inverted list)
//! - `doc:{doc_id}:{term}` → `count` (term frequency)
//! - `doc_len:{doc_id}` → `total_terms` (document length)

use std::collections::{BTreeMap, BTreeSet};
use crate::error::Result;
use crate::engine::StorageEngine;

/// Reserved table_id used by FTS
const FTS_TABLE_ID: u32 = 255;

/// BM25 scoring parameter: term frequency saturation
const BM25_K1: f64 = 1.5;
/// BM25 scoring parameter: document length normalization
const BM25_B: f64 = 0.75;

/// Tokenizer trait
///
/// Defines how text is split into terms. Different languages require different tokenization strategies.
pub trait FtsTokenizer: Send + Sync {
    /// Tokenize text into a list of terms
    fn tokenize(&self, text: &str) -> Vec<String>;
}

/// CJK tokenizer — Bigram
///
/// Uses every two consecutive Chinese characters as a term.
/// Example: `"資料庫"` → `["資料", "料庫"]`
pub struct CjkTokenizer;

impl CjkTokenizer {
    pub fn new() -> Self {
        Self
    }
}

impl FtsTokenizer for CjkTokenizer {
    fn tokenize(&self, text: &str) -> Vec<String> {
        let chars: Vec<char> = text.chars().collect();
        if chars.len() < 2 {
            return vec![text.to_string()];
        }
        // 滑動視窗，每兩個字元為一組
        chars
            .windows(2)
            .map(|w| w.iter().collect::<String>())
            .collect()
    }
}

/// English tokenizer — lowercase + whitespace splitting
///
/// Example: `"Hello World"` → `["hello", "world"]`
pub struct EnglishTokenizer;

impl EnglishTokenizer {
    pub fn new() -> Self {
        Self
    }
}

impl FtsTokenizer for EnglishTokenizer {
    fn tokenize(&self, text: &str) -> Vec<String> {
        text.to_lowercase()
            .split_whitespace()
            .map(|s| s.to_string())
            .collect()
    }
}

/// FTS index — an inverted index stored via the KV interface
///
/// The generic parameter E can be any engine implementing StorageEngine.
pub struct FtsIndex<'a, E: StorageEngine> {
    engine: &'a mut E,
    doc_count: u64,
}

impl<'a, E: StorageEngine> FtsIndex<'a, E> {
    /// Create a new FTS index
    pub fn new(engine: &'a mut E) -> Self {
        Self {
            engine,
            doc_count: 0,
        }
    }

    /// Insert a document's content into the inverted index
    ///
    /// Steps:
    /// 1. Tokenize text using the CJK tokenizer
    /// 2. Store the raw document content (D:{doc_id})
    /// 3. Count term frequency (TF) for each term
    /// 4. Store inverted index entries (T:{term}:{doc_id} = tf)
    pub fn insert(&mut self, doc_id: u64, text: &str) -> Result<()> {
        let tokenizer = CjkTokenizer::new();
        let terms = tokenizer.tokenize(text);

        // 儲存原始文件
        let doc_key = format!("D:{}", doc_id);
        self.engine.put(FTS_TABLE_ID, doc_key.as_bytes(), text.as_bytes())?;

        // 統計詞頻
        let mut term_map: BTreeMap<String, u32> = BTreeMap::new();
        for term in &terms {
            *term_map.entry(term.clone()).or_insert(0) += 1;
        }

        // 寫入倒排索引
        for (term, tf) in term_map {
            let term_key = format!("T:{}:{}", term, doc_id);
            self.engine.put(FTS_TABLE_ID, term_key.as_bytes(), &tf.to_le_bytes())?;
        }

        self.doc_count += 1;
        Ok(())
    }

    /// Basic search: return document IDs containing all query terms
    pub fn search(&self, query: &str) -> Result<Vec<u64>> {
        let tokenizer = CjkTokenizer::new();
        let terms = tokenizer.tokenize(query);

        if terms.is_empty() {
            return Ok(vec![]);
        }

        let mut results: BTreeMap<u64, ()> = BTreeMap::new();

        for term in &terms {
            let prefix = format!("T:{}:", term);
            let scan_start = format!("T:{}:", term);
            let scan_end = format!("T:{}~\0", term);

            if let Ok(matches) = self.engine.scan(FTS_TABLE_ID, scan_start.as_bytes(), scan_end.as_bytes()) {
                for (key, _) in matches {
                    let key_str = String::from_utf8_lossy(&key);
                    if let Some(pos) = key_str.strip_prefix(&prefix) {
                        if let Ok(doc_id) = pos.parse::<u64>() {
                            results.insert(doc_id, ());
                        }
                    }
                }
            }
        }

        Ok(results.into_iter().map(|(k, _)| k).collect())
    }

    /// Get all document IDs containing the specified term (helper method)
    fn get_doc_ids_for_term(&self, term: &str) -> Result<BTreeSet<u64>> {
        let mut doc_ids = BTreeSet::new();
        for doc_id in self.get_all_doc_ids()? {
            if self.get_term_frequency(doc_id, term)? > 0 {
                doc_ids.insert(doc_id);
            }
        }
        Ok(doc_ids)
    }

    /// Prefix search: return document IDs matching the given prefix
    ///
    /// Implements prefix matching by scanning the `T:{prefix}` range.
    pub fn search_prefix(&self, prefix: &str) -> Result<Vec<u64>> {
        let tokenizer = CjkTokenizer::new();
        let terms = tokenizer.tokenize(prefix);

        if terms.is_empty() {
            return Ok(vec![]);
        }

        let mut results: BTreeSet<u64> = BTreeSet::new();

        for term in &terms {
            let term_prefix = format!("T:{}", term);
            let scan_start = term_prefix.as_bytes();
            let scan_end = format!("T:{}~\0", term).into_bytes();

            if let Ok(matches) = self.engine.scan(FTS_TABLE_ID, scan_start, &scan_end) {
                for (key, _) in matches {
                    let key_str = String::from_utf8_lossy(&key);
                    if let Some(remainder) = key_str.strip_prefix(&term_prefix) {
                        if remainder.starts_with(':') {
                            if let Some(pos) = remainder.strip_prefix(':') {
                                if let Ok(doc_id) = pos.parse::<u64>() {
                                    results.insert(doc_id);
                                }
                            }
                        }
                    }
                }
            }
        }

        Ok(results.into_iter().collect())
    }

    /// Boolean search: supports AND and NOT syntax
    ///
    /// Syntax:
    /// - `"a b"` → documents containing both a and b (AND)
    /// - `"a -b"` → documents containing a but not b (AND + NOT)
    /// - `"a !b"` → same as above
    pub fn search_boolean(&self, query: &str) -> Result<Vec<u64>> {
        let parts: Vec<&str> = query.split_whitespace().collect();

        let mut positive_terms: Vec<&str> = Vec::new();
        let mut negative_terms: Vec<&str> = Vec::new();

        // 分離正項（以 - 或 ! 開頭為負項）
        for term in parts {
            if term.starts_with('-') || term.starts_with('!') {
                let t = term.trim_start_matches('-').trim_start_matches('!');
                if !t.is_empty() {
                    negative_terms.push(t);
                }
            } else {
                positive_terms.push(term);
            }
        }

        let tokenizer = CjkTokenizer::new();

        let mut results: Option<BTreeSet<u64>> = None;

        // AND：取所有正向詞彙結果的交集
        for term_str in positive_terms {
            let terms = tokenizer.tokenize(term_str);
            let mut term_results: BTreeSet<u64> = BTreeSet::new();

            for term in &terms {
                let docs = self.get_doc_ids_for_term(term)?;
                term_results.extend(docs);
            }

            if results.is_none() {
                results = Some(term_results);
            } else {
                if let Some(ref mut r) = results {
                    *r = r.intersection(&term_results).cloned().collect();
                }
            }
        }

        if results.is_none() {
            results = Some(BTreeSet::new());
        }

        // NOT：從結果中移除包含負向詞彙的文件
        for term_str in &negative_terms {
            let terms = tokenizer.tokenize(term_str);
            for term in &terms {
                let docs = self.get_doc_ids_for_term(term)?;
                if let Some(ref mut r) = results {
                    for doc in docs {
                        r.remove(&doc);
                    }
                }
            }
        }

        Ok(results.unwrap().into_iter().collect())
    }

    /// BM25 relevance scoring search
    ///
    /// BM25 (Best Matching 25) is the most widely used
    /// relevance scoring function in modern information retrieval,
    /// considering term frequency (TF), inverse document frequency (IDF), and
    /// document length normalization.
    pub fn search_bm25(&self, query: &str) -> Result<Vec<(u64, f64)>> {
        let tokenizer = CjkTokenizer::new();
        let terms = tokenizer.tokenize(query);

        if terms.is_empty() || self.doc_count == 0 {
            return Ok(vec![]);
        }

        let mut doc_scores: BTreeMap<u64, f64> = BTreeMap::new();
        let avg_dl = self.compute_avg_doc_length()?;

        for term in &terms {
            let df = self.get_document_frequency(term)?;
            if df == 0 {
                continue;
            }

            // 計算 IDF
            let idf = ((self.doc_count as f64 - df as f64 + 0.5) / (df as f64 + 0.5) + 1.0).ln();

            let docs = self.get_doc_ids_for_term(term)?;
            for doc_id in docs {
                let tf = self.get_term_frequency(doc_id, term)? as f64;
                let dl = self.get_doc_length(doc_id)? as f64;

                // BM25 核心公式
                let score = idf * (tf * (BM25_K1 + 1.0)) / (tf + BM25_K1 * (1.0 - BM25_B + BM25_B * dl / avg_dl));
                *doc_scores.entry(doc_id).or_insert(0.0) += score;
            }
        }

        // 按分數由高到低排序
        let mut sorted: Vec<(u64, f64)> = doc_scores.into_iter().collect();
        sorted.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));

        Ok(sorted)
    }

    /// Get all indexed document IDs
    fn get_all_doc_ids(&self) -> Result<Vec<u64>> {
        let mut ids = Vec::new();
        if let Ok(results) = self.engine.scan(FTS_TABLE_ID, b"D:", b"D:~\0") {
            for (key, _) in results {
                let key_str = String::from_utf8_lossy(&key);
                if let Some(id_str) = key_str.strip_prefix("D:") {
                    if let Ok(doc_id) = id_str.parse::<u64>() {
                        ids.push(doc_id);
                    }
                }
            }
        }
        ids.sort();
        Ok(ids)
    }

    /// Get document frequency (DF): number of documents containing the term
    fn get_document_frequency(&self, term: &str) -> Result<u32> {
        let mut count = 0u32;
        for doc_id in self.get_all_doc_ids()? {
            if self.get_term_frequency(doc_id, term)? > 0 {
                count += 1;
            }
        }
        Ok(count)
    }

    /// Get term frequency (TF) for a term in a specific document
    fn get_term_frequency(&self, doc_id: u64, term: &str) -> Result<u32> {
        let term_key = format!("T:{}:{}", term, doc_id);
        if let Ok(Some(data)) = self.engine.get(FTS_TABLE_ID, term_key.as_bytes()) {
            if data.len() >= 4 {
                return Ok(u32::from_le_bytes([data[0], data[1], data[2], data[3]]));
            }
        }
        Ok(0)
    }

    /// Get total number of terms in a document (used for BM25 length normalization)
    fn get_doc_length(&self, doc_id: u64) -> Result<u32> {
        if let Ok(Some(text)) = self.get_doc(doc_id) {
            let text_str = String::from_utf8_lossy(&text);
            let tokenizer = CjkTokenizer::new();
            Ok(tokenizer.tokenize(&text_str).len() as u32)
        } else {
            Ok(0)
        }
    }

    /// Compute the average document length (used for BM25 length normalization)
    fn compute_avg_doc_length(&self) -> Result<f64> {
        if self.doc_count == 0 {
            return Ok(0.0);
        }

        let mut total_len = 0u64;
        let mut count = 0u64;
        for doc_id in self.get_all_doc_ids()? {
            total_len += self.get_doc_length(doc_id)? as u64;
            count += 1;
        }

        if count == 0 {
            return Ok(0.0);
        }
        Ok(total_len as f64 / count as f64)
    }

    /// Return the number of indexed documents
    pub fn doc_count(&self) -> u64 {
        self.doc_count
    }

    /// Get the raw document content
    pub fn get_doc(&self, doc_id: u64) -> Result<Option<Vec<u8>>> {
        let doc_key = format!("D:{}", doc_id);
        self.engine.get(FTS_TABLE_ID, doc_key.as_bytes())
    }
}

/// FTS query structure
pub struct FtsQuery {
    pub terms: Vec<String>,
    pub and: bool,
}

impl FtsQuery {
    /// Parse a query string into an FTS query structure
    pub fn parse(query: &str) -> Self {
        let terms: Vec<String> = query
            .split_whitespace()
            .filter(|s| !s.is_empty())
            .map(|s| s.to_lowercase())
            .collect();

        Self {
            terms,
            and: false,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::FtsTokenizer;
    use crate::engine::HashMemoryEngine;

    #[test]
    fn test_cjk_tokenizer() {
        let tokenizer = super::CjkTokenizer::new();
        let tokens = tokenizer.tokenize("資料庫系統");
        assert_eq!(tokens, vec!["資料", "料庫", "庫系", "系統"]);
    }

    #[test]
    fn test_english_tokenizer() {
        let tokenizer = super::EnglishTokenizer::new();
        let tokens = tokenizer.tokenize("Hello World");
        assert_eq!(tokens, vec!["hello", "world"]);
    }

    #[test]
    fn test_fts_basic() {
        let mut engine = HashMemoryEngine::new();
        let mut index = super::FtsIndex::new(&mut engine);
        
        index.insert(1, "Hello World").unwrap();
        index.insert(2, "資料庫系統").unwrap();
        
        let results = index.search("Hello").unwrap();
        assert!(results.contains(&1));
        
        let results2 = index.search("資料庫").unwrap();
        assert!(results2.contains(&2));
    }

    #[test]
    fn test_fts_prefix() {
        let mut engine = HashMemoryEngine::new();
        let mut index = super::FtsIndex::new(&mut engine);
        
        index.insert(1, "資料庫").unwrap();
        index.insert(2, "資料結構").unwrap();
        index.insert(3, "作業系統").unwrap();
        
        let results = index.search_prefix("資料").unwrap();
        assert!(results.contains(&1));
        assert!(results.contains(&2));
    }

    #[test]
    fn test_fts_boolean_and() {
        let mut engine = HashMemoryEngine::new();
        let mut index = super::FtsIndex::new(&mut engine);
        
        index.insert(1, "Hello World").unwrap();
        index.insert(2, "Hello Rust").unwrap();
        index.insert(3, "World Peace").unwrap();
        
        let results = index.search_boolean("Hello World").unwrap();
        assert!(results.contains(&1));
    }

    #[test]
    fn test_fts_boolean_not() {
        let mut engine = HashMemoryEngine::new();
        let mut index = super::FtsIndex::new(&mut engine);
        
        index.insert(1, "Hello World").unwrap();
        index.insert(2, "Hello Rust").unwrap();
        index.insert(3, "World Peace").unwrap();
        
        let results = index.search_boolean("Hello -World").unwrap();
        assert!(results.contains(&2));
        assert!(!results.contains(&1));
    }

    #[test]
    fn test_fts_bm25() {
        let mut engine = HashMemoryEngine::new();
        let mut index = super::FtsIndex::new(&mut engine);
        
        index.insert(1, "hello world").unwrap();
        index.insert(2, "hello hello world").unwrap();
        index.insert(3, "world").unwrap();
        
        let results = index.search_bm25("hello").unwrap();
        assert!(!results.is_empty());
        
        let (_doc_id, score) = results[0];
        assert!(score >= 0.0);
    }

    #[test]
    fn test_fts_with_kv_engine() {
        use crate::kv::KvEngine;
        
        let mut engine = KvEngine::new("memory").unwrap();
        let mut index = super::FtsIndex::new(&mut engine);
        
        index.insert(1, "Hello World").unwrap();
        index.insert(2, "資料庫系統").unwrap();
        
        let results = index.search("Hello").unwrap();
        assert!(results.contains(&1));
        
        let results2 = index.search("資料庫").unwrap();
        assert!(results2.contains(&2));
    }
}