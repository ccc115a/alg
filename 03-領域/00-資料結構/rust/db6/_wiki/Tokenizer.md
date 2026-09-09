# Tokenizer（分詞器）

## 概述

分詞器（Tokenizer）是將文本拆分為有意義的語言單元（稱為「詞」或「語素」）的程式元件。在資訊檢索、自然語言處理、資料庫全文檢索等領域，分詞是進行文字分析的基礎步驟。

分詞的品質直接影響全文檢索的效果：
- **粒度太粗**：如「資料庫系統」不分詞，搜尋「資料庫」會失敗
- **粒度太細**：如每個字分開，會產生大量噪音

## 分詞的難題

不同語言的分詞難度差異很大：

### 英文分詞

英文相對簡單，因為單詞之間有空格分隔：

```
Input:  "Database systems are important!"
Output: ["database", "systems", "are", "important"]
```

基本步驟：
1. 轉換為小寫
2. 移除標點符號
3. 分離單詞
4. 詞形還原（stemming）：running → run

### 中文分詞

中文沒有明確的分詞邊界，是最困難的分詞任務之一：

```
Input:  "資料庫系統很重要"
Possible segmentations:
- ["資料庫", "系統", "很重要"]
- ["資料", "庫系統", "很", "重要"]
- ["資料", "庫", "系統", "很", "重要"]
```

需要使用統計模型或字典來確定正確的分詞方式。

### 日文分詞

日文同時使用：
- 空格分隔的單詞（但使用全形空白）
- 三種字母系統：平假名、片假名、漢字

```
Input:  "データベースシステム"
Output: ["データベース", "システム"]  (片假名)
```

### 韓文分詞

韓文類似中文，也是無空格的書寫系統。

## 分詞器的主要步驟

### 1. 字符正規化（Character Normalization）

```python
def normalize(text):
    # 全形轉半形
    text = str.maketrans('ＡＢＣＤ', 'ABCD').translate(text)
    
    # 大寫轉小寫
    text = text.lower()
    
    # 移除重音符號
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    
    return text
```

### 2. 字符過濾（Character Filtering）

移除或替換不需要處理的字符：

```python
def filter_chars(text):
    # 移除數字
    text = re.sub(r'\d+', '', text)
    
    # 替換標點為空格
    text = re.sub(r'[^\w\s]', ' ', text)
    
    return text
```

### 3. 斷句（Sentence Segmentation）

將長文本分割為句子：

```python
def segment_sentences(text):
    # 使用句號、問號、感嘆號分割
    sentences = re.split(r'[。！？\.\!\?]', text)
    return [s for s in sentences if s.strip()]
```

### 4. 分詞（Word Tokenization）

核心步驟，根據語言特性分詞。

### 5. 停用詞移除（Stopword Removal）

移除高頻但無意義的詞：

```python
stopwords = {'的', '是', '在', '了', '和', 'the', 'is', 'at', 'which'}

def remove_stopwords(tokens):
    return [t for t in tokens if t not in stopwords]
```

### 6. 詞形還原（Stemming / Lemmatization）

**Stemming（詞根提取）**：暴力移除詞尾：
```
running → run
 databases → databas
```

**Lemmatization（詞形還原）**：基於詞典的規範化：
```
running → run
 databases → database
```

## 英文分詞器

### Porter Stemmer

最經典的英文詞幹提取演算法：

```python
import nltk
stemmer = nltk.PorterStemmer()
print(stemmer.stem("running"))  # run
print(stemmer.stem("databases"))  # databas
```

### Lancaster Stemmer

比 Porter 更激進：

```python
stemmer = nltk.LancasterStemmer()
print(stemmer.stem("running"))  # run
print(stemmer.stem("databases"))  # databas
```

## 中文分詞器

### 結巴分詞（Jieba）

最受歡迎的中文分詞 Python 庫：

```python
import jieba

# 精確模式
print(list(jieba.cut("資料庫系統很重要")))
# ['資料庫', '系統', '很', '重要']

# 全模式（所有可能的詞）
print(list(jieba.cut("資料庫系統很重要", cut_all=True)))
# ['資料', '資料庫', '庫系', '系統', '很', '重要']

# 搜尋引擎模式（適合搜尋）
print(list(jieba.cut_for_search("資料庫系統很重要")))
# ['資料', '資料庫', '庫系', '系統', '很', '重要']
```

### 演算法原理

結巴分詞使用：
1. **前綴字典**：Trie 樹結構
2. **HMM 模型**：處理未登錄詞
3. **DAG**：構建所有可能的分詞圖
4. **最短路徑**：選擇最短的分詞路徑

## 日文分詞器

### MeCab

最流行的日文分詞器：

```python
import fugashi

tagger = fugashi.Tagger()
text = "データベースシステム"
result = tagger.parse(text)
# [ ('データベース', 名詞), ('システム', 名詞) ]
```

### Kuromoji

Java/Node.js 的日文分詞器：

```python
import kuromoji

tokenizer = kuromoji.builder().build()
tokens = tokenizer.tokenize("データベースシステム")
for token in tokens:
    print(token.surface)  # 原始文字
    print(token.reading)  # 讀音
```

## 在 db6 中的分詞器

db6 的 [FTS 模組](../src/fts/) 實作了分詞器：

```rust
pub trait FtsTokenizer: Send + Sync {
    fn tokenize(&self, text: &str) -> Vec<String>;
}
```

### CjkTokenizer

用於中日韓文字的分詞器，採用簡單的二元分詞（bigram）策略：

```rust
pub struct CjkTokenizer;

impl FtsTokenizer for CjkTokenizer {
    fn tokenize(&self, text: &str) -> Vec<String> {
        let mut tokens = Vec::new();
        let chars: Vec<char> = text.chars().collect();
        
        // 滑動視窗大小為 2
        for window in chars.windows(2) {
            let token: String = window.iter().collect();
            tokens.push(token);
        }
        
        tokens
    }
}
```

輸入：「資料庫」
輸出：["資料", "料庫"]

### EnglishTokenizer

用於英文的分詞器：

```rust
pub struct EnglishTokenizer;

impl FtsTokenizer for EnglishTokenizer {
    fn tokenize(&self, text: &str) -> Vec<String> {
        // 1. 轉小寫
        // 2. 移除非字母字符
        // 3. 分詞
        // 4. Porter Stemming
        let text = text.to_lowercase();
        let re = Regex::new(r"[a-z]+").unwrap();
        
        let mut tokens = Vec::new();
        for mat in re.find_iter(&text) {
            let word = stem(&mat.as_str().to_string());
            tokens.push(word);
        }
        
        tokens
    }
}
```

## N-gram 模型

除了詞式分詞，還有基於 N-gram 的方法：

| N | 名稱 | 範例 | 用途 |
|---|------|------|------|
| 1 | Unigram | ["資", "料", "庫"] | 單字 |
| 2 | Bigram | ["資料", "料庫"] | 常用於中文 FTS |
| 3 | Trigram | ["資料庫"] | 精確匹配 |

### Bigram 的優缺點

優點：
- 簡單，無需詞典
- 處理 OOV（未登錄詞）能力強

缺點：
- 索引佔用空間大
- 搜尋精確度較低

## 分詞器的評估指標

| 指標 | 說明 |
|------|------|
| Precision | 分出的詞中正確的比例 |
| Recall | 應該分出的詞中被分出的比例 |
| F1 Score | Precision 和 Recall 的調和平均 |

## 選擇分詞器的考量

1. **語言支援**：中文、日文、英文需要不同的分詞器
2. **效能**：分詞速度影響索引建構時間
3. **準確度**：根據應用場景選擇精確模式或全模式
4. **索引大小**：二元分詞會產生更大的索引

## 延伸閱讀

- "Foundation of Statistical Natural Language Processing" by Manning and Schütze
- Jieba GitHub: https://github.com/fxsjy/jieba
- Lucene Analysis: https://lucene.apache.org/core/9_5_0/core/org/apache/lucene/analysis/package-summary.html