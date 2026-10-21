//! 非動態規劃解法：Boyer-Moore 單字搜尋（精確匹配）。
//!
//! 原理
//!     從 pattern 右端往左比較；失配時根據兩個啟發式跳躍：
//!       1. 壞字元 (bad character)：失配字元 x 在 pattern 中最右出現位置
//!          → 跳 j - bad[x]（bad[x] 未定義時跳 j+1）
//!       2. 好後綴 (good suffix)：已匹配的後綴在 pattern 中其他出現位置
//!          → 跳 good[j]
//!     兩者取較大跳量。
//!
//! 複雜度
//!     預處理 O(m²)；搜尋平均 O(n/m)（最佳）、最壞 O(n·m)。
//!
//! 注意：BM 做的是「精確匹配」；模糊定位（容忍錯字）需要編輯距離 DP。
//! 兩者解決的是 word search 的不同變體——這正是 DP 與非 DP 的分工。

use std::collections::HashMap;

/// 回傳 pattern 在 text 中所有出現的起始位置。
pub fn boyer_moore(text: &str, pattern: &str) -> Vec<usize> {
    let tv: Vec<char> = text.chars().collect();
    let pv: Vec<char> = pattern.chars().collect();
    let n = tv.len();
    let m = pv.len();
    if m == 0 {
        return (0..=n).collect();
    }
    // 壞字元表：每個字元在 pattern 中的最右位置
    let mut bad: HashMap<char, usize> = HashMap::new();
    for (i, &c) in pv.iter().enumerate() {
        bad.insert(c, i);
    }
    // 好綴表（與 Python 版一致的保守版本）
    let mut good = vec![m; m];
    let mut j = m;
    for i in (0..m).rev() {
        if is_border(&pv, i) {
            j = i;
        }
        good[i] = if j < m { j - i } else { m - i };
    }

    let mut results = Vec::new();
    let mut s = 0usize;
    while s + m <= n {
        let mut j = m as isize - 1;
        while j >= 0 && pv[j as usize] == tv[s + j as usize] {
            j -= 1;
        }
        if j < 0 {
            results.push(s);
            s += 1;
        } else {
            let x = tv[s + j as usize];
            let bad_pos: isize = bad.get(&x).map(|&v| v as isize).unwrap_or(-1);
            let skip_bc = (j - bad_pos).max(1) as usize;
            let skip_bs = good[j as usize];
            s += skip_bc.max(skip_bs).max(1);
        }
    }
    results
}

fn is_border(p: &[char], i: usize) -> bool {
    p[i..] == p[..p.len() - i]
}
