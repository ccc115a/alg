# Inverted Index（倒排索引）

## 概述

倒排索引（Inverted Index）是一種常用於全文檢索的核心資料結構。與正向索引（文件 → 詞）不同，倒排索引是從詞到文件的映射，使得關鍵字搜尋可以在 O(1) 或 O(log n) 時間內完成。

倒排索引是搜尋引擎（如 Elasticsearch、Apache Solr）的核心技術，也是資料庫 FTS（Full-Text Search）功能的基礎。

## 正向索引 vs 倒排索引

### 正向索引（Forward Index）

```
文件1: "資料庫系統很有趣"
文件2: "資料庫索引設計"
文件3: "系統程式設計"

正向索引：
文件1 → [資料庫, 系統, 很有趣]
文件2 → [資料庫, 索引, 設計]
文件3 → [系統, 程式, 設計]
```

要搜尋「資料庫」，必須遍歷所有文件。

### 倒排索引（Inverted Index）

```
倒排索引：
"資料庫" → [文件1, 文件2]
"系統"   → [文件1, 文件3]
"索引"   → [文件2]
"設計"   → [文件2, 文件3]
"很有趣" → [文件1]
"程式"   → [文件3]
```

要搜尋「資料庫」，直接查詢倒排索引得到 [文件1, 文件2]。

## 資料結構

### 基本結構

```rust
pub struct InvertedIndex {
    pub dictionary: HashMap<String, PostingList>,
    pub documents: HashMap<DocumentId, Document>,
}

pub struct PostingList {
    pub postings: Vec<Posting>,
}

pub struct Posting {
    pub document_id: DocumentId,
    pub positions: Vec<u32>,  // 詞在文件中出現的位置
    pub term_frequency: u32,
}

pub struct Document {
    pub id: DocumentId,
    pub content: String,
}
```

### 壓縮格式

倒排索引通常需要壓縮以節省空間：

**文件 ID 列表**：
```
原始：[3, 5, 6, 8, 15, 20, 21, 23, 30]
Delta：[3, 2, 1, 2, 7, 5, 1, 2, 7]
Varint：[3, 2, 1, 2, 7, 5, 1, 2, 7]  // 小數字用更少位元組
```

常見壓縮演算法：
- **Varint**：可變長度整數編碼
- **FOR（Frame of Reference）**：區塊壓縮
- **Roaring Bitmap**：混合壓縮格式

## 建構流程

### 1. 文件收集

```rust
let documents = vec![
    Document { id: 1, content: "資料庫系統很有趣" },
    Document { id: 2, content: "資料庫索引設計" },
    Document { id: 3, content: "系統程式設計" },
];
```

### 2. 分詞

```rust
fn tokenize(text: &str, tokenizer: &dyn Tokenizer) -> Vec<String> {
    tokenizer.tokenize(text)
}

// 假設使用簡單的二元分詞
// "資料庫系統很有趣" → ["資料庫", "統系", "很有趣", ...]
```

### 3. 建立倒排列表

```rust
let mut index = InvertedIndex::new();

for doc in documents {
    let tokens = tokenize(&doc.content, &cjk_tokenizer);
    for (pos, term) in tokens.iter().enumerate() {
        index.insert(term, doc.id, pos as u32);
    }
}
```

### 4. 壓縮

```rust
for posting_list in index.dictionary.values_mut() {
    posting_list.compress();
}
```

## 查詢流程

### 單詞查詢

搜尋「資料庫」：

```rust
fn search(&self, query: &str) -> Vec<DocumentId> {
    let tokens = self.tokenizer.tokenize(query);
    
    // 取第一個詞的倒排列表
    if let Some(posting_list) = self.dictionary.get(&tokens[0]) {
        return posting_list.documents();
    }
    
    vec![]
}
```

### AND 查詢

搜尋「資料庫 AND 索引」：

```rust
fn search_and(&self, terms: &[String]) -> Vec<DocumentId> {
    let mut results: Vec<DocumentId> = None;
    
    for term in terms {
        if let Some(posting_list) = self.dictionary.get(term) {
            let docs: HashSet<_> = posting_list.documents().collect();
            results = match results {
                None => Some(docs),
                Some(prev) => Some(prev.intersection(&docs).cloned().collect()),
            };
        } else {
            return vec![];  // 任一詞不存在
        }
    }
    
    results.unwrap_or_default()
}
```

### OR 查詢

搜尋「資料庫 OR 索引」：

```rust
fn search_or(&self, terms: &[String]) -> Vec<DocumentId> {
    let mut results = HashSet::new();
    
    for term in terms {
        if let Some(posting_list) = self.dictionary.get(term) {
            results.extend(posting_list.documents());
        }
    }
    
    results.into_iter().collect()
}
```

## 排序（Ranking）

搜尋結果需要按相關性排序：

### TF-IDF

```rust
fn tf_idf(term: &str, doc_id: DocumentId, index: &InvertedIndex) -> f64 {
    let tf = index.get_tf(term, doc_id);  // 詞頻
    let df = index.get_df(term);          // 文件頻率
    let n = index.total_documents();      // 總文件數
    
    let idf = ((n as f64) / (df as f64)).ln();
    tf * idf
}
```

### BM25

```rust
fn bm25(tf: f64, doc_len: u32, avg_len: f64, df: u64, n: u64) -> f64 {
    let k1 = 1.2;
    let b = 0.75;
    
    let idf = ((n - df + 0.5) / (df + 0.5)).ln();
    let tf_component = (tf * (k1 + 1.0)) / (tf + k1 * (1.0 - b + b * (doc_len as f64 / avg_len)));
    
    idf * tf_component
}
```

## 實務考量

### 記憶體管理

大規模倒排索引需要考慮：
- **壓縮**：減少記憶體佔用
- **分片**：將索引分散到多個機器
- **快取**：熱門查詢結果快取

### 即時更新

新文件加入時需要更新索引：

```rust
fn add_document(&mut self, doc: Document) {
    let tokens = self.tokenize(&doc.content);
    for (pos, term) in tokens.iter().enumerate() {
        self.insert(term, doc.id, pos as u32);
    }
    self.documents.insert(doc.id, doc);
}
```

### 刪除標記

文件刪除時不能立即從索引移除：

```rust
// 使用墓碑標記
struct Posting {
    document_id: DocumentId,
    deleted: bool,
    // ...
}

fn search(&self, term: &str) -> Vec<DocumentId> {
    self.dictionary.get(term)
        .map(|list| list.filter(|p| !p.deleted).map(|p| p.document_id))
        .unwrap_or_default()
}
```

## 知名系統使用倒排索引

| 系統 | 應用場景 |
|------|----------|
| **Elasticsearch** | 全文搜尋、分析 |
| **Apache Solr** | 企業搜尋 |
| **Meilisearch** | 即時搜尋 |
| **SQLite FTS5** | 資料庫全文檢索 |
| **PostgreSQL tsvector** | 全文搜尋 |

## 在 db6 中的實現

db6 的 [FTS 模組](../src/fts/) 使用倒排索引：

```rust
pub struct FtsIndex {
    tokenizer: Box<dyn FtsTokenizer>,
    inverted_index: HashMap<String, Vec<DocumentId>>,
    documents: HashMap<DocumentId, String>,
}

impl FtsIndex {
    pub fn insert(&mut self, doc_id: u64, text: &str) {
        let tokens = self.tokenizer.tokenize(text);
        for token in tokens {
            self.inverted_index
                .entry(token)
                .or_insert_with(Vec::new)
                .push(doc_id);
        }
    }
    
    pub fn search(&self, query: &str) -> Vec<u64> {
        let tokens = self.tokenizer.tokenize(query);
        // AND 查詢：取交集
        let mut result = Vec::new();
        for token in &tokens {
            if let Some(docs) = self.inverted_index.get(token) {
                if result.is_empty() {
                    result = docs.clone();
                } else {
                    result = result.intersection(docs).cloned().collect();
                }
            } else {
                return vec![];
            }
        }
        result
    }
}
```

## 延伸閱讀

- Manning, C. D., Raghavan, P., & Schütze, H. (2008). Introduction to Information Retrieval. Cambridge University Press.
- Zobel, J., & Moffat, A. (2006). Inverted Files for Text Search Engines. ACM Computing Surveys.
- ElasticSearch Guide: https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html