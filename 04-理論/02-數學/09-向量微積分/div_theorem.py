import sympy as sp

# 1. 定義符號變數
x, y, z = sp.symbols('x y z')

# 2. 定義向量場 F(x, y, z) = x*i + y*j + z*k
P = x
Q = y
R = z
F = (P, Q, R)

print("--- 散度定理示範 ---")
print(f"向量場 F = ({P}, {Q}, {R})")
print(f"體積 V: 0 <= x, y, z <= 1 (單位立方體)")
print("-" * 20)

## A. 計算體積分 (左邊)
# ------------------------------

# 1. 計算散度 (Divergence)
# div(F) = dP/dx + dQ/dy + dR/dz
div_F = sp.diff(P, x) + sp.diff(Q, y) + sp.diff(R, z)

# 2. 體積分計算 (三重積分 over V)
# 由於散度是一個常數，積分很容易
# 體積分 = integrate(div_F, (x, 0, 1), (y, 0, 1), (z, 0, 1))
volume_integral = sp.integrate(div_F, (x, 0, 1), (y, 0, 1), (z, 0, 1))

print(f"A. 體積分 (左邊):")
print(f"   散度 div(F) = {div_F}")
print(f"   三重積分結果 = {volume_integral}")
print("-" * 20)

## B. 計算面積分 (右邊) (通量)
# ------------------------------

# 單位立方體有 6 個表面，我們需要計算 F 穿過每個表面的通量，然後相加。
# n 是單位外法向量。通量 = F * n * dS

flux_sides = []

# 1. 表面 S1: x = 1 (n = (1, 0, 0))
#    dS = dy dz
#    F * n = (1)*1 + y*0 + z*0 = 1
flux_S1 = sp.integrate(1, (y, 0, 1), (z, 0, 1))
flux_sides.append(("x=1", flux_S1))

# 2. 表面 S2: x = 0 (n = (-1, 0, 0))
#    dS = dy dz
#    F * n = (0)*(-1) + y*0 + z*0 = 0
flux_S2 = sp.integrate(0, (y, 0, 1), (z, 0, 1))
flux_sides.append(("x=0", flux_S2))

# 3. 表面 S3: y = 1 (n = (0, 1, 0))
#    dS = dx dz
#    F * n = x*0 + (1)*1 + z*0 = 1
flux_S3 = sp.integrate(1, (x, 0, 1), (z, 0, 1))
flux_sides.append(("y=1", flux_S3))

# 4. 表面 S4: y = 0 (n = (0, -1, 0))
#    dS = dx dz
#    F * n = x*0 + (0)*(-1) + z*0 = 0
flux_S4 = sp.integrate(0, (x, 0, 1), (z, 0, 1))
flux_sides.append(("y=0", flux_S4))

# 5. 表面 S5: z = 1 (n = (0, 0, 1))
#    dS = dx dy
#    F * n = x*0 + y*0 + (1)*1 = 1
flux_S5 = sp.integrate(1, (x, 0, 1), (y, 0, 1))
flux_sides.append(("z=1", flux_S5))

# 6. 表面 S6: z = 0 (n = (0, 0, -1))
#    dS = dx dy
#    F * n = x*0 + y*0 + (0)*(-1) = 0
flux_S6 = sp.integrate(0, (x, 0, 1), (y, 0, 1))
flux_sides.append(("z=0", flux_S6))

# 總通量 (Total Flux)
surface_integral = sum(flux for _, flux in flux_sides)

print(f"B. 面積分 (右邊 - 總通量):")
for name, flux in flux_sides:
    print(f"   表面 {name} 通量: {flux}")
print(f"   總和 (六個表面相加) = {surface_integral}")
print("-" * 20)

## C. 結論
# ------------------------------

print("C. 驗證結果:")
if volume_integral == surface_integral:
    print(f"✅ 兩邊相等: {volume_integral} = {surface_integral}")
    print("散度定理在此例中得到驗證。")
else:
    print(f"❌ 兩邊不相等: 體積分 = {volume_integral}, 面積分 = {surface_integral}")