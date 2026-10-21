"""驗證 LCS DP 與 Myers O(ND) diff 結果一致，並簡易計時。"""

import random
import timeit

from lcs_dp import diff_lcs
from myers_nondp import myers_diff


def random_pair(n: int, sigma: str = "ABC") -> tuple[str, str]:
    return (
        "".join(random.choice(sigma) for _ in range(n)),
        "".join(random.choice(sigma) for _ in range(n)),
    )


def check(a: str, b: str) -> None:
    ops1 = diff_lcs(a, b)
    ops2 = myers_diff(a, b)
    # 還原驗證
    for ops, name in ((ops1, "LCS"), (ops2, "Myers")):
        rebuilt = "".join(ch for op, ch in ops if op != "+")
        assert rebuilt == a, f"{name} 刪除/保留錯誤"
        rebuilt_b = "".join(ch for op, ch in ops if op != "-")
        assert rebuilt_b == b, f"{name} 插入/保留錯誤"
    # 編輯次數（+ 與 - 的總數）應相同（同為最短編輯腳本的一種）
    edits1 = sum(1 for op, _ in ops1 if op != "=")
    edits2 = sum(1 for op, _ in ops2 if op != "=")
    assert edits1 == edits2, f"編輯次數不同: {edits1} vs {edits2}"
    print(f"  OK len={len(a)} edits={edits1}")


if __name__ == "__main__":
    random.seed(42)
    print("正確性驗證：")
    for n in (10, 50, 200):
        for _ in range(3):
            check(*random_pair(n))

    print("\n計時 (n=300, 含大量相同字元):")
    a = "".join(random.choice("ABCD") for _ in range(300))
    b = a[:150] + "".join(random.choice("ABCD") for _ in range(150))
    t_lcs = timeit.timeit(lambda: diff_lcs(a, b), number=20) / 20
    t_myers = timeit.timeit(lambda: myers_diff(a, b), number=20) / 20
    print(f"  LCS DP      : {t_lcs*1000:8.3f} ms")
    print(f"  Myers O(ND) : {t_myers*1000:8.3f} ms")
    print(f"  speedup     : {t_lcs / t_myers:8.2f}x")
