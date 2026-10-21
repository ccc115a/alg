//! 驗證 C(n,k) 的 DP 與遞迴結果一致，並計時比較重複子問題的代價。

mod dp_comb;
mod recurse_comb_nondp;

use std::time::Instant;

const CASES: &[(usize, usize)] = &[
    (5, 2),
    (10, 3),
    (20, 10),
    (30, 15),
    (50, 25),
    (100, 50),
];

fn check() {
    for &(n, k) in CASES {
        let gt = dp_comb::comb_1d(n, k); // 以 1D DP 為準，另用 2D/階乘互校
        assert_eq!(dp_comb::comb_2d(n, k), gt, "2d DP 錯誤: C({},{})", n, k);
        assert_eq!(
            recurse_comb_nondp::comb_factorial(n, k),
            gt,
            "階乘錯誤: C({},{})",
            n,
            k
        );
        if n <= 25 {
            assert_eq!(
                recurse_comb_nondp::comb_recursive(n, k),
                gt,
                "遞迴錯誤: C({},{})",
                n,
                k
            );
        }
    }
    println!("正確性: 全部一致（DP 1D/2D 與階乘互校）");
}

fn main() {
    check();

    println!("\n計時:");
    let (n, k) = (500usize, 250usize);
    let reps = 100;
    let t0 = Instant::now();
    for _ in 0..reps {
        let _ = dp_comb::comb_1d(n, k);
    }
    let t_1d = t0.elapsed().as_secs_f64() / reps as f64;
    let t0 = Instant::now();
    for _ in 0..reps {
        let _ = dp_comb::comb_2d(n, k);
    }
    let t_2d = t0.elapsed().as_secs_f64() / reps as f64;
    let t0 = Instant::now();
    for _ in 0..reps {
        let _ = recurse_comb_nondp::comb_factorial(n, k);
    }
    let t_fact = t0.elapsed().as_secs_f64() / reps as f64;
    println!("  DP 1D (O(nk) 時間/O(k) 空間) : {:10.1} us", t_1d * 1e6);
    println!("  DP 2D (O(nk) 時間/O(nk) 空間): {:10.1} us", t_2d * 1e6);
    println!("  階乘公式 (O(n) 迭代)         : {:10.1} us", t_fact * 1e6);

    println!("\n純遞迴 vs DP (小 n 示範重複子問題):");
    for nn in [10usize, 15, 20, 25, 28] {
        let k = nn / 2;
        let t0 = Instant::now();
        let _ = recurse_comb_nondp::comb_recursive(nn, k);
        let t_rec = t0.elapsed().as_secs_f64();
        let reps = 1000;
        let t0 = Instant::now();
        for _ in 0..reps {
            let _ = dp_comb::comb_1d(nn, k);
        }
        let t_dp = t0.elapsed().as_secs_f64() / reps as f64;
        println!(
            "  n={:3} k={:3}  遞迴={:10.3} ms  DP={:8.2} us",
            nn,
            k,
            t_rec * 1e3,
            t_dp * 1e6
        );
    }
}
