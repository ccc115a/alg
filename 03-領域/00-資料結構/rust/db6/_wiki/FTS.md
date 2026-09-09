# FTS（Full-Text Search，全文檢索）

## 概述

全文檢索（Full-Text Search，簡稱 FTS）是一種在一個或多個文本欄位中搜尋關鍵字的技術，與精確匹配查詢不同，全文檢索需要理解文本的語意、處理分詞、計算相關性排序。

傳統的 SQL WHERE 子句只能做精確匹配或前綴匹配：
```sql
-- 精確匹配
SELECT * FROM articles WHERE title = 'database';

-- 前綴匹配（通常不使用索引）
SELECT * FROM articles WHERE title LIKE 'data%';
```

全文檢索可以找到包含「database」的文章，即使標題是「Introduction to Database Systems」：
```sql
-- 全文檢索
SELECT * FROM articles WHERE MATCH(title) AGAINST('database');
```

## 全文檢索的組成部分

### 1. 分詞器（Tokenizer）

分詞是將文本拆分為詞（term/token）的過程。不同語言需要不同的分詞策略：

**英文分詞**：
```
"Database systems are fascinating!"
→ ["database", "systems", "are", "fascinating"]
```

**中文分詞（日語、韓語類似）**：
```
"資料庫系統很有趣"
→ ["資料庫", "資料", "庫系", "系統"]  (結巴分詞的不同模式)
或者
→ ["資料庫", "系統"]  (精確模式)
```

常見分詞器：
- **英文**：Porter Stemmer、Lancaster Stemmer
- **中文**：結巴分詞、IK Analyzer
- **日文**：Mecab、Kuromoji

詳細說明請參閱 [Tokenizer.md](Tokenizer.md)。

### 2. 倒排索引（Inverted Index）

倒排索引是全文檢索的核心資料結構：

**正向索引（Document → Terms）**：
```
文件1: "Database systems are fast"
文件2: "Database systems are powerful"
文件3: "Machine learning is powerful"
```

**倒排索引（Term → Documents）**：
```
"database"  → [文件1, 文件2]
"systems"  → [文件1, 文件2]
"are"      → [文件1, 文件2]
"fast"     → [文件1]
"powerful" → [文件2, 文件3]
"machine"  → [文件3]
"learning" → [文件3]
```

### 3. 相關性排序（Ranking）

搜尋結果需要按相關性排序，常用演算法：

**TF-IDF（詞頻-逆文檔頻率）**：
```
TF-IDF(term, doc) = TF(term, doc) × IDF(term)

TF = 文檔中 term 出現的次數
IDF = log(總文檔數 / 包含 term 的文檔數)
```

**BM25**：TF-IDF 的改良版，是 Lucene、Elasticsearch 等系統的核心排序演算法。

## 全文檢索的 SQL 語法

### SQLite FTS5

```sql
-- 建立 FTS5 虛擬表
CREATE VIRTUAL TABLE articles_fts USING fts5(
    title,
    content,
    content='articles'  -- 關聯到實際表
);

-- 全文檢索查詢
SELECT * FROM articles_fts WHERE title MATCH 'database';

-- 布林查詢
SELECT * FROM articles_fts WHERE articles_fts MATCH '"database systems" AND sqlite';

-- 前綴查詢
SELECT * FROM articles_fts WHERE articles_fts MATCH 'datab*';
```

### PostgreSQL 全文檢索

```sql
-- 啟用擴展
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- 使用 tsvector 和 tsquery
SELECT * FROM articles
WHERE to_tsvector('english', title) @@ to_tsquery('english', 'database');
```

### MySQL 全文檢索

```sql
-- 建立全文索引
ALTER TABLE articles ADD FULLTEXT(title, content);

-- 全文檢索
SELECT * FROM articles
WHERE MATCH(title, content) AGAINST('database' IN NATURAL LANGUAGE MODE);

-- 布林模式
SELECT * FROM articles
WHERE MATCH(title, content) AGAINST('+database -sqlite' IN BOOLEAN MODE);
```

## 倒排索引的實作

倒排索引的典型結構：

```rust
struct InvertedIndex {
    // 詞典：詞 → 詞資訊（文件頻率、指標等）
    dictionary: HashMap<String, TermInfo>,
    // 倒排列表：詞 → [文件 ID, 位置, ...]
    postings: Vec<PostingList>,
}

struct TermInfo {
    doc_freq: u64,      // 包含該詞的文件數
    posting_list_id: u64,
}

struct PostingList {
    doc_ids: Vec<u64>,
    positions: Vec<u64>,  // 可選：位置資訊
}
```

### 索引建構流程

1. **文件收集**：讀取要索引的文件
2. **分詞**：使用分詞器將文本拆分為詞
3. **停用詞過濾**：移除常見詞（the, is, a 等）
4. **詞形還原**：將詞還原為詞根（running → run）
5. **建立倒排索引**：更新詞典和倒排列表
6. **壓縮**：壓縮倒排列表以節省空間

## 相關性計算的細節

### TF-IDF 公式

```rust
fn tf_idf(tf: f64, df: u64, n: u64) -> f64 {
    let idf = (n as f64 / df as f64).ln();
    tf * idf
}
```

### BM25 公式

```rust
fn bm25(tf: f64, doc_len: u64, avg_len: f64, df: u64, n: u64, k1: f64, b: f64) -> f64 {
    let idf = ((n - df + 0.5) / (df + 0.5)).ln();
    let tf_component = (tf * (k1 + 1.0)) / (tf + k1 * (1.0 - b + b * (doc_len as f64 / avg_len)));
    idf * tf_component
}
```

其中：
- `k1`：詞頻飽和參數（通常 1.2-2.0）
- `b`：文件長度正規化參數（通常 0.75）

## 搜尋引擎與資料庫的 FTS

### Elasticsearch / Solr

基於 Lucene 的搜尋引擎：
- 分散式架構
- 豐富的查詢 DSL
- 即時索引更新

### Meilisearch

新興的搜尋引擎：
- 簡單易用
- 高度相關的預設排序
- 支援中文分詞

### 資料庫內建 FTS

- **PostgreSQL**：pg_trgm + 全文檢索
- **MySQL**： InnoDB FTS（在 5.7+ 版本）
- **SQLite**：FTS5 虛擬表

## 在 db6 中的 FTS

db6 的 [FTS 模組](../src/fts/) 實作了全文檢索功能：

```rust
pub struct FtsIndex {
    tokenizer: Box<dyn FtsTokenizer>,
    inverted_index: HashMap<String, Vec<DocumentId>>,
}
```

支援的功能：
- **多種分詞器**：CjkTokenizer（中文/日文/韓文）、EnglishTokenizer（英文）
- **布林查詢**：AND、OR、NOT
- **前綴匹配**：如 `datab*` 匹配 database、datacenter
- **BM25 排序**：根據相關性排序結果

詳細實作說明，請參考 [Tokenizer.md](Tokenizer.md)。

## 全文檢索的限制與最佳化

### 限制

1. **即時性**：大文件時，索引更新延遲
2. **記憶體**：倒排索引可能很大
3. **語言支援**：中文等語言的分詞難題

### 最佳化策略

1. **增量索引**：只索引變更的內容
2. **壓縮**：使用 FOR 編碼、Frame of Reference 等技術
3. **快取**：快取熱門查詢結果
4. **副本**：使用搜尋引擎處理讀取，資料庫處理寫入

## 延伸閱讀

- Manning, C. D., Raghavan, P., & Schütze, H. (2008). Introduction to Information Retrieval. Cambridge University Press.
- Zobel, J., & Moffat, A. (2006). Inverted Files for Text Search Engines. ACM Computing Surveys.
- Elasticsearch Guide: https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html