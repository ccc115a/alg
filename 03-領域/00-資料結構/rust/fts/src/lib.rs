use std::collections::HashMap;

/// A CJK-aware tokenizer that produces bigrams for Chinese characters
/// and preserves ASCII alphanumeric tokens.
pub fn tokenize(text: &str) -> Vec<String> {
    let mut tokens = Vec::new();
    let mut buf = String::new();
    let mut run_is_ascii = false;

    for ch in text.chars() {
        if ch.is_ascii_alphanumeric() || ch == '_' || ch == '.' || ch == '+' || ch == '-' {
            if !run_is_ascii && !buf.is_empty() {
                tokens.extend(cjk_bigrams(&buf));
                buf.clear();
            }
            run_is_ascii = true;
            buf.push(ch);
        } else if is_cjk(ch) {
            if run_is_ascii && !buf.is_empty() {
                tokens.push(buf.clone().to_lowercase());
                buf.clear();
            }
            run_is_ascii = false;
            buf.push(ch);
        } else {
            if !buf.is_empty() {
                if run_is_ascii {
                    tokens.push(buf.clone().to_lowercase());
                } else {
                    tokens.extend(cjk_bigrams(&buf));
                }
                buf.clear();
            }
        }
    }
    if !buf.is_empty() {
        if run_is_ascii {
            tokens.push(buf.clone().to_lowercase());
        } else {
            tokens.extend(cjk_bigrams(&buf));
        }
    }

    tokens
}

fn cjk_bigrams(s: &str) -> Vec<String> {
    let chars: Vec<char> = s.chars().collect();
    let mut result = Vec::new();
    if chars.len() == 1 {
        result.push(chars[0].to_string());
    } else {
        for i in 0..chars.len() - 1 {
            let bigram: String = chars[i..=i + 1].iter().collect();
            result.push(bigram);
        }
    }
    result
}

fn is_cjk(ch: char) -> bool {
    matches!(ch,
        '\u{4E00}'..='\u{9FFF}' |
        '\u{3400}'..='\u{4DBF}' |
        '\u{F900}'..='\u{FAFF}' |
        '\u{2F800}'..='\u{2FA1F}'
    )
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum SearchMode {
    And,
    Or,
}

#[derive(Debug, Clone)]
pub struct SearchResult {
    pub doc_id: usize,
    pub line: String,
    pub score: f64,
}

pub struct Index {
    inverted: HashMap<String, Vec<usize>>,
    docs: Vec<String>,
}

impl Index {
    pub fn new() -> Self {
        Index {
            inverted: HashMap::new(),
            docs: Vec::new(),
        }
    }

    pub fn build(lines: &[impl AsRef<str>]) -> Self {
        let mut idx = Index::new();
        for line in lines {
            idx.add_doc(line.as_ref());
        }
        idx
    }

    pub fn add_doc(&mut self, line: &str) {
        let doc_id = self.docs.len();
        self.docs.push(line.to_string());
        let terms = tokenize(line);
        let mut seen = std::collections::HashSet::new();
        for term in terms {
            if seen.insert(term.clone()) {
                self.inverted.entry(term).or_default().push(doc_id);
            }
        }
    }

    pub fn search(&self, query: &str, mode: SearchMode) -> Vec<SearchResult> {
        let query_terms = tokenize(query);
        if query_terms.is_empty() {
            return Vec::new();
        }

        let mut doc_scores: HashMap<usize, f64> = HashMap::new();
        let mut doc_term_count: HashMap<usize, usize> = HashMap::new();

        for term in &query_terms {
            if let Some(postings) = self.inverted.get(term) {
                for &doc_id in postings {
                    *doc_scores.entry(doc_id).or_insert(0.0) += 1.0;
                    *doc_term_count.entry(doc_id).or_insert(0) += 1;
                }
            }
        }

        let total_terms = query_terms.len() as f64;
        let mut results: Vec<SearchResult> = match mode {
            SearchMode::And => {
                let threshold = query_terms.len();
                doc_scores
                    .into_iter()
                    .filter(|(doc_id, _)| doc_term_count.get(doc_id).copied().unwrap_or(0) == threshold)
                    .map(|(doc_id, score)| SearchResult {
                        doc_id,
                        line: self.docs[doc_id].clone(),
                        score: score / total_terms,
                    })
                    .collect()
            }
            SearchMode::Or => {
                doc_scores
                    .into_iter()
                    .map(|(doc_id, score)| SearchResult {
                        doc_id,
                        line: self.docs[doc_id].clone(),
                        score: score / total_terms,
                    })
                    .collect()
            }
        };

        results.sort_by(|a, b| {
            b.score
                .partial_cmp(&a.score)
                .unwrap()
                .then_with(|| a.doc_id.cmp(&b.doc_id))
        });
        results
    }

    pub fn doc_count(&self) -> usize {
        self.docs.len()
    }

    pub fn term_count(&self) -> usize {
        self.inverted.len()
    }

    pub fn get_doc(&self, id: usize) -> Option<&str> {
        self.docs.get(id).map(|s| s.as_str())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    // --- tokenizer tests ---

    #[test]
    fn test_tokenize_ascii() {
        let tokens = tokenize("hello world");
        assert_eq!(tokens, vec!["hello", "world"]);
    }

    #[test]
    fn test_tokenize_cjk_bigram() {
        let tokens = tokenize("人工智慧");
        assert_eq!(tokens, vec!["人工", "工智", "智慧"]);
    }

    #[test]
    fn test_tokenize_cjk_short() {
        let tokens = tokenize("人");
        assert_eq!(tokens, vec!["人"]);
    }

    #[test]
    fn test_tokenize_two_chars() {
        let tokens = tokenize("人工");
        assert_eq!(tokens, vec!["人工"]);
    }

    #[test]
    fn test_tokenize_mixed() {
        let tokens = tokenize("AI 人工智慧");
        assert_eq!(tokens, vec!["ai", "人工", "工智", "智慧"]);
    }

    #[test]
    fn test_tokenize_case_insensitive() {
        let tokens = tokenize("Hello World");
        assert_eq!(tokens, vec!["hello", "world"]);
    }

    #[test]
    fn test_tokenize_punctuation() {
        let tokens = tokenize("人工智慧，機器學習！");
        assert_eq!(tokens, vec!["人工", "工智", "智慧", "機器", "器學", "學習"]);
    }

    #[test]
    fn test_tokenize_empty() {
        let tokens = tokenize("");
        assert!(tokens.is_empty());
    }

    #[test]
    fn test_tokenize_english_only() {
        let tokens = tokenize("full text search engine");
        assert_eq!(tokens, vec!["full", "text", "search", "engine"]);
    }

    #[test]
    fn test_tokenize_english_with_hyphen() {
        let tokens = tokenize("state-of-the-art");
        assert_eq!(tokens, vec!["state-of-the-art"]);
    }

    #[test]
    fn test_tokenize_english_with_numbers() {
        let tokens = tokenize("CJK 2.0 FTS");
        assert_eq!(tokens, vec!["cjk", "2.0", "fts"]);
    }

    #[test]
    fn test_tokenize_cjk_no_cross_boundary() {
        let tokens = tokenize("智慧 機器");
        assert_eq!(tokens, vec!["智慧", "機器"]);
    }

    // --- index tests ---

    fn test_corpus() -> Vec<String> {
        vec![
            "機器學習是人工智慧的重要分支".to_string(),
            "台北的夜市有許多美味的小吃".to_string(),
            "人工智慧醫療輔助系統能幫助醫生做診斷".to_string(),
            "深度學習是機器學習的一個子領域".to_string(),
            "今天天氣真好".to_string(),
        ]
    }

    #[test]
    fn test_search_or() {
        let corpus = test_corpus();
        let idx = Index::build(&corpus);
        let results = idx.search("人工智慧", SearchMode::Or);
        assert!(!results.is_empty());
        let ids: Vec<usize> = results.iter().map(|r| r.doc_id).collect();
        assert!(ids.contains(&0));
        assert!(ids.contains(&2));
    }

    #[test]
    fn test_search_and() {
        let corpus = test_corpus();
        let idx = Index::build(&corpus);
        let results = idx.search("人工智慧 機器學習", SearchMode::And);
        assert_eq!(results.len(), 1);
        assert_eq!(results[0].doc_id, 0);
    }

    #[test]
    fn test_search_no_match() {
        let corpus = test_corpus();
        let idx = Index::build(&corpus);
        let results = idx.search("不存在", SearchMode::Or);
        assert!(results.is_empty());
    }

    #[test]
    fn test_search_english_in_cjk_corpus() {
        let corpus = vec!["machine learning is ai".to_string()];
        let idx = Index::build(&corpus);
        let results = idx.search("machine", SearchMode::Or);
        assert_eq!(results.len(), 1);
        assert_eq!(results[0].doc_id, 0);
    }

    #[test]
    fn test_term_count() {
        let corpus = test_corpus();
        let idx = Index::build(&corpus);
        assert!(idx.term_count() > 0);
    }

    #[test]
    fn test_get_doc() {
        let corpus = test_corpus();
        let idx = Index::build(&corpus);
        assert_eq!(idx.get_doc(0), Some("機器學習是人工智慧的重要分支"));
        assert_eq!(idx.get_doc(99), None);
    }

    #[test]
    fn test_empty_corpus() {
        let corpus: Vec<String> = vec![];
        let idx = Index::build(&corpus);
        assert_eq!(idx.doc_count(), 0);
        assert_eq!(idx.term_count(), 0);
        let results = idx.search("test", SearchMode::Or);
        assert!(results.is_empty());
    }

    #[test]
    fn test_add_doc_incremental() {
        let mut idx = Index::new();
        assert_eq!(idx.doc_count(), 0);
        idx.add_doc("第一句測試");
        assert_eq!(idx.doc_count(), 1);
        idx.add_doc("第二句測試");
        assert_eq!(idx.doc_count(), 2);
    }

    #[test]
    fn test_search_scoring() {
        let corpus = vec![
            "人工智慧與機器學習".to_string(),
            "人工智慧".to_string(),
        ];
        let idx = Index::build(&corpus);
        let results = idx.search("人工智慧 機器學習", SearchMode::Or);
        assert_eq!(results.len(), 2);
        assert!(results[0].score >= results[1].score);
    }

    #[test]
    fn test_search_english_scoring() {
        let corpus = vec![
            "machine learning deep learning".to_string(),
            "machine learning".to_string(),
        ];
        let idx = Index::build(&corpus);
        let results = idx.search("machine learning", SearchMode::Or);
        assert_eq!(results.len(), 2);
        assert!(results[0].score >= results[1].score);
    }

    #[test]
    fn test_search_and_english() {
        let corpus = vec![
            "machine learning is fun".to_string(),
            "machine only".to_string(),
        ];
        let idx = Index::build(&corpus);
        let results = idx.search("machine learning", SearchMode::And);
        assert_eq!(results.len(), 1);
        assert_eq!(results[0].doc_id, 0);
    }
}
