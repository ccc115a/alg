"""驗證 DP regex 與 NFA 模擬結果一致，並計時。"""

import random
import re
import timeit

from dp_match import is_match
from nfa_nondp import nfa_match

# 兩邊都支援的子集語法：字元、'.'、'*'
TESTS = [
    ("aa", "a", False),
    ("aa", "a*", True),
    ("ab", ".*", True),
    ("aab", "c*a*b", True),
    ("mississippi", "mis*is*p*.", False),
    ("ab", ".*c", False),
    ("aaa", "a*a", True),
    ("abab", "ab*", False),   # ab* = a + 零或多個 b，不含 "abab"
    ("abc", "a.c", True),
]

# NFA 額外支援 '|' 與 '()' 的測試
NFA_ONLY_TESTS = [
    ("ab", "(a|b)*", True),
    ("abc", "(a|b)*c", True),
    ("xyz", "(a|b)*c", False),
    ("abab", "(ab)*", True),
]


def naive_match(s: str, p: str) -> bool:
    """以 Python re 當 ground truth（語法相容子集）。"""
    try:
        return bool(re.fullmatch(p, s))
    except re.error:
        raise


if __name__ == "__main__":
    print("正確性驗證 (DP + NFA，語法: 字元/./ *):")
    for s, p, _ in TESTS:
        r_dp = is_match(s, p)
        r_nfa = nfa_match(s, p)
        r_gt = naive_match(s, p)
        assert r_dp == r_gt, f"DP 錯誤: {s=} {p=} {r_dp} != {r_gt}"
        assert r_nfa == r_gt, f"NFA 錯誤: {s=} {p=} {r_nfa} != {r_gt}"
        print(f"  {s!r:12} {p!r:12} -> {r_dp}")

    print("\nNFA 額外語法 (| 與 ()):")
    for s, p, _ in NFA_ONLY_TESTS:
        r_nfa = nfa_match(s, p)
        r_gt = naive_match(s, p)
        assert r_nfa == r_gt, f"NFA 錯誤: {s=} {p=} {r_nfa} != {r_gt}"
        print(f"  {s!r:12} {p!r:12} -> {r_nfa}")

    # 隨機 fuzz
    random.seed(1)
    alphabet = "ab"
    print("\n隨機 fuzz 200 組：")
    checked = 0
    for _ in range(200):
        s = "".join(random.choice(alphabet) for _ in range(random.randint(0, 8)))
        p = "".join(random.choice("ab.*") for _ in range(random.randint(0, 8)))
        try:
            gt = naive_match(s, p)
        except re.error:
            continue
        # 簡化：跳過 re 不允許的 "*" 開頭與連續 "**"
        if p.startswith("*") or "**" in p:
            continue
        assert is_match(s, p) == gt, f"DP: {s=} {p=}"
        assert nfa_match(s, p) == gt, f"NFA: {s=} {p=}"
        checked += 1
    print(f"  {checked} 組全部通過")

    print("\n計時 (text=10k, pattern='a*abb')：")
    text = "".join(random.choice("ab") for _ in range(10_000))
    pat = "a*abb"

    def run_dp():
        for i in range(0, 400):
            is_match(text[i : i + 120], pat)

    def run_nfa():
        for i in range(0, 400):
            nfa_match(text[i : i + 120], pat)

    t_dp = timeit.timeit(run_dp, number=3) / 3
    t_nfa = timeit.timeit(run_nfa, number=3) / 3
    print(f"  DP   : {t_dp*1000:8.3f} ms")
    print(f"  NFA  : {t_nfa*1000:8.3f} ms")
