"""非動態規劃解法：Aho-Corasick 多模式精確匹配自動機（海量敏感詞過濾）。

原理（AC 自動機，1975）
    1. 把所有敏感詞建成 trie。
    2. BFS 建 fail link：每個節點指向「最長真後綴仍匹配的節點」。
    3. 輸出鏈 (output link)：fail 指到詞尾時也視為命中（處理「敏感詞」
       作為更長詞的子串，如「敏感詞典」命中「敏感詞」）。
    4. 掃描文字時維持當前自動機狀態，每讀一字元沿 trie 走、失配跳 fail，
       沿 output 鏈收集所有命中。

複雜度：建機 O(Σ|word|)、掃描 O(全文長 + 命中數)，
與敏感詞數量幾乎無關——這是過濾百萬級詞庫的工業標準。
"""

from __future__ import annotations

from collections import deque


class AhoCorasick:
    def __init__(self, words: list[str]):
        # trie
        self.goto: list[dict[str, int]] = [{}]
        self.fail: list[int] = [0]
        self.output: list[list[str]] = [[]]
        for w in words:
            node = 0
            for ch in w:
                if ch not in self.goto[node]:
                    self.goto[node][ch] = len(self.goto)
                    self.goto.append({})
                    self.fail.append(0)
                    self.output.append([])
                node = self.goto[node][ch]
            self.output[node].append(w)
        # fail link (BFS)
        q: deque[int] = deque()
        for ch, nxt in self.goto[0].items():
            self.fail[nxt] = 0
            q.append(nxt)
        while q:
            r = q.popleft()
            for ch, s in self.goto[r].items():
                q.append(s)
                state = self.fail[r]
                while state and ch not in self.goto[state]:
                    state = self.fail[state]
                self.fail[s] = self.goto[state].get(ch, 0)
                self.output[s] += self.output[self.fail[s]]

    def search(self, text: str) -> list[tuple[int, str]]:
        """回傳 (結束位置, 命中詞) 列表。"""
        results: list[tuple[int, str]] = []
        state = 0
        for i, ch in enumerate(text):
            while state and ch not in self.goto[state]:
                state = self.fail[state]
            state = self.goto[state].get(ch, 0)
            for w in self.output[state]:
                results.append((i, w))
        return results


def aho_filter(text: str, words: list[str]) -> list[tuple[int, str, str]]:
    """回傳 (開始位置, 結束位置, 詞)；開始位置 = 結束位置 - len(詞) + 1。"""
    ac = AhoCorasick(words)
    return [(i - len(w) + 1, i, w) for i, w in ac.search(text)]


if __name__ == "__main__":
    words = ["敏感詞", "壞人", "垃圾", "敏感"]
    text = "這是敏感詞和垃圾東西，也有敏感詞典"
    for h in aho_filter(text, words):
        print(h)
