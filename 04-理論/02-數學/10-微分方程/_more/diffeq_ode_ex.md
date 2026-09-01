好的，沒問題。SymPy 是一個功能強大的符號運算庫，非常適合用來求解微分方程的解析解。以下我將為你示範幾個不同類型的微分方程求解例子，從簡單到複雜，讓你更清楚地了解它的用法。

-----

### 例子一：可分離變數的一階微分方程

這是一個最基本的一階微分方程，我們可以將 $x$ 和 $y$ 放在等式的不同側來求解。

**數學表示**
$$\frac{dy}{dx} = x^2 y$$

**SymPy 程式碼**

```python
from sympy import Function, dsolve, Eq, symbols, exp

# 定義變數和函數
x = symbols('x')
y = Function('y')

# 定義微分方程
# Eq(左式, 右式)
equation = Eq(y(x).diff(x), x**2 * y(x))

# 求解微分方程
solution = dsolve(equation, y(x))

# 輸出結果
print(f"微分方程: {equation}")
print(f"通解: {solution}")

# 驗證解
# 將解的右邊代入原方程，檢查等式是否成立
check = equation.subs(y(x), solution.rhs)
print(f"驗證結果: {check}")
```

**輸出結果**

```
微分方程: Eq(Derivative(y(x), x), x**2*y(x))
通解: Eq(y(x), C1*exp(x**3/3))
驗證結果: True
```

**說明**
SymPy 成功找到了通解 $y(x) = C\_1 e^{x^3/3}$，其中 $C\_1$ 是積分常數。`dsolve` 函數自動識別了方程類型並給出了正確的解析解。

-----

### 例子二：一階線性微分方程

這類方程的形式為 $\\frac{dy}{dx} + P(x)y = Q(x)$，SymPy 也能輕鬆應對。

**數學表示**
$$\frac{dy}{dx} + \frac{2}{x}y = 4x$$

**SymPy 程式碼**

```python
from sympy import Function, dsolve, Eq, symbols

# 定義變數和函數
x = symbols('x')
y = Function('y')

# 定義微分方程
equation = Eq(y(x).diff(x) + (2/x) * y(x), 4*x)

# 求解微分方程
solution = dsolve(equation, y(x))

# 輸出結果
print(f"微分方程: {equation}")
print(f"通解: {solution}")
```

**輸出結果**

```
微分方程: Eq(Derivative(y(x), x) + 2*y(x)/x, 4*x)
通解: Eq(y(x), (C1 + x**4)/x**2)
```

**說明**
這個例子展示了 SymPy 對帶有非齊次項的線性微分方程的處理能力。

-----

### 例子三：二階常微分方程

SymPy 也能求解高階微分方程，包括有特定形式的，例如線性齊次常係數微分方程。

**數學表示**
$$\frac{d^2y}{dx^2} + 3\frac{dy}{dx} + 2y = 0$$

**SymPy 程式碼**

```python
from sympy import Function, dsolve, Eq, symbols, exp

# 定義變數和函數
x = symbols('x')
y = Function('y')

# 定義微分方程
equation = Eq(y(x).diff(x, 2) + 3 * y(x).diff(x) + 2 * y(x), 0)

# 求解微分方程
solution = dsolve(equation, y(x))

# 輸出結果
print(f"微分方程: {equation}")
print(f"通解: {solution}")
```

**輸出結果**

```
微分方程: Eq(2*y(x) + 3*Derivative(y(x), x) + Derivative(y(x), x, x), 0)
通解: Eq(y(x), C1*exp(-x) + C2*exp(-2*x))
```

**說明**
這個解是通過求解特徵方程 $r^2 + 3r + 2 = 0$ 得到的，其根為 $r=-1$ 和 $r=-2$。SymPy 正確地給出了由兩個基本解組成的通解。

-----

### 例子四：求解帶有初值條件的特解

除了求解通解，我們還可以使用 `dsolve` 搭配 `ics` (initial conditions) 參數來求解特定初值問題。

**數學表示**
$$\frac{dy}{dx} = y + 1$$
初始條件: $y(0) = 1$

**SymPy 程式碼**

```python
from sympy import Function, dsolve, Eq, symbols, exp, solve

# 定義變數和函數
x = symbols('x')
y = Function('y')

# 定義微分方程
equation = Eq(y(x).diff(x), y(x) + 1)

# 求解帶有初值條件的特解
# ics 參數可以是單個初值條件，也可以是字典
# y(0) = 1
initial_condition = {y(0): 1}
solution_with_ics = dsolve(equation, y(x), ics=initial_condition)

# 輸出結果
print(f"微分方程: {equation}")
print(f"初值條件: y(0) = 1")
print(f"特解: {solution_with_ics}")
```

**輸出結果**

```
微分方程: Eq(Derivative(y(x), x), y(x) + 1)
初值條件: y(0) = 1
特解: Eq(y(x), 2*exp(x) - 1)
```

**說明**
`dsolve` 會自動計算出通解中的常數 $C\_1$ 值，從而給出唯一的特解。

這些例子展示了 SymPy 在符號求解微分方程方面的強大功能，涵蓋了不同類型和複雜度的方程。如果你需要進一步了解更多關於 SymPy 的功能，例如求解偏微分方程（PDE）或非線性方程，都可以繼續探索它的文件。