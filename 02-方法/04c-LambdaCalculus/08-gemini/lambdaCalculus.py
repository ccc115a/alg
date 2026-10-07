# --------------------------------------------------
# 1. Church Booleans (布林值與邏輯閘)
# --------------------------------------------------
TRUE  = lambda x: lambda y: x
FALSE = lambda x: lambda y: y

IF   = lambda p: lambda a: lambda b: p(a)(b)
AND  = lambda p: lambda q: p(q)(FALSE)
OR   = lambda p: lambda q: p(TRUE)(q)
NOT  = lambda p: p(FALSE)(TRUE)

# --------------------------------------------------
# 2. Church Numerals (自然數與算術運算)
# --------------------------------------------------
ZERO = lambda f: lambda x: x
ONE  = lambda f: lambda x: f(x)
TWO  = lambda f: lambda x: f(f(x))
THREE = lambda f: lambda x: f(f(f(x)))

# 加 1 (Successor: n + 1)
SUCC = lambda n: lambda f: lambda x: f(n(f)(x))

# 加法 (PLUS: m + n)
PLUS = lambda m: lambda n: m(SUCC)(n)

# 乘法 (MULT: m * n)
MULT = lambda m: lambda n: lambda f: m(n(f))

# 判斷是否為 0 (IS_ZERO)
IS_ZERO = lambda n: n(lambda x: FALSE)(TRUE)

# 減 1 (PRED: 構造 Pairing 技巧)
PAIR = lambda x: lambda y: lambda f: f(x)(y)
FIRST = lambda p: p(TRUE)
SECOND = lambda p: p(FALSE)

PRED_STEP = lambda p: PAIR(SECOND(p))(SUCC(SECOND(p)))
PRED = lambda n: FIRST(n(PRED_STEP)(PAIR(ZERO)(ZERO)))

# 減法 (SUB: m - n)
SUB = lambda m: lambda n: n(PRED)(m)

# --------------------------------------------------
# 3. Z Combinator 與純粹遞迴 (階乘)
# --------------------------------------------------
Z = lambda f: (lambda x: f(lambda v: x(x)(v)))(lambda x: f(lambda v: x(x)(v)))

# 純粹的階乘函數（沒有任何 Python 數字與條件判斷）
PURE_FACT = Z(
    lambda f: lambda n: 
        IF(IS_ZERO(n))
          (lambda v: ONE)                           # Then 分支 (包裹延遲求值)
          (lambda v: MULT(n)(f(PRED(n))))           # Else 分支 (包裹延遲求值)
          (None)                                    # 觸發延遲執行的參數
)

# --------------------------------------------------
# 4. 輔助函數 (轉換為 Python 印出結果)
# --------------------------------------------------
def to_bool(church_bool):
    return church_bool(True)(False)

def to_int(church_num):
    return church_num(lambda x: x + 1)(0)

# --------------------------------------------------
# 測試執行
# --------------------------------------------------
print("--- 邏輯測試 ---")
print("TRUE and FALSE :", to_bool(AND(TRUE)(FALSE)))  # False
print("TRUE or FALSE  :", to_bool(OR(TRUE)(FALSE)))   # True
print("NOT FALSE      :", to_bool(NOT(FALSE)))        # True

print("\n--- 算術測試 ---")
print("2 + 3 =", to_int(PLUS(TWO)(THREE)))             # 5
print("2 * 3 =", to_int(MULT(TWO)(THREE)))             # 6
print("3 - 1 =", to_int(PRED(THREE)))                  # 2

print("\n--- 純粹 Lambda 遞迴測試 (階乘) ---")
print("3! =", to_int(PURE_FACT(THREE)))                # 6 (即 3 * 2 * 1)