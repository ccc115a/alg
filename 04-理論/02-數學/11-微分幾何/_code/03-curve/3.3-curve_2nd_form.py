from sympy import symbols, Matrix, diff, cos, sin, simplify, sqrt
import numpy as np

# 1. 定義符號變數和曲面參數
u, v = symbols('u v') # 曲面參數
R, r_a = symbols('R r_a', real=True, positive=True) # R: 大半徑, r_a: 小半徑

# 2. 定義圓環面 (Torus) 參數化曲面 $\mathbf{r}(u, v)$
x = (R + r_a * cos(v)) * cos(u)
y = (R + r_a * cos(v)) * sin(u)
z = r_a * sin(v)
r = Matrix([x, y, z])

print(f"--- 圓環面 (Torus) 的第二基本形式與曲率計算 ---")
print(f"曲面 $\\mathbf{{r}}(u, v)$:\n{r.T}")

# 3. 第一基本形式係數 (E, F, G) - 來自 3.2 節
# 協變度量張量 $g_{ij}$
r_u = diff(r, u)
r_v = diff(r, v)
E = simplify(r_u.dot(r_u))
F = simplify(r_u.dot(r_v))
G = simplify(r_v.dot(r_v))
g_det = simplify(E * G - F**2) # 度量行列式 $g$

# 4. 單位法向量 $\mathbf{n}$ 的計算
# 法向量 $\mathbf{r}_u \times \mathbf{r}_v$
normal_vec_raw = r_u.cross(r_v)
# 法向量範數 $\|\mathbf{r}_u \times \mathbf{r}_v\| = \sqrt{\det(g_{ij})} = \sqrt{g}$
normal_vec_norm = sqrt(g_det)

# 單位法向量 $\mathbf{n}$
n = (1 / normal_vec_norm) * normal_vec_raw
n = simplify(n)

print(f"\n單位法向量 $\\mathbf{{n}}$:\n{n.T}")
print("-" * 50)

# 5. 第二基本形式係數 (L, M, N) 的計算
# 需要計算二階導數 $\mathbf{r}_{uu}, \mathbf{r}_{uv}, \mathbf{r}_{vv}$
r_uu = diff(r_u, u)
r_uv = diff(r_u, v)
r_vv = diff(r_v, v)

# L = $\mathbf{r}_{uu} \cdot \mathbf{n}$
L = simplify(r_uu.dot(n))

# M = $\mathbf{r}_{uv} \cdot \mathbf{n}$
M = simplify(r_uv.dot(n))

# N = $\mathbf{r}_{vv} \cdot \mathbf{n}$
N = simplify(r_vv.dot(n))

print(f"第二基本形式係數 L: {L}")
print(f"第二基本形式係數 M: {M}")
print(f"第二基本形式係數 N: {N}")
print("-" * 50)

# 6. 高斯曲率 K 與 平均曲率 H 的計算

# 高斯曲率 $K = \frac{LN - M^2}{EG - F^2}$
K_numerator = simplify(L * N - M**2)
K = K_numerator / g_det
K = simplify(K)

# 平均曲率 $H = \frac{EN - 2FM + GL}{2(EG - F^2)}$
H_numerator = simplify(E * N - 2 * F * M + G * L)
H = H_numerator / (2 * g_det)
H = simplify(H)

print(f"\n高斯曲率 $K$: {K}")
print(f"平均曲率 $H$: {H}")
print("="*50)

# 7. 數值驗證 (特定點: R=5, r_a=2, u=0, v=0)
# 此點為 $x=R+r_a, y=0, z=0$ (外圈最遠點)

R_val, ra_val = 5.0, 2.0
u_val, v_val = 0.0, 0.0

# 替代符號變數
K_num = K.subs({R: R_val, r_a: ra_val, u: u_val, v: v_val})
H_num = H.subs({R: R_val, r_a: ra_val, u: u_val, v: v_val})

K_val = float(K_num)
H_val = float(H_num)

# 理論結果: 在外圈 K = 1 / (r_a * (R + r_a))
K_theory = 1 / (ra_val * (R_val + ra_val))

print(f"\n--- 數值驗證 (R={R_val}, r_a={ra_val}, 點 $u=0, v=0$) ---")
print(f"數值高斯曲率 $K$: {K_val:.6f}")
print(f"數值平均曲率 $H$: {H_val:.6f}")
print(f"理論高斯曲率 K: {K_theory:.6f}")