"""非動態規劃解法：BLAST 風格 seed-and-expand（近似本地比對）。

原理（仿 NCBI BLAST 的核心流程）
    1. Seed：掃過 query，把每個 k-mer 送進 hash table 找資料庫中
       的「相同或高分相似」短片段（word hit）。
    2. Extend (HSP)：從每個 hit 往左右延伸，只要累計分數仍上升就繼續，
       停止後回頭取區間內最大分數的延伸（X-drop 啟發式）。
    輸出每個高分片段 (HSP) 的分數與區間。

注意：這是啟發式演算法，「通常」找到與 Smith-Waterman 相同或非常接近的
最佳本地比對，但不保證最優；換取的是實務上數個數量級的速度。

複雜度：設 query 長 n、db 長 m、seed 長 k、相似度閾值 w
    時間 ~ O(n + m + hits·extend)，常遠小於 O(nm)。
"""

from __future__ import annotations

from collections import defaultdict


def blast_search(
    query: str,
    db: str,
    k: int = 3,
    match: int = 2,
    mismatch: int = -1,
    xdrop: int = 2,
) -> list[tuple[int, int, int, int, int]]:
    """回傳 HSP 列表 (q_start, q_end, db_start, db_end, score)，依分數遞減。"""
    # 1. 建立 db 的 k-mer index
    index: dict[str, list[int]] = defaultdict(list)
    for i in range(len(db) - k + 1):
        index[db[i : i + k]].append(i)

    hsps: list[tuple[int, int, int, int, int]] = []
    seen: set[tuple[int, int]] = set()

    # 2. 找 seed
    for qi in range(len(query) - k + 1):
        word = query[qi : qi + k]
        for di in index.get(word, ()):
            if (qi, di) in seen:
                continue
            seen.add((qi, di))
            # 3. X-drop 延伸
            score, q_end, d_end = _extend_right(
                query, db, qi + k, di + k, match, mismatch, xdrop
            )
            score2, q_start, d_start = _extend_left(
                query, db, qi, di, match, mismatch, xdrop
            )
            total = score + score2 + k * match
            hsps.append((q_start, q_end, d_start, d_end, total))

    hsps.sort(key=lambda h: -h[4])
    return hsps


def _extend_right(
    q: str, db: str, i: int, j: int, match: int, mismatch: int, xdrop: int
) -> tuple[int, int, int]:
    best = cur = 0
    best_i, best_j = i, j
    while i < len(q) and j < len(db):
        cur += match if q[i] == db[j] else mismatch
        i, j = i + 1, j + 1
        if cur > best:
            best, best_i, best_j = cur, i, j
        elif best - cur > xdrop:
            break
    return best, best_i, best_j


def _extend_left(
    q: str, db: str, i: int, j: int, match: int, mismatch: int, xdrop: int
) -> tuple[int, int, int]:
    best = cur = 0
    best_i, best_j = i, j
    while i > 0 and j > 0:
        cur += match if q[i - 1] == db[j - 1] else mismatch
        i, j = i - 1, j - 1
        if cur > best:
            best, best_i, best_j = cur, i, j
        elif best - cur > xdrop:
            break
    return best, best_i, best_j


if __name__ == "__main__":
    db = "TTTTTTTTTTGGCTGAGCTATTTTTTTTTTT"
    query = "TCATAAGGCT"
    for hsp in blast_search(query, db):
        print(hsp)
