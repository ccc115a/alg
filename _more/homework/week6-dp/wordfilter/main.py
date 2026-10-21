"""驗證 trie+DP 模糊過濾 與 Aho-Corasick 精確過濾，並計時。"""

import random
import timeit

from aho_corasick_nondp import AhoCorasick, aho_filter
from dp_filter import dp_scan

WORDS = ["敏感詞", "壞人", "垃圾", "共產黨", "病毒", "詐騙", "毒品"]


def check_exact() -> None:
    """k=0 時 DP 結果的詞集合應涵蓋 AC 的精確命中。"""
    random.seed(5)
    text = "".join(random.choice("這是敏感詞和垃圾東西病毒詐騙毒品共產黨人") for _ in range(300))
    ac_hits = {(pos, w) for pos, _, w in aho_filter(text, WORDS)}
    dp_hits = {(pos, w) for pos, w, d in dp_scan(text, WORDS, k=0)}
    assert ac_hits == dp_hits, f"AC vs DP(k=0) 不一致: {ac_hits ^ dp_hits}"
    print(f"精確匹配一致性: OK (共 {len(ac_hits)} 命中)")


def check_fuzzy() -> None:
    """加入錯字的變體，k=1 應能命中。"""
    text = "這有敏感词哦"  # 词 是 简体，與 敏感詞 不同
    hits = dp_scan(text, ["敏感詞"], k=1)
    assert any(w == "敏感詞" for _, w, _ in hits), f"模糊匹配失敗: {hits}"
    print(f"模糊匹配: OK {hits}")


if __name__ == "__main__":
    check_exact()
    check_fuzzy()

    random.seed(11)
    # 大量詞庫 + 長文本
    vocab = ["敏感詞", "壞人", "垃圾", "共產黨", "病毒", "詐騙", "毒品"]
    big_words = vocab + [f"詞{i:04}" for i in range(2000)]
    text = "".join(random.choice("這是敏感詞和垃圾東西病毒詐騙毒品共產黨人") for _ in range(50_000))

    print("\n海量詞過濾 (2007 詞, text=50k):")
    t_ac = timeit.timeit(lambda: aho_filter(text, big_words), number=3) / 3
    print(f"  Aho-Corasick : {t_ac*1000:8.3f} ms")
    print(f"  命中數       : {len(aho_filter(text, big_words))}")

    # DP 模糊掃描只在小詞庫上可行
    t_dp = timeit.timeit(lambda: dp_scan(text[:300], vocab, k=1), number=20) / 20
    print(f"\ntrie+DP 模糊 (7 詞, text=300, k=1): {t_dp*1000:8.3f} ms")
