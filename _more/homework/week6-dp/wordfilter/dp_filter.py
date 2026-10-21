"""動態規劃解法：敏感詞過濾（trie + DP 模糊匹配，容忍 ≤k 編輯距離）。

原理
    把敏感詞建成 trie；對文字的每個起始位置 i，在 trie 上跑
    「編輯距離 ≤ k」的 DP 逐層往下走。
    狀態 dp[node][j] = 文字第 i 位起、走到 trie node、已花費 j 編輯距離。
    若在某 node 是詞尾且 j ≤ k，即命中（模糊敏感詞）。

優勢：一次掃過 trie 即可同時匹配所有敏感詞的「近似變體」
（如「习大大」→「习大大」等諧音/錯字變體），這是純精確 AC 機做不到的。

複雜度：設文字長 L、敏感詞 trie 節點數 T、容忍距離 k
    時間 O(L · k · T_child)，空間 O(T · k)。

精確匹配（k=0）時退化為 trie 掃描。
"""

from __future__ import annotations


class TrieNode:
    __slots__ = ("children", "word_end", "word")

    def __init__(self) -> None:
        self.children: dict[str, TrieNode] = {}
        self.word_end = False
        self.word: str | None = None


def build_trie(words: list[str]) -> TrieNode:
    root = TrieNode()
    for w in words:
        node = root
        for ch in w:
            node = node.children.setdefault(ch, TrieNode())
        node.word_end = True
        node.word = w
    return root


def dp_scan(text: str, words: list[str], k: int = 0) -> list[tuple[int, str, int]]:
    """回傳命中列表 (起始位置, 詞, 編輯距離)，詞尾距離 <= k 即命中。"""
    root = build_trie(words)
    hits: list[tuple[int, str, int]] = []
    n = len(text)
    for i in range(n):
        # prev[j] = 上一層（深度 d）編輯距離為 j 的最佳節點集合 → 用 dict: node -> min cost
        # BFS 式 DP：cur 層的 (node, cost)
        cur: dict[TrieNode, int] = {root: 0}
        for d in range(i, n):
            ch = text[d]
            nxt: dict[TrieNode, int] = {}
            for node, cost in cur.items():
                # 命中檢查（詞尾）
                if node.word_end and cost <= k:
                    hits.append((i, node.word or "", cost))
                if cost > k:
                    continue
                # 完全匹配：往下走
                if ch in node.children:
                    cnode = node.children[ch]
                    if cost < nxt.get(cnode, k + 1):
                        nxt[cnode] = cost
                # 編輯操作：插入/取代/刪除——在 trie 上等價於「跳過文字」或「跳過 trie 節點」
                # 插入（多打字，文字不動）：在同一 trie 位置多走一步
                for c2, cnode2 in node.children.items():
                    if cost + 1 < nxt.get(cnode2, k + 1):
                        nxt[cnode2] = cost + 1  # 取代
                    if cost + 1 < nxt.get(node, k + 1):
                        nxt[node] = cost + 1  # 插入（消耗文字字元不動 trie）
            cur = nxt
            if not cur:
                break
        # 補上末尾的詞尾檢查
        for node, cost in cur.items():
            if node.word_end and cost <= k:
                hits.append((i, node.word or "", cost))
    return hits


if __name__ == "__main__":
    words = ["敏感詞", "壞人", "垃圾"]
    text = "這是敏感词和垃圾東西"
    for h in dp_scan(text, words, k=1):
        print(h)
