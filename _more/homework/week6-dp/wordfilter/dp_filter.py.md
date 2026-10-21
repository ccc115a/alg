# dp_filter.py — trie + DP 模糊敏感詞過濾

## 用途

在文字中偵測敏感詞及其「編輯距離 ≤ k」的變體（錯字、簡繁差、諧音近形字）。

## 類別與函式

| 名稱 | 說明 |
|---|---|
| `TrieNode` | trie 節點（children / word_end / word） |
| `build_trie(words)` | 建立敏感詞 trie |
| `dp_scan(text, words, k=0)` | 回傳 `(起始位置, 詞, 編輯距離)`，距離 ≤ k 即命中 |

## 原理

把敏感詞建成 trie；從文字每個位置 `i` 出發，在 trie 上跑
「編輯距離 ≤ k」的逐層 DP。走到 trie 詞尾且累計花費 ≤ k 即命中。

## 狀態定義

```
cur[node] = 從起始位置 i 出發、走到 trie node、所需的最小編輯距離
```

每讀一個文字字元，對 `cur` 中每個 `(node, cost)` 做轉移得到下一層 `nxt`。

## 轉移方程

對每個 `(node, cost)`（`cost ≤ k`）：

| 操作 | trie 上的動作 | 花費 |
|---|---|---|
| 完全匹配 | `nxt[node.children[ch]] = min(現值, cost)` | +0 |
| 取代 | `nxt[node.children[c2]] = min(…, cost+1)` 對每個 c2≠ch | +1 |
| 插入（文字多打字） | `nxt[node] = min(…, cost+1)`（同 node 多走一個 trie 字元） | +1 |
| 刪除（文字漏字） | 由下一層「同 node 轉移」隱含處理（跳過文字字元不動 trie） | +1 |

詞尾檢查：`node.word_end and cost <= k` → 命中 `(i, node.word, cost)`。

## 複雜度

- 每起始位置 O(k · trie 節點 × branching)，全部 **O(L·k·T)**
- k=0 時退化為精確 trie 掃描

## 特性

- 能抓變體：「敏感词」（簡體词≠詞）在 k=1 下命中「敏感詞」
- 詞庫一大就慢（每位置都可能展開整個 trie）→ 海量詞庫用 AC 自動機
  （見 `aho_corasick_nondp.py`）
- 實務常兩層：AC 精確快掃 + trie+DP 對可疑片段精驗
