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