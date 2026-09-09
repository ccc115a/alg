use std::fs;

const CORPUS_PATH: &str = "data/corpus.txt";

#[test]
fn test_corpus_exists() {
    let content = fs::read_to_string(CORPUS_PATH)
        .expect("corpus.txt 應該存在");
    let lines: Vec<&str> = content.lines().collect();
    assert_eq!(lines.len(), 100, "corpus.txt 應該有 100 行");
}

#[test]
fn test_corpus_non_empty_lines() {
    let content = fs::read_to_string(CORPUS_PATH).unwrap();
    for (i, line) in content.lines().enumerate() {
        assert!(!line.trim().is_empty(), "第 {} 行不應為空白", i + 1);
        assert!(line.chars().any(|c| c.is_alphabetic()), "第 {} 行應包含文字", i + 1);
    }
}

#[test]
fn test_build_index_from_corpus() {
    let content = fs::read_to_string(CORPUS_PATH).unwrap();
    let lines: Vec<String> = content.lines().map(|s| s.to_string()).collect();
    let idx = fts::Index::build(&lines);

    assert_eq!(idx.doc_count(), 100);
    assert!(idx.term_count() > 0, "索引應包含詞項");
}

#[test]
fn test_search_chinese_bigram() {
    let content = fs::read_to_string(CORPUS_PATH).unwrap();
    let lines: Vec<String> = content.lines().map(|s| s.to_string()).collect();
    let idx = fts::Index::build(&lines);

    // "人工智慧" appears at least in lines 2, 3, 23
    let results = idx.search("人工智慧", fts::SearchMode::Or);
    assert!(!results.is_empty(), "搜尋「人工智慧」應有結果");
    assert!(results.len() >= 2, "至少應有 2 筆結果");

    let line = results[0].line.clone();
    assert!(line.contains("人工智慧"), "結果應包含「人工智慧」");
}

#[test]
fn test_search_ascii_term() {
    let content = fs::read_to_string(CORPUS_PATH).unwrap();
    let lines: Vec<String> = content.lines().map(|s| s.to_string()).collect();
    let idx = fts::Index::build(&lines);

    // CRISPR appears in gene editing line
    let results = idx.search("CRISPR", fts::SearchMode::Or);
    assert!(!results.is_empty());
    let has_gene = results.iter().any(|r| r.line.contains("基因"));
    assert!(has_gene, "CRISPR 搜尋結果應與基因相關");
}

#[test]
fn test_search_case_insensitive() {
    let content = fs::read_to_string(CORPUS_PATH).unwrap();
    let lines: Vec<String> = content.lines().map(|s| s.to_string()).collect();
    let idx = fts::Index::build(&lines);

    let r1 = idx.search("docker", fts::SearchMode::Or);
    let r2 = idx.search("Docker", fts::SearchMode::Or);
    assert_eq!(r1.len(), r2.len(), "大小寫搜尋結果應相同");
}

#[test]
fn test_search_and_mode() {
    let content = fs::read_to_string(CORPUS_PATH).unwrap();
    let lines: Vec<String> = content.lines().map(|s| s.to_string()).collect();
    let idx = fts::Index::build(&lines);

    // "區塊鏈 金融" should only match lines containing both terms
    let results = idx.search("區塊鏈 金融", fts::SearchMode::And);
    assert!(!results.is_empty(), "AND 搜尋應有結果");
    for r in &results {
        assert!(r.line.contains("區塊鏈"), "結果應包含「區塊鏈」");
        assert!(r.line.contains("金融"), "結果應包含「金融」");
    }
}

#[test]
fn test_search_non_existent() {
    let content = fs::read_to_string(CORPUS_PATH).unwrap();
    let lines: Vec<String> = content.lines().map(|s| s.to_string()).collect();
    let idx = fts::Index::build(&lines);

    let results = idx.search("xzxyzwqwerty", fts::SearchMode::Or);
    assert!(results.is_empty(), "不存在的詞彙應回傳空結果");
}

#[test]
fn test_relevance_scoring() {
    let content = fs::read_to_string(CORPUS_PATH).unwrap();
    let lines: Vec<String> = content.lines().map(|s| s.to_string()).collect();
    let idx = fts::Index::build(&lines);

    let results = idx.search("機器學習 深度學習 人工智慧", fts::SearchMode::Or);
    assert!(!results.is_empty());

    // score should be non-increasing
    for w in results.windows(2) {
        assert!(
            w[0].score >= w[1].score,
            "分數應遞減排序: {} ({}) >= {} ({})",
            w[0].doc_id, w[0].score, w[1].doc_id, w[1].score
        );
    }
}

#[test]
fn test_search_order_stability() {
    let content = fs::read_to_string(CORPUS_PATH).unwrap();
    let lines: Vec<String> = content.lines().map(|s| s.to_string()).collect();
    let idx = fts::Index::build(&lines);

    let r1 = idx.search("區塊鏈", fts::SearchMode::Or);
    let r2 = idx.search("區塊鏈", fts::SearchMode::Or);
    assert_eq!(r1.len(), r2.len());
    for (a, b) in r1.iter().zip(r2.iter()) {
        assert_eq!(a.doc_id, b.doc_id);
    }
}

#[test]
fn test_add_doc_incremental() {
    let mut idx = fts::Index::new();
    assert_eq!(idx.doc_count(), 0);
    idx.add_doc("測試第一句");
    assert_eq!(idx.doc_count(), 1);
    idx.add_doc("測試第二句關於機器學習");
    assert_eq!(idx.doc_count(), 2);

    let results = idx.search("機器學習", fts::SearchMode::Or);
    assert_eq!(results.len(), 1);
    assert_eq!(results[0].doc_id, 1);
}

#[test]
fn test_search_with_numbers() {
    let content = fs::read_to_string(CORPUS_PATH).unwrap();
    let lines: Vec<String> = content.lines().map(|s| s.to_string()).collect();
    let idx = fts::Index::build(&lines);

    let results = idx.search("5G", fts::SearchMode::Or);
    assert!(!results.is_empty());
    let has_5g = results.iter().any(|r| r.line.contains("5G"));
    assert!(has_5g, "應找到含 5G 的結果");
}

#[test]
fn test_multiple_terms_or() {
    let content = fs::read_to_string(CORPUS_PATH).unwrap();
    let lines: Vec<String> = content.lines().map(|s| s.to_string()).collect();
    let idx = fts::Index::build(&lines);

    let results = idx.search("咖啡 茶 啤酒", fts::SearchMode::Or);
    assert!(!results.is_empty());
}

#[test]
fn test_debug_index_properties() {
    let content = fs::read_to_string(CORPUS_PATH).unwrap();
    let lines: Vec<String> = content.lines().map(|s| s.to_string()).collect();
    let idx = fts::Index::build(&lines);

    assert!(idx.doc_count() > 0);
    assert!(idx.term_count() > 0);
    assert!(idx.term_count() < 10000, "詞項數量應合理");

    // verify all docs accessible
    for i in 0..idx.doc_count() {
        assert!(idx.get_doc(i).is_some(), "文件 {} 應可存取", i);
    }
    assert!(idx.get_doc(999).is_none(), "超出範圍應回傳 None");
}
