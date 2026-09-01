import sympy as sp
from sympy import symbols, Function, Eq, dsolve, pde_separate, pdsolve
import numpy as np
import matplotlib.pyplot as plt

# 定義符號變數
x, y, z, t = symbols('x y z t')
u = Function('u')
C1, C2 = symbols('C1 C2')

print("=" * 60)
print("SymPy 偏微分方程求解例子")
print("=" * 60)

# 例子 1: 一維熱傳導方程 (Heat Equation)
print("\n1. 一維熱傳導方程: ∂u/∂t = k * ∂²u/∂x²")
print("-" * 50)

# 定義 u(x,t)
u1 = Function('u1')
k = symbols('k', positive=True)

# 熱傳導方程: u_t = k * u_xx
heat_eq = Eq(u1(x,t).diff(t), k * u1(x,t).diff(x, 2))
print(f"方程: {heat_eq}")

# 使用分離變數法
try:
    heat_sol = pdsolve(heat_eq, u1(x,t))
    print(f"通解: {heat_sol}")
except:
    print("使用分離變數法求解...")
    # 假設解的形式為 u(x,t) = X(x)T(t)
    X = Function('X')
    T = Function('T')
    
    # 分離後的常微分方程
    print("假設 u(x,t) = X(x)T(t)")
    print("分離變數後得到:")
    print("T'(t)/T(t) = k * X''(x)/X(x) = -λ")

# 例子 2: 一維波動方程 (Wave Equation)
print("\n2. 一維波動方程: ∂²u/∂t² = c² * ∂²u/∂x²")
print("-" * 50)

u2 = Function('u2')
c = symbols('c', positive=True)

# 波動方程: u_tt = c² * u_xx
wave_eq = Eq(u2(x,t).diff(t, 2), c**2 * u2(x,t).diff(x, 2))
print(f"方程: {wave_eq}")

try:
    wave_sol = pdsolve(wave_eq, u2(x,t))
    print(f"通解: {wave_sol}")
except:
    print("d'Alembert 解: u(x,t) = f(x-ct) + g(x+ct)")

# 例子 3: Laplace 方程 (二維)
print("\n3. 二維 Laplace 方程: ∂²u/∂x² + ∂²u/∂y² = 0")
print("-" * 50)

u3 = Function('u3')

# Laplace 方程: u_xx + u_yy = 0
laplace_eq = Eq(u3(x,y).diff(x, 2) + u3(x,y).diff(y, 2), 0)
print(f"方程: {laplace_eq}")

# 嘗試分離變數
try:
    sep_result = pde_separate(laplace_eq, u3(x,y), [x, y])
    print(f"分離變數結果: {sep_result}")
except:
    print("使用分離變數: u(x,y) = X(x)Y(y)")
    print("得到: X''(x)/X(x) + Y''(y)/Y(y) = 0")

# 例子 4: 一維擴散方程的特解
print("\n4. 一維擴散方程特解求解")
print("-" * 50)

# 使用具體的初始條件和邊界條件
u4 = Function('u4')
D = symbols('D', positive=True)

# 擴散方程: u_t = D * u_xx
diffusion_eq = Eq(u4(x,t).diff(t), D * u4(x,t).diff(x, 2))
print(f"方程: {diffusion_eq}")

# 假設解的形式
print("假設解: u(x,t) = exp(-λt) * sin(nπx/L)")
print("其中 λ = D * (nπ/L)²")

# 例子 5: 使用 SymPy 求解具體的 PDE
print("\n5. 求解具體的線性 PDE")
print("-" * 50)

# 定義一個簡單的 PDE: u_x + u_y = 0
u5 = Function('u5')
simple_pde = Eq(u5(x,y).diff(x) + u5(x,y).diff(y), 0)
print(f"方程: {simple_pde}")

try:
    simple_sol = pdsolve(simple_pde, u5(x,y))
    print(f"解: {simple_sol}")
except Exception as e:
    print(f"無法直接求解: {e}")
    print("這是一個特徵線方程，解為: u(x,y) = f(x-y)")

# 例子 6: 非齊次 PDE
print("\n6. 非齊次偏微分方程")
print("-" * 50)

u6 = Function('u6')
# u_x + u_y = x + y
nonhom_pde = Eq(u6(x,y).diff(x) + u6(x,y).diff(y), x + y)
print(f"方程: {nonhom_pde}")

print("這類方程需要使用特徵線方法或其他數值方法求解")

# 例子 7: 驗證解
print("\n7. 驗證 PDE 解")
print("-" * 50)

# 驗證 u = x² + y² 是否為 Laplace 方程的解
test_u = x**2 + y**2
laplacian = test_u.diff(x, 2) + test_u.diff(y, 2)
print(f"測試函數: u = {test_u}")
print(f"Laplacian: ∇²u = {laplacian}")
print(f"是否為調和函數: {laplacian == 0}")

# 驗證 u = e^(-t) * sin(x) 是否為熱傳導方程的解
test_u2 = sp.exp(-t) * sp.sin(x)
heat_check = test_u2.diff(t) - test_u2.diff(x, 2)
print(f"\n測試函數: u = {test_u2}")
print(f"熱傳導方程檢驗: u_t - u_xx = {heat_check}")
print(f"是否為解: {heat_check == 0}")

print("\n" + "=" * 60)
print("注意事項:")
print("1. SymPy 對複雜 PDE 的求解能力有限")
print("2. 許多實際問題需要數值方法")
print("3. 邊界條件和初始條件對解的唯一性很重要")
print("4. 分離變數法是常用的解析方法")
print("=" * 60)