from sympy import symbols, diff, cos, sin

# 1. 定義符號變數
# 坐標變數 $x, y$
x, y = symbols('x y')

# 2. 定義一個符號函數 $f(x, y)$
f = cos(x*y) + x**3 + y

print(f"原始函數 f(x, y): {f}")

# 3. 計算偏導數
# 計算 $\frac{\partial f}{\partial x}$
df_dx = diff(f, x)
print(f"對 $x$ 的偏導數 $\\frac{{\\partial f}}{{\\partial x}}$: {df_dx}")

# 計算 $\frac{{\partial^2 f}}{{\partial x \partial y}}$
d2f_dxdy = diff(f, x, y)
print(f"二階混合偏導數 $\\frac{{\\partial^2 f}}{{\\partial x \\partial y}}$: {d2f_dxdy}")
