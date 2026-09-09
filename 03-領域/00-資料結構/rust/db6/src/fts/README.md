# fts/ — 全文搜尋 (Full-Text Search)

## 概覽

建構在 StorageEngine 之上的倒排索引系統，支援 CJK（中日韓）與英文全文搜尋。

## 模組列表

| 檔案 | 說明 |
|------|------|
| `mod.rs` | FtsIndex、FtsTokenizer trait、CjkTokenizer、EnglishTokenizer |

## 核心原理

**倒排索引 (inverted index)** 將詞彙映射到包含該詞的文件列表：

```
"rust" → [doc1, doc2]
"fast" → [doc1]
```

內部使用 `FTS_TABLE_ID = 255` 作為 KV 儲存空間。

## 搜尋語法

| 語法 | 說明 |
|------|------|
| `query` | 基本查詢 (OR 合併所有詞) |
| `a AND b` | 結果交集 |
| `a OR b` | 結果聯集 |
| `a NOT b` | 減法 |
| `pre*` | 前綴匹配 |

## BM25 評分

相關性排序使用 BM25 演算法，參數 `k1=1.5`、`b=0.75`。

## 相關連結

- `fts.md` — 全文搜尋架構詳解
- `engine/README.md` — 儲存引擎層
- `sql/parser/ast.md` — MATCH 子句語法
