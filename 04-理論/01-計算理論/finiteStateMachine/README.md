# 有限狀態機 (Finite State Machine)

有限狀態機（FSM）是計算理論中最簡單的計算模型，用於識別正則語言。

## 什麼是有限狀態機？

有限狀態機是一種抽象的計算模型，由以下組成：

```
┌────────────────────────────────────────────┐
│              有限狀態機 (FSM)                │
├────────────────────────────────────────────┤
│  • 有限的狀態集合 Q                         │
│  • 輸入字母表 Σ                            │
│  • 轉移函數 δ: Q × Σ → Q                   │
│  • 起始狀態 q₀ ∈ Q                         │
│  • 接受狀態集合 F ⊆ Q                       │
└────────────────────────────────────────────┘
```

## 確定性 vs 非確定性

### DFA (Deterministic)
- 每個狀態對每個輸入只有**一個**轉移
- 記憶體需求：O(1)

### NFA (Non-deterministic)
- 每個狀態對每個輸入可能有**多個**轉移
- ε-轉移（空字元轉移）
- 任何 NFA 都可以轉換為等價的 DFA

## 程式實現

### FSM 核心類別

```python
class FiniteStateMachine:
    def __init__(self, start, finals, actionMap):
        self.actionMap = actionMap  # 轉移表
        self.start = start          # 起始狀態
        self.finals = finals        # 接受狀態集合
    
    def accept(self, s):
        state = self.start
        i = 0
        while i < len(s):
            # 查詢轉移表：'state,input' → next_state
            state = self.actionMap.get(f'{state},{s[i]}')
            if state is None: return False  # 無轉移 → 拒絕
            i += 1
        return state in self.finals  # 最終狀態是否為接受狀態
```

### 轉移表表示法

```python
# actionMap 的鍵格式：'{current_state},{input_symbol}'
fsm = FiniteStateMachine('s0', ['s1'], {
    's0,a': 's1',
    's1,b': 's2',
    's2,c': 's2',
})
```

## 範例：aⁿbᵐ 語言

**語言描述**: 以任意數量 `a` 開頭，後面跟著一個或多個 `b` 的字串

```python
# anbm.py
fsm = FiniteStateMachine('s1', ['s2'], {
    's1,a': 's1',  # s1: 讀取 a，保持 s1
    's1,b': 's2',  # s1 → s2: 讀到第一個 b
    's2,b': 's2',  # s2: 繼續讀取 b
})
```

**狀態圖**:
```
      a
┌─────────┐
↓         │
(s1)──────┘
│ a       ↓ b
↓         (s2) ←── b
│
└───────── (拒絕)
```

**測試**:
```bash
$ python anbm.py
a: False      # 只有 a，沒有 b
aab: True     # 符合模式
aabaa: False  # b 後面不能有 a
aabbb: True   # 多個 b 也符合
```

## 範例：偶數個 0

**語言描述**: 包含偶數個 `0` 的二進位字串

```python
# even0.py
fsm = FiniteStateMachine('s1', ['s1'], {
    's1,0': 's2',  # 讀到 0：奇數個 → s2
    's1,1': 's1',  # 讀到 1：狀態不變
    's2,0': 's1',  # 讀到 0：偶數個 → s1
    's2,1': 's2',  # 讀到 1：狀態不變
})
```

**狀態圖**:
```
        1
   ┌─────────────┐
   ↓  0          │
(s1)─────────(s2)
   ↑             │
   └────── 1 ────┘
```

**狀態意義**:
- `s1`: 到目前為止讀到**偶數**個 0
- `s2`: 到目前為止讀到**奇數**個 0

## 範例：任意數量 a

**語言描述**: 只包含 `a` 的字串（空字串也接受）

```python
# an.py
fsm = FiniteStateMachine('s0', ['s0'], {
    's0,a': 's0'  # 持續讀取 a，保持 s0
})
```

因為 `s0` 是起始狀態也是接受狀態，所以：
- 空字串 → 在 `s0` → 接受 ✓
- `aaa` → 一直在 `s0` → 接受 ✓
- `aab` → 無 `s0,a` 轉移 → 拒絕 ✗

## FSM 的限制

有限狀態機**無法**識別以下語言：

| 語言 | 原因 |
|------|------|
| aⁿbⁿ (n≥1) | 需要記憶計數器 |
| aⁿbⁿcⁿ (n≥1) | 需要兩個計數器 |
| 匹配的括號 | 需要棧來追蹤深度 |

這些語言需要更強大的計算模型（如 PDA 或 Turing Machine）。

## 正則語言的封閉性

正則語言對以下運算封閉：
- **聯集**: A ∪ B
- **連接**: A · B
- **Kleene 星號**: A*
- **補集**: ¬A
- **交集**: A ∩ B

## 與其他模型的關係

```
正則表達式 (Regex)
       ↓ 等價
有限狀態機 (FSM)
       ↓ 等價
正則文法 (Regular Grammar)
       ↓ 等價
正則表達式 (Regular Expression)
```

## 實際應用

1. **詞彙分析器 (Lexer)**: 正則表達式 → NFA → DFA
2. **協定設計**: TCP 狀態機、HTTP 狀態碼
3. **硬體設計**: 數位電路、狀態機
4. **遊戲 AI**: 狀態機器人

## 學習重點

1. **狀態設計**: 如何用狀態表示「記憶」
2. **轉移函數**: 完整處理所有輸入
3. **接受條件**: 最終狀態是否在接受集合
4. **DFA 化簡**: 最少狀態數

## 執行測試

```bash
$ python finiteStateMachine.py
aaa: True
aab: False
010: True
101: False
```
