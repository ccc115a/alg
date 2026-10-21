//! 非動態規劃解法：C(n, k) 純遞迴（無記憶化）。
//!
//! 原理
//!     直接用定義式的遞迴分解：
//!         C(n, k) = C(n-1, k-1) + C(n-1, k)
//!     未加 memo 的遞迴會重複計算大量相同的子問題，
//!     樹狀展開節點數是 O(2^n) 級。
//!
//! 複雜度：時間 O(2^n)、空間 O(n)（遞迴深度）。
//! 這正是「需要動態規劃」的教科書例子：重疊子問題 + 最優子結構。
//! 這裡用 u128；n ≤ 170 左右內不會溢位。

/// 純遞迴，直接反映 Pascal 公式。
pub fn comb_recursive(n: usize, k: usize) -> u128 {
    if k > n {
        return 0;
    }
    if k == 0 || k == n {
        return 1;
    }
    comb_recursive(n - 1, k - 1) + comb_recursive(n - 1, k)
}

/// 用階乘公式的乘法形式（每步可整除，中間值不超過最終結果）。
/// 大 n 溢位 u128 時用 wrapping 避免 panic（僅供計時，值不可信）。
pub fn comb_factorial(n: usize, k: usize) -> u128 {
    if k > n {
        return 0;
    }
    let k = k.min(n - k);
    let mut result: u128 = 1;
    for i in 1..=k {
        result = result
            .wrapping_mul((n - k + i) as u128)
            .wrapping_div(i as u128);
    }
    result
}
