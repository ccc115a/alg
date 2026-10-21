//! 動態規劃解法：edit distance（編輯距離）定位最相似單字。
//!
//! 問題：在字典 D 中，找出與 query 編輯距離最小的單字（模糊搜尋/拼寫檢查）。
//!
//! 狀態定義
//!     dp[i][j] = query 前 i 字元 vs 候選 前 j 字元 的編輯距離。
//!
//! 轉移方程
//!     dp[i][j] = dp[i-1][j-1]                      若 q[i-1]==c[j-1]
//!              = 1 + min(dp[i-1][j],               刪除
//!                        dp[i][j-1],               插入
//!                        dp[i-1][j-1])             取代
//!
//! 複雜度：每個候選 O(|q|·|c|)，全部 O(Σ|c|·|q|)。

pub fn edit_distance(a: &str, b: &str) -> usize {
    let av: Vec<char> = a.chars().collect();
    let bv: Vec<char> = b.chars().collect();
    let n = av.len();
    let m = bv.len();
    let mut dp = vec![vec![0usize; m + 1]; n + 1];
    for i in 0..=n {
        dp[i][0] = i;
    }
    for j in 0..=m {
        dp[0][j] = j;
    }
    for i in 1..=n {
        for j in 1..=m {
            dp[i][j] = if av[i - 1] == bv[j - 1] {
                dp[i - 1][j - 1]
            } else {
                1 + dp[i - 1][j].min(dp[i][j - 1]).min(dp[i - 1][j - 1])
            };
        }
    }
    dp[n][m]
}

/// 回傳 (編輯距離, 單字) 列表，距離 <= max_dist，依距離遞增。
pub fn fuzzy_search(query: &str, dictionary: &[&str], max_dist: usize) -> Vec<(usize, String)> {
    let mut results: Vec<(usize, String)> = Vec::new();
    let qlen = query.chars().count();
    for &word in dictionary {
        let wlen = word.chars().count();
        if wlen.abs_diff(qlen) > max_dist {
            continue; // 長度剪枝
        }
        let d = edit_distance(query, word);
        if d <= max_dist {
            results.push((d, word.to_string()));
        }
    }
    results.sort_by(|a, b| a.0.cmp(&b.0).then(a.1.cmp(&b.1)));
    results
}
