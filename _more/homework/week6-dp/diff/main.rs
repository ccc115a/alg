//! 驗證 LCS DP 與 Myers O(ND) diff 結果一致，並簡易計時。

mod lcs_dp;
mod myers_nondp;

use std::time::Instant;

/// 簡易 xorshift PRNG（避免依賴外部 crate）
struct Rng(u64);
impl Rng {
    fn new(seed: u64) -> Self {
        Rng(seed | 1)
    }
    fn next(&mut self) -> u64 {
        self.0 ^= self.0 << 13;
        self.0 ^= self.0 >> 7;
        self.0 ^= self.0 << 17;
        self.0
    }
    fn pick(&mut self, sigma: &[char]) -> char {
        sigma[(self.next() % sigma.len() as u64) as usize]
    }
}

fn random_string(rng: &mut Rng, n: usize, sigma: &[char]) -> String {
    (0..n).map(|_| rng.pick(sigma)).collect()
}

fn check(a: &str, b: &str) {
    let ops1 = lcs_dp::diff_lcs(a, b);
    let ops2 = myers_nondp::myers_diff(a, b);
    for (ops, name) in [(&ops1, "LCS"), (&ops2, "Myers")] {
        let rebuilt: String = ops
            .iter()
            .filter(|(op, _)| *op != '+')
            .map(|(_, ch)| *ch)
            .collect();
        assert_eq!(rebuilt, a, "{} 刪除/保留錯誤", name);
        let rebuilt_b: String = ops
            .iter()
            .filter(|(op, _)| *op != '-')
            .map(|(_, ch)| *ch)
            .collect();
        assert_eq!(rebuilt_b, b, "{} 插入/保留錯誤", name);
    }
    let edits1 = ops1.iter().filter(|(op, _)| *op != '=').count();
    let edits2 = ops2.iter().filter(|(op, _)| *op != '=').count();
    assert_eq!(edits1, edits2, "編輯次數不同: {} vs {}", edits1, edits2);
    println!("  OK len={} edits={}", a.chars().count(), edits1);
}

fn main() {
    println!("正確性驗證：");
    let mut rng = Rng::new(42);
    let sigma: Vec<char> = "ABC".chars().collect();
    for n in [10usize, 50, 200] {
        for _ in 0..3 {
            let a = random_string(&mut rng, n, &sigma);
            let b = random_string(&mut rng, n, &sigma);
            check(&a, &b);
        }
    }

    println!("\n計時 (n=300, 含大量相同字元):");
    let a = random_string(&mut rng, 300, &"ABCD".chars().collect::<Vec<_>>());
    let b: String = a.chars().take(150).chain(random_string(&mut rng, 150, &"ABCD".chars().collect::<Vec<_>>()).chars()).collect();
    let reps = 20;
    let t0 = Instant::now();
    for _ in 0..reps {
        let _ = lcs_dp::diff_lcs(&a, &b);
    }
    let t_lcs = t0.elapsed().as_secs_f64() / reps as f64;
    let t0 = Instant::now();
    for _ in 0..reps {
        let _ = myers_nondp::myers_diff(&a, &b);
    }
    let t_myers = t0.elapsed().as_secs_f64() / reps as f64;
    println!("  LCS DP      : {:8.3} ms", t_lcs * 1e3);
    println!("  Myers O(ND) : {:8.3} ms", t_myers * 1e3);
    println!("  speedup     : {:8.2}x", t_lcs / t_myers);
}
