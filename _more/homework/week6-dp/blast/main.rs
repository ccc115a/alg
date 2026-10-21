//! 驗證 Smith-Waterman (DP) 與 seed-and-expand (啟發式) 的分數/區間，並計時。

mod seed_expand_nondp;
mod smith_waterman_dp;

use std::time::Instant;

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

fn make_case() -> (String, String) {
    let mut rng = Rng::new(7);
    let sigma: Vec<char> = "ACGT".chars().collect();
    let ref_seq: String = (0..400).map(|_| rng.pick(&sigma)).collect();
    let mut a: Vec<char> = ref_seq.chars().skip(50).take(100).collect();
    // 8% 突變
    for _ in 0..8 {
        let pos = (rng.next() % a.len() as u64) as usize;
        a[pos] = rng.pick(&sigma);
    }
    let pre: String = (0..200).map(|_| rng.pick(&sigma)).collect();
    let post: String = (0..200).map(|_| rng.pick(&sigma)).collect();
    let db: String = format!("{}{}{}", pre, a.iter().collect::<String>(), post);
    (a.iter().collect(), db)
}

fn main() {
    let (query, db) = make_case();
    println!("query len={}, db len={}", query.chars().count(), db.chars().count());

    let (score, ia, ib) = smith_waterman_dp::smith_waterman(&query, &db, 2, -1, -1);
    println!("Smith-Waterman : score={} a[{}:{}] db[{}:{}]", score, ia.0, ia.1, ib.0, ib.1);

    let hsps = seed_expand_nondp::blast_search(&query, &db, 4, 2, -1, 2);
    let top = hsps[0];
    println!("BLAST seed-exp : score={} a[{}:{}] db[{}:{}]", top.4, top.0, top.1, top.2, top.3);
    println!("分數比 (blast/SW) = {:.3}", top.4 as f64 / score as f64);

    let reps = 5;
    let t0 = Instant::now();
    for _ in 0..reps {
        let _ = smith_waterman_dp::smith_waterman(&query, &db, 2, -1, -1);
    }
    let t_sw = t0.elapsed().as_secs_f64() / reps as f64;
    let t0 = Instant::now();
    for _ in 0..reps {
        let _ = seed_expand_nondp::blast_search(&query, &db, 4, 2, -1, 2);
    }
    let t_bl = t0.elapsed().as_secs_f64() / reps as f64;
    println!("\nSmith-Waterman : {:8.3} ms", t_sw * 1e3);
    println!("BLAST seed-exp : {:8.3} ms", t_bl * 1e3);
    println!("speedup        : {:8.2}x", t_sw / t_bl);
}
