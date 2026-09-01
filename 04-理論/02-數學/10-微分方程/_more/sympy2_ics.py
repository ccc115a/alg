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