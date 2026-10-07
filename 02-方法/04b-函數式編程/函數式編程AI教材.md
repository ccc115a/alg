# 函數式編程

* [函數式編程](https://zh.wikipedia.org/zh-tw/%E5%87%BD%E6%95%B0%E5%BC%8F%E7%BC%96%E7%A8%8B)

Monad 是一個同時實作了 map 與 flatMap 的容器。

## ccc: 請寫一套 函數式編程的教材

這是一套為物件導向與命令式開發者量身打造的「函數式編程（Functional Programming, FP）實戰與心法教材」。採用「觀念轉變 $\rightarrow$ 核心四大支柱 $\rightarrow$ 高階組合技巧 $\rightarrow$ 專案級實戰」的結構，幫助學生擺頭傳統 Side Effects（副作用）的思維，寫出更強健、易測試且無 Bug 的程式碼。

---

# 🌀 函數式編程（Functional Programming）完整講義

> **核心思維：** 命令式（Imperative）關注 **How to do**（一步步如何改變狀態）；函數式（Functional）關注 **What to be**（資料與資料之間的映射關係）。

---

## 階段一：觀念轉變 —— 什麼是 FP？

在傳統命令式編程中，我們習慣建立「變數」、透過「迴圈」與「條件判斷」去改變共享的記憶體狀態。然而，**共享狀態（Shared Mutable State）是軟體開發中絕大多數 Bug 的根源**。

FP 是一種程式設計典範（Paradigm），它將計算過程視為**數學上的函數求值**，並避免改變狀態與可變數據。

### 命令式 vs. 函數式 對比

```python
# 範例：找出陣列中的偶數，並將其平方後加總

# 🔴 命令式 (Imperative): 關心步驟、維護狀態 (total, x)
numbers = [1, 2, 3, 4, 5, 6]
total = 0
for x in numbers:
    if x % 2 == 0:
        square = x * x
        total += square

# 🟢 函數式 (Declarative / FP): 關心資料轉化管道 (Pipeline)
from functools import reduce

numbers = [1, 2, 3, 4, 5, 6]
total = reduce(
    lambda acc, x: acc + x,
    map(lambda x: x ** 2, filter(lambda x: x % 2 == 0, numbers)),
    0
)

```

---

## 階段二：FP 的四大核心支柱（The 4 Pillars）

掌握 FP，必須理解並貫徹以下四大核心原則：

```
                    ┌─────────────────────────┐
                    │    1. 純函數 (Pure)     │ ── 無副作用、可預測
                    └────────────┬────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │  2. 不可變性 (Immutable)│ ── 狀態不更新，只產生新資料
                    └────────────┬────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │ 3. 一等公民 (First-Class)│ ── 函數可當作參數/回傳值傳遞
                    └────────────┬────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │ 4. 宣告式轉換 (Transform)│ ── map / filter / reduce
                    └─────────────────────────┘

```

---

### 1. 純函數（Pure Functions）與無副作用（No Side Effects）

**純函數的定義：**

1. **相同的輸入，必定得到相同的輸出**（具有確定性 Determinism）。
2. **執行過程中無副作用（No Side Effects）**：不修改外部變數、不修改傳入的參數、不進行 I/O 操作（如印出 log、讀寫檔案、發送 HTTP 請求）。

```python
# ❌ 不純 (Impure): 依賴外部狀態，且會產生副作用
tax_rate = 0.05
def calculate_price_impure(cart):
    global tax_rate
    cart['total'] = cart['subtotal'] * (1 + tax_rate) # 修改了傳入的物件！
    return cart['total']

# ✅ 純函數 (Pure): 只依賴輸入參數，回傳新結果，不破壞外部資料
def calculate_price_pure(subtotal, tax):
    return subtotal * (1 + tax)

```

---

### 2. 不可變性（Immutability）

在 FP 中，變數一旦建立就**不能被重新賦值（Reassign）或修改（Mutate）**。如果需要更新資料，必須**基於舊資料建立一份全新的資料**。

```python
# ❌ 可變 (Mutable): 修改原有串列
def add_item_impure(arr, item):
    arr.append(item)
    return arr

# ✅ 不可變 (Immutable): 使用 Copy-on-Write 概念回傳新串列
def add_item_pure(arr, item):
    return arr + [item]  # 或在 JS 使用 [...arr, item]

```

---

### 3. 一等公民函數（First-Class & Higher-Order Functions）

在 FP 語言中，**函數是一等公民（First-Class Citizen）**，意味著函數可以像普通數字或字串一樣：

* 賦值給變數
* 作為參數傳遞給其他函數
* 作為其他函數的回傳值

接受函數作為參數，或回傳函數的函數，稱為**高階函數（Higher-Order Function, HOF）**。

```python
# 高階函數範例：製造一個「折扣器」函數
def make_discounter(discount):
    # 回傳一個新的函數
    return lambda price: price * (1 - discount)

ten_percent_off = make_discounter(0.10)
twenty_percent_off = make_discounter(0.20)

print(ten_percent_off(100))      # 90.0
print(twenty_percent_off(100))   # 80.0

```

---

### 4. 集合三劍客：`map` / `filter` / `reduce`

FP 廢棄了 `for` / `while` 迴圈，改用這三個高階函數處理集合轉化：

| 函數 | 目的 | 輸入 $\rightarrow$ 輸出 關係 |
| --- | --- | --- |
| **`map(fn, list)`** | 將陣列中每個元素進行一對一映射轉換 | 長度為 $N$ 的陣列 $\rightarrow$ 長度為 $N$ 的新陣列 |
| **`filter(fn, list)`** | 根據條件篩選符合條件的元素 | 長度為 $N$ 的陣列 $\rightarrow$ 長度 $\le N$ 的新陣列 |
| **`reduce(fn, list, init)`** | 將整個陣列的元素累加/折疊為單一數值或結構 | 長度為 $N$ 的陣列 $\rightarrow$ **單一值** (數字、字典、物件等) |

---

## 階段三：進階 FP 組合技巧（Advanced FP Concepts）

當基礎建立後，我們可以利用以下進階技巧將多個小純函數組合成複雜的業務邏輯：

### 1. 柯里化（Currying）

將一個接受多個參數的函數，轉換成**一連串只接受單一參數的函數**。

$$\text{f}(a, b, c) \longrightarrow \text{f}(a)(b)(c)$$

```python
# 傳統多參數函數
def add(a, b):
    return a + b

# Curried 版本
def curried_add(a):
    return lambda b: a + b

add_five = curried_add(5)
print(add_five(10)) # 15

```

---

### 2. 函數組合（Function Composition & Pipe）

將多個小函數像水管一樣串聯起來，上一級函數的輸出自動作為下一級函數的輸入：

$$(f \circ g)(x) = f(g(x))$$

```python
# 實作 Pipe (從左到右執行組合)
from functools import reduce

def pipe(*functions):
    return lambda initial_val: reduce(lambda acc, fn: fn(acc), functions, initial_val)

# 定義原子級純函數
strip_str = lambda s: s.strip()
uppercase = lambda s: s.upper()
add_exclamation = lambda s: s + "!!!"

# 組合出新的業務函數
format_greeting = pipe(strip_str, uppercase, add_exclamation)

print(format_greeting("   hello world ")) # "HELLO WORLD!!!"

```

---

## 階段四：隨堂實戰練習題庫

請試著**不使用任何迴圈（`for` / `while`）**與**不修改任何變數**來完成以下題目：

| 題號 | 題目名稱 | 難易度 | 核心觀念 |
| --- | --- | --- | --- |
| **Q1** | 自製組合器（Implement `compose` & `pipe`） | 🟢 入門 | 高階函數與 `reduce` 的應用 |
| **Q2** | 購物車金額計算（Cart Calculator） | 🟡 中等 | `filter` $\rightarrow$ `map` $\rightarrow$ `reduce` 資料管道鏈 |
| **Q3** | 統計文章單字頻率（Word Frequency Count） | 🟡 中等 | 使用 `reduce` 將 List 轉化為 Dict 結構 |
| **Q4** | 處理安全空值：Monad / Option 模式 | 🔴 進階 | 避免 `NullPointerException` 的 FP 模式 |

---

## 階段五：教材總結與代碼 Review 清單

寫完 FP 代碼後，請檢查：

* [ ] 我的函數是否全是 **Pure Function**？（沒有讀寫外部全域變數、沒有修改輸入參數）
* [ ] 程式碼中是否徹底銷毀了 **`for` / `while` 迴圈**，並改用 `map/filter/reduce` 或遞迴？
* [ ] 所有資料變更時，是否都採用了 **Immutable（不可變）** 方式建立新物件？
* [ ] 函數是否足夠小且單一職責，並能透過 `pipe` / `compose` 進行組合？

## ccc: 請幫我補充一份進階 FP 專題講義，詳細說明什麼是 Functor, Monad 以及如何用 Maybe Monad 解決 Null/None 問題。

這是一份專為具備 FP 基礎（已了解純函數、高階函數、`map/filter/reduce`）的開發者設計的**進階 FP 專題講義**。

本講義旨在用最直觀的方式破解 Category Theory（範疇論）中看似深奧的名詞，並透過程式碼說明如何用 **Maybe Monad** 優雅解決軟體開發中最棘手的 `NullPointerException`（或 Python 的 `AttributeError: 'NoneType' object has no attribute`）。

---

# 🌀 進階 FP 專題講義：Functor, Monad 與 Null/None 防護網

> **核心概念：**
> * **Functor** 是一個「把值裝在盒子裡」，並允許你對盒子內的值進行 **映射（`map`）** 的容器。
> * **Monad** 是一個「允許你把回傳新盒子的函數」，透過 **扁平化（`flatMap` / `bind`）** 鏈結起來的容器。
> 
> 

---

## 階段一：觀念建立 —— 「盒子（Container）」心法

在 FP 中，處理不確定性（如：`None`、錯誤處理、非同步）的秘密武器就是**將資料封裝進一個「容器/盒子」中**。我們不直接操作原始數值，而是操作這個盒子。

```
普通數值 x:         [ 5 ]

裝在盒子裡的數值:   ┌───────┐
                   │  [ 5 ]│  <-- Container (Box)
                   └───────┘

```

---

## 階段二：什麼是 Functor（函子）？

### 1. 定義

**Functor** 是一個實現了 `map` 方法的容器。

* **普通函數：** $A \rightarrow B$（將值 $A$ 轉為值 $B$）
* **`Functor.map` 做的事：** 接受一個普通函數 $f(A) \rightarrow B$，解開盒子取出 $A$，執行 $f(A)$ 得到 $B$，再把 $B$ **裝回同種類型的盒子裡**。

### 2. 示意圖

```
┌───────┐                      ┌───────┐
│  [A]  │  ─── map( f ) ────>  │  [B]  │
└───────┘  (取出 A 變 B 再裝回) └───────┘

```

### 3. Python 手寫實作：`Container` Functor

```python
class Container:
    def __init__(self, value):
        self._value = value

    # 實作 map，讓它成為一個 Functor
    def map(self, fn):
        # 1. 取出內部的 self._value
        # 2. 執行 fn(self._value)
        # 3. 重新封裝成 Container 回傳
        return Container(fn(self._value))

    def __repr__(self):
        return f"Container({self._value})"

# 測試 Functor
box = Container(5)
result = box.map(lambda x: x * 2).map(lambda x: x + 10)

print(result) # 輸出: Container(20)

```

---

## 階段三：什麼是 Monad（單子）？

### 1. 為何需要 Monad？（Functor 的痛點）

假設你有一個會回傳「盒子」的函數（例如從資料庫或 API 尋找資料，找不到回傳空盒子）：

```python
def safe_divide(x):
    # 這個函數本身就回傳 Container！
    return Container(10 / x) if x != 0 else Container(None)

```

如果你用 Functor 的 `map` 來鏈結它：

```python
result = Container(2).map(safe_divide)
print(result) # 輸出: Container(Container(5.0))  <-- 嵌套了兩層盒子！

```

如果連續鏈結多次，就會出現 `Container(Container(Container(...)))` 的「嵌套地獄（Nested Boxes）」。

### 2. Monad 的解法：`flatMap`（或稱 `bind` / `chain`）

**Monad** 是一個同時實作了 `map` 與 **`flatMap`** 的容器。

`flatMap` 做的事：對盒子內的值執行一個**會回傳新盒子的函數**，但最後**把多餘的那層盒子攤平（Flat）**。

```
┌──────────────┐                          ┌───────┐
│Container([A])│  ─── flatMap( f_box ) ─> │  [B]  │
└──────────────┘ (攤平兩層盒子，保留單層)   └───────┘

```

---

## 階段四：實戰應用 —— Maybe Monad 徹底擊滅 Null/None

在傳統命令式程式碼中，連續存取嵌套物件（如 `user.address.street.name`）需要寫滿醜陋的空值檢查（Defensive Code）：

```python
# ❌ 傳統命令式：滿滿的 None 檢查 (Pyramid of Doom)
def get_street_name_imperative(user):
    if user is not None:
        address = user.get('address')
        if address is not None:
            street = address.get('street')
            if street is not None:
                return street.get('name')
    return None

```

### 1. 實作 `Maybe` Monad (`Just` 與 `Nothing`)

`Maybe` 是一個抽象類別，有兩個子類別：

1. **`Just(val)`**：代表**有值**的盒子。
2. **`Nothing`**：代表空值（Null/None）的盒子。

```python
from abc import ABC, abstractmethod

class Maybe(ABC):
    @abstractmethod
    def map(self, fn):
        pass

    @abstractmethod
    def flatMap(self, fn):
        pass

# 1. 有值的盒子
class Just(Maybe):
    def __init__(self, value):
        self._value = value

    def map(self, fn):
        # 正常轉換，並包回 Just
        return Just(fn(self._value))

    def flatMap(self, fn):
        # 執行回傳 Maybe 的函數，不重複打包
        return fn(self._value)

    def get_or_else(self, default):
        return self._value

    def __repr__(self):
        return f"Just({self._value})"

# 2. 代表空值的盒子
class Nothing(Maybe):
    def map(self, fn):
        # 當前是 Nothing 時，直接忽略任何操作，繼續回傳 Nothing
        return self

    def flatMap(self, fn):
        return self

    def get_or_else(self, default):
        # 若最終是 Nothing，回傳預設值
        return default

    def __repr__(self):
        return "Nothing"

```

---

### 2. 使用 Maybe Monad 改寫鏈結呼叫

有了 `Maybe`，我們可以寫一個安全取值的 Helper 函數：

```python
def safe_get(prop_name):
    """回傳一個函數：傳入 dict，回傳封裝在 Maybe 中的屬性值"""
    def _getter(d):
        if isinstance(d, dict) and prop_name in d and d[prop_name] is not None:
            return Just(d[prop_name])
        return Nothing()
    return _getter

```

#### 測試案例：安全流式存取（Pipeline）

```python
# 測試資料 1: 完整的使用者資料
user_complete = {
    "name": "Alice",
    "address": {
        "street": {
            "name": "忠孝東路"
        }
    }
}

# 測試資料 2: 缺失 address 的使用者資料
user_incomplete = {
    "name": "Bob"
}

def get_street_name_functional(user_dict):
    return (
        Just(user_dict)
        .flatMap(safe_get("address"))
        .flatMap(safe_get("street"))
        .flatMap(safe_get("name"))
        .get_or_else("未知街道")
    )

# 測試執行
print("完整資料結果:", get_street_name_functional(user_complete))  
# 輸出: 完整資料結果: 忠孝東路

print("缺失資料結果:", get_street_name_functional(user_incomplete))
# 輸出: 缺失資料結果: 未知街道

```

---

## 階段五：心法總結與對比表格

### 1. Functor vs Monad 快速對照

| 概念 | 核心方法 | 傳入函數型態 $f$ | 解決的問題 |
| --- | --- | --- | --- |
| **Functor** | `map(f)` | $A \rightarrow B$ （純數值轉換） | 在不解包的情況下對盒子內的值做變換 |
| **Monad** | `flatMap(f)` | $A \rightarrow \text{Box}(B)$ （會回傳盒子的轉換） | 避免 `Box(Box(...))` 的多層嵌套地獄 |

### 2. 為什麼 Maybe Monad 如此強大？

1. **短路機制（Short-circuiting）**：一旦資料管道中的某一步變成了 `Nothing`，後續所有的 `map` 與 `flatMap` 都不會真正執行，直接一路一路傳遞 `Nothing` 到終點。
2. **聲明式無例外**：程式碼完全沒有 `try-catch` 或任何 `if x is None` 判斷，邏輯呈單向資料流（Dataflow），非常乾淨。
3. **這就是現代語言 Optional / Maybe 的底層原型**：
* Swift 的 `Optional` 與 `?` 語法
* Rust 的 `Option<T>` (與 `and_then` 方法)
* Java 8+ 的 `Optional.flatMap()`
* JavaScript / TypeScript 的 Optional Chaining (`user?.address?.street?.name`)