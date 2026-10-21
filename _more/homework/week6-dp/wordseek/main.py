"""驗證 edit-distance DP (模糊搜尋) 與 Boyer-Moore (精確搜尋)，並計時。"""

import random
import timeit

from boyer_moore_nondp import boyer_moore
from dp_search import edit_distance, fuzzy_search

DICT = [
    "hello", "world", "hallo", "help", "hell", "shell", "word",
    "ward", "hold", "held", "hero", "hover", "habit", "harbor",
    " wisdom", "wise", "wish", "witch", "with", "within", "wizard",
]


def check_bm() -> None:
    text = "ababcababcabc"
    assert boyer_moore(text, "abc") == [2, 7, 10]
    assert boyer_moore("aaaaaa", "aa") == [0, 1, 2, 3, 4]
    assert boyer_moore("hello", "xyz") == []
    # 對照 str.find
    random.seed(3)
    t = "".join(random.choice("abc") for _ in range(2000))
    p = "abcabc"
    ours = boyer_moore(t, p)
    expected = []
    i = t.find(p)
    while i != -1:
        expected.append(i)
        i = t.find(p, i + 1)
    assert ours == expected
    print("Boyer-Moore 正確性: OK")


def check_dp() -> None:
    assert edit_distance("kitten", "sitting") == 3
    assert edit_distance("flaw", "lawn") == 2
    r = fuzzy_search("helo", [w.strip() for w in DICT])
    print(f"fuzzy_search('helo') -> {r[:5]} ...")
    # 距離 1 的應該包含 hell, hallo, hello? hello 距離=1 (insert l)
    top_words = [w for d, w in r if d == 1]
    assert "hell" in top_words
    print("Edit distance DP 正確性: OK")


if __name__ == "__main__":
    check_bm()
    check_dp()

    random.seed(9)
    text = "".join(random.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(200_000))
    pattern = text[100_000:100_016]

    print("\n精確搜尋 (text=200k, pattern=16):")
    t_bm = timeit.timeit(lambda: boyer_moore(text, pattern), number=5) / 5
    t_py = timeit.timeit(lambda: text.find(pattern), number=5) / 5
    print(f"  Boyer-Moore : {t_bm*1000:8.3f} ms")
    print(f"  str.find    : {t_py*1000:8.3f} ms")

    print("\n模糊搜尋 (dictionary=22 words, query='helo'):")
    words = [w.strip() for w in DICT]
    t_fz = timeit.timeit(lambda: fuzzy_search("helo", words), number=500) / 500
    print(f"  edit-dist DP: {t_fz*1000:8.3f} ms / 查詢")
