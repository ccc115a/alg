# aho_corasick_nondp.py — Aho-Corasick 多模式自動機

## 用途

一次掃描文字，同時匹配數千～數百萬個敏感詞（精確匹配），
是 grep、IDS、敏感詞過濾的工業標準。

## 類別與函式

| 名稱 | 說明 |
|---|---|
| `AhoCorasick(words)` | 建 trie + fail link + output link |
| `AhoCorasick.search(text)` | 回傳 `(結束位置, 命中詞)` 列表 |
| `aho_filter(text, words)` | 回傳 `(開始位置, 結束位置, 詞)` |

## 原理（三步構造）

### 1. 建 trie

所有敏感詞插入同一棵 trie；詞尾節點記錄完整詞。

### 2. BFS 建 fail link

對每個狀態 `s`，其 fail 指向「最長真後綴仍是有效 trie 路徑」的狀態：

```
state = fail[r]
while state and ch not in goto[state]: state = fail[state]
fail[s] = goto[state].get(ch, 0)
```

失配時沿 fail 跳，等價於「退到最長可續匹配的後綴」。

### 3. 合併 output link

```
output[s] += output[fail[s]]
```

若 fail 指到詞尾，則 `s` 也視為命中（處理子串命中，
如「敏感詞典」含「敏感詞」）。

## 掃描

```
state = 0
for i, ch in enumerate(text):
    while state and ch not in goto[state]: state = fail[state]
    state = goto[state].get(ch, 0)
    收集 output[state] 所有命中
```

每字元均攤 **O(1)**（沿 fail 的總步數被攤平）。

## 複雜度

- 建 trie **O(Σ|word|)**
- 建 fail **O(Σ|word| · σ)** 或路徑壓縮後 O(Σ|word|)
- 掃描 **O(全文長 + 命中數)** — 與詞庫大小幾乎無關

## 與 DP 的關係

fail link 本質上是「最長後綴匹配」的轉移表，
可視為自動機視角的多模式動態規劃；
而 trie+DP（見 `dp_filter.py`）加上編輯距離後能做模糊匹配，
但代價隨詞庫成長——兩者分工明確。
