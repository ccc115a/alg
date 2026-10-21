//! 驗證 trie+DP 模糊過濾 與 Aho-Corasick 精確過濾，並計時。

mod aho_corasick_nondp;
mod dp_filter;

use std::time::Instant;
use std::collections::HashSet;

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

const WORDS: &[&str] = &["敏感詞", "壞人", "垃圾", "共產黨", "病毒", "詐騙", "毒品"];

fn random_text(rng: &mut Rng, n: usize) -> String {
    let sigma: Vec<char> = "這是敏感詞和垃圾東西病毒詐騙毒品共產黨人".chars().collect();
    (0..n).map(|_| rng.pick(&sigma)).collect()
}

fn check_exact() {
    let mut rng = Rng::new(5);
    let text = random_text(&mut rng, 300);
    let ac_hits: HashSet<(usize, String)> = aho_corasick_nondp::aho_filter(&text, WORDS)
        .into_iter()
        .map(|(s, _, w)| (s, w))
        .collect();
    let dp_hits: HashSet<(usize, String)> = dp_filter::dp_scan(&text, WORDS, 0)
        .into_iter()
        .map(|(pos, w, _)| (pos, w))
        .collect();
    assert_eq!(ac_hits, dp_hits, "AC vs DP(k=0) 不一致");
    println!("精確匹配一致性: OK (共 {} 命中)", ac_hits.len());
}

fn check_fuzzy() {
    // 「词」是簡體，與「詞」不同 → k=1 應命中
    let text = "這有敏感词哦";
    let hits = dp_filter::dp_scan(text, &["敏感詞"], 1);
    assert!(
        hits.iter().any(|(_, w, _)| w == "敏感詞"),
        "模糊匹配失敗: {:?}",
        hits
    );
    println!("模糊匹配: OK {:?}", hits);
}

fn main() {
    check_exact();
    check_fuzzy();

    let mut rng = Rng::new(11);
    let mut big_words: Vec<String> = WORDS.iter().map(|s| s.to_string()).collect();
    for i in 0..2000 {
        big_words.push(format!("詞{:04}", i));
    }
    let big_refs: Vec<&str> = big_words.iter().map(|s| s.as_str()).collect();
    let text = random_text(&mut rng, 50_000);

    println!("\n海量詞過濾 ({} 詞, text=50k):", big_refs.len());
    let reps = 3;
    let t0 = Instant::now();
    let mut n_hits = 0;
    for _ in 0..reps {
        n_hits = aho_corasick_nondp::aho_filter(&text, &big_refs).len();
    }
    let t_ac = t0.elapsed().as_secs_f64() / reps as f64;
    println!("  Aho-Corasick : {:8.3} ms", t_ac * 1e3);
    println!("  命中數       : {}", n_hits);

    // DP 模糊掃描只在小詞庫上可行
    let short: String = text.chars().take(300).collect();
    let reps = 20;
    let t0 = Instant::now();
    for _ in 0..reps {
        let _ = dp_filter::dp_scan(&short, WORDS, 1);
    }
    let t_dp = t0.elapsed().as_secs_f64() / reps as f64;
    println!("\ntrie+DP 模糊 ({} 詞, text=300, k=1): {:8.3} ms", WORDS.len(), t_dp * 1e3);
}
