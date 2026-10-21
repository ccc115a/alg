//! 動態規劃解法：正規表達式比對 (支援 . 與 *)。
//!
//! 支援語法：'.' 匹配任意單一字元，'*' 匹配前一個字元零次或多次。
//!
//! 狀態定義
//!     dp[i][j] = s 的前 i 個字元是否能完全匹配 p 的前 j 個 pattern。
//!
//! 轉移方程
//!     p[j-1] 是普通字元或 '.'：
//!         dp[i][j] = dp[i-1][j-1] and s[i-1] == p[j-1] (或 p[j-1]=='.')
//!     p[j-1] 是 '*'，令前驅 token = p[j-2]：
//!         - 零次：dp[i][j] = dp[i][j-2]
//!         - 一次以上：dp[i-1][j] and s[i-1] 匹配 token
//!
//! 複雜度：時間 O(nm)、空間 O(nm)。

/// s 是否完全匹配 p（fullmatch 語義）。
pub fn is_match(s: &str, p: &str) -> bool {
    let sv: Vec<char> = s.chars().collect();
    let pv: Vec<char> = p.chars().collect();
    let n = sv.len();
    let m = pv.len();
    let mut dp = vec![vec![false; m + 1]; n + 1];
    dp[0][0] = true;
    for j in 2..=m {
        if pv[j - 1] == '*' {
            dp[0][j] = dp[0][j - 2];
        }
    }
    for i in 1..=n {
        for j in 1..=m {
            if pv[j - 1] == '*' {
                dp[i][j] = dp[i][j - 2]; // 零次
                let tok = pv[j - 2];
                if tok == '.' || tok == sv[i - 1] {
                    dp[i][j] |= dp[i - 1][j]; // 一次以上（'*' 留著繼續吃）
                }
            } else if pv[j - 1] == '.' || pv[j - 1] == sv[i - 1] {
                dp[i][j] = dp[i - 1][j - 1];
            }
        }
    }
    dp[n][m]
}

/// text 中所有「有前綴完全匹配 pattern」的起始位置。
pub fn find_matches(text: &str, pattern: &str) -> Vec<usize> {
    let tv: Vec<char> = text.chars().collect();
    let mut results = Vec::new();
    for i in 0..tv.len() {
        if match_prefix(&tv, i, pattern) {
            results.push(i);
        }
    }
    results
}

/// 檢查 tv[start:] 是否有某前綴完全匹配 p。
fn match_prefix(tv: &[char], start: usize, p: &str) -> bool {
    let pv: Vec<char> = p.chars().collect();
    let n = tv.len() - start;
    let m = pv.len();
    let mut dp = vec![vec![false; m + 1]; n + 1];
    dp[0][0] = true;
    for j in 2..=m {
        if pv[j - 1] == '*' {
            dp[0][j] = dp[0][j - 2];
        }
    }
    for i in 1..=n {
        for j in 1..=m {
            if pv[j - 1] == '*' {
                dp[i][j] = dp[i][j - 2];
                let tok = pv[j - 2];
                if tok == '.' || tok == tv[start + i - 1] {
                    dp[i][j] |= dp[i - 1][j];
                }
            } else if pv[j - 1] == '.' || pv[j - 1] == tv[start + i - 1] {
                dp[i][j] = dp[i - 1][j - 1];
            }
        }
        if dp[i][m] {
            return true;
        }
    }
    false
}
