from sympy import symbols, Matrix, diff, sqrt, simplify
import numpy as np

# 1. 定義符號變數和曲線
t = symbols('t')
a, b = symbols('a b', real=True, positive=True) # 螺旋線的參數 (a: 半徑, b: 高度比例)

# 定義一條螺旋線 (Helix) 參數化曲線 $\mathbf{r}(t)$ in $\mathbb{R}^3$
# $\mathbf{r}(t) = (a \cos t, a \sin t, b t)$
r = Matrix([a * cos(t), a * sin(t), b * t])

print(f"--- 曲線的弗雷內標架 (Frenet Frame) 符號計算 ---")
print(f"曲線 $\\mathbf{{r}}(t)$: {r.T}")

# 2. 計算一階、二階、三階導數

# 一階導數 (速度向量 $\mathbf{r}'$)
r_prime = diff(r, t)
print(f"\n一階導數 $\\mathbf{{r}}'(t)$: {r_prime.T}")

# 二階導數 (加速度向量 $\mathbf{r}''$)
r_double_prime = diff(r_prime, t)
print(f"二階導數 $\\mathbf{{r}}''(t)$: {r_double_prime.T}")

# 三階導數
r_triple_prime = diff(r_double_prime, t)

# 3. 計算重要輔助量
# 速度的平方 (用於弧長參數和曲率分母)
speed_sq = r_prime.dot(r_prime)
speed = sqrt(speed_sq)

# $\mathbf{r}' \times \mathbf{r}''$ 向量的範數 (Numerator of Curvature)
r_cross_r = r_prime.cross(r_double_prime)
norm_r_cross_r_sq = r_cross_r.dot(r_cross_r)
norm_r_cross_r = sqrt(norm_r_cross_r_sq)

# 4. 弗雷內標架的計算

# A. 切線向量 (Tangent Vector) $\mathbf{T}$
T = (1 / speed) * r_prime
T = simplify(T) # 符號簡化

# B. 曲率 (Curvature) $\kappa$
kappa = norm_r_cross_r / speed**3
kappa = simplify(kappa)

# C. 主法線向量 (Normal Vector) $\mathbf{N}$
# 最簡單的計算方式是 $\mathbf{N} = \frac{\mathbf{r}' \times \mathbf{r}''}{\|\mathbf{r}' \times \mathbf{r}''\|} \times \mathbf{T}$
# 或使用 $\mathbf{N} = \frac{\mathbf{T}'}{\|\mathbf{T}'\|}$ (但 $\mathbf{T}'$ 符號計算複雜)
# 我們使用定義 $\mathbf{N} = \frac{\mathbf{T}'}{\kappa}$ 
T_prime = diff(T, t)
norm_T_prime = sqrt(T_prime.dot(T_prime)) # $\|\mathbf{T}'\|$
N_raw = (1 / norm_T_prime) * T_prime
N = simplify(N_raw)

# D. 次法線向量 (Binormal Vector) $\mathbf{B}$
# $\mathbf{B} = \mathbf{T} \times \mathbf{N}$
B = T.cross(N)
B = simplify(B)

# E. 撓率 (Torsion) $\tau$
# $\tau = \frac{(\mathbf{r}' \times \mathbf{r}'') \cdot \mathbf{r}'''}{\|\mathbf{r}' \times \mathbf{r}''\|^2}$
numerator_tau = r_cross_r.dot(r_triple_prime)
denominator_tau = norm_r_cross_r_sq
tau = numerator_tau / denominator_tau
tau = simplify(tau)

print("\n" + "="*50)
print("--- 弗雷內標架與曲率/撓率 (解析解) ---")
print(f"速度 $\\mathbf{{r}}'$ 範數 $|\\mathbf{{r}}'|$: {speed}")
print(f"切線向量 $\\mathbf{{T}}$: {T.T}")
print(f"主法線向量 $\\mathbf{{N}}$: {N.T}")
print(f"次法線向量 $\\mathbf{{B}}$: {B.T}")
print(f"曲率 $\\kappa$: {kappa}")
print(f"撓率 $\\tau$: {tau}")
print("="*50)


# 5. 在特定點進行數值計算 (假設 a=3, b=4, t=$\pi/2$)
a_val, b_val, t_val = 3.0, 4.0, np.pi/2

# 符號替換並轉換為數值
T_num = T.subs({a: a_val, b: b_val, t: t_val})
N_num = N.subs({a: a_val, b: b_val, t: t_val})
B_num = B.subs({a: a_val, b: b_val, t: t_val})
kappa_num = kappa.subs({a: a_val, b: b_val, t: t_val})
tau_num = tau.subs({a: a_val, b: b_val, t: t_val})

# 將 SymPy Matrix 轉換為 NumPy array 進行美化輸出
T_arr = np.array(T_num).astype(float).flatten()
N_arr = np.array(N_num).astype(float).flatten()
B_arr = np.array(B_num).astype(float).flatten()
kappa_val = float(kappa_num)
tau_val = float(tau_num)

print(f"\n--- 數值計算 (a={a_val}, b={b_val}, t={t_val}) ---")
print(f"數值切線 $\\mathbf{{T}}$: {T_arr.round(4)}")
print(f"數值主法線 $\\mathbf{{N}}$: {N_arr.round(4)}")
print(f"數值次法線 $\\mathbf{{B}}$: {B_arr.round(4)}")
print(f"數值曲率 $\\kappa$: {kappa_val:.4f}")
print(f"數值撓率 $\\tau$: {tau_val:.4f}")