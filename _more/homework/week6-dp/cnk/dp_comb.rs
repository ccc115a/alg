//! 動態規劃解法：C(n, k) 組合數。
//!
//! 狀態定義
//!     dp[i][j] = C(i, j) = 從 i 個取出 j 個的組合數。
//!
//! 轉移方程（Pascal 公式）
//!     C(n, k) = C(n-1, k-1) + C(n-1, k)
//!     初值 C(i, 0) = C(i, i) = 1
//!
//! 空間可壓縮成一維：dp[j] = dp[j] + dp[j-1]，從 j = min(i, k) 倒著更新。
//!
//! 複雜度：時間 O(nk)、空間 O(k)（壓縮後）。
//! 這裡用 u128 + wrapping_add：正確性驗證案例 (n≤100) 不溢位，
//! 計時用的大 n (500) 會溢位但不 panic（純量測速度）。

pub fn comb_2d(n: usize, k: usize) -> u128 {
    if k > n {
        return 0;
    }
    let mut dp = vec![vec![0u128; k + 1]; n + 1];
    for i in 0..=n {
        dp[i][0] = 1;
        for j in 1..=i.min(k) {
            dp[i][j] = dp[i - 1][j - 1].wrapping_add(dp[i - 1][j]);
        }
    }
    dp[n][k]
}

pub fn comb_1d(n: usize, k: usize) -> u128 {
    if k > n {
        return 0;
    }
    let mut dp = vec![0u128; k + 1];
    dp[0] = 1;
    for i in 1..=n {
        for j in (1..=i.min(k)).rev() {
            dp[j] = dp[j].wrapping_add(dp[j - 1]);
        }
    }
    dp[k]
}
