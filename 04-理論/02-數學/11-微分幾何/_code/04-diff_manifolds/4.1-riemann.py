from sympy import symbols, Matrix, sin, simplify
import numpy as np

# 1. 定義符號變數
# 坐標變數 $x^i$: $\theta, \phi$ (球坐標系中的角度)
theta, phi = symbols('theta phi')
a = symbols('a', real=True, positive=True) # 半徑符號 (常數)
coordinates = [theta, phi]
N = 2

print(f"--- 黎曼流形 度量張量 $g_{{ij}}$ 與指標操作示範 (球坐標) ---")

# 2. 定義黎曼度量張量 $g_{ij}$ (協變)
# 2D 球面 (半徑為 $a$) 的度量張量:
# $g_{ij} = \begin{pmatrix} a^2 & 0 \\ 0 & a^2 \sin^2 \theta \end{pmatrix}$
g_ij_sym = Matrix([
    [a**2, 0],
    [0, a**2 * sin(theta)**2]
])

# 3. 計算逆度量張量 $g^{ij}$ (逆變)
# 用於提升指標
g_upper_sym = g_ij_sym.inv().applyfunc(simplify)

print(f"\n協變度量張量 $g_{{ij}}$:\n{g_ij_sym}")
print(f"\n逆變度量張量 $g^{{ij}}$:\n{g_upper_sym}")
print("-" * 50)

# 4. 數值計算：選擇一個點和一個數值向量
# 選擇點 P: $\theta = \pi/2$ (赤道), $\phi = 0$。假設半徑 $a=1$。
theta_val, phi_val, a_val = np.pi/2, 0.0, 1.0

# 數值度量張量
g_ij_num = np.array(g_ij_sym.subs({theta: theta_val, a: a_val})).astype(float)
g_upper_num = np.array(g_upper_sym.subs({theta: theta_val, a: a_val})).astype(float)

# 定義一個逆變向量 (Contravariant Vector) $v^i$ 的數值分量
# $v^{\theta}=2, v^{\phi}=3$
v_upper = np.array([2.0, 3.0])

print(f"數值點 $(\\theta, \\phi) = (\\pi/2, 0)$ 處的 $g_{{ij}}$:\n{g_ij_num.round(4)}")
print(f"數值逆變向量 $v^i$: {v_upper.round(4)}")
print("-" * 50)


# 5. 降低指標 (Lowering Index)
# 公式： $v_i = g_{ij} v^j$
# 使用 einsum 標記: 'ij,j->i' (縮並 $j$ 得到 $i$)
v_lower = np.einsum('ij,j->i', g_ij_num, v_upper)

print(f"降低指標後的協變向量 $v_i = g_{{ij}} v^j$: {v_lower.round(4)}")
# 驗證: $v_0 = g_{00} v^0 + g_{01} v^1 = 1 \cdot 2 + 0 \cdot 3 = 2$
#       $v_1 = g_{10} v^0 + g_{11} v^1 = 0 \cdot 2 + 1 \cdot 3 = 3$ (因為 $\sin(\pi/2)=1$)


# 6. 提升指標 (Raising Index)
# 公式： $\omega^i = g^{ij} \omega_j$
# 假設我們有一個協變向量 $\omega_j$
omega_lower = np.array([5.0, 10.0])

# 使用 einsum 標記: 'ij,j->i' (這裡 i, j 是上標)
omega_upper = np.einsum('ij,j->i', g_upper_num, omega_lower)

print(f"---")
print(f"數值協變向量 $\\omega_j$: {omega_lower.round(4)}")
print(f"提升指標後的逆變向量 $\\omega^i = g^{{ij}} \\omega_j$: {omega_upper.round(4)}")
# 驗證: $\omega^0 = g^{00} \omega_0 = (1/a^2) \cdot 5 = 5$
#       $\omega^1 = g^{11} \omega_1 = (1/(a^2 \sin^2 \theta)) \cdot 10 = 10$

# 7. 驗證內積 (Inner Product)
# 內積 $S = g_{ij} v^i w^j$
# 這裡我們用 $v^i$ 和 $\omega_j$ 來驗證 $v^i \omega_i$ 的結果與 $g_{ij} v^i \omega^j$ 相同
inner_product_contravariant_covariant = np.einsum('i,i->', v_upper, v_lower)
print(f"\n驗證內積 $v^i v_i$: {inner_product_contravariant_covariant.round(4)}")