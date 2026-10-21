"""動態規劃解法：Smith-Waterman 本地比對 (local alignment)。

狀態定義
    H[i][j] = 以 a[0..i-1] 結尾、b[0..j-1] 結尾的最佳本地比對分數。

轉移方程
    H[i][j] = max(0,                          # 重新起點
                  H[i-1][j-1] + s(a[i-1], b[j-1]),  # 對角：配對/錯配
                  H[i-1][j] + gap,            # 刪除
                  H[i][j-1] + gap)            # 插入
    其中 s(match)=+2, s(mismatch)=-1, gap=-1（可調）。

從分數最大的格子往回追溯即可得到最優本地比對區段。
複雜度：時間 O(nm)、空間 O(nm)（可優化到 O(min(n,m)) 只求分數）。
"""

from __future__ import annotations


def smith_waterman(
    a: str,
    b: str,
    match: int = 2,
    mismatch: int = -1,
    gap: int = -1,
) -> tuple[int, tuple[int, int], tuple[int, int]]:
    """回傳 (最高分, a 上區間 [start,end), b 上區間 [start,end))。"""
    n, m = len(a), len(b)
    H = [[0] * (m + 1) for _ in range(n + 1)]
    best, best_pos = 0, (0, 0)
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            s = match if a[i - 1] == b[j - 1] else mismatch
            H[i][j] = max(
                0,
                H[i - 1][j - 1] + s,
                H[i - 1][j] + gap,
                H[i][j - 1] + gap,
            )
            if H[i][j] > best:
                best, best_pos = H[i][j], (i, j)
    # 回溯
    i, j = best_pos
    end_a, end_b = i, j
    while i > 0 and j > 0 and H[i][j] > 0:
        s = match if a[i - 1] == b[j - 1] else mismatch
        if H[i][j] == H[i - 1][j - 1] + s:
            i, j = i - 1, j - 1
        elif H[i][j] == H[i - 1][j] + gap:
            i -= 1
        else:
            j -= 1
    return best, (i, end_a), (j, end_b)


if __name__ == "__main__":
    score, ia, ib = smith_waterman("TCATAAGGCT", "GGCTGAGCTA")
    print(f"score={score} a[{ia[0]}:{ia[1]}] b[{ib[0]}:{ib[1]}]")
