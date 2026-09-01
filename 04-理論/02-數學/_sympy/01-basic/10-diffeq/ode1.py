"""
SymPy 微分方程 (ODE/PDE) 求解器示範
展示常微分方程和偏微分方程的符號求解
"""

from sympy import symbols, Function, Eq, dsolve, diff, sin, cos, exp, sqrt, pi
from sympy import simplify, apart, expand, integrate, Derivative
from sympy.solvers.ode import classify_ode
import sympy as sp

print("=" * 70)
print("SymPy 微分方程求解器 (ODE Solver)")
print("=" * 70)

# 定義符號和函數
t, x = symbols('t x', real=True)
y = Function('y')
f = Function('f')

print("\n符號定義:")
print(f"  獨立變數: t, x")
print(f"  函數: y(t), f(x)")

print("\n" + "=" * 70)
print("1. 一階常微分方程")
print("=" * 70)

print("\n(1) 可分離變數 (Separable)")
print("─" * 50)

# dy/dt = y
ode1 = Eq(y(t).diff(t), y(t))
print(f"\n微分方程: {ode1}")
print("dy/dt = y")

# 求解
sol1 = dsolve(ode1, y(t))
print(f"\n解: {sol1}")
print("通解: y(t) = C₁·exp(t)")

# 分類
classification1 = classify_ode(ode1, y(t))
print(f"\n方程類型: {classification1}")

print("\n(2) 可分離變數 - 帶初值條件")
print("─" * 50)

# dy/dt = 2ty, y(0) = 1
ode2 = Eq(y(t).diff(t), 2*t*y(t))
print(f"\n微分方程: {ode2}")
print("dy/dt = 2ty")

# 求通解
sol2 = dsolve(ode2, y(t))
print(f"\n通解: {sol2}")

# 帶初值條件
sol2_ic = dsolve(ode2, y(t), ics={y(0): 1})
print(f"特解 (y(0)=1): {sol2_ic}")

print("\n(3) 一階線性方程")
print("─" * 50)

# dy/dt + y = exp(t)
ode3 = Eq(y(t).diff(t) + y(t), exp(t))
print(f"\n微分方程: {ode3}")
print("dy/dt + y = exp(t)")

sol3 = dsolve(ode3, y(t))
print(f"\n解: {sol3}")

# 驗證解
print("\n驗證解:")
y_sol = sol3.rhs
lhs = y_sol.diff(t) + y_sol
rhs = exp(t)
print(f"代入左側: {simplify(lhs)}")
print(f"右側: {rhs}")
print(f"驗證: {simplify(lhs - rhs) == 0} ✓")

print("\n" + "=" * 70)
print("2. 二階常微分方程")
print("=" * 70)

print("\n(1) 簡諧振動 (Simple Harmonic Oscillator)")
print("─" * 50)

# y'' + y = 0
ode4 = Eq(y(t).diff(t, 2) + y(t), 0)
print(f"\n微分方程: {ode4}")
print("d²y/dt² + y = 0")

sol4 = dsolve(ode4, y(t))
print(f"\n解: {sol4}")
print("通解: y(t) = C₁·cos(t) + C₂·sin(t)")

# 帶初值條件
sol4_ic = dsolve(ode4, y(t), ics={y(0): 1, y(t).diff(t).subs(t, 0): 0})
print(f"\n特解 (y(0)=1, y'(0)=0): {sol4_ic}")

classification4 = classify_ode(ode4, y(t))
print(f"\n方程類型: {classification4}")

print("\n(2) 阻尼振動 (Damped Oscillator)")
print("─" * 50)

# y'' + 2y' + 5y = 0
ode5 = Eq(y(t).diff(t, 2) + 2*y(t).diff(t) + 5*y(t), 0)
print(f"\n微分方程: {ode5}")
print("d²y/dt² + 2dy/dt + 5y = 0")

sol5 = dsolve(ode5, y(t))
print(f"\n解: {sol5}")
print("包含 exp(-t) 的衰減振盪")

print("\n(3) 強迫振動 (Forced Oscillator)")
print("─" * 50)

# y'' + y = cos(2t)
ode6 = Eq(y(t).diff(t, 2) + y(t), cos(2*t))
print(f"\n微分方程: {ode6}")
print("d²y/dt² + y = cos(2t)")

sol6 = dsolve(ode6, y(t))
print(f"\n解: {sol6}")
print("齊次解 + 特解")

print("\n" + "=" * 70)
print("3. 高階常微分方程")
print("=" * 70)

print("\n三階線性常係數方程")
print("─" * 50)

# y''' - y = 0
ode7 = Eq(y(t).diff(t, 3) - y(t), 0)
print(f"\n微分方程: {ode7}")
print("d³y/dt³ - y = 0")

sol7 = dsolve(ode7, y(t))
print(f"\n解: {sol7}")

print("\n" + "=" * 70)
print("4. 非線性微分方程")
print("=" * 70)

print("\n(1) Bernoulli 方程")
print("─" * 50)

# dy/dt = y - y²
ode8 = Eq(y(t).diff(t), y(t) - y(t)**2)
print(f"\n微分方程: {ode8}")
print("dy/dt = y - y²")

sol8 = dsolve(ode8, y(t))
print(f"\n解: {sol8}")

classification8 = classify_ode(ode8, y(t))
print(f"\n方程類型: {classification8}")

print("\n(2) Riccati 方程")
print("─" * 50)

# dy/dt = y² + 1
ode9 = Eq(y(t).diff(t), y(t)**2 + 1)
print(f"\n微分方程: {ode9}")
print("dy/dt = y² + 1")

sol9 = dsolve(ode9, y(t))
print(f"\n解: {sol9}")

print("\n" + "=" * 70)
print("5. 微分方程組")
print("=" * 70)

print("\n線性微分方程組 (Lotka-Volterra 模型)")
print("─" * 50)

x_func = Function('x')
y_func = Function('y')

# 捕食者-獵物模型 (簡化版)
print("\ndx/dt = x - xy")
print("dy/dt = -y + xy")

# SymPy 對方程組的支援有限，這裡演示單個方程
print("\n(對於方程組，通常需要數值方法或特殊技巧)")

print("\n" + "=" * 70)
print("6. 偏微分方程 (PDE)")
print("=" * 70)

print("\n(1) 波動方程 (Wave Equation)")
print("─" * 50)

# 使用 pdsolve
from sympy import pdsolve, symbols, Function

x, t = symbols('x t')
u = Function('u')

# ∂²u/∂t² = c² ∂²u/∂x²
c = symbols('c', positive=True, real=True)
wave_eq = Eq(u(x, t).diff(t, 2), c**2 * u(x, t).diff(x, 2))
print(f"\n波動方程: ∂²u/∂t² = c² ∂²u/∂x²")

try:
    sol_wave = pdsolve(wave_eq, u(x, t))
    print(f"\n解: {sol_wave}")
except:
    print("\n一般解: u(x,t) = f(x-ct) + g(x+ct)")
    print("(d'Alembert 解)")

print("\n(2) 熱傳導方程 (Heat Equation)")
print("─" * 50)

# ∂u/∂t = α ∂²u/∂x²
alpha = symbols('alpha', positive=True, real=True)
print(f"\n熱傳導方程: ∂u/∂t = α ∂²u/∂x²")
print("解需要邊界條件")
print("典型解: u(x,t) = Σ Aₙ exp(-α n²π²t/L²) sin(nπx/L)")

print("\n(3) 拉普拉斯方程 (Laplace Equation)")
print("─" * 50)

print(f"\n拉普拉斯方程: ∇²u = ∂²u/∂x² + ∂²u/∂y² = 0")
print("調和函數")

# 簡單例子
u_laplace = x**2 - t**2
laplacian = u_laplace.diff(x, 2) + u_laplace.diff(t, 2)
print(f"\nu(x,t) = x² - t²")
print(f"∇²u = {laplacian}")
print("這是一個調和函數 ✓")

print("\n" + "=" * 70)
print("7. 物理應用實例")
print("=" * 70)

print("\n(1) 自由落體運動")
print("─" * 50)

g = symbols('g', positive=True, real=True)
ode_gravity = Eq(y(t).diff(t, 2), -g)
print(f"\n加速度方程: {ode_gravity}")
print("d²y/dt² = -g")

sol_gravity = dsolve(ode_gravity, y(t))
print(f"\n通解: {sol_gravity}")

# 帶初值條件 y(0) = 0, y'(0) = v0
v0 = symbols('v0', real=True)
sol_gravity_ic = dsolve(ode_gravity, y(t), ics={y(0): 0, y(t).diff(t).subs(t, 0): v0})
print(f"特解 (y(0)=0, v(0)=v₀): {sol_gravity_ic}")

print("\n(2) RC 電路")
print("─" * 50)

R, C, V0 = symbols('R C V_0', positive=True, real=True)
V = Function('V')

# RC dV/dt + V = 0
ode_rc = Eq(R*C*V(t).diff(t) + V(t), 0)
print(f"\n電路方程: RC dV/dt + V = 0")

sol_rc = dsolve(ode_rc, V(t))
print(f"\n通解: {sol_rc}")

# 帶初值條件
sol_rc_ic = dsolve(ode_rc, V(t), ics={V(0): V0})
print(f"特解 (V(0)=V₀): {sol_rc_ic}")

print("\n(3) 單擺 (小角度近似)")
print("─" * 50)

L, g_val = symbols('L g', positive=True, real=True)
theta = Function('theta')

# θ'' + (g/L)θ = 0
ode_pendulum = Eq(theta(t).diff(t, 2) + (g_val/L)*theta(t), 0)
print(f"\n單擺方程: d²θ/dt² + (g/L)θ = 0")

sol_pendulum = dsolve(ode_pendulum, theta(t))
print(f"\n解: {sol_pendulum}")
print("簡諧振動,週期 T = 2π√(L/g)")

print("\n(4) 放射性衰變")
print("─" * 50)

lambda_decay = symbols('lambda', positive=True, real=True)
N = Function('N')

# dN/dt = -λN
ode_decay = Eq(N(t).diff(t), -lambda_decay*N(t))
print(f"\n衰變方程: dN/dt = -λN")

sol_decay = dsolve(ode_decay, N(t))
print(f"\n解: {sol_decay}")

N0 = symbols('N_0', positive=True)
sol_decay_ic = dsolve(ode_decay, N(t), ics={N(0): N0})
print(f"特解 (N(0)=N₀): {sol_decay_ic}")
print("指數衰變: N(t) = N₀ exp(-λt)")

print("\n" + "=" * 70)
print("8. 可用的求解方法")
print("=" * 70)

print("\nSymPy 支援的 ODE 類型:")
print("✓ 可分離變數 (separable)")
print("✓ 齊次方程 (homogeneous)")
print("✓ 一階線性 (1st_linear)")
print("✓ Bernoulli 方程")
print("✓ Riccati 方程")
print("✓ 恰當方程 (exact)")
print("✓ 線性常係數方程 (nth_linear_constant_coeff)")
print("✓ Euler 方程")
print("✓ Liouville 方程")
print("✓ 以及更多...")

print("\n查看方程類型:")
example_ode = Eq(y(t).diff(t), y(t))
methods = classify_ode(example_ode, y(t))
print(f"dy/dt = y 的類型: {methods}")

print("\n" + "=" * 70)
print("9. 級數解法 (Series Solutions)")
print("=" * 70)

print("\n對於無法用初等函數表示的方程,可以使用級數解")

# 例: Airy 方程
# y'' - xy = 0
ode_airy = Eq(y(x).diff(x, 2) - x*y(x), 0)
print(f"\nAiry 方程: y'' - xy = 0")

try:
    sol_airy = dsolve(ode_airy, y(x))
    print(f"解: {sol_airy}")
except:
    print("解: 以 Airy 函數 Ai(x) 和 Bi(x) 表示")
    print("y(x) = C₁·Ai(x) + C₂·Bi(x)")

print("\n" + "=" * 70)
print("10. 數值方法提示")
print("=" * 70)

print("\n當符號解不存在或太複雜時:")
print("• 使用 scipy.integrate.odeint")
print("• 使用 scipy.integrate.solve_ivp")
print("• SymPy 可以生成數值求解器的代碼")

print("\n範例:")
print("""
from scipy.integrate import odeint
import numpy as np

def model(y, t):
    dydt = -2 * y
    return dydt

y0 = 5
t = np.linspace(0, 5, 100)
y = odeint(model, y0, t)
""")

print("\n" + "=" * 70)
print("示範完成!")
print("=" * 70)

print("\n摘要:")
print("SymPy 提供了強大的微分方程求解功能:")
print("✓ 常微分方程 (ODE) - 符號解")
print("✓ 偏微分方程 (PDE) - 部分支援")
print("✓ 初值問題 (IVP)")
print("✓ 邊值問題 (BVP)")
print("✓ 線性和非線性方程")
print("✓ 方程分類和識別")
print("✓ 解的驗證")

print("\n適用於:")
print("• 物理學 (力學、電磁學、量子力學)")
print("• 工程學 (控制理論、電路分析)")
print("• 生物學 (族群動力學)")
print("• 經濟學 (增長模型)")
print("• 化學 (反應動力學)")

print("\n限制:")
print("• 並非所有方程都有符號解")
print("• 複雜方程可能需要數值方法")
print("• 方程組支援有限")
print("• PDE 求解功能較基礎")