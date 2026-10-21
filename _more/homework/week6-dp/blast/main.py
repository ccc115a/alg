"""驗證 Smith-Waterman (DP) 與 seed-and-expand (啟發式) 的分數/區間，並計時。"""

import random
import timeit

from seed_expand_nondp import blast_search
from smith_waterman_dp import smith_waterman


def make_case() -> tuple[str, str]:
    """從同一條 DNA 取兩段加上突變，模擬真實比對。"""
    random.seed(7)
    ref = "".join(random.choice("ACGT") for _ in range(400))
    a = list(ref[50:150])
    for pos in random.sample(range(len(a)), 8):  # 8% 突變
        a[pos] = random.choice("ACGT")
    db = "".join(random.choice("ACGT") for _ in range(200)) + "".join(a) \
        + "".join(random.choice("ACGT") for _ in range(200))
    return "".join(a), db


if __name__ == "__main__":
    query, db = make_case()
    print(f"query len={len(query)}, db len={len(db)}")

    score, ia, ib = smith_waterman(query, db)
    print(f"Smith-Waterman : score={score} a[{ia[0]}:{ia[1]}] db[{ib[0]}:{ib[1]}]")

    hsps = blast_search(query, db, k=4)
    top = hsps[0]
    print(f"BLAST seed-exp : score={top[4]} a[{top[0]}:{top[1]}] db[{top[2]}:{top[3]}]")
    print(f"分數比 (blast/SW) = {top[4] / score:.3f}")

    t_sw = timeit.timeit(lambda: smith_waterman(query, db), number=5) / 5
    t_bl = timeit.timeit(lambda: blast_search(query, db, k=4), number=5) / 5
    print(f"\nSmith-Waterman : {t_sw*1000:8.3f} ms")
    print(f"BLAST seed-exp : {t_bl*1000:8.3f} ms")
    print(f"speedup        : {t_sw / t_bl:8.2f}x")
