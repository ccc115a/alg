from sympy import Function, dsolve, Eq, sin, symbols, integrate

# 定義符號變數和函數
x = symbols('x')
y = Function('y')

# 定義微分方程
# Eq(左式, 右式)
equation = Eq(y(x).diff(x), sin(x))

# 求解微分方程
solution = dsolve(equation, y(x))

# 輸出結果
print(f'微分方程: {equation}')
print(f'通解: {solution}')

# 你也可以驗證解是否正確
print(f'驗證解的微分: {solution.rhs.diff(x)}')