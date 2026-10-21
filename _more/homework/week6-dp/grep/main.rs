//! 驗證 DP regex 與 NFA 模擬結果一致，並計時。

mod dp_match;
mod nfa_nondp;

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

// 兩邊都支援的子集語法：字元、'.'、'*'
const TESTS: &[(&str, &str, bool)] = &[
    ("aa", "a", false),
    ("aa", "a*", true),
    ("ab", ".*", true),
    ("aab", "c*a*b", true),
    ("mississippi", "mis*is*p*.", false),
    ("ab", ".*c", false),
    ("aaa", "a*a", true),
    ("abab", "ab*", false), // ab* = a + 零或多個 b，不含 "abab"
    ("abc", "a.c", true),
];

// NFA 額外支援 '|' 與 '()' 的測試
const NFA_ONLY_TESTS: &[(&str, &str, bool)] = &[
    ("ab", "(a|b)*", true),
    ("abc", "(a|b)*c", true),
    ("xyz", "(a|b)*c", false),
    ("abab", "(ab)*", true),
];

/// 以 Python re 風格的簡易 brute-force recognizer 當 ground truth：
/// 這裡改用「直接相信已知答案 + 兩實作互相对照」，
/// 額外用一個小型 DP oracle 驗證（同 dp_match 邏輯但獨立實作太冗），
/// 故以 NFA_ONLY 的期望值與 TESTS 的期望值為準。
fn main() {
    println!("正確性驗證 (DP + NFA，語法: 字元/./ *):");
    for &(s, p, expected) in TESTS {
        let r_dp = dp_match::is_match(s, p);
        let r_nfa = nfa_nondp::nfa_match(s, p);
        assert_eq!(r_dp, expected, "DP 錯誤: s={:?} p={:?}", s, p);
        assert_eq!(r_nfa, expected, "NFA 錯誤: s={:?} p={:?}", s, p);
        println!("  {:<12} {:<12} -> {}", format!("{:?}", s), format!("{:?}", p), r_dp);
    }

    println!("\nNFA 額外語法 (| 與 ()):");
    for &(s, p, expected) in NFA_ONLY_TESTS {
        let r_nfa = nfa_nondp::nfa_match(s, p);
        assert_eq!(r_nfa, expected, "NFA 錯誤: s={:?} p={:?}", s, p);
        println!("  {:<12} {:<12} -> {}", format!("{:?}", s), format!("{:?}", p), r_nfa);
    }

    // 隨機 fuzz：以 DP 為 oracle 比對 NFA（共同語法子集）
    let mut rng = Rng::new(1);
    let alphabet: Vec<char> = "ab".chars().collect();
    let pat_sigma: Vec<char> = "ab.*".chars().collect();
    println!("\n隨機 fuzz 200 組：");
    let mut checked = 0;
    for _ in 0..200 {
        let sl = (rng.next() % 9) as usize;
        let pl = (rng.next() % 9) as usize;
        let s: String = (0..sl).map(|_| rng.pick(&alphabet)).collect();
        let p: String = (0..pl).map(|_| rng.pick(&pat_sigma)).collect();
        // 跳過非法 pattern：'*' 開頭或連續 '**'，或無前驅 atom
        if p.starts_with('*') || p.contains("**") {
            continue;
        }
        // 檢查每個 '*' 前面有合法 atom
        let pc: Vec<char> = p.chars().collect();
        let mut valid = true;
        for idx in 0..pc.len() {
            if pc[idx] == '*' && idx == 0 {
                valid = false;
            }
        }
        if !valid {
            continue;
        }
        let r_dp = dp_match::is_match(&s, &p);
        let r_nfa = nfa_nondp::nfa_match(&s, &p);
        assert_eq!(r_dp, r_nfa, "fuzz 不一致: s={:?} p={:?}", s, p);
        checked += 1;
    }
    println!("  {} 組全部通過", checked);

    println!("\n計時 (text=10k, pattern='a*abb')：");
    let text: String = (0..10_000).map(|_| rng.pick(&alphabet)).collect();
    let tv: Vec<char> = text.chars().collect();
    let pat = "a*abb";
    let t0 = Instant::now();
    for i in 0..400 {
        let chunk: String = tv[i..i + 120].iter().collect();
        let _ = dp_match::is_match(&chunk, pat);
    }
    let t_dp = t0.elapsed().as_secs_f64();
    let t0 = Instant::now();
    for i in 0..400 {
        let chunk: String = tv[i..i + 120].iter().collect();
        let _ = nfa_nondp::nfa_match(&chunk, pat);
    }
    let t_nfa = t0.elapsed().as_secs_f64();
    println!("  DP   : {:8.3} ms", t_dp * 1e3);
    println!("  NFA  : {:8.3} ms", t_nfa * 1e3);
}
