# 計算理論 (Theory of Computation)

本目錄收錄了計算理論的核心主題，從基礎的有限狀態機到萬能的圖靈機，展示了計算的本質與極限。

## 目錄

| 主題 | 說明 | 核心概念 |
|------|------|----------|
| [finiteStateMachine/](finiteStateMachine/README.md) | 有限狀態機 | DFA、狀態轉移 |
| [grammar/](grammar/README.md) | 形式文法 | CFG、Chomsky 階層 |
| [lambda/](lambda/README.md) | Lambda 演算 | 閉包、Y Combinator |
| [turingMachine/](turingMachine/README.md) | 圖靈機 | 停機問題、Church-Turing 論點 |

## 計算理論的層次結構

```
┌─────────────────────────────────────────────────────────┐
│                    Turing Machine                        │
│                 (圖靈機 - 完整計算能力)                    │
├─────────────────────────────────────────────────────────┤
│                   Lambda Calculus                        │
│                 (λ 演算 - 函數式計算)                     │
├─────────────────────────────────────────────────────────┤
│               Context-Free Grammar                       │
│              (上下文無關文法 - 程式語言語法)                 │
├─────────────────────────────────────────────────────────┤
│              Regular Expression / FSM                    │
│            (正規表達式 / 有限狀態機)                       │
└─────────────────────────────────────────────────────────┘
```

## Chomsky 語言階層

| 層次 | 名稱 | 語法類型 | 自動機 | 範例 |
|------|------|----------|--------|------|
| Type 0 | 無限制文法 | 任意規則 | 圖靈機 | 任意語言 |
| Type 1 | 上下文相關 | αAβ → αγβ | 線性有界自動機 | aⁿbⁿcⁿ |
| Type 2 | 上下文無關 | A → γ | 下推自動機 | aⁿbⁿ |
| Type 3 | 正規文法 | A → aB, A → a | 有限狀態機 | a* |

## 計算的三大問題

### 1. 停機問題 (Halting Problem)
> 不存在一個程式能判斷任意程式是否會停止。

這是 Turing 在 1936 年證明的，是計算理論中最著名的不可判定問題。

### 2. 圖靈機的通用性
> 圖靈機可以模擬任何其他圖靈機。

這導致了通用圖靈機的概念，為現代電腦的理論基礎。

### 3. Church-Turing 論點
> Lambda 演算與圖靈機具有相同的計算能力。

這確立了「可計算性」的數學定義。

## 為什麼學習計算理論？

1. **理解語言設計**: 正規文法 → RE, CFG → 程式語言語法
2. **掌握編譯器原理**: Lexer/Parser 的理論基礎
3. **認識計算極限**: 什麼能算、什麼不能算
4. **培養抽象思維**: 從具體機器到抽象模型

## 執行方式

```bash
# 有限狀態機
cd finiteStateMachine
python an.py          # 接受任意數量的 a
python even0.py       # 接受包含偶數個 0 的二進位串
python anbm.py        # 接受 a開頭、後面跟著 b 的字串

# 形式文法
cd grammar
python anbn.py        # 產生 aⁿbⁿ 形式的字串
python anbncn.py       # 產生 aⁿbⁿcⁿ (上下文相關)
python english.py      # 產生簡單英文句子

# Lambda 演算
cd lambda
cd 01-full && python lambdaCalculus.py    # 完整實現
cd 02-short && python lambdaCalculus.py   # 精簡實現
cd 03-interpreter && python lambda.py program.lc

# 圖靈機
cd turingMachine
python TuringMachine.py    # 測試 aⁿbⁿcⁿ 語言
```
