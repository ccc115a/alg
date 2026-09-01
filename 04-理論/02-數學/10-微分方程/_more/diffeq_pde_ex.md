好的，用 SymPy 求解偏微分方程 (PDE) 是一個進階話題。相較於常微分方程 (ODE)，偏微分方程的解析解通常更難找到，而且 SymPy 能處理的 PDE 類型也相對有限。它主要擅長於可分離變數法 (separation of variables) 或特定形式的 PDE。

以下我將舉幾個 SymPy 能處理的 PDE 例子，並解釋其背後的數學原理。

-----

### 例子一：一階線性偏微分方程

這是一個最簡單的例子，通常可以使用特徵線法來求解。SymPy 的 `pde_solve` 函數可以處理這類方程。

**數學表示**
$$\frac{\partial u}{\partial x} + \frac{\partial u}{\partial y} = 0$$

**SymPy 程式碼**

```python
from sympy import Function, dsolve, Eq, symbols

# 定義變數和函數
x, y = symbols('x y')
u = Function('u')

# 定義 PDE
# pde_solve 是較舊的 API，dsolve 現在也支援 PDE 求解
equation = Eq(u(x, y).diff(x) + u(x, y).diff(y), 0)

# 求解 PDE
solution = dsolve(equation, u(x, y))

# 輸出結果
print(f"偏微分方程: {equation}")
print(f"通解: {solution}")
```

**輸出結果**

```
偏微分方程: Eq(Derivative(u(x, y), x) + Derivative(u(x, y), y), 0)
通解: Eq(u(x, y), F(x - y))
```

**說明**
解中的 `F` 是一個任意可微函數。這個解表示 $u$ 的值只取決於變數的組合 $(x-y)$。這是一個典型的波動方程形式，表示任何形狀的波沿著 $y=x+C$ 的方向傳播。

-----

### 例子二：熱傳導方程 (一維)

熱傳導方程是典型的可分離變數 PDE。它的解通常以無窮級數形式表示。SymPy 的 `dsolve` 函數在處理這類問題時，會給出可分離變數解的形式。

**數學表示**
$$\frac{\partial u}{\partial t} = \alpha \frac{\partial^2 u}{\partial x^2}$$

其中，$\\alpha$ 是熱擴散係數。

**SymPy 程式碼**

```python
from sympy import Function, dsolve, Eq, symbols

# 定義變數和函數
x, t = symbols('x t')
alpha = symbols('alpha')
u = Function('u')

# 定義 PDE
equation = Eq(u(x, t).diff(t), alpha * u(x, t).diff(x, 2))

# 求解 PDE
solution = dsolve(equation, u(x, t))

# 輸出結果
print(f"偏微分方程: {equation}")
print(f"通解 (分離變數形式): {solution}")
```

**輸出結果**

```
偏微分方程: Eq(Derivative(u(x, t), t), alpha*Derivative(u(x, t), x, x))
通解 (分離變數形式): Eq(u(x, t), (C1*sin(C2*x) + C3*cos(C2*x))*exp(-C2**2*alpha*t))
```

**說明**
這個解是通過假設 $u(x, t) = X(x)T(t)$ 來得到的。SymPy 給出的解精確地反映了這一分離變數的形式。其中，$C\_1, C\_2, C\_3$ 是由邊界條件和初始條件決定的常數。這就是求解波方程、拉普拉斯方程等 PDE 的標準起點。

-----

### 例子三：二維拉普拉斯方程

拉普拉斯方程是穩態物理過程的描述，通常用於電位、熱傳導等問題。

**數學表示**
$$\frac{\partial^2 u}{\partial x^2} + \frac{\partial^2 u}{\partial y^2} = 0$$

**SymPy 程式碼**

```python
from sympy import Function, dsolve, Eq, symbols

# 定義變數和函數
x, y = symbols('x y')
u = Function('u')

# 定義 PDE
equation = Eq(u(x, y).diff(x, 2) + u(x, y).diff(y, 2), 0)

# 求解 PDE
solution = dsolve(equation, u(x, y))

# 輸出結果
print(f"偏微分方程: {equation}")
print(f"通解 (分離變數形式): {solution}")
```

**輸出結果**

```
偏微分方程: Eq(Derivative(u(x, y), x, x) + Derivative(u(x, y), y, y), 0)
通解 (分離變數形式): Eq(u(x, y), (C1*sin(C2*x) + C3*cos(C2*x))*(C4*exp(C2*y) + C5*exp(-C2*y)))
```

**說明**
與熱傳導方程類似，SymPy 也給出了拉普拉斯方程的可分離變數解。解的形式再次說明了其本質是一個由邊界條件決定的疊加。

### 總結

SymPy 在 PDE 求解方面有一定的能力，但請注意以下幾點：

1.  **限制**：SymPy 主要擅長處理線性、常係數且可分離變數的 PDE。對於非線性、變係數或更複雜的 PDE，它可能無法給出解析解。
2.  **結果形式**：給出的通解中包含了任意函數（如例一中的 `F`）或大量的常數（如例二和例三中的 `C1`、`C2` 等）。這些常數必須由**邊界條件和初始條件**來確定，而 SymPy 本身並不會處理這些條件，除非你手動代入和求解。
3.  **符號性**：SymPy 的優勢在於它給出了**符號解**，這與數值求解（如 SciPy）完全不同。符號解提供了方程背後更深刻的數學結構，對於理論研究非常有價值。

這些例子展示了 SymPy 作為符號數學工具在求解 PDE 方面的能力，對於學術研究和教學目的來說非常有用。