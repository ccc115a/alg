//! 動態規劃解法：Smith-Waterman 本地比對 (local alignment)。
//!
//! 狀態定義
//!     H[i][j] = 以 a[0..i-1] 結尾、b[0..j-1] 結尾的最佳本地比對分數。
//!
//! 轉移方程
//!     H[i][j] = max(0,                          # 重新起點
//!                   H[i-1][j-1] + s(a[i-1], b[j-1]),  # 對角：配對/錯配
//!                   H[i-1][j] + gap,            # 刪除
//!                   H[i][j-1] + gap)            # 插入
//!
//! 從分數最大的格子往回追溯即可得到最優本地比對區段。
//! 複雜度：時間 O(nm)、空間 O(nm)。

/// 回傳 (最高分, a 上區間 [start,end), b 上區間 [start,end))。
pub fn smith_waterman(a: &str, b: &str, match_score: i32, mismatch: i32, gap: i32) -> (i32, (usize, usize), (usize, usize)) {
    let av: Vec<char> = a.chars().collect();
    let bv: Vec<char> = b.chars().collect();
    let n = av.len();
    let m = bv.len();
    let mut h = vec![vec![0i32; m + 1]; n + 1];
    let mut best = 0i32;
    let mut best_pos = (0usize, 0usize);
    for i in 1..=n {
        for j in 1..=m {
            let s = if av[i - 1] == bv[j - 1] { match_score } else { mismatch };
            h[i][j] = (0i32)
                .max(h[i - 1][j - 1] + s)
                .max(h[i - 1][j] + gap)
                .max(h[i][j - 1] + gap);
            if h[i][j] > best {
                best = h[i][j];
                best_pos = (i, j);
            }
        }
    }
    // 回溯
    let (mut i, mut j) = best_pos;
    let (end_a, end_b) = (i, j);
    while i > 0 && j > 0 && h[i][j] > 0 {
        let s = if av[i - 1] == bv[j - 1] { match_score } else { mismatch };
        if h[i][j] == h[i - 1][j - 1] + s {
            i -= 1;
            j -= 1;
        } else if h[i][j] == h[i - 1][j] + gap {
            i -= 1;
        } else {
            j -= 1;
        }
    }
    (best, (i, end_a), (j, end_b))
}
