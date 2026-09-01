import sympy as sp
from sympy import symbols, diff, sqrt, simplify, Eq, solve, cos, sin, pi, integrate
from sympy.vector import CoordSys3D, Del, gradient, divergence, curl
import numpy as np

print("=" * 60)
print("馬克士威電磁波推導 (使用 SymPy)")
print("=" * 60)

# 定義符號變數
t, x, y, z = symbols('t x y z', real=True)
mu_0, epsilon_0, c = symbols('mu_0 epsilon_0 c', positive=True)

# 定義座標系統
C = CoordSys3D('C')

print("\n1. 馬克士威方程組 (真空中):")
print("   ∇ · E = 0           (高斯定律)")
print("   ∇ · B = 0           (磁場無源)")
print("   ∇ × E = -∂B/∂t      (法拉第定律)")
print("   ∇ × B = μ₀ε₀ ∂E/∂t  (安培-馬克士威定律)")

# 定義電場和磁場的分量
Ex, Ey, Ez = symbols('Ex Ey Ez', cls=sp.Function)
Bx, By, Bz = symbols('Bx By Bz', cls=sp.Function)

# 考慮沿 z 方向傳播的平面波
# 電場在 x 方向，磁場在 y 方向
print("\n2. 假設平面波解:")
print("   E = Ex(z,t) î")
print("   B = By(z,t) ĵ")

# 定義場的函數形式
E_x = Ex(z, t)
B_y = By(z, t)

print(f"\n3. 應用 ∇ × E = -∂B/∂t:")

# 計算 ∇ × E
# 對於 E = Ex(z,t) î，只有 ∂Ex/∂z ≠ 0
curl_E_y = -diff(E_x, z)  # (∇ × E)_y = -∂Ex/∂z

# ∂B/∂t
dB_dt_y = -diff(B_y, t)

# 法拉第定律: ∇ × E = -∂B/∂t
faraday_eq = Eq(curl_E_y, dB_dt_y)
print(f"   -∂Ex/∂z = -∂By/∂t")
print(f"   即: ∂Ex/∂z = ∂By/∂t  ... (1)")

print(f"\n4. 應用 ∇ × B = μ₀ε₀ ∂E/∂t:")

# 計算 ∇ × B
# 對於 B = By(z,t) ĵ，只有 ∂By/∂z ≠ 0
curl_B_x = diff(B_y, z)  # (∇ × B)_x = ∂By/∂z

# μ₀ε₀ ∂E/∂t
mu_eps_dE_dt_x = mu_0 * epsilon_0 * diff(E_x, t)

# 安培-馬克士威定律: ∇ × B = μ₀ε₀ ∂E/∂t
ampere_eq = Eq(curl_B_x, mu_eps_dE_dt_x)
print(f"   ∂By/∂z = μ₀ε₀ ∂Ex/∂t  ... (2)")

print(f"\n5. 推導波動方程:")
print("   對方程 (1) 關於 z 求偏微分:")
print("   ∂²Ex/∂z² = ∂²By/∂z∂t")

print("\n   對方程 (2) 關於 t 求偏微分:")
print("   ∂²By/∂z∂t = μ₀ε₀ ∂²Ex/∂t²")

print("\n   結合兩式得到 Ex 的波動方程:")
print("   ∂²Ex/∂z² = μ₀ε₀ ∂²Ex/∂t²")

# 定義波動方程
wave_eq_E = Eq(diff(E_x, z, 2), mu_0 * epsilon_0 * diff(E_x, t, 2))
print(f"\n   數學表達式: {wave_eq_E}")

# 同理可得 By 的波動方程
wave_eq_B = Eq(diff(B_y, z, 2), mu_0 * epsilon_0 * diff(B_y, t, 2))
print(f"   對 By: {wave_eq_B}")

print(f"\n6. 光速的推導:")
print("   標準波動方程形式: ∂²f/∂z² = (1/v²) ∂²f/∂t²")
print("   比較係數得: 1/v² = μ₀ε₀")
print("   因此波速: v = 1/√(μ₀ε₀) ≡ c")

# 計算光速表達式
c_expr = 1/sqrt(mu_0 * epsilon_0)
print(f"\n   c = {c_expr}")

print(f"\n7. 平面波解:")
print("   設 Ex(z,t) = E₀ cos(kz - ωt)")
print("   其中 k = ω/c 是波數")

# 定義具體的波解
E0, omega, k = symbols('E0 omega k', real=True)
phase = k*z - omega*t

Ex_solution = E0 * sp.cos(phase)
print(f"\n   Ex(z,t) = {Ex_solution}")

# 從法拉第定律求 By
# ∂Ex/∂z = ∂By/∂t
dEx_dz = diff(Ex_solution, z)
print(f"\n   ∂Ex/∂z = {dEx_dz}")

# 積分得到 By
By_from_faraday = sp.integrate(dEx_dz, t)
By_solution = (E0 * k / omega) * sp.sin(phase)
print(f"   By(z,t) = {By_solution}")

print(f"\n8. E 和 B 的關係:")
print("   從 ∇ × E = -∂B/∂t 和 ∇ × B = μ₀ε₀ ∂E/∂t")
print("   可以證明: |B| = |E|/c")

# 驗證 E 和 B 的關係
E_amplitude = E0
B_amplitude = E0 * k / omega
print(f"\n   |E| = {E_amplitude}")
print(f"   |B| = {B_amplitude}")
print(f"   由於 k = ω/c，所以 |B| = |E| × (k/ω) = |E|/c")

print(f"\n9. 電磁波的性質:")
print("   • E 和 B 相互垂直")
print("   • E 和 B 都垂直於傳播方向")
print("   • E 和 B 同相位振盪")
print("   • 波速 c = 1/√(μ₀ε₀) ≈ 3×10⁸ m/s")
print("   • 這就是光!")

print(f"\n10. 數值驗證 (使用 SI 單位):")
# 在 SI 單位制中的數值
mu_0_val = 4e-7 * sp.pi  # H/m
epsilon_0_val = 8.854e-12  # F/m

c_numerical = 1/sqrt(mu_0_val * epsilon_0_val)
print(f"    μ₀ = 4π × 10⁻⁷ H/m")
print(f"    ε₀ = 8.854 × 10⁻¹² F/m")
print(f"    c = 1/√(μ₀ε₀) ≈ {float(c_numerical.evalf()):.3e} m/s")

print(f"\n" + "=" * 60)
print("結論: 馬克士威成功預測了電磁波的存在，")
print("並證明光就是電磁波！")
print("=" * 60)