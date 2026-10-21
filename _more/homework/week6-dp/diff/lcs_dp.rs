//! 動態規劃解法：LCS (最長共同子序列) 產生 diff。
//!
//! 狀態定義
//!     dp[i][j] = a 的前 i 個字元與 b 的前 j 個字元的 LCS 長度
//!
//! 轉移方程
//!     dp[i][j] = dp[i-1][j-1] + 1            若 a[i-1] == b[j-1]
//!              = max(dp[i-1][j], dp[i][j-1]) 否則
//!
//! 回溯時，'=' 來自對角線，'-' 代表刪除 a 的字元，'+' 代表插入 b 的字元。

/// 回傳 op 列表：('=' , ch) 相同 / ('-', ch) 刪除 / ('+', ch) 插入。
pub fn diff_lcs(a: &str, b: &str) -> Vec<(char, char)> {
    let av: Vec<char> = a.chars().collect();
    let bv: Vec<char> = b.chars().collect();
    let n = av.len();
    let m = bv.len();
    let mut dp = vec![vec![0usize; m + 1]; n + 1];
    for i in 1..=n {
        for j in 1..=m {
            dp[i][j] = if av[i - 1] == bv[j - 1] {
                dp[i - 1][j - 1] + 1
            } else {
                dp[i - 1][j].max(dp[i][j - 1])
            };
        }
    }
    let mut ops = Vec::new();
    let (mut i, mut j) = (n, m);
    while i > 0 || j > 0 {
        if i > 0 && j > 0 && av[i - 1] == bv[j - 1] && dp[i][j] == dp[i - 1][j - 1] + 1 {
            ops.push(('=', av[i - 1]));
            i -= 1;
            j -= 1;
        } else if j > 0 && (i == 0 || dp[i][j] == dp[i][j - 1]) {
            ops.push(('+', bv[j - 1]));
            j -= 1;
        } else {
            ops.push(('-', av[i - 1]));
            i -= 1;
        }
    }
    ops.reverse();
    ops
}

pub fn format_diff(a: &str, b: &str) -> String {
    diff_lcs(a, b)
        .into_iter()
        .map(|(op, ch)| format!("{} {}", op, ch))
        .collect::<Vec<_>>()
        .join("\n")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_format() {
        let out = format_diff("ABCABBA", "CBABAC");
        assert!(out.contains('='));
        assert!(out.contains('+'));
        assert!(out.contains('-'));
    }
}
