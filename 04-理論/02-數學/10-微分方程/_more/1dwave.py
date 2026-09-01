from sympy import Function, dsolve, Eq, symbols

# 定義變數和函數
x, t = symbols('x t')
v = symbols('v', real=True, positive=True)
u = Function('u')

# 定義一維波方程
# 注意：SymPy 的 dsolve 函數需要我們將方程整理為右邊為 0 的形式
equation = Eq(u(x, t).diff(t, 2), v**2 * u(x, t).diff(x, 2))

# 求解 PDE
solution = dsolve(equation, u(x, t))

# 輸出結果
print(f"偏微分方程: {equation}")
print(f"通解: {solution}")