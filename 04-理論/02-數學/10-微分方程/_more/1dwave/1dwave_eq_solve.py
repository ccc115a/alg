import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from sympy import symbols, Function, Eq, dsolve, cos, sin, exp, I, pi
from sympy.abc import x, t

print("=== 波方程的 SymPy 求解 ===")
print()

# 定義符號和函數
u = Function('u')(x, t)  # 波函數 u(x,t)
v = symbols('v', positive=True)  # 波速 v > 0

print("1. 波方程的定義:")
print("   ∂²u/∂t² = v² ∂²u/∂x²")
print()

# 定義波方程
wave_eq = Eq(u.diff(t, 2), v**2 * u.diff(x, 2))
print("2. SymPy 表示的波方程:")
print(f"   {wave_eq}")
print()

print("=== 方法一：特徵線方法（d'Alembert 解） ===")
print()

# d'Alembert 通解
print("3. d'Alembert 通解（行波解）:")
print("   u(x,t) = f(x - vt) + g(x + vt)")
print("   其中 f 和 g 是任意可微函數")
print()

# 示例：正弦波解
A, k, omega, phi = symbols('A k omega phi', real=True)
print("4. 正弦波特解示例:")
u_sin = A * sin(k*x - omega*t + phi)
print(f"   u(x,t) = {u_sin}")
print("   其中 ω = kv（色散關係）")
print()

# 驗證正弦波解
print("5. 驗證正弦波解滿足波方程:")
lhs = u_sin.diff(t, 2)
rhs = v**2 * u_sin.diff(x, 2)
print(f"   ∂²u/∂t² = {lhs}")
print(f"   v²∂²u/∂x² = {rhs}")

# 將 omega = k*v 代入驗證
omega_relation = k * v
lhs_sub = lhs.subs(omega, omega_relation)
rhs_sub = rhs.subs(omega, omega_relation)
print(f"   當 ω = kv 時:")
print(f"   ∂²u/∂t² = {lhs_sub}")
print(f"   v²∂²u/∂x² = {rhs_sub}")
print(f"   等式成立：{sp.simplify(lhs_sub - rhs_sub) == 0}")
print()

print("=== 方法二：分離變數法 ===")
print()

print("6. 假設 u(x,t) = X(x)T(t)，代入波方程得到:")
print("   X(x)T''(t) = v²X''(x)T(t)")
print("   分離變數：T''(t)/v²T(t) = X''(x)/X(x) = -k²")
print()

# 定義分離後的函數
X = Function('X')(x)
T = Function('T')(t)
k_sep = symbols('k', real=True)

print("7. 求解時間部分 T''(t) + (kv)²T(t) = 0:")
T_eq = Eq(T.diff(t, 2) + (k_sep*v)**2 * T, 0)
T_sol = dsolve(T_eq, T)
print(f"   {T_sol}")
print()

print("8. 求解空間部分 X''(x) + k²X(x) = 0:")
X_eq = Eq(X.diff(x, 2) + k_sep**2 * X, 0)
X_sol = dsolve(X_eq, X)
print(f"   {X_sol}")
print()

print("9. 完整的分離變數解:")
print("   u(x,t) = [A·cos(kx) + B·sin(kx)] × [C·cos(kvt) + D·sin(kvt)]")
print("   或展開為:")
print("   u(x,t) = A₁·cos(kx)cos(kvt) + A₂·cos(kx)sin(kvt)")
print("            + A₃·sin(kx)cos(kvt) + A₄·sin(kx)sin(kvt)")
print()

print("=== 常見的波解類型 ===")
print()

# 示例解
print("10. 常見波解示例:")
print()

# 右行波
u_right = Function('f')(x - v*t)
print(f"    a) 右行波: u(x,t) = f(x - vt)")
print(f"       例如: u(x,t) = sin(x - vt)")

# 左行波  
u_left = Function('g')(x + v*t)
print(f"    b) 左行波: u(x,t) = g(x + vt)")
print(f"       例如: u(x,t) = cos(x + vt)")

# 駐波
print(f"    c) 駐波: u(x,t) = A·sin(kx)cos(kvt)")
print(f"       這是兩個反向傳播波的疊加")

print()
print("11. 邊界條件和初始條件:")
print("    - 固定端: u(0,t) = u(L,t) = 0")
print("    - 自由端: ∂u/∂x|ₓ₌₀ = ∂u/∂x|ₓ₌ₗ = 0") 
print("    - 初始位移: u(x,0) = f(x)")
print("    - 初始速度: ∂u/∂t|ₜ₌₀ = g(x)")
print()

print("=== 特殊情況：有界弦的駐波解 ===")
print()

# 有界弦的解
L = symbols('L', positive=True)  # 弦長
n = symbols('n', integer=True, positive=True)  # 模式數

print("12. 長度為 L 的固定端弦的駐波解:")
print("    邊界條件: u(0,t) = u(L,t) = 0")
print("    特征頻率: ωₙ = nπv/L  (n = 1,2,3,...)")
print("    對應波數: kₙ = nπ/L")
print()

# 第 n 個模式的解
u_n = sin(n*pi*x/L) * cos(n*pi*v*t/L)
print(f"13. 第 n 個模式的解:")
print(f"    uₙ(x,t) = Aₙ·sin(nπx/L)cos(nπvt/L)")
print()

print("14. 一般解（所有模式的疊加）:")
print("    u(x,t) = Σ[n=1 to ∞] Aₙ·sin(nπx/L)cos(nπvt/L + φₙ)")
print("    其中 Aₙ 和 φₙ 由初始條件決定")
print()

print("=== 總結 ===")
print()
print("波方程 ∂²u/∂t² = v²∂²u/∂x² 的通解包括:")
print("1. d'Alembert 解: u(x,t) = f(x-vt) + g(x+vt)")
print("2. 行波解: u(x,t) = A·sin(kx ± ωt + φ)，其中 ω = kv")
print("3. 駐波解: u(x,t) = A·sin(kx)cos(ωt + φ)")
print("4. 一般解是以上基本解的線性疊加")
print()
print("具體的解取決於:")
print("- 邊界條件（固定端、自由端等）")
print("- 初始條件（初始位移和速度）")
print("- 波傳播的幾何形狀（一維、二維、三維）")