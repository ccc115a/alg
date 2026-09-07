在純粹的 Lambda Calculus 中，定義加法（`SUCC`）非常直觀，但實作減一演算法（Predecessor, $\text{PRED}$）卻被譽為邱奇數演算中最精妙的難題之一（歷史上 Alonzo Church 本人困擾許久，最終由其學生 Stephen Kleene 在看牙醫時想出解答）。

以下詳細拆解 $\text{PRED}$ 的演算法邏輯、數學推導與 Scheme 實作。

---

### **一、 演算法核心邏輯（Kleene's Trick）**

#### **1. 為什麼 $\text{PRED}$ 很難？**

邱奇數（Church Numerals）是**單向**的函數套用：

* $0 = \lambda f. \lambda x. x$
* $3 = \lambda f. \lambda x. f (f (f \, x))$

因為沒有「倒帶（Un-apply）」函數的機制，我們無法直接從 $f(f(f \, x))$ 中「剝離」一層 $f$。

#### **2. 解法：利用 Pair 記錄「當前值與前值」**

Kleene 的天才構想是：**不要試圖拆除 $f$，而是從 $0$ 開始重新建構，並用序對（Pair）同時記錄兩代狀態 $(N, N-1)$。**

* 初始狀態（Step 0）：$(0, 0)$
* 套用 1 次（Step 1）：$(1, 0)$
* 套用 2 次（Step 2）：$(2, 1)$
* 套用 3 次（Step 3）：$(3, 2)$

當我們要算 $n - 1$ 時，只要讓這個轉移函數作用 $n$ 次，最後取出序對的右邊元素（$N-1$）即為答案！若 $n = 0$，右邊元素依舊是 $0$（符合 $0 - 1 = 0$ 的飽和減法法則）。

---

### **二、 數學推導與符號定義**

#### **1. 基礎元件**

* **Church Pair：** $\text{PAIR} \equiv \lambda a. \lambda b. \lambda m. m \, a \, b$
* **Selector（CAR/CDR）：**
* $\text{FIRST} \equiv \lambda p. p \, (\lambda x. \lambda y. x)$
* $\text{SECOND} \equiv \lambda p. p \, (\lambda x. \lambda y. y)$



#### **2. 狀態轉移函數（Step Function）**

定義一個函數 $S$，傳入序對 $(a, b)$，回傳新序對 $(a + 1, a)$：


$$S \equiv \lambda p. \text{PAIR} \,\, (\text{SUCC} \, (\text{FIRST} \, p)) \,\, (\text{FIRST} \, p)$$

#### **3. 減一演算法（$\text{PRED}$）推導**

給定邱奇數 $n$：

1. 建立初始序對：$P_0 = \text{PAIR} \,\, 0 \,\, 0$
2. 將轉移函數 $S$ 套用在 $P_0$ 上 $n$ 次：$(n \, S \, P_0)$
3. 取出右側元素（$\text{SECOND}$）：

$$\text{PRED} \equiv \lambda n. \text{SECOND} \,\, (n \,\, S \,\, (\text{PAIR} \,\, 0 \,\, 0))$$



---

### **三、 Scheme (LISP) 完整實作**

以下完全不使用 Scheme 原生的 `cons`、`car`、`cdr` 或算術運算子，純粹使用 `lambda` 實作：

```scheme
;; 1. 定義基礎 Church Booleans 與 Pairs
(define church-true  (lambda (x) (lambda (y) x)))
(define church-false (lambda (x) (lambda (y) y)))

(define church-cons
  (lambda (x)
    (lambda (y)
      (lambda (m) ((m x) y)))))

(define church-car (lambda (p) (p church-true)))
(define church-cdr (lambda (p) (p church-false)))

;; 2. 定義 Church Numerals & SUCC
(define church-zero (lambda (f) (lambda (x) x)))

(define church-succ
  (lambda (n)
    (lambda (f)
      (lambda (x)
        (f ((n f) x))))))

;; 建立數字 1, 2, 3 供測試
(define church-one   (church-succ church-zero))
(define church-two   (church-succ church-one))
(define church-three (church-succ church-two))

;; 3. 實作 PRED (減一演算法)
(define church-pred
  (lambda (n)
    ;; 取出 Step 執行 n 次後的第二個元素 (即 n - 1)
    (church-cdr
     ((n (lambda (p)
           ;; 轉移函數 Step: (a, b) -> (a + 1, a)
           ((church-cons (church-succ (church-car p)))
            (church-car p))))
      ;; 初始狀態: (0, 0)
      ((church-cons church-zero) church-zero)))))

;; 輔助轉換函數 (僅用於驗證結果)
(define (church->int n)
  ((n (lambda (x) (+ x 1))) 0))

;; 4. 驗證結果
(church->int (church-pred church-three)) ; 輸出 2
(church->int (church-pred church-one))   ; 輸出 0
(church->int (church-pred church-zero))  ; 輸出 0 (邊界條件: 0 - 1 = 0)

```

---

### **四、 延伸：Subtraction（減法演算法）**

有了 $\text{PRED}$ 後，$m - n$ 的邏輯就非常簡單了——**對 $m$ 連續套用 $n$ 次 $\text{PRED}$**：

$$\text{SUB} \equiv \lambda m. \lambda n. n \,\, \text{PRED} \,\, m$$

在 Scheme 中實作：

```scheme
(define church-sub
  (lambda (m)
    (lambda (n)
      ((n church-pred) m))))

;; 測試 3 - 1 = 2
(church->int ((church-sub church-three) church-one)) ; 輸出 2

```


## 請詳細說明並提供只用 Lambda Calculus Church Numeral 減一演算法（PRED）的邏輯、數學推導

在純粹的無型別 Lambda Calculus（Untyped $\lambda$-Calculus）中，減一演算法（Predecessor, $\text{PRED}$）的推導非常精妙。這個解法由史蒂芬·克萊尼（Stephen Kleene）提出，稱為 **Kleene's Trick**。

---

### **一、 演算法核心邏輯**

#### **1. 為什麼 $\text{PRED}$ 難以直接求得？**

邱奇數（Church Numerals）是**單向**的函數重複套用：

* $0 \equiv \lambda f. \lambda x. x$
* $1 \equiv \lambda f. \lambda x. f \, x$
* $n \equiv \lambda f. \lambda x. f^n(x)$

由於 Lambda Calculus 沒有內建「剝離/倒帶」函數套用的機制，我們無法直接從 $f^n(x)$ 中刪除一層 $f$。

#### **2. Kleene 的核心構想：序對（Pair）轉移**

Kleene 的做法是**不要嘗試拆卸 $f$，而是從 $0$ 開始重新建構**。

透過一個序對（Pair）同時記錄「當前值與前一個值」：$(N, N-1)$。

* **初始狀態（Step 0）：** $P_0 = (0, 0)$
* **轉移 1 次（Step 1）：** $P_1 = (1, 0)$
* **轉移 2 次（Step 2）：** $P_2 = (2, 1)$
* **轉移 3 次（Step 3）：** $P_3 = (3, 2)$
* **轉移 $n$ 次（Step $n$）：** $P_n = (n, n-1)$

要求出 $\text{PRED}(n)$，只要讓這個轉移函數在初始序對 $P_0$ 上作用 $n$ 次，最後取出序對的右邊元素（$n-1$）即可。若 $n = 0$，取出右邊元素依舊是 $0$（符合 $0 - 1 = 0$ 的飽和減法）。

---

### **二、 數學元件與推導**

為了完全不依賴外部語法，我們必須先建構基礎的 Lambda 工具元件：

#### **1. 基礎工具定義**

* **Church Pair（序對建構）：**

$$\text{PAIR} \equiv \lambda a. \lambda b. \lambda m. m \, a \, b$$


* **取第一項（$\text{FIRST}$ / $\text{CAR}$）：**

$$\text{FIRST} \equiv \lambda p. p \, (\lambda x. \lambda y. x)$$


* **取第二項（$\text{SECOND}$ / $\text{CDR}$）：**

$$\text{SECOND} \equiv \lambda p. p \, (\lambda x. \lambda y. y)$$


* **後繼函數（$\text{SUCC}$）：**

$$\text{SUCC} \equiv \lambda n. \lambda f. \lambda x. f \, (n \, f \, x)$$


* **邱奇數 $0$：**

$$0 \equiv \lambda f. \lambda x. x$$



---

#### **2. 轉移函數（Step Function）定義**

定義一個轉移函數 $S$，傳入序對 $p = (a, b)$，回傳新序對 $(a + 1, a)$：

$$S \equiv \lambda p. \text{PAIR} \,\, (\text{SUCC} \, (\text{FIRST} \, p)) \,\, (\text{FIRST} \, p)$$

---

#### **3. 減一演算法 $\text{PRED}$ 的最終表達式**

將初始序對定義為 $P_0 \equiv \text{PAIR} \,\, 0 \,\, 0$。

給定邱奇數 $n$，將轉移函數 $S$ 套用在 $P_0$ 上 $n$ 次：$(n \, S \, P_0)$，最後取第二項：

$$\text{PRED} \equiv \lambda n. \text{SECOND} \,\, (n \,\, S \,\, (\text{PAIR} \,\, 0 \,\, 0))$$

展開 $S$ 與 $P_0$ 後，完整的純 Lambda 算式為：

$$\text{PRED} \equiv \lambda n. \text{SECOND} \,\, \left( n \,\, (\lambda p. \text{PAIR} \,\, (\text{SUCC} \, (\text{FIRST} \, p)) \,\, (\text{FIRST} \, p)) \,\, (\text{PAIR} \,\, 0 \,\, 0) \right)$$

---

### **三、 $\beta$-reduction（歸約）詳細推導過程**

以求解 $\text{PRED} \,\, 1$ 為例，驗證其是否可簡化為 $0$：

1. **代入 $\text{PRED} \,\, 1$：**

$$\text{PRED} \,\, 1 \xrightarrow{\beta} \text{SECOND} \,\, (1 \,\, S \,\, P_0)$$


2. **展開數字 $1$（套用 $S$ 函數 1 次）：**
因為 $1 \equiv \lambda f. \lambda x. f \, x$，所以 $1 \,\, S \,\, P_0 \xrightarrow{\beta} S \,\, P_0$。
算式變為：

$$\text{SECOND} \,\, (S \,\, P_0)$$


3. **計算 $S \,\, P_0$（執行轉移）：**

$$S \,\, P_0 \xrightarrow{\beta} \text{PAIR} \,\, (\text{SUCC} \, (\text{FIRST} \, P_0)) \,\, (\text{FIRST} \, P_0)$$


* 其中 $\text{FIRST} \, P_0 \xrightarrow{\beta} 0$
* 其中 $\text{SUCC} \, 0 \xrightarrow{\beta} 1$
因此：

$$S \,\, P_0 \xrightarrow{\beta} \text{PAIR} \,\, 1 \,\, 0$$




4. **取出第二項：**

$$\text{SECOND} \,\, (\text{PAIR} \,\, 1 \,\, 0) \xrightarrow{\beta} 0$$



最終求得 $\text{PRED} \,\, 1 \xrightarrow{\beta} 0$，推導完畢。

---

### **四、 時間複雜度與結論**

| 演算法 | 時間複雜度 | 說明 |
| --- | --- | --- |
| **加法（$\text{SUCC}$）** | $\mathcal{O}(1)$ | 直接外包一層 $f$ 即可完成。 |
| **減一（$\text{PRED}$）** | $\mathcal{O}(n)$ | 必須從 $0$ 開始執行 $n$ 次轉移函數，重構整個計數過程。 |

Kleene's Trick 證明了即使在看似極端受限、沒有記憶體位址與暫存器的純 Lambda Calculus 系統中，只要透過「閉包狀態記錄」與「迭代重構」，依然能夠實現完整的算術減法系統。

