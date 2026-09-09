//! Tokenizer：將文字切成 token 串
//!
//! 策略：
//!   - 英語 / 拉丁文：以空白與標點切詞，轉小寫，去除空 token
//!   - CJK（中日韓）字元：bigram（連續兩字組成一個 token）
//!   - 混合文字：先切出英文詞，再對 CJK 段落做 bigram
//!   - Unicode 正規化：NFKC（全形→半形、大寫→小寫）
//!
//! 範例：
//!   "Hello World"  → ["hello", "world"]
//!   "資料庫"       → ["資料", "料庫"]
//!   "SQL 資料庫"   → ["sql", "資料", "料庫"]

/// 一個切出的 token 及其在原文的位置
#[derive(Debug, Clone, PartialEq)]
pub struct Token {
    pub term:   String,  // 正規化後的 token 文字
    pub offset: usize,   // 在原始字元序列的起始 char index
}

// ── 字元分類 ─────────────────────────────────────────────────────────────

fn is_cjk(c: char) -> bool {
    matches!(c,
        '\u{4E00}'..='\u{9FFF}'   |  // CJK 統一表意文字
        '\u{3400}'..='\u{4DBF}'   |  // CJK 擴充 A
        '\u{20000}'..='\u{2A6DF}' |  // CJK 擴充 B
        '\u{F900}'..='\u{FAFF}'   |  // CJK 相容
        '\u{2E80}'..='\u{2EFF}'   |  // CJK 部首補充
        '\u{3040}'..='\u{309F}'   |  // 平假名
        '\u{30A0}'..='\u{30FF}'   |  // 片假名
        '\u{AC00}'..='\u{D7AF}'      // 韓文音節
    )
}

fn is_word_char(c: char) -> bool {
    c.is_alphanumeric() && !is_cjk(c)
}

// ── NFKC 簡易實作（僅處理常見全形） ──────────────────────────────────────

fn nfkc_lower(s: &str) -> String {
    s.chars().map(|c| {
        // 全形 ASCII（Ａ–Ｚ、ａ–ｚ、０–９）→ 半形
        let half = match c {
            '\u{FF01}'..='\u{FF5E}' => {
                char::from_u32(c as u32 - 0xFF01 + 0x21).unwrap_or(c)
            }
            '\u{3000}' => ' ',  // 全形空格
            _ => c,
        };
        // 轉小寫
        half.to_lowercase().next().unwrap_or(half)
    }).collect()
}

// ── Tokenizer ────────────────────────────────────────────────────────────

pub struct Tokenizer;

impl Tokenizer {
    pub fn new() -> Self { Tokenizer }

    /// 主要入口：對一段文字切 token
    pub fn tokenize(&self, text: &str) -> Vec<Token> {
        let normalized = nfkc_lower(text);
        let chars: Vec<char> = normalized.chars().collect();
        let mut tokens = Vec::new();
        let mut i = 0;

        while i < chars.len() {
            let c = chars[i];

            if is_cjk(c) {
                // CJK 段落：bigram
                let start = i;
                // 收集連續 CJK 字元
                let mut end = i;
                while end < chars.len() && is_cjk(chars[end]) {
                    end += 1;
                }
                // 對這段 CJK 做 bigram
                for j in start..end {
                    if j + 1 < end {
                        let term: String = chars[j..j+2].iter().collect();
                        tokens.push(Token { term, offset: j });
                    }
                    // 單字也索引（長度 1 的 CJK 段落）
                    if end - start == 1 {
                        tokens.push(Token { term: chars[j].to_string(), offset: j });
                    }
                }
                i = end;
            } else if is_word_char(c) {
                // 英語詞：收集到非詞字元為止
                let start = i;
                while i < chars.len() && is_word_char(chars[i]) {
                    i += 1;
                }
                let term: String = chars[start..i].iter().collect();
                if !term.is_empty() {
                    tokens.push(Token { term, offset: start });
                }
            } else {
                i += 1; // 跳過空白與標點
            }
        }

        tokens
    }

    /// 只回傳去重後的 term 集合（用於建立索引）
    pub fn terms(&self, text: &str) -> Vec<String> {
        let mut seen = std::collections::HashSet::new();
        self.tokenize(text).into_iter()
            .filter(|t| seen.insert(t.term.clone()))
            .map(|t| t.term)
            .collect()
    }
}

impl Default for Tokenizer {
    fn default() -> Self { Self::new() }
}

// ── 測試 ─────────────────────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;

    fn terms(text: &str) -> Vec<String> {
        Tokenizer::new().tokenize(text).into_iter().map(|t| t.term).collect()
    }

    #[test]
    fn english_basic() {
        let t = terms("Hello World");
        assert_eq!(t, vec!["hello", "world"]);
    }

    #[test]
    fn english_punctuation() {
        let t = terms("foo, bar! baz.");
        assert_eq!(t, vec!["foo", "bar", "baz"]);
    }

    #[test]
    fn english_lowercase() {
        let t = terms("SQL DATABASE");
        assert_eq!(t, vec!["sql", "database"]);
    }

    #[test]
    fn cjk_bigram() {
        let t = terms("資料庫");
        assert_eq!(t, vec!["資料", "料庫"]);
    }

    #[test]
    fn cjk_single_char() {
        let t = terms("書");
        assert_eq!(t, vec!["書"]);
    }

    #[test]
    fn mixed_text() {
        let t = terms("SQL 資料庫");
        assert!(t.contains(&"sql".to_string()));
        assert!(t.contains(&"資料".to_string()));
        assert!(t.contains(&"料庫".to_string()));
    }

    #[test]
    fn japanese() {
        let t = terms("データベース");
        // 片假名 bigram
        assert!(t.len() >= 2);
        assert_eq!(t[0], "デー");
    }

    #[test]
    fn korean() {
        let t = terms("데이터베이스");
        assert!(t.len() >= 2);
    }

    #[test]
    fn fullwidth_ascii() {
        // 全形英文字母轉半形小寫
        let t = terms("ＳＱＬ");
        assert_eq!(t, vec!["sql"]);
    }

    #[test]
    fn empty_string() {
        assert!(terms("").is_empty());
    }

    #[test]
    fn numbers_and_letters() {
        let t = terms("v2.0 release");
        assert!(t.contains(&"v2".to_string()) || t.contains(&"v".to_string()));
        assert!(t.contains(&"release".to_string()));
    }

    #[test]
    fn dedup_terms() {
        let terms = Tokenizer::new().terms("the cat sat on the mat");
        // "the" 只出現一次
        assert_eq!(terms.iter().filter(|t| t.as_str() == "the").count(), 1);
    }
}
