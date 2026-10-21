"""非動態規劃解法：Boyer-Moore 單字搜尋（精確匹配）。

原理
    從 pattern 右端往左比較；失配時根據兩個啟發式跳躍：
      1. 壞字元 (bad character)：失配字元 x 在 pattern 中最右出現位置
         → bad_char[c] = max{ i : p[i]==c }，跳 max(1, j - bad_char[x])
      2. 好後綴 (good suffix)：已匹配的後綴在 pattern 中其他出現位置
         → 用後綴表跳，處理「好後綴是別處前綴」的情形
    兩者取較大跳量。

複雜度
    預處理 O(m·σ) + O(m)；搜尋平均 O(n/m)（最佳）、最壞 O(n·m)。
    實務上是「精確單字串搜尋」最快的通用演算法之一（grep 的 BM 模式）。

注意：BM 做的是「精確匹配」；模糊定位（容忍錯字）需要編輯距離 DP。
兩者解決的是 word search 的不同變體——這正是 DP 與非 DP 的分工。
"""

from __future__ import annotations


def boyer_moore(text: str, pattern: str) -> list[int]:
    """回傳 pattern 在 text 中所有出現的起始位置。"""
    if not pattern:
        return []
    n, m = len(text), len(pattern)
    # 壞字元表
    bad = {c: i for i, c in enumerate(pattern)}
    # 好後缀表：suffix[i] = 與後綴 p[i:] 相同的最右其他位置，-1 表無
    suffix = _build_suffix(pattern)
    # good[i] = 後綴 p[i:] 失配時可跳的距離
    good = [m] * m
    j = m
    for i in range(m - 1, -1, -1):
        if _is_border(pattern, i):
            j = i
        good[i] = j - i if j < m else m - i
        # 處理好後綴完全不出現但有前綴匹配情形 → 直接用 m 跳
    results = []
    s = 0
    while s <= n - m:
        j = m - 1
        while j >= 0 and pattern[j] == text[s + j]:
            j -= 1
        if j < 0:
            results.append(s)
            s += 1
        else:
            skip_bc = j - bad.get(text[s + j], -1)
            skip_bs = good[j]
            s += max(1, skip_bc, skip_bs)
    return results


def _build_suffix(pattern: str) -> list[int]:
    m = len(pattern)
    suffix = [-1] * m
    for i in range(m - 1):
        for j in range(i, -1, -1):
            if pattern[m - 1 - i : m] == pattern[m - 1 - j - i : m - 1 - j]:
                suffix[i] = m - 1 - j - i
            else:
                break
    return suffix


def _is_border(pattern: str, i: int) -> bool:
    """p[i:] 是否為 pattern 的前綴 border（好後綴出現在開頭）。"""
    return pattern[i:] == pattern[: len(pattern) - i]


if __name__ == "__main__":
    print(boyer_moore("ababcababcabc", "abc"))
    print(boyer_moore("aaaaaa", "aa"))
