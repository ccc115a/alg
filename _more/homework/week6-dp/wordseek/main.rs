//! 驗證 edit-distance DP (模糊搜尋) 與 Boyer-Moore (精確搜尋)，並計時。

mod boyer_moore_nondp;
mod dp_search;

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

const DICT: &[&str] = &[
    "hello", "world", "hallo", "help", "hell", "shell", "word", "ward", "hold", "held", "hero",
    "hover", "habit", "harbor", "wisdom", "wise", "wish", "witch", "with", "within", "wizard",
];

fn check_bm() {
    assert_eq!(boyer_moore_nondp::boyer_moore("ababcababcabc", "abc"), vec![2, 7, 10]);
    assert_eq!(boyer_moore_nondp::boyer_moore("aaaaaa", "aa"), vec![0, 1, 2, 3, 4]);
    assert!(boyer_moore_nondp::boyer_moore("hello", "xyz").is_empty());
    // 對照 naive find
    let mut rng = Rng::new(3);
    let sigma: Vec<char> = "abc".chars().collect();
    let t: String = (0..2000).map(|_| rng.pick(&sigma)).collect();
    let p = "abcabc";
    let ours = boyer_moore_nondp::boyer_moore(&t, p);
    let mut expected = Vec::new();
    let tv: Vec<char> = t.chars().collect();
    let pv: Vec<char> = p.chars().collect();
    for start in 0..tv.len().saturating_sub(pv.len() - 1) {
        if tv[start..start + pv.len()] == pv[..] {
            expected.push(start);
        }
    }
    assert_eq!(ours, expected);
    println!("Boyer-Moore 正確性: OK");
}

fn check_dp() {
    assert_eq!(dp_search::edit_distance("kitten", "sitting"), 3);
    assert_eq!(dp_search::edit_distance("flaw", "lawn"), 2);
    let r = dp_search::fuzzy_search("helo", DICT, 2);
    let top: Vec<&str> = r
        .iter()
        .filter(|(d, _)| *d == 1)
        .map(|(_, w)| w.as_str())
        .collect();
    assert!(top.contains(&"hell"), "距離 1 應包含 hell: {:?}", r);
    println!("fuzzy_search('helo') -> {:?} ...", &r[..r.len().min(5)]);
    println!("Edit distance DP 正確性: OK");
}

fn main() {
    check_bm();
    check_dp();

    let mut rng = Rng::new(9);
    let sigma: Vec<char> = "abcdefghijklmnopqrstuvwxyz".chars().collect();
    let text: String = (0..200_000).map(|_| rng.pick(&sigma)).collect();
    let tv: Vec<char> = text.chars().collect();
    let pattern: String = tv[100_000..100_016].iter().collect();

    println!("\n精確搜尋 (text=200k, pattern=16):");
    let reps = 5;
    let t0 = Instant::now();
    for _ in 0..reps {
        let _ = boyer_moore_nondp::boyer_moore(&text, &pattern);
    }
    let t_bm = t0.elapsed().as_secs_f64() / reps as f64;
    // 內建 str find 當基準
    let t0 = Instant::now();
    for _ in 0..reps {
        let _ = text.find(&pattern);
    }
    let t_py = t0.elapsed().as_secs_f64() / reps as f64;
    println!("  Boyer-Moore : {:8.3} ms", t_bm * 1e3);
    println!("  str::find   : {:8.3} ms", t_py * 1e3);

    println!("\n模糊搜尋 (dictionary={} words, query='helo'):", DICT.len());
    let reps = 500;
    let t0 = Instant::now();
    for _ in 0..reps {
        let _ = dp_search::fuzzy_search("helo", DICT, 2);
    }
    let t_fz = t0.elapsed().as_secs_f64() / reps as f64;
    println!("  edit-dist DP: {:8.3} ms / 查詢", t_fz * 1e3);
}
