# Lambda 演算 (Lambda Calculus)

**標籤**: #Lambda演算 #函數式 #Church編碼 #Y_Combinator #計算理論
**日期**: 2024-01-15
**更新**: 2026-04-27

Lambda 演算是阿隆佐·丘奇（Alonzo Church）在 1936 年發明的計算模型，與圖靈機等價，是函數式編程的理論基礎。與圖靈機從狀態和轉移的角度描述計算不同，Lambda 演算從函數的角度描述計算，強調函數的應用和代換。這種視角對現代程式語言的設計，特別是函數式程式語言，產生了深遠的影響。

## 歷史背景

1936 年，丘奇為了研究希爾伯特的判定問題，提出了 Lambda 演算。同一年，圖靈也提出了圖靈機模型。後來證明這兩種計算模型是等價的——任何一種可以計算的函數，另一種也可以計算。

這一發現奠定了 Church-Turing 論點的基礎：任何「可有效計算」的函數都可以用 Lambda 演算或圖靈機來表示。

## 核心語法

Lambda 演算的語法非常精簡，只有三種表達式：

```
項 (Term) ::= 變數 x
            | λ 變數 . 項     (抽象/函數定義)
            | (項 項)          (應用/函數呼叫)
```

**語法範例**：
```
λx.x           # 恆等函數：接受 x 並返回 x
λx.λy.x       # 雙參數函數（柯里化）：先接受 x，返回一個接受 y 並返回 x 的函數
(λx.x) y      # 應用：將 y 傳給恆等函數
```

這個簡單的語法系統雖然看起來非常基本，但卻具有極為強大的表達能力。

## 三種轉換規則

Lambda 演算中有三個重要的轉換規則，它們定義了函數如何被操作和求值：

### α轉換 (Alpha Conversion)

α轉換允許更改函數的參數名稱而不改變其語義。這是因為參數名稱只是綁定變數的佔位符，其具體名稱並不重要。

```
λx.M = λy.M[x/y]
```

這裡 M[x/y] 表示將 M 中所有自由出現的 x 替換為 y。進行α轉換時需要注意避免捕獲自由變數。

### β歸約 (Beta Reduction)

β歸約是函數應用的核心規則。當我們將一個函數應用於一個參數時，我們用參數替換函數體中的綁定變數。

```
(λx.M) N → M[x/N]
```

這表示：將 λx.M 應用於 N，相當於將 M 中的 x 替換為 N。

例如：
- (λx.x) y → y （應用恆等函數）
- (λx.x) (λy.y) → λy.y （函數作為參數）
- (λx.λy.x) a b → a （柯里化應用）

### η轉換 (Eta Conversion)

η轉換反映了函數的 extensionality 原則：如果兩個函數對所有參數都產生相同的結果，則它們是等價的。

```
λx.(M x) = M   (前提：x 不在 M 中自由出現)
```

這個規則說明：一個接受參數 x 並將 M 應用於 x 的函數，等價於 M 本身。

## Church 編碼

Church 編碼是一種用 Lambda 演算表示資料結構的方法，它展示了 Lambda 演算的強大表達能力。

### 布爾值

在 Lambda 演算中，布爾值可以這樣表示：

```
TRUE  = λx.λy.x    # 返回第一個參數
FALSE = λx.λy.y   # 返回第二個參數
IF    = λc.λx.λy.c x y  # 條件選擇
```

使用這些定義：
- IF TRUE a b → a
- IF FALSE a b → b

我們可以定義邏輯運算：
```
AND   = λp.λq.p q p      # p 為真則返回 q，否則返回 p
OR    = λp.λq.p p q      # p 為真則返回 p，否則返回 q
NOT   = λc.c FALSE TRUE  # 翻轉布爾值
```

### 丘奇數 (Church Numerals)

丘奇數將自然數表示為函數：

```
ZERO  = λf.λx.x           # 應用 f 零次
ONE   = λf.λx.f x         # 應用 f 一次
TWO   = λf.λx.f (f x)     # 應用 f 兩次
THREE = λf.λx.f (f (f x)) # 應用 f 三次
...
n     = λf.λx.fⁿ x        # 應用 f n 次
```

基數運算可以這樣定義：

```
SUCC  = λn.λf.λx.f (n f x)     # 後繼：n + 1
ADD   = λm.λn.λf.λx.m f (n f x) # 加法：m + n
MULT  = λm.λn.λf.m (n f)        # 乘法：m × n
PRED  = λn.λf.λx.n (λg.λh.h (g f)) (λu.x) (λu.u)  # 前驅：n - 1（若 n > 0）
SUB   = λm.λn.n PRED m          # 減法：m - n
```

### 序對

序對可以用以下方式表示：

```
PAIR  = λx.λy.λf.f x y     # 創建序對
FIRST = λp.p TRUE          # 取得第一個元素
SECOND = λp.p FALSE        # 取得第二個元素
```

### 列表

列表可以通過序對遞迴定義：

```
NIL   = PAIR TRUE TRUE             # 空列表
NULL  = λp.p TRUE                  # 判斷是否為空
CONS  = λh.λt.PAIR FALSE (PAIR h t) # 構建列表
HEAD  = λp.FIRST (SECOND p)        # 取得列表頭
TAIL  = λp.SECOND (SECOND p)       # 取得列表尾
```

## Y Combinator

Y Combinator 是實現遞迴的關鍵。在 Lambda 演算中，函數沒有名字，但我們可以使用 Y Combinator 來定義遞迴函數。

### 定義

```
Y = λf.(λx.f (x x)) (λx.f (x x))
```

### 為什麼需要 Y Combinator

在普通 Lambda 演算中，無法直接定義遞迴函數，因為函數不能引用自己。Y Combinator 通過「自我應用」解決了這個問題：

```
Y F = F (Y F)
```

這意味著 Y F 會展開為 F (Y F)，而 Y F 再次出現，形成遞迴。

### 應用：階層函數

使用 Y Combinator 可以定義階層函數：

```
FACT = Y (λf.λn. 
          (IS_ZERO n) 
            ONE 
            (MULT n (f (PRED n))))
```

這定義了一個可以計算階層的函數：FACT ZERO = ONE，FACT (SUCC n) = n × FACT n。

## 與圖靈機的比較

| 特性 | Lambda 演算 | 圖靈機 |
|------|-------------|--------|
| 發明者 | Alonzo Church | Alan Turing |
| 年份 | 1936 | 1936 |
| 核心概念 | 函數應用與代換 | 狀態與轉移 |
| 資料表示 | Church 編碼 | 符號串 |
| 計算方式 | 代換 | 狀態轉移 |
| 程式設計傾向 | 函數式 | 命令式 |

## 發展脈絡

Lambda 演算的發展對程式語言產生了深遠影響：

```
Lambda 演算 (1936)
      ↓
Lisp (1958) - 第一個函數式語言，由 John McCarthy 創建
      ↓
Scheme, Clojure, Racket - Lisp 的現代變體
      ↓
ML, OCaml, Haskell - 強類型函數式語言
      ↓
現代語言的函數式特性 (Python, JavaScript, Rust, Go)
```

## 求值策略

Lambda 演算的求值策略影響函數何時被求值：

### 應用次序 (Applicative Order)

先求值所有函數的參數，然後應用函數。這相當於大多數程式語言的嚴格求值。

### 正常次序 (Normal Order)

先應用函數，然後在需要時才求值參數。這是「惰性求值」的基礎。

對於 Lambda 演算，這兩種策略不一定產生相同的結果，特別是對於不終止的計算。

## 相關資源

- 相關概念：[圖靈機](圖靈機.md)
- 相關概念：[形式文法](形式文法.md)
- 相關概念：[計算理論](計算理論.md)

## 舉例說明

### 舉例：β歸約的實際計算

表達式：(λx. x + 1) 5

β歸約過程：
- 將參數 5 替換 x
- 得到 5 + 1
- 結果：6

另一個例子：(λx. λy. x + y) 3 4
- 先應用 3：(λy. 3 + y) 4
- 再應用 4：3 + 4 = 7

### 舉例：Church 數的運算

數字 2 表示為：λf. λx. f (f x)

加法：λm. λn. λf. λx. m f (n f x)

計算 TWO + ONE：
- (λm.λn.λf.λx.m f (n f x)) TWO ONE
- = λf.λx.TWO f (ONE f x)
- = λf.λx.(λf'.λx'.f'(f' x')) f (λf'.λx'.f' x') f x
- = λf.λx.f (f (f x))
- = THREE

### 舉例：Y Combinator 實現遞迴

沒有 Y Combinator，無法定義遞迴：
fact = λn. IF (n==0) 1 (n * fact(n-1))
                    ↑
               此處 fact 未定義！

使用 Y Combinator：
Y = λf.(λx.f (x x)) (λx.f (x x))

fact = Y (λf. λn. IF (n==0) 1 (n * f(n-1)))

計算 fact 3：
- Y F 3
- = F (Y F) 3
- = IF (3==0) 1 (3 * (Y F) 2)
- = 3 * (Y F) 2
- = 3 * 2 * (Y F) 1
- = 3 * 2 * 1 * (Y F) 0
- = 3 * 2 * 1 * 1
- = 6

### 舉例：應用次序 vs 正常次序

表達式：(λx. x x) (λx. x x)

- 應用次序：先求參數 (λx.x x)，但這會進入無限遞迴
- 正常次序：先應用外層，永遠不求值

正常次序可能永不終止，但有時能避免一些問題（如無窮資料結構）。

---

**Tags**: #Lambda演算 #函數式 #Church編碼 #Y_Combinator #計算理論