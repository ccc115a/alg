import sympy as sp
import numpy as np

# 1. 定義符號變數
x, y, z, t = sp.symbols('x y z t')

# 2. 定義向量場 F(x, y, z) = -y*i + x*j + 0*k
P = -y
Q = x
R = 0
F = sp.Matrix([P, Q, R])

print("--- 旋度定理示範 (斯托克斯定理) ---")
print(f"向量場 F = ({P}, {Q}, {R})")
print(f"曲面 S: 單位圓盤 (x^2 + y^2 <= 1, z = 0)，法向量 n = (0, 0, 1)")
print("-" * 25)

## A. 計算線積分 (右邊) (環量)
# ------------------------------

# 1. 參數化邊界曲線 C: 單位圓 x^2 + y^2 = 1, z=0
# 遵循右手定則，法向量 n=(0, 0, 1) 指向 z 正方向，曲線 C 必須是逆時針方向。
# r(t) = (cos(t), sin(t), 0), t 屬於 [0, 2*pi]
r_t = sp.Matrix([sp.cos(t), sp.sin(t), 0])
dr_dt = sp.diff(r_t, t)  # 這是 dr/dt

# 2. 將 F 替換為 r(t)
F_at_t = F.subs({x: r_t[0], y: r_t[1], z: r_t[2]})

# 3. 計算 F * dr/dt (點積)
integrand_line = F_at_t.dot(dr_dt)

# 4. 線積分 (從 t=0 到 2*pi)
line_integral = sp.integrate(integrand_line, (t, 0, 2 * sp.pi))

print("A. 線積分 (右邊 - 環量):")
print(f"   參數化曲線 r(t) = {r_t.T}")
print(f"   F * dr/dt = {integrand_line}")
print(f"   線積分結果 = {line_integral}")
print("-" * 25)

## B. 計算曲面積分 (左邊) (旋度的通量)
# ------------------------------------

# 1. 計算旋度 (Curl) ∇ × F
# curl(F) = (dR/dy - dQ/dz)i + (dP/dz - dR/dx)j + (dQ/dx - dP/dy)k
curl_F_i = sp.diff(R, y) - sp.diff(Q, z)
curl_F_j = sp.diff(P, z) - sp.diff(R, x)
curl_F_k = sp.diff(Q, x) - sp.diff(P, y)
curl_F = sp.Matrix([curl_F_i, curl_F_j, curl_F_k])

# 2. 定義曲面法向量 n
# S 位於 z=0 平面，面向正 z 軸，因此 n = (0, 0, 1)
n_vector = sp.Matrix([0, 0, 1])

# 3. 計算 (∇ × F) · n (點積)
integrand_surface = curl_F.dot(n_vector)

# 4. 曲面積分計算
# S 是單位圓盤 (x^2 + y^2 <= 1)，使用極座標更容易。
# dA = dx dy (在 z=0 平面上)
# (∇ × F) · n = 2
# 曲面積分 = integrate(2, (y, ...), (x, ...))
# 或者直接 2 * Area(S)

# 由於被積函數是一個常數 2，我們可以直接計算：
# 圓盤面積 Area(S) = pi * r^2 = pi * 1^2 = pi
surface_integral = 2 * sp.pi

print("B. 曲面積分 (左邊 - 旋度通量):")
print(f"   旋度 curl(F) = {curl_F.T}")
print(f"   (∇ × F) · n = {integrand_surface}")
print(f"   積分區域 S 面積 = pi")
print(f"   曲面積分結果 (2 * pi) = {surface_integral}")
print("-" * 25)

## C. 結論
# ------------------------------

print("C. 驗證結果:")
if line_integral == surface_integral:
    print(f"✅ 兩邊相等: {line_integral} = {surface_integral}")
    print("旋度定理（斯托克斯定理）在此例中得到驗證。")
else:
    print(f"❌ 兩邊不相等: 線積分 = {line_integral}, 曲面積分 = {surface_integral}")
