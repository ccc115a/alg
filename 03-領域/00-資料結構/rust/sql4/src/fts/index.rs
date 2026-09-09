//! 倒排索引（Inverted Index）
//!
//! 資料結構：
//!   term  →  PostingList { df, postings: [(doc_id, tf, positions)] }
//!
//! 儲存於獨立的 B+Tree（key = term, value = 序列化的 PostingList）
//!
//! 排序演算法：BM25
//!   score(D,Q) = Σ IDF(qi) * (tf * (k1+1)) / (tf + k1*(1-b+b*|D|/avgdl))
//!   IDF(qi) = ln((N - df + 0.5) / (df + 0.5) + 1)

use std::collections::HashMap;

use crate::btree::node::Key;
use crate::btree::tree::BPlusTree;
use crate::pager::storage::MemoryStorage;

// ── Posting ───────────────────────────────────────────────────────────────

/// 單一文件的出現資訊
#[derive(Debug, Clone)]
pub struct Posting {
    pub doc_id:    u64,
    pub tf:        u32,        // term frequency（出現次數）
    pub positions: Vec<u32>,   // 在文件中的字元位置（用於短語搜尋）
}

/// 一個 term 的完整 posting list
#[derive(Debug, Clone)]
pub struct PostingList {
    pub df:       u32,           // document frequency
    pub postings: Vec<Posting>,
}

// ── 序列化 ────────────────────────────────────────────────────────────────
//
// 格式：
//   [0..4]  df       : u32
//   [4..8]  n_docs   : u32
//   per doc:
//     [0..8]   doc_id   : u64
//     [8..12]  tf       : u32
//     [12..16] n_pos    : u32
//     [16..]   positions: u32 * n_pos

fn encode_posting_list(pl: &PostingList) -> Vec<u8> {
    let mut buf = Vec::new();
    buf.extend_from_slice(&pl.df.to_le_bytes());
    buf.extend_from_slice(&(pl.postings.len() as u32).to_le_bytes());
    for p in &pl.postings {
        buf.extend_from_slice(&p.doc_id.to_le_bytes());
        buf.extend_from_slice(&p.tf.to_le_bytes());
        buf.extend_from_slice(&(p.positions.len() as u32).to_le_bytes());
        for pos in &p.positions {
            buf.extend_from_slice(&pos.to_le_bytes());
        }
    }
    buf
}

fn decode_posting_list(bytes: &[u8]) -> PostingList {
    let mut cur = 0;
    let df     = u32::from_le_bytes(bytes[cur..cur+4].try_into().unwrap()); cur += 4;
    let n_docs = u32::from_le_bytes(bytes[cur..cur+4].try_into().unwrap()) as usize; cur += 4;
    let mut postings = Vec::with_capacity(n_docs);
    for _ in 0..n_docs {
        let doc_id = u64::from_le_bytes(bytes[cur..cur+8].try_into().unwrap()); cur += 8;
        let tf     = u32::from_le_bytes(bytes[cur..cur+4].try_into().unwrap()); cur += 4;
        let n_pos  = u32::from_le_bytes(bytes[cur..cur+4].try_into().unwrap()) as usize; cur += 4;
        let mut positions = Vec::with_capacity(n_pos);
        for _ in 0..n_pos {
            positions.push(u32::from_le_bytes(bytes[cur..cur+4].try_into().unwrap())); cur += 4;
        }
        postings.push(Posting { doc_id, tf, positions });
    }
    PostingList { df, postings }
}

// ── InvertedIndex ─────────────────────────────────────────────────────────

/// BM25 參數
const K1: f64 = 1.2;
const B:  f64 = 0.75;

pub struct InvertedIndex {
    /// term → PostingList，存於 B+Tree
    tree:    BPlusTree<MemoryStorage>,
    /// 各文件的詞數（用於計算 avgdl）
    doc_len: HashMap<u64, u32>,
    /// 總文件數
    n_docs:  u64,
}

impl InvertedIndex {
    pub fn new() -> Self {
        InvertedIndex {
            tree:    BPlusTree::new(64, MemoryStorage::new()),
            doc_len: HashMap::new(),
            n_docs:  0,
        }
    }

    // ── 索引建立 ──────────────────────────────────────────────────────────

    /// 新增或更新一份文件
    /// `doc_id`：文件識別碼（對應資料表的 rowid）
    /// `tokens`：Tokenizer 切出的 token 串（含位置）
    pub fn index_document(&mut self, doc_id: u64, tokens: &[super::tokenizer::Token]) {
        // 先刪除舊的（更新場景）
        self.remove_document(doc_id);

        // 統計 tf 與 positions
        let mut tf_map: HashMap<String, (u32, Vec<u32>)> = HashMap::new();
        for tok in tokens {
            let e = tf_map.entry(tok.term.clone()).or_insert((0, Vec::new()));
            e.0 += 1;
            e.1.push(tok.offset as u32);
        }

        self.doc_len.insert(doc_id, tokens.len() as u32);
        self.n_docs += 1;

        // 更新每個 term 的 posting list
        for (term, (tf, positions)) in tf_map {
            let key = Key::Text(term.clone());
            let mut pl = self.tree.search(&key)
                .map(|b| decode_posting_list(&b))
                .unwrap_or(PostingList { df: 0, postings: Vec::new() });

            pl.df += 1;
            pl.postings.push(Posting { doc_id, tf, positions });
            self.tree.insert(key, encode_posting_list(&pl));
        }
    }

    /// 移除一份文件的所有 posting
    pub fn remove_document(&mut self, doc_id: u64) {
        if self.doc_len.remove(&doc_id).is_none() { return; }
        self.n_docs = self.n_docs.saturating_sub(1);

        // 掃描所有 term 移除此 doc（成本較高，實際系統可用標記刪除）
        let min = Key::Text(String::new());
        let max = Key::Text("\u{10FFFF}".repeat(4));
        let records = self.tree.range_search(&min, &max);

        let updates: Vec<(String, PostingList)> = records.into_iter().filter_map(|r| {
            let Key::Text(term) = &r.key else { return None; };
            let mut pl = decode_posting_list(&r.value);
            let before = pl.postings.len();
            pl.postings.retain(|p| p.doc_id != doc_id);
            if pl.postings.len() < before {
                pl.df = pl.postings.len() as u32;
                Some((term.clone(), pl))
            } else { None }
        }).collect();

        for (term, pl) in updates {
            let key = Key::Text(term);
            if pl.postings.is_empty() {
                self.tree.delete(&key);
            } else {
                self.tree.insert(key, encode_posting_list(&pl));
            }
        }
    }

    // ── 搜尋 ──────────────────────────────────────────────────────────────

    /// 單一 term 搜尋，回傳 (doc_id, bm25_score) 列表，依分數降序
    pub fn search_term(&mut self, term: &str) -> Vec<(u64, f64)> {
        let key = Key::Text(term.to_lowercase());
        let pl = match self.tree.search(&key) {
            Some(b) => decode_posting_list(&b),
            None    => return vec![],
        };
        let scores = self.bm25_scores(&pl);
        let mut result: Vec<(u64, f64)> = scores.into_iter().collect();
        result.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));
        result
    }

    /// 多 term AND 搜尋（所有 term 都必須出現）
    pub fn search_and(&mut self, terms: &[&str]) -> Vec<(u64, f64)> {
        if terms.is_empty() { return vec![]; }

        let mut scores: Option<HashMap<u64, f64>> = None;

        for term in terms {
            let key = Key::Text(term.to_lowercase());
            let pl = match self.tree.search(&key) {
                Some(b) => decode_posting_list(&b),
                None    => return vec![],  // AND：任一 term 不存在即無結果
            };
            let term_scores = self.bm25_scores(&pl);
            scores = Some(match scores {
                None => term_scores,
                Some(existing) => {
                    // 交集 + 累加分數
                    existing.into_iter()
                        .filter_map(|(doc, s)| term_scores.get(&doc).map(|ts| (doc, s + ts)))
                        .collect()
                }
            });
        }

        let mut result: Vec<(u64, f64)> = scores.unwrap_or_default().into_iter().collect();
        result.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));
        result
    }

    /// 多 term OR 搜尋（任一 term 出現即計入）
    pub fn search_or(&mut self, terms: &[&str]) -> Vec<(u64, f64)> {
        let mut combined: HashMap<u64, f64> = HashMap::new();
        for term in terms {
            let key = Key::Text(term.to_lowercase());
            if let Some(b) = self.tree.search(&key) {
                let pl = decode_posting_list(&b);
                for (doc, score) in self.bm25_scores(&pl) {
                    *combined.entry(doc).or_insert(0.0) += score;
                }
            }
        }
        let mut result: Vec<(u64, f64)> = combined.into_iter().collect();
        result.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));
        result
    }

    /// 短語搜尋（terms 必須連續出現）
    pub fn search_phrase(&mut self, terms: &[&str]) -> Vec<(u64, f64)> {
        if terms.is_empty() { return vec![]; }

        // 先取第一個 term 的 posting list 作為候選
        let key0 = Key::Text(terms[0].to_lowercase());
        let pl0 = match self.tree.search(&key0) {
            Some(b) => decode_posting_list(&b),
            None    => return vec![],
        };

        // 取得其餘 term 的 posting lists
        let rest_pls: Vec<PostingList> = terms[1..].iter().map(|t| {
            let key = Key::Text(t.to_lowercase());
            self.tree.search(&key).map(|b| decode_posting_list(&b))
                .unwrap_or(PostingList { df: 0, postings: vec![] })
        }).collect();

        let mut matched_docs: Vec<u64> = Vec::new();

        'doc: for p0 in &pl0.postings {
            // 對每個候選文件，檢查 positions 是否連續
            let rest_postings: Vec<Option<&Posting>> = rest_pls.iter()
                .map(|pl| pl.postings.iter().find(|p| p.doc_id == p0.doc_id))
                .collect();

            if rest_postings.iter().any(|p| p.is_none()) { continue; }

            // 嘗試找到連續的位置序列
            'pos: for &start_pos in &p0.positions {
                for (i, rp) in rest_postings.iter().enumerate() {
                    let expected = start_pos + (i as u32 + 1);
                    if !rp.unwrap().positions.contains(&expected) { continue 'pos; }
                }
                matched_docs.push(p0.doc_id);
                continue 'doc;
            }
        }

        // 對匹配文件計算 BM25（以第一個 term 的分數為基礎）
        let base_scores = self.bm25_scores(&pl0);
        let mut result: Vec<(u64, f64)> = matched_docs.into_iter()
            .filter_map(|doc| base_scores.get(&doc).map(|s| (doc, *s)))
            .collect();
        result.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));
        result
    }

    // ── BM25 ──────────────────────────────────────────────────────────────

    fn avg_doc_len(&self) -> f64 {
        if self.doc_len.is_empty() { return 1.0; }
        self.doc_len.values().map(|&l| l as f64).sum::<f64>() / self.doc_len.len() as f64
    }

    fn bm25_scores(&self, pl: &PostingList) -> HashMap<u64, f64> {
        let n = self.n_docs as f64;
        let df = pl.df as f64;
        let avgdl = self.avg_doc_len();

        // IDF
        let idf = ((n - df + 0.5) / (df + 0.5) + 1.0).ln();

        pl.postings.iter().map(|p| {
            let tf = p.tf as f64;
            let dl = self.doc_len.get(&p.doc_id).copied().unwrap_or(1) as f64;
            let score = idf * (tf * (K1 + 1.0)) / (tf + K1 * (1.0 - B + B * dl / avgdl));
            (p.doc_id, score)
        }).collect()
    }

    // ── 統計 ──────────────────────────────────────────────────────────────

    pub fn doc_count(&self) -> u64 { self.n_docs }

    pub fn term_count(&mut self) -> usize {
        let min = Key::Text(String::new());
        let max = Key::Text("\u{10FFFF}".repeat(4));
        self.tree.range_search(&min, &max).len()
    }
}

impl Default for InvertedIndex {
    fn default() -> Self { Self::new() }
}

// ── 測試 ─────────────────────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;
    use crate::fts::tokenizer::Tokenizer;

    fn make_index() -> InvertedIndex {
        let tok = Tokenizer::new();
        let mut idx = InvertedIndex::new();
        let docs = vec![
            (1u64, "Rust is a systems programming language"),
            (2,    "Python is a high level programming language"),
            (3,    "資料庫管理系統"),
            (4,    "Rust 程式語言很快"),
            (5,    "SQL 資料庫查詢語言"),
        ];
        for (id, text) in docs {
            let tokens = tok.tokenize(text);
            idx.index_document(id, &tokens);
        }
        idx
    }

    #[test]
    fn search_english_term() {
        let mut idx = make_index();
        let r = idx.search_term("rust");
        assert_eq!(r.len(), 2);
        let ids: Vec<u64> = r.iter().map(|(id, _)| *id).collect();
        assert!(ids.contains(&1));
        assert!(ids.contains(&4));
    }

    #[test]
    fn search_cjk_term() {
        let mut idx = make_index();
        let r = idx.search_term("資料");
        assert_eq!(r.len(), 2);
        let ids: Vec<u64> = r.iter().map(|(id, _)| *id).collect();
        assert!(ids.contains(&3));
        assert!(ids.contains(&5));
    }

    #[test]
    fn search_and() {
        let mut idx = make_index();
        // "programming" AND "language" 在 doc 1 和 2 同時出現
        let r = idx.search_and(&["programming", "language"]);
        assert_eq!(r.len(), 2);
    }

    #[test]
    fn search_and_no_result() {
        let mut idx = make_index();
        let r = idx.search_and(&["rust", "python"]);
        // 沒有同時包含兩者的文件
        assert_eq!(r.len(), 0);
    }

    #[test]
    fn search_or() {
        let mut idx = make_index();
        let r = idx.search_or(&["rust", "python"]);
        assert_eq!(r.len(), 3); // doc 1, 2, 4
    }

    #[test]
    fn bm25_ordering() {
        let mut idx = make_index();
        // doc 1 出現 "language" 一次，doc 2 也出現一次
        // 但 doc 1 較短，所以 TF 正規化後分數可能略高
        let r = idx.search_term("language");
        assert!(!r.is_empty());
        // 確保有排序（分數遞減）
        for i in 1..r.len() {
            assert!(r[i-1].1 >= r[i].1);
        }
    }

    #[test]
    fn remove_document() {
        let mut idx = make_index();
        idx.remove_document(1);
        let r = idx.search_term("rust");
        // 只剩 doc 4
        assert_eq!(r.len(), 1);
        assert_eq!(r[0].0, 4);
    }

    #[test]
    fn update_document() {
        let tok = Tokenizer::new();
        let mut idx = InvertedIndex::new();
        let tokens = tok.tokenize("hello world");
        idx.index_document(1, &tokens);

        // 更新 doc 1
        let new_tokens = tok.tokenize("hello rust");
        idx.index_document(1, &new_tokens);

        // "world" 不再出現
        assert!(idx.search_term("world").is_empty());
        assert!(!idx.search_term("rust").is_empty());
    }

    #[test]
    fn doc_count() {
        let idx = make_index();
        assert_eq!(idx.doc_count(), 5);
    }

    #[test]
    fn mixed_language_search() {
        let mut idx = make_index();
        // "語言" 在 doc 3? 不在，在 doc 4 和 5
        let r = idx.search_term("語言");
        let ids: Vec<u64> = r.iter().map(|(id, _)| *id).collect();
        assert!(ids.contains(&4) || ids.contains(&5));
    }
}
