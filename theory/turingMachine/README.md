# 圖靈機 (Turing Machine)

圖靈機是 Alan Turing 在 1936 年提出的抽象計算模型，被認為是電腦科學的理論基石。

## 什麼是圖靈機？

圖靈機是一種抽象的計算設備，由以下組成：

```
┌─────────────────────────────────────────────────────────┐
│                      圖靈機                               │
├─────────────────────────────────────────────────────────┤
│  • 無限長度的磁帶 (Tape)                                 │
│  • 讀寫頭 (Head) - 可讀取、寫入、移動                    │
│  • 狀態寄存器 (State Register)                           │
│  • 轉移函數 (Transition Function)                       │
└─────────────────────────────────────────────────────────┘
```

## 形式定義

圖靈機 M = (Q, Σ, Γ, δ, q₀, q_accept, q_reject)

| 符號 | 意義 |
|------|------|
| Q | 狀態集合 |
| Σ | 輸入字母表（不含空白） |
| Γ | 磁帶字母表（含空白 □） |
| δ | 轉移函數 |
| q₀ | 起始狀態 |
| q_accept | 接受狀態 |
| q_reject | 拒絕狀態 |

## 轉移函數

```
δ(q, a) = (p, b, L/R)

含義：當處於狀態 q、讀到符號 a 時，
      轉移到狀態 p，寫入 b，向左(L)或向右(R)移動
```

## 程式實現

### TuringMachine 類別

```python
class TuringMachine:
    def __init__(self, states, ichars, ochars, actionMap, start, accepts, rejects):
        self.states = states       # Q: 狀態集合
        self.ichars = ichars       # Σ: 輸入字母表
        self.ochars = ochars       # Γ: 磁帶字母表
        self.actionMap = actionMap  # δ: 轉移函數
        self.start = start          # q₀: 起始狀態
        self.accepts = accepts      # q_accept: 接受狀態
        self.rejects = rejects      # q_reject: 拒絕狀態
    
    def run(self, tape):
        self.tape = list(tape + '________')  # 初始化磁帶
        state = self.start                         # 起始狀態
        i = 0                                      # 讀寫頭位置
        
        while True:
            ichar = self.tape[i]
            acts = self.action(state, ichar)
            if acts is None: return False  # 無轉移 → 拒絕
            
            state, ochar, move = acts
            self.tape[i] = ochar            # 寫入磁帶
            
            if move == 'L': i -= 1 if i > 0 else 0   # 左移
            elif move == 'R': i += 1                   # 右移
            
            if state in self.accepts: return True
            if state in self.rejects: return False
```

### 轉移函數格式

```python
actionMap = {
    '0,a': '1,_,R',   # δ(0, a) = (1, _, R)
    '1,b': '2,x,R',   # δ(1, b) = (2, x, R)
}
# 格式：'{state},{input}': '{next_state},{output},{move}'
```

## 範例：aⁿbⁿcⁿ 語言

**語言描述**: aⁿbⁿcⁿ (n ≥ 1)，如 `abc`, `aabbcc`, `aaabbbccc`

### 演算法思想

```
1. 讀取一個 a，標記為 x
2. 向右找到對應的 b，標記為 x
3. 向右找到對應的 c，標記為 x
4. 重複直到所有 a,b,c 都被處理
```

### 狀態圖

```
digraph TuringMachine_anbncn {
    rankdir=LR;
    
    node [shape = doublecircle]; 0 3;
    node [shape = circle];
    
    0 -> 1 [ label = "a/_,R" ];        # 讀a，標記為空
    1 -> 1 [ label = "a/a,R" ];         # 跳過a
    1 -> 1 [ label = "x/x,R" ];         # 跳過x
    1 -> 2 [ label = "b/x,R" ];         # 讀b，標記為x
    2 -> 2 [ label = "x/x,R" ];         # 跳過x
    2 -> 2 [ label = "b/b,R" ];         # 跳過b
    2 -> 5 [ label = "c/x,L" ];         # 讀c，標記為x
    5 -> 5 [ label = "x/x,L" ];         # 左移，跳過x
    5 -> 0 [ label = "_/_,R" ];         # 回到開頭
    0 -> 4 [ label = "x/x,R" ];         # 確認所有都處理
    0 -> 3 [ label = "_/_,L" ];         # 接受
    4 -> 4 [ label = "x/x,R" ];
    4 -> 3 [ label = "_/_,L" ];
}
```

### 執行軌跡 (abc)

```
磁帶: [a][b][c]________
位置:  0  1  2  3  4

狀態 0: 讀 a → 寫 _，右移 → 狀態 1
磁帶: [_][b][c]________

狀態 1: 讀 b → 寫 x，右移 → 狀態 2
磁帶: [_][x][c]________

狀態 2: 讀 c → 寫 x，左移 → 狀態 5
磁帶: [_][x][x]________

狀態 5: 左移，回到開頭
磁帶: [_][x][x]________
位置:  0  1  2

狀態 0: 讀 _ → 右移 → 狀態 4
磁帶: [_][x][x]________

狀態 4: 讀 x → 右移
磁帶: [_][x][x]________

狀態 4: 讀 _ → 左移 → 狀態 3 (接受)
```

### 完整轉移表

```python
tm = TuringMachine(
    states=['0','1','2','3','4','5'],
    ichars=['a','b','c'],
    ochars=['a','b','c','x','_'],
    actionMap={
        '0,a': '1,_,R',
        '1,a': '1,a,R',
        '1,x': '1,x,R',
        '1,b': '2,x,R',
        '2,x': '2,x,R',
        '2,b': '2,b,R',
        '2,c': '5,x,L',
        '5,x': '5,x,L',
        '5,a': '5,a,L',
        '5,b': '5,b,L',
        '5,_': '0,_,R',
        '0,x': '4,x,R',
        '0,_': '3,_,L',
        '4,x': '4,x,R',
        '4,_': '3,_,L',
    },
    start='0',
    accepts=['3'],
    rejects=[]
)
```

## 圖靈機的變體

### 單磁帶 → 多磁帶

多磁帶圖靈機可以平行處理，但計算能力相同。

### 圖靈機 vs DFA

| 特性 | DFA | 圖靈機 |
|------|-----|--------|
| 磁帶 | 無 | 無限 |
| 移動 | 只能前進 | 左/右/靜止 |
| 寫入 | 否 | 是 |
| 計算能力 | 正規語言 | 任何可計算問題 |

## 圖靈機的極限

### 停機問題 (Halting Problem)

> **不存在**一個圖靈機 H，能判斷任意圖靈機 M 在輸入 w 上是否會停止。

**證明思路**（反證法）:

假設存在 H(M, w)：
- 若 M 在 w 上停機，H 返回「是」
- 若 M 在 w 上不停機，H 返回「否」

構造悖論機器 P：
- 輸入 M
- 若 H(M, M) 返回「是」（即 M 在 M 上停機），則 P 進入無限循環
- 若 H(M, M) 返回「否」（即 M 在 M 上不停機），則 P 停機

問：P(P) 會停機嗎？
- 若停機 → H(P, P) 返回「是」→ P(P) 應該不停機 → 矛盾！
- 若不停機 → H(P, P) 返回「否」→ P(P) 應該停機 → 矛盾！

因此 H 不存在。

### entscheidungsproblem

> 是否存在一個演算法，能判斷任意數學陳述的真偽？

圖靈機證明了這是不可能的。

## Church-Turing 論點

> 任何可計算的函數都可以由圖靈機計算。

這個論點是不可證明的，因為「可計算」本身沒有精確定義，但它已被廣泛接受。

## 圖靈機的實際意義

### 通用圖靈機 (UTM)

圖靈機可以接受另一個圖靈機的描述作為輸入，模擬其執行。

這意味著：
- 軟體可以控制硬體（軟體定義行為）
- 電腦可以模擬其他電腦

### 現代電腦的理論基礎

```
圖靈機概念 (1936)
     ↓
馮紐曼架構 (1945)
     ↓
現代電腦 (1950s-)
```

## 執行測試

```bash
$ python TuringMachine.py
: False          # 空字串不接受
ab: False        # 不符合 aⁿbⁿcⁿ
abc: True        # 符合！
aabbc: False      # b 和 c 數量不符
aabbcc: True      # 符合！
```

## 複雜度理論

圖靈機也用於定義計算複雜度：

| 複雜度類別 | 定義 | 範例 |
|-----------|------|------|
| P | 多項式時間 | 排序、搜索 |
| NP | 非確定性多項式時間 | 旅行商問題 |
| PSPACE | 多項式空間 | 博弈問題 |
| EXPTIME | 指數時間 | 棋類遊戲 |

## 學習重點

1. **磁帶操作**: 讀、寫、移動
2. **狀態設計**: 如何用狀態表示「進度」
3. **符號標記**: 用額外符號記錄已處理位置
4. **停機判定**: 識別接受 vs 拒絕
5. **複雜度**: 理解 P vs NP 問題

## 視覺化工具

- [JFLAP](http://www.jflap.org/) - 互動式圖靈機模擬器
- [Turing Machine Simulator](https://turingmachinesimulator.com/)
- [edotor.net](https://edotor.net/) - 狀態圖繪製
