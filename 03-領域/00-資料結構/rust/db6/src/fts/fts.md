# fts/mod.rs — 全文搜尋 (FTS)

## 理論基礎：倒排索引

**倒排索引 (inverted index)** 是全文搜尋的核心資料結構。與傳統的正向索引（文件 → 詞彙）相反，倒排索引記錄的是 **詞彙 → 文件** 的映射。

### 範例

文件 1: "Rust is fast"
文件 2: "Rust is safe"

```
倒排索引：
"rust" → [doc1, doc2]
"fast" → [doc1]
"safe" → [doc2]
```

## 架構

FTS 索引建構在 `StorageEngine` 之上，使用預留的 `FTS_TABLE_ID = 255` 儲存索引資料：

```
FTS_TABLE_ID (255)
├── term:{term} → [doc_id1, doc_id2, ...]    // 倒排列表
├── doc:{doc_id}:{term} → count              // 詞頻
├── doc_len:{doc_id} → total_terms           // 文件長度
└── next_doc_id → current_max               // ID 計數器
```

## FtsTokenizer Trait

### CjkTokenizer

專為 CJK (中日韓) 文字設計，使用 **bigram (二元分詞)**：將連續的兩個字元作為一個詞彙。

```
"資料庫" → ["資料", "料庫"]
```

### EnglishTokenizer

英文分詞：轉小寫後按空白分割。

```
"Hello World" → ["hello", "world"]
```

## 搜尋類型

| 類型 | 語法 | 實作方式 |
|------|------|---------|
| 基本 | `"query"` | 直接查詢倒排索引 |
| AND | `"a AND b"` | 取兩組 doc_id 的交集 |
| OR | `"a OR b"` | 取兩組 doc_id 的聯集 |
| NOT | `"a NOT b"` | 從 a 的結果減去 b 的結果 |
| 前綴 | `"pre*"` | 掃描符合前綴的 term |

## BM25 評分

**BM25 (Best Matching 25)** 是現代資訊檢索中最廣泛使用的相關性評分函數：

```
BM25(doc, query) = Σ IDF(term) × TF(term, doc) × (k1 + 1) / (TF + k1 × (1 - b + b × doc_len / avg_doc_len))
```

參數：
- `k1 = 1.5` — 詞頻飽和參數
- `b = 0.75` — 文件長度正規化參數

## 相關資源

- `engine/mod.md` — StorageEngine 介面
- `sql/parser/ast.md` — FTS 的 MATCH 子句
