//! 非動態規劃解法：Aho-Corasick 多模式精確匹配自動機（海量敏感詞過濾）。
//!
//! 原理（AC 自動機，1975）
//!     1. 把所有敏感詞建成 trie。
//!     2. BFS 建 fail link：每個節點指向「最長真後綴仍匹配的節點」。
//!     3. 輸出鏈：fail 指到詞尾時也視為命中（處理子串命中）。
//!     4. 掃描文字時維持當前自動機狀態，每讀一字元沿 trie 走、失配跳 fail，
//!        沿 output 鏈收集所有命中。
//!
//! 複雜度：建機 O(Σ|word|)、掃描 O(全文長 + 命中數)，
//! 與敏感詞數量幾乎無關——過濾百萬級詞庫的工業標準。

use std::collections::VecDeque;

pub struct AhoCorasick {
    goto: Vec<std::collections::HashMap<char, usize>>,
    fail: Vec<usize>,
    output: Vec<Vec<String>>,
}

impl AhoCorasick {
    pub fn new(words: &[&str]) -> Self {
        let mut goto: Vec<std::collections::HashMap<char, usize>> = vec![Default::default()];
        let mut fail = vec![0usize];
        let mut output: Vec<Vec<String>> = vec![Vec::new()];
        for w in words {
            let mut node = 0usize;
            for ch in w.chars() {
                if let Some(&next) = goto[node].get(&ch) {
                    node = next;
                } else {
                    goto.push(Default::default());
                    fail.push(0usize);
                    output.push(Vec::new());
                    let new_node = goto.len() - 1;
                    goto[node].insert(ch, new_node);
                    node = new_node;
                }
            }
            output[node].push(w.to_string());
        }
        // fail link (BFS)
        let mut q: VecDeque<usize> = VecDeque::new();
        for &nxt in goto[0].values() {
            fail[nxt] = 0;
            q.push_back(nxt);
        }
        while let Some(r) = q.pop_front() {
            let keys: Vec<char> = goto[r].keys().copied().collect();
            for ch in keys {
                let s = goto[r][&ch];
                q.push_back(s);
                let mut state = fail[r];
                while state != 0 && !goto[state].contains_key(&ch) {
                    state = fail[state];
                }
                fail[s] = *goto[state].get(&ch).unwrap_or(&0);
                // 合併 output
                let outs = output[fail[s]].clone();
                output[s].extend(outs);
            }
        }
        AhoCorasick { goto, fail, output }
    }

    /// 回傳 (結束位置, 命中詞) 列表。結束位置以 char 計。
    pub fn search(&self, text: &str) -> Vec<(usize, String)> {
        let mut results = Vec::new();
        let mut state = 0usize;
        for (i, ch) in text.chars().enumerate() {
            while state != 0 && !self.goto[state].contains_key(&ch) {
                state = self.fail[state];
            }
            state = *self.goto[state].get(&ch).unwrap_or(&0);
            for w in &self.output[state] {
                results.push((i, w.clone()));
            }
        }
        results
    }
}

/// 回傳 (開始位置, 結束位置, 詞)；開始位置 = 結束位置 - len(詞) + 1。
pub fn aho_filter(text: &str, words: &[&str]) -> Vec<(usize, usize, String)> {
    let ac = AhoCorasick::new(words);
    ac.search(text)
        .into_iter()
        .map(|(i, w)| {
            let start = i + 1 - w.chars().count();
            (start, i, w)
        })
        .collect()
}
