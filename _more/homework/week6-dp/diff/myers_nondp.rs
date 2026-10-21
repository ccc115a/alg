//! 非動態規劃解法：Myers O(ND) diff 演算法 (1986)。
//!
//! 核心思想
//!     不求 LCS 表，而是把問題看成在編輯圖 (edit graph) 上找
//!     從 (0,0) 到 (N,M)、只允許向右(插入)/向下(刪除)/對角(相同)移動
//!     的最短路徑。D = 編輯次數 = N + M - 2*LCS。
//!     對每個對角線 k = x - y，只追蹤該對角線最右的 x (V[k])，
//!     用「蛇行 (snake)」延伸相同字元，逐層擴展 D。
//!
//! 複雜度
//!     時間 O(ND)、空間 O(D)；D 為兩檔差異大小，通常遠小於 N+M。

use std::collections::HashMap;

/// 回傳 op 列表：('=' , ch) 相同 / ('-', ch) 刪除 / ('+', ch) 插入。
pub fn myers_diff(a: &str, b: &str) -> Vec<(char, char)> {
    let av: Vec<char> = a.chars().collect();
    let bv: Vec<char> = b.chars().collect();
    let n = av.len() as isize;
    let m = bv.len() as isize;
    let max_d = (n + m) as usize;
    let mut v: HashMap<isize, isize> = HashMap::new();
    v.insert(1, 0);
    let mut trace: Vec<HashMap<isize, isize>> = Vec::new();
    for d in 0..=max_d {
        trace.push(v.clone());
        let d_i = d as isize;
        let mut k = -d_i;
        while k <= d_i {
            let mut x = if k == -d_i
                || (k != d_i
                    && *v.get(&(k - 1)).unwrap_or(&-1) < *v.get(&(k + 1)).unwrap_or(&-1))
            {
                *v.get(&(k + 1)).unwrap_or(&0)
            } else {
                *v.get(&(k - 1)).unwrap_or(&0) + 1
            };
            let mut y = x - k;
            while x < n && y < m && av[x as usize] == bv[y as usize] {
                x += 1;
                y += 1;
            }
            v.insert(k, x);
            if x >= n && y >= m {
                return backtrack(&av, &bv, d, &trace);
            }
            k += 2;
        }
    }
    unreachable!()
}

fn backtrack(
    a: &[char],
    b: &[char],
    d: usize,
    trace: &[HashMap<isize, isize>],
) -> Vec<(char, char)> {
    let mut ops = Vec::new();
    let mut x = a.len() as isize;
    let mut y = b.len() as isize;
    for dd in (1..=d).rev() {
        let v_prev = &trace[dd];
        let dd_i = dd as isize;
        let k = x - y;
        let prev_k = if k == -dd_i
            || (k != dd_i
                && *v_prev.get(&(k - 1)).unwrap_or(&-1) < *v_prev.get(&(k + 1)).unwrap_or(&-1))
        {
            k + 1
        } else {
            k - 1
        };
        let prev_x = *v_prev.get(&prev_k).unwrap_or(&0);
        let prev_y = prev_x - prev_k;
        while x > prev_x && y > prev_y {
            x -= 1;
            y -= 1;
            ops.push(('=', a[x as usize]));
        }
        if x == prev_x {
            ops.push(('+', b[(y - 1) as usize]));
            y -= 1;
        } else {
            ops.push(('-', a[(x - 1) as usize]));
            x -= 1;
        }
    }
    while x > 0 && y > 0 {
        x -= 1;
        y -= 1;
        ops.push(('=', a[x as usize]));
    }
    ops.reverse();
    ops
}
