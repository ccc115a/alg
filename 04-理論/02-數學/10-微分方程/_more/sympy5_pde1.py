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