//! 非動態規劃解法：Thompson NFA 模擬（grep/egrep 的正規表示式引擎原理）。
//!
//! 原理
//!     把 pattern 編譯成 NFA（非確定性有限自動機）：
//!       - 普通字元 c：建一個 c 轉移
//!       - '.'          ：建一個「任意字元」轉移
//!       - 串接         ：子機器頭尾相連（ε 邊）
//!       - '*'          ：加 ε-環（可跳過、可重複）
//!       - '|'          ：兩分支（ε 到兩邊，兩邊再 ε 到匯合點）
//!     模擬時維持「當前可能處於的所有狀態集合」，每讀一個字元就並行推進
//!     （ε-closure + 轉移）。接受狀態在集合中即匹配成功。
//!
//! 與 DP 的 dp[i][j] 在本質上等價——「第 i 字元後可能處於的狀態集」
//! 就是 DP 表的一列——但實作上以圖遍歷而非表格填寫呈現。
//!
//! 複雜度：編譯 O(|p|)、模擬每字元 O(|p|)，總計 O(n·|p|)。

use std::collections::HashSet;

/// 支援語法：字元、'.'、'*'、'|'、'()'。'*' 綁定前一個 atom。
pub struct Nfa {
    /// (char_or_None, to)；None 表 ε
    trans: Vec<Vec<(Option<char>, usize)>>,
    start: usize,
    accept: usize,
}

impl Nfa {
    pub fn new(pattern: &str) -> Self {
        let chars: Vec<char> = pattern.chars().collect();
        let mut nfa = Nfa {
            trans: Vec::new(),
            start: 0,
            accept: 0,
        };
        let (_, start, accept) = nfa.parse(&chars, 0, chars.len());
        nfa.start = start;
        nfa.accept = accept;
        nfa
    }

    fn new_state(&mut self) -> usize {
        self.trans.push(Vec::new());
        self.trans.len() - 1
    }

    fn add(&mut self, fr: usize, ch: Option<char>, to: usize) {
        self.trans[fr].push((ch, to));
    }

    /// 解析 alternation：branch ('|' branch)*。回傳 (新 i, 入口, 出口)。
    fn parse(&mut self, p: &[char], mut i: usize, end: usize) -> (usize, usize, usize) {
        let entry = self.new_state();
        let exit = self.new_state();
        let mut cur_entry = entry;
        loop {
            let (ni, tail) = self.parse_seq(p, i, end, cur_entry);
            i = ni;
            self.add(tail, None, exit);
            if i < end && p[i] == '|' {
                i += 1;
                cur_entry = self.new_state();
                self.add(entry, None, cur_entry); // 分支入口
            } else {
                break;
            }
        }
        (i, entry, exit)
    }

    /// 解析串接的 atom/atom* 序列。回傳 (新 i, 出口狀態)。
    fn parse_seq(&mut self, p: &[char], mut i: usize, end: usize, start: usize) -> (usize, usize) {
        let mut cur = start;
        while i < end && p[i] != '|' && p[i] != ')' {
            if p[i] == '(' {
                i += 1;
                let (ni, sub_in, sub_out) = self.parse(p, i, end);
                i = ni;
                assert!(i < end && p[i] == ')', "missing ')'");
                i += 1; // 跳過 ')'
                // group 也支援 '*'
                if i < end && p[i] == '*' {
                    i += 1;
                    let body_in = self.new_state();
                    let out = self.new_state();
                    self.add(cur, None, body_in);
                    self.add(cur, None, out); // 零次
                    self.add(body_in, None, sub_in); // 進入子機器
                    self.add(sub_out, None, out); // 離開子機器
                    self.add(out, None, body_in); // 重複
                    cur = out;
                } else {
                    self.add(cur, None, sub_in);
                    cur = sub_out;
                }
                continue;
            }
            // atom
            let ch = p[i];
            i += 1;
            if i < end && p[i] == '*' {
                i += 1;
                let body_in = self.new_state();
                let out = self.new_state();
                self.add(cur, None, body_in); // 進入
                self.add(cur, None, out); // 跳過（零次）
                self.add(body_in, Some(ch), out); // 吃一個字元
                self.add(out, None, body_in); // 重複（環）
                cur = out;
            } else {
                let nxt = self.new_state();
                self.add(cur, Some(ch), nxt);
                cur = nxt;
            }
        }
        (i, cur)
    }

    fn epsilon_closure(&self, states: &mut HashSet<usize>) {
        let mut stack: Vec<usize> = states.iter().copied().collect();
        while let Some(s) = stack.pop() {
            for &(ch, t) in &self.trans[s] {
                if ch.is_none() && states.insert(t) {
                    stack.push(t);
                }
            }
        }
    }

    /// text 是否完全匹配 pattern（fullmatch 語義，與 DP 版一致）。
    pub fn match_text(&self, text: &str) -> bool {
        let mut cur: HashSet<usize> = HashSet::new();
        cur.insert(self.start);
        self.epsilon_closure(&mut cur);
        for ch in text.chars() {
            let mut nxt: HashSet<usize> = HashSet::new();
            for &s in &cur {
                for &(c, t) in &self.trans[s] {
                    if let Some(pc) = c {
                        if pc == '.' || pc == ch {
                            nxt.insert(t);
                        }
                    }
                }
            }
            if nxt.is_empty() {
                return false;
            }
            cur = nxt;
            self.epsilon_closure(&mut cur);
        }
        cur.contains(&self.accept)
    }
}

pub fn nfa_match(s: &str, p: &str) -> bool {
    Nfa::new(p).match_text(s)
}
