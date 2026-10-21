//! 動態規劃解法：敏感詞過濾（trie + DP 模糊匹配，容忍 ≤k 編輯距離）。
//!
//! 原理
//!     把敏感詞建成 trie；對文字的每個起始位置 i，在 trie 上跑
//!     「編輯距離 ≤ k」的 DP 逐層往下走。
//!     狀態：cur[node] = 從起始位置 i 走到 trie node 的最小編輯距離。
//!     若在某 node 是詞尾且距離 ≤ k，即命中（模糊敏感詞）。
//!
//! 優勢：可同時匹配所有敏感詞的「近似變體」（錯字、簡繁差等）。
//!
//! 複雜度：設文字長 L、trie 節點數 T、容忍距離 k
//!     時間 O(L · k · T_child)，空間 O(T)。

use std::collections::HashMap;

#[derive(Default)]
pub struct TrieNode {
    children: HashMap<char, usize>,
    word_end: bool,
    word: Option<String>,
}

pub struct Trie {
    nodes: Vec<TrieNode>,
}

impl Trie {
    pub fn new() -> Self {
        Trie {
            nodes: vec![TrieNode::default()],
        }
    }

    pub fn insert(&mut self, w: &str) {
        let mut node = 0usize;
        for ch in w.chars() {
            if let Some(&next) = self.nodes[node].children.get(&ch) {
                node = next;
            } else {
                self.nodes.push(TrieNode::default());
                let new_node = self.nodes.len() - 1;
                self.nodes[node].children.insert(ch, new_node);
                node = new_node;
            }
        }
        self.nodes[node].word_end = true;
        self.nodes[node].word = Some(w.to_string());
    }
}

/// 回傳命中列表 (起始位置, 詞, 編輯距離)，詞尾距離 <= k 即命中。
pub fn dp_scan(text: &str, words: &[&str], k: usize) -> Vec<(usize, String, usize)> {
    let mut trie = Trie::new();
    for w in words {
        trie.insert(w);
    }
    let tv: Vec<char> = text.chars().collect();
    let mut hits: Vec<(usize, String, usize)> = Vec::new();
    for i in 0..tv.len() {
        // cur: node -> min cost
        let mut cur: HashMap<usize, usize> = HashMap::new();
        cur.insert(0usize, 0usize);
        for d in i..tv.len() {
            let ch = tv[d];
            let mut nxt: HashMap<usize, usize> = HashMap::new();
            for (&node, &cost) in cur.iter() {
                // 命中檢查（詞尾）
                if trie.nodes[node].word_end && cost <= k {
                    hits.push((i, trie.nodes[node].word.clone().unwrap(), cost));
                }
                if cost > k {
                    continue;
                }
                // 完全匹配：往下走
                if let Some(&cnode) = trie.nodes[node].children.get(&ch) {
                    let e = nxt.entry(cnode).or_insert(k + 1);
                    if cost < *e {
                        *e = cost;
                    }
                }
                // 編輯操作
                for (&c2, &cnode2) in trie.nodes[node].children.iter() {
                    let _ = c2;
                    let e = nxt.entry(cnode2).or_insert(k + 1);
                    if cost + 1 < *e {
                        *e = cost + 1; // 取代
                    }
                }
                // 插入（消耗 trie 字元不動文字，等價於同 node 多走一步）
                let e = nxt.entry(node).or_insert(k + 1);
                if cost + 1 < *e {
                    *e = cost + 1;
                }
            }
            cur = nxt;
            if cur.is_empty() {
                break;
            }
        }
        // 補上末尾的詞尾檢查
        for (&node, &cost) in cur.iter() {
            if trie.nodes[node].word_end && cost <= k {
                hits.push((i, trie.nodes[node].word.clone().unwrap(), cost));
            }
        }
    }
    hits
}
