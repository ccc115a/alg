# 形式文法 (Formal Grammar)

形式文法是描述語言的數學工具，定義了如何產生合法的字串。

## 什麼是形式文法？

形式文法 G 由四個元素組成：

```
G = (N, Σ, P, S)

其中：
  N  - 非終結符集合 (Non-terminals)
  Σ  - 終結符集合 (Terminals)
  P  - 產生式規則集合 (Productions)
  S  - 起始符號 (Start Symbol)
```

## 產生式規則

產生式規則的形式：`α → β`

意思是「將 α 替換為 β」

**範例**:
```
S → aSb
S → ε
```

這表示：S 可以產生 aSb，或者產生空字串 ε。

## Chomsky 語言階層

| 層次 | 名稱 | 規則形式 | 自動機 | 表达能力 |
|------|------|----------|--------|----------|
| Type 0 | 無限制 | α → β (α ≠ ε) | 圖靈機 | 完整 |
| Type 1 | 上下文相關 | αAβ → αγβ | 線性有界 | 中等 |
| Type 2 | 上下文無關 | A → γ | 下推自動機 | 足夠 |
| Type 3 | 正規 | A → a, A → aB | 有限狀態機 | 有限 |

## 程式實現

### 文法產生器

```python
from random import *

def gen(G):
    lefts = list(G.keys())
    rule = " S "  # 從起始符號開始
    
    while True:
        # 找到第一個非終結符
        for left0 in lefts:
            left = f' {left0} '
            i = rule.find(left)
            if i != -1:
                # 隨機選擇一個產生式
                rights = G[left0]
                ri = randrange(0, len(rights))
                right = f' {rights[ri]} '
                
                # 替換
                rule = rule[0:i] + right + rule[i+len(left):]
                print(rule)
                
                # 全部都是終結符 → 完成
                if rule == rule.lower():
                    return rule
                break
```

### 產生式定義格式

```python
G = {
    "S": ["a S b", "ε"],  # 終結符用小寫或符號
    "A": ["a A", "a"],    # 非終結符用大寫
}
```

## 範例：aⁿbⁿ 語言（上下文無關）

**語言描述**: 任意數量的 a 後面跟著相同數量的 b

```python
# anbn.py
G = {
    "S": ["a S b", "a b"]  # 遞迴產生對稱的 a...b
}
```

**產生過程**:
```
 S
a S b
a a b b      ← a b
a a a b b b  ← a a b b b
```

**狀態轉換圖**:
```
S ──a──→ S ──a──→ S
 ↑               ↓
 └────── b ←─────┘
```

## 範例：aⁿbⁿcⁿ 語言（上下文相關）

這是**無法**用上下文無關文法產生的語言，需要上下文相關文法。

```python
# anbncn.py
G = {
    "S": ["a B C", "a S B C"],
    
    # 交換 B 和 C 的位置 (上下文相關)
    "C B": ["C Z"],
    "C Z": ["W Z"],
    "W Z": ["W C"],
    "W C": ["B C"],
    
    # 轉換為小寫
    "a B": ["a b"],
    "b B": ["b b"],
    "b C": ["b c"],
    "c C": ["c c"]
}
```

**產生過程**:
```
S
a B C
a a B C C
a a b C C     (a B → a b)
a a b c C     (b C → b c)
a a b c c     (c C → c c)
```

**為什麼是上下文相關？**

規則 `C B → C Z` 需要 B 在 C 左邊時才能應用——這是「上下文」的概念。

## 範例：英語句子產生

### 簡單版本

```python
# english.py
G = {
    "S": ["NP VP"],
    "NP": ["D N"],
    "VP": ["V NP"],
    "N": ["dog", "cat"],
    "V": ["eat", "chase"],
    "D": ["a", "the"]
}
```

**產生結果**:
```
 S
NP VP
D N VP
the N VP
the dog VP
the dog V NP
the dog chase NP
the dog chase D N
the dog chase a cat
```

### 形容詞版本

```python
# english2.py
G = {
    "S": ["NP VP"],
    "NP": ["D N", "D A N"],  # 可以有形容詞
    "A": ["black", "white", "little", "big"],
    # ...
}
```

### 關係子句版本

```python
# english3.py
G = {
    "S": ["NP VP", "NP VP PP"],
    "PP": ["that NP V"],  # 關係子句
    # ...
}
```

## 範例：算術表達式

```python
# exp.py
G = {
    "S": ["E"],
    "E": ["T", "T + E", "T - E", "T * E", "T / E"],
    "T": ["N", "( E )"],
    "N": ["x", "y", "0", "1", "2"]
}
```

**產生的表達式**:
```
x + y * 2
x * y - ( 1 + 2 )
```

## 文法與自動機的對應

```
┌────────────────────────────────────────────────────────────┐
│                      編譯器前端                              │
├────────────────────────────────────────────────────────────┤
│  原始碼                                                     │
│     ↓                                                      │
│  [正規表達式] ────────→ [Lexer/FSM]                        │
│     ↓                                                      │
│  [上下文無關文法] ──→ [Parser/PDA]                         │
│     ↓                                                      │
│  [語法樹/AST]                                               │
└────────────────────────────────────────────────────────────┘
```

## 自上而下 vs 自下而上解析

| 方法 | 策略 | 問題 |
|------|------|------|
| LL(1) | 自上而下、遞歸下降 | 左遞迴、無法處理歧義 |
| LR(1) | 自下而上、移位歸約 | 建表複雜、錯誤訊息差 |

## 歧義性文法

有些文法對同一輸入有多種解析方式：

```python
# 歧義：2 + 3 * 4
# 可以理解為 (2 + 3) * 4 = 20
# 或 2 + (3 * 4) = 14
```

**解決方法**:
1. 重新設計文法（消除歧義）
2. 加入語意規則（運算子優先順序）
3. 使用 GLR 解析器

## 實際應用

1. **程式語言語法**: C、Java、Python 的語法定義
2. **JSON/XML**: 標記語言的結構定義
3. **SQL**: 資料庫查詢語言
4. **網路協定**: HTTP、TCP 的狀態描述

## 執行測試

```bash
$ python anbn.py
 S
 a S b
 a a b b
 a a a b b b

$ python english.py
 S
 NP VP
 D N VP
 the dog V NP
 the dog eat D N
 the dog eat a cat

$ python exp.py
 E
 T * E
 x * T + E
 x * y + N
 x * y + 2
```

## 學習重點

1. **規則設計**: 如何用規則描述語言結構
2. **終結 vs 非終結**: 什麼時候該引入新的非終結符
3. **遞迴結構**: 表達重複和巢狀
4. **語言證明**: 數學歸納法證明文法正確性
