"""非動態規劃解法：Myers O(ND) diff 演算法 (1986)。

核心思想
    不求 LCS 表，而是把問題看成在編輯圖 (edit graph) 上找
    從 (0,0) 到 (N,M)、只允許向右(插入)/向下(刪除)/對角(相同)移動
    的最短路徑。D = 編輯次數 = N + M - 2*LCS。
    對每個對角線 k = x - y，只追蹤該對角線最右的 x (V[k])，
    用「蛇行 (snake)」延伸相同字元，逐層擴展 D。

複雜度
    時間 O(ND)、空間 O(D)；D 為兩檔差異大小，通常遠小於 N+M，
    所以實際比 O(NM) 的 LCS DP 快很多。
"""

from __future__ import annotations


def myers_diff(a: str, b: str) -> list[tuple[str, str]]:
    """回傳 op 列表：('=', ch) / ('-', ch) 刪除 / ('+', ch) 插入。"""
    n, m = len(a), len(b)
    max_d = n + m
    v: dict[int, int] = {1: 0}
    # 為了回溯，記錄每層 D 的 V 快照
    trace: list[dict[int, int]] = []
    for d in range(max_d + 1):
        trace.append(dict(v))
        for k in range(-d, d + 1, 2):
            if k == -d or (k != d and v.get(k - 1, -1) < v.get(k + 1, -1)):
                x = v.get(k + 1, 0)  # 向下 (插入 b 的字元)
            else:
                x = v.get(k - 1, 0) + 1  # 向右 (刪除 a 的字元)
            y = x - k
            while x < n and y < m and a[x] == b[y]:
                x, y = x + 1, y + 1  # 蛇行：對角線延伸
            v[k] = x
            if x >= n and y >= m:
                return _backtrack(a, b, d, trace)
    raise RuntimeError("unreachable")


def _backtrack(
    a: str, b: str, d: int, trace: list[dict[int, int]]
) -> list[tuple[str, str]]:
    ops: list[tuple[str, str]] = []
    x, y = len(a), len(b)
    for dd in range(d, 0, -1):
        v_prev = trace[dd]
        k = x - y
        if k == -dd or (k != dd and v_prev.get(k - 1, -1) < v_prev.get(k + 1, -1)):
            prev_k = k + 1
        else:
            prev_k = k - 1
        prev_x = v_prev.get(prev_k, 0)
        prev_y = prev_x - prev_k
        # 蛇行段
        while x > prev_x and y > prev_y:
            x, y = x - 1, y - 1
            ops.append(("=", a[x]))
        if x == prev_x:
            ops.append(("+", b[y - 1]))  # 向下：插入
            y -= 1
        else:
            ops.append(("-", a[x - 1]))  # 向右：刪除
            x -= 1
    while x > 0 and y > 0:
        x, y = x - 1, y - 1
        ops.append(("=", a[x]))
    ops.reverse()
    return ops


if __name__ == "__main__":
    for op, ch in myers_diff("ABCABBA", "CBABAC"):
        print(op, ch)
