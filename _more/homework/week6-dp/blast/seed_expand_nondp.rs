//! 非動態規劃解法：BLAST 風格 seed-and-expand（近似本地比對）。
//!
//! 原理（仿 NCBI BLAST 的核心流程）
//!     1. Seed：掃過 query，把每個 k-mer 送進 hash table 找資料庫中
//!        的「相同或高分相似」短片段（word hit）。
//!     2. Extend (HSP)：從每個 hit 往左右延伸，只要累計分數仍上升就繼續，
//!        停止後回頭取區間內最大分數的延伸（X-drop 啟發式）。
//!     輸出每個高分片段 (HSP) 的分數與區間。
//!
//! 注意：這是啟發式演算法，不保證最優；換取實務上數個數量級的速度。
//! 複雜度：設 query 長 n、db 長 m、seed 長 k
//!     時間 ~ O(n + m + hits·extend)，常遠小於 O(nm)。

use std::collections::HashMap;

/// 回傳 HSP 列表 (q_start, q_end, db_start, db_end, score)，依分數遞減。
pub fn blast_search(
    query: &str,
    db: &str,
    k: usize,
    match_score: i32,
    mismatch: i32,
    xdrop: i32,
) -> Vec<(usize, usize, usize, usize, i32)> {
    let q: Vec<char> = query.chars().collect();
    let d: Vec<char> = db.chars().collect();
    // 1. 建立 db 的 k-mer index
    let mut index: HashMap<String, Vec<usize>> = HashMap::new();
    if d.len() >= k {
        for i in 0..=d.len() - k {
            let word: String = d[i..i + k].iter().collect();
            index.entry(word).or_default().push(i);
        }
    }

    let mut hsps: Vec<(usize, usize, usize, usize, i32)> = Vec::new();
    let mut seen: HashMap<(usize, usize), ()> = HashMap::new();

    // 2. 找 seed
    if q.len() >= k {
        for qi in 0..=q.len() - k {
            let word: String = q[qi..qi + k].iter().collect();
            if let Some(positions) = index.get(&word) {
                for &di in positions {
                    if seen.insert((qi, di), ()).is_some() {
                        continue;
                    }
                    // 3. X-drop 延伸
                    let (score_r, q_end, d_end) =
                        extend_right(&q, &d, qi + k, di + k, match_score, mismatch, xdrop);
                    let (score_l, q_start, d_start) =
                        extend_left(&q, &d, qi, di, match_score, mismatch, xdrop);
                    let total = score_l + score_r + (k as i32) * match_score;
                    hsps.push((q_start, q_end, d_start, d_end, total));
                }
            }
        }
    }

    hsps.sort_by(|a, b| b.4.cmp(&a.4));
    hsps
}

fn extend_right(
    q: &[char],
    db: &[char],
    mut i: usize,
    mut j: usize,
    match_score: i32,
    mismatch: i32,
    xdrop: i32,
) -> (i32, usize, usize) {
    let mut best = 0i32;
    let mut cur = 0i32;
    let (mut bi, mut bj) = (i, j);
    while i < q.len() && j < db.len() {
        cur += if q[i] == db[j] { match_score } else { mismatch };
        i += 1;
        j += 1;
        if cur > best {
            best = cur;
            bi = i;
            bj = j;
        } else if best - cur > xdrop {
            break;
        }
    }
    (best, bi, bj)
}

fn extend_left(
    q: &[char],
    db: &[char],
    mut i: usize,
    mut j: usize,
    match_score: i32,
    mismatch: i32,
    xdrop: i32,
) -> (i32, usize, usize) {
    let mut best = 0i32;
    let mut cur = 0i32;
    let (mut bi, mut bj) = (i, j);
    while i > 0 && j > 0 {
        cur += if q[i - 1] == db[j - 1] { match_score } else { mismatch };
        i -= 1;
        j -= 1;
        if cur > best {
            best = cur;
            bi = i;
            bj = j;
        } else if best - cur > xdrop {
            break;
        }
    }
    (best, bi, bj)
}
