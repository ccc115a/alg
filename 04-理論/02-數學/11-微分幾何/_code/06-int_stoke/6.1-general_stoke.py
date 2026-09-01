from sympy import symbols, diff, integrate, Matrix, simplify

# 1. 定義符號變數和坐標
x, y = symbols('x y')
t = symbols('t') # 曲線積分參數
coords = [x, y]

print(f"--- 第 6 章：廣義斯托克斯定理 (Green's Theorem) 驗證 ---")
print(f"流形 $M$: 單位正方形 $[0, 1] \\times [0, 1]$")

# 2. 定義 1 形式 $\omega$
# $\omega = P dx + Q dy$
P = x**2 * y    # $\omega_x$ 係數
Q = x * y**2    # $\omega_y$ 係數

print(f"\n定義 1 形式 $\\omega$: $P={P}$, $Q={Q}$")
print("-" * 50)


# =========================================================================
# I. LHS: 計算面積分 $\int_M d\omega$
# =========================================================================

# 3. 計算外微分 $d\omega = (\frac{\partial Q}{\partial x} - \frac{\partial P}{\partial y}) dx \wedge dy$
partial_Q_x = diff(Q, x)
partial_P_y = diff(P, y)

integrand_LHS = partial_Q_x - partial_P_y # $\frac{\partial Q}{\partial x} - \frac{\partial P}{\partial y}$
integrand_LHS_simplified = simplify(integrand_LHS)

print(f"LHS 外微分 $d\\omega$ 的係數 $\\frac{{\partial Q}}{{\partial x}} - \\frac{{\partial P}}{{\partial y}}$: {integrand_LHS_simplified}")

# 4. 執行面積分 (對 $y$ 從 0 到 1, 對 $x$ 從 0 到 1)
# $\iint_{[0,1]^2} (y^2 - x^2) dy dx$
area_integral_y = integrate(integrand_LHS, (y, 0, 1))
area_integral_LHS = integrate(area_integral_y, (x, 0, 1))

print(f"LHS 面積分 $\\int_M d\\omega$: {area_integral_LHS}")
print("-" * 50)


# =========================================================================
# II. RHS: 計算曲線積分 $\oint_{\partial M} \omega$
# =========================================================================

# 5. 參數化邊界 $\partial M$ (逆時針方向)
# $\oint_{\partial M} \omega = \sum_{i=1}^4 \int_{C_i} \omega$
line_integral_RHS = 0

# C1: 底部 (y=0) - 從 $x=0$ 到 $x=1$
# 參數化: $x=t, y=0$, $t \in [0, 1]$. $dx=dt, dy=0$.
P1 = P.subs({x: t, y: 0})
Q1 = Q.subs({x: t, y: 0})
integrand1 = P1 * diff(t, t) + Q1 * diff(0, t) # $P dx + Q dy = P dt + Q (0)$
integral1 = integrate(integrand1, (t, 0, 1))
line_integral_RHS += integral1
print(f"RHS 曲線 C1 (底部, y=0): {integral1}")

# C2: 右側 (x=1) - 從 $y=0$ 到 $y=1$
# 參數化: $x=1, y=t$, $t \in [0, 1]$. $dx=0, dy=dt$.
P2 = P.subs({x: 1, y: t})
Q2 = Q.subs({x: 1, y: t})
integrand2 = P2 * diff(1, t) + Q2 * diff(t, t) # $P (0) + Q dt$
integral2 = integrate(integrand2, (t, 0, 1))
line_integral_RHS += integral2
print(f"RHS 曲線 C2 (右側, x=1): {integral2}")

# C3: 頂部 (y=1) - 從 $x=1$ 到 $x=0$ (反向)
# 參數化: $x=1-t, y=1$, $t \in [0, 1]$. $dx=-dt, dy=0$.
P3 = P.subs({x: 1-t, y: 1})
Q3 = Q.subs({x: 1-t, y: 1})
integrand3 = P3 * diff(1-t, t) + Q3 * diff(1, t) # $P (-dt) + Q (0)$
integral3 = integrate(integrand3, (t, 0, 1))
line_integral_RHS += integral3
print(f"RHS 曲線 C3 (頂部, y=1): {integral3}")

# C4: 左側 (x=0) - 從 $y=1$ 到 $y=0$ (反向)
# 參數化: $x=0, y=1-t$, $t \in [0, 1]$. $dx=0, dy=-dt$.
P4 = P.subs({x: 0, y: 1-t})
Q4 = Q.subs({x: 0, y: 1-t})
integrand4 = P4 * diff(0, t) + Q4 * diff(1-t, t) # $P (0) + Q (-dt)$
integral4 = integrate(integrand4, (t, 0, 1))
line_integral_RHS += integral4
print(f"RHS 曲線 C4 (左側, x=0): {integral4}")

print(f"\nRHS 總曲線積分 $\\oint_{{\partial M}} \\omega$: {simplify(line_integral_RHS)}")
print("-" * 50)


# 6. 結論驗證
verification = simplify(area_integral_LHS - line_integral_RHS)

print(f"\n驗證結果:")
print(f"左側 $\\int_M d\\omega$: {area_integral_LHS}")
print(f"右側 $\\int_{{\partial M}} \\omega$: {line_integral_RHS}")
print(f"LHS - RHS (應為 0): {verification}")
print("\n結論: $\\int_M d\\omega = \\int_{{\partial M}} \\omega$，廣義斯托克斯定理（格林定理）驗證成功。")