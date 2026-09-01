from sympy import symbols, Matrix, diff, simplify, sqrt, cos, acos, pi
import numpy as np

# 1. 定義符號變數和坐標
# 坐標 $x^1=r, x^2=\theta$ (極坐標)
r, theta = symbols('r theta', real=True, positive=True)
coords = [r, theta]
N = 2

print(f"--- 第 7 章：黎曼度量的幾何應用 (極坐標) ---")
print(f"坐標 $(x^1, x^2) = (r, \\theta)$")
print("-" * 50)


# 2. 定義黎曼度量張量 $g_{ij}$ (協變)
# 極坐標的度量張量: $g_{ij} = \begin{pmatrix} 1 & 0 \\ 0 & r^2 \end{pmatrix}$
g_ij_sym = Matrix([
    [1, 0],
    [0, r**2]
])

# 3. 計算逆變度量張量 $g^{ij}$ (用於提升指標)
g_upper_sym = g_ij_sym.inv().applyfunc(simplify)
g_det = simplify(g_ij_sym.det())

print(f"協變度量張量 $g_{{ij}}$:\n{g_ij_sym}")
print(f"度量行列式 $\\det(g)$: {g_det}")
print("-" * 50)


# 4. 數值點與數值向量定義
# 選擇點 P: $r=2, \theta=\pi/4$
r_val, theta_val = 2.0, pi / 4
P_subs = {r: r_val, theta: theta_val}

# 提取數值度量張量
g_ij_num = np.array(g_ij_sym.subs(P_subs)).astype(float)

# 定義兩個逆變向量 (Contravariant Vectors) $\mathbf{v}$ 和 $\mathbf{w}$
# $\mathbf{v} = v^r \frac{\partial}{\partial r} + v^{\theta} \frac{\partial}{\partial \theta}$
v_upper = np.array([1.0, 0.5]) # $v^r=1, v^{\theta}=0.5$
w_upper = np.array([-0.5, 1.0]) # $w^r=-0.5, w^{\theta}=1.0$

print(f"數值點 $P$: $(r, \\theta) = ({r_val}, \\pi/4)$ 處")
print(f"向量 $\\mathbf{{v}}$ 逆變分量 $v^i$: {v_upper}")
print(f"向量 $\\mathbf{{w}}$ 逆變分量 $w^i$: {w_upper}")
print("-" * 50)


# =========================================================================
# I. 內積與長度 (Inner Product and Length)
# =========================================================================

# 5. 內積公式: $\mathbf{v} \cdot \mathbf{w} = g_{ij} v^i w^j$
# 使用 numpy.einsum 執行 $\sum_{i,j} g_{ij} v^i w^j$
inner_product = np.einsum('ij,i,j->', g_ij_num, v_upper, w_upper)

# 6. 向量長度 (範數) 公式: $\|\mathbf{v}\| = \sqrt{g_{ij} v^i v^j}$
v_norm_sq = np.einsum('ij,i,j->', g_ij_num, v_upper, v_upper)
v_norm = np.sqrt(v_norm_sq)

w_norm_sq = np.einsum('ij,i,j->', g_ij_num, w_upper, w_upper)
w_norm = np.sqrt(w_norm_sq)

print(f"I. 長度與內積計算:")
print(f"內積 $\\mathbf{{v}} \\cdot \\mathbf{{w}}$: {inner_product:.4f}")
print(f"向量 $\\mathbf{{v}}$ 的長度 $\\|\\mathbf{{v}}\\|$: {v_norm:.4f}")
print(f"向量 $\\mathbf{{w}}$ 的長度 $\\|\\mathbf{{w}}\\|$: {w_norm:.4f}")
print("-" * 50)


# =========================================================================
# II. 角度 (Angle)
# =========================================================================

# 7. 角度公式: $\cos(\\alpha) = \frac{\mathbf{v} \cdot \mathbf{w}}{\|\mathbf{v}\| \|\mathbf{w}\|}$
cos_alpha = inner_product / (v_norm * w_norm)
# 確保 cos_alpha 在 [-1, 1] 範圍內，以防浮點誤差
cos_alpha = np.clip(cos_alpha, -1.0, 1.0)
angle_radians = np.arccos(cos_alpha)
angle_degrees = np.degrees(angle_radians)

print(f"II. 角度計算:")
print(f"$\\cos(\\alpha)$: {cos_alpha:.4f}")
print(f"向量 $\\mathbf{{v}}$ 與 $\\mathbf{{w}}$ 之間的夾角 $\\alpha$: {angle_radians:.4f} 弧度 ({angle_degrees:.2f} 度)")
print("-" * 50)


# =========================================================================
# III. 體積元素 (Volume Element)
# =========================================================================

# 8. 體積元素公式: $d\\text{{Vol}} = \sqrt{{\det(g)}} \, dx^1 \wedge \dots \wedge dx^N$
# 對於極坐標 ($N=2$): $d\\text{{Area}} = \sqrt{r^2} \, dr \wedge d\\theta = r \, dr d\\theta$
volume_element_factor = sqrt(g_det)
volume_element_factor_val = float(volume_element_factor.subs(P_subs))

print(f"III. 體積元素計算:")
print(f"體積元素係數 $\\sqrt{{\\det(g)}}$: {volume_element_factor}")
print(f"在點 $P$ 處的數值 $\\sqrt{{\\det(g)}}|_{P}$: {volume_element_factor_val:.4f}")
print(f"面積元素 $d\\text{{Area}} = {volume_element_factor} \, dr d\\theta$")