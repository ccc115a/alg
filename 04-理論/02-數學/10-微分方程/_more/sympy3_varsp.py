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