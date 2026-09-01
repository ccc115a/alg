from sympy import symbols, Matrix, diff, simplify, pprint
import numpy as np

# 1. 定義符號變數和坐標
# 坐標 $x^1=r, x^2=\theta$
r, theta = symbols('r theta', real=True, positive=True)
coords = [r, theta]
N = 2

print(f"--- 第 8 章：克里斯托費爾符號 $\\Gamma^k_{{ij}}$ 與協變微分計算 (極坐標) ---")

# 2. 定義黎曼度量張量 $g_{ij}$ (協變)
# 極坐標的度量張量: $g_{ij} = \begin{pmatrix} 1 & 0 \\ 0 & r^2 \end{pmatrix}$
g_ij_sym = Matrix([
    [1, 0],
    [0, r**2]
])

# 3. 計算逆變度量張量 $g^{ij}$ (用於提升指標)
g_upper_sym = g_ij_sym.inv().applyfunc(simplify)

print(f"\n協變度量張量 $g_{{ij}}$:\n{g_ij_sym}")
print(f"逆變度量張量 $g^{{ij}}$:\n{g_upper_sym}")
print("-" * 50)


# 4. 函數：計算克里斯托費爾符號 $\Gamma^k_{ij}$
def calculate_christoffel_symbols(g_ij, g_upper, coords, N):
    """計算黎曼流形的克里斯托費爾符號 (第二類) $\Gamma^k_{ij}$"""
    
    # 儲存結果：三維陣列 $\Gamma[k][i][j]$
    gamma = np.empty((N, N, N), dtype=object)

    for k in range(N):
        for i in range(N):
            for j in range(N):
                sum_term = 0
                for m in range(N):
                    # 1. 計算括號內的三項偏導數
                    # $\partial_i g_{mj}$
                    term1 = diff(g_ij[m, j], coords[i])
                    
                    # $\partial_j g_{mi}$
                    term2 = diff(g_ij[m, i], coords[j])
                    
                    # $-\partial_m g_{ij}$
                    term3 = diff(g_ij[i, j], coords[m])
                    
                    # 2. $\Gamma^k_{ij} = \frac{1}{2} g^{km} (\partial_i g_{mj} + \partial_j g_{mi} - \partial_m g_{ij})$
                    gamma_bracket = (term1 + term2 - term3) / 2
                    
                    # $g^{km} \times (\dots)$
                    sum_term += g_upper[k, m] * gamma_bracket
                
                gamma[k, i, j] = simplify(sum_term)

    return gamma

# 5. 執行計算並打印結果 (符號解)
Gamma_symbols = calculate_christoffel_symbols(g_ij_sym, g_upper_sym, coords, N)

print("\n--- 克里斯托費爾符號 $\\Gamma^k_{{ij}}$ 解析解 ---")
# 打印所有非零的分量
for k in range(N):
    for i in range(N):
        for j in range(N):
            if Gamma_symbols[k, i, j] != 0:
                print(f"\\Gamma^{k+1}_{{{i+1}{j+1}}} = ", end="")
                pprint(Gamma_symbols[k, i, j])
                
print("\n" + "="*70)

# =========================================================================
# II. 協變微分 (Covariant Derivative)
# =========================================================================

# 6. 數值點與數值向量定義
# 選擇點 P: $r=2, \theta=\pi/4$
r_val, theta_val = 2.0, np.pi / 4
P_subs = {r: r_val, theta: theta_val}

# A. 提取數值克里斯托費爾符號
Gamma_num = np.zeros((N, N, N))
for k in range(N):
    for i in range(N):
        for j in range(N):
            Gamma_num[k, i, j] = float(Gamma_symbols[k, i, j].subs(P_subs))

# B. 定義一個逆變向量場 $\mathbf{v}$ (Contravariant Vector Field)
# 假設 $v^r = r^2 + \theta$, $v^{\theta} = r \cos(\theta)$
v_r_sym = r**2 + theta
v_theta_sym = r * cos(theta)
v_sym = Matrix([v_r_sym, v_theta_sym])

# C. 計算向量場在點 $P$ 處的偏導數 $\frac{\partial v^i}{\partial x^j}$
partial_v_sym = v_sym.jacobian(coords)

# 提取數值
v_num = np.array(v_sym.subs(P_subs)).astype(float)
partial_v_num = np.array(partial_v_sym.subs(P_subs)).astype(float)


# 7. 計算協變微分 $\nabla_j v^i = \frac{\partial v^i}{\partial x^j} + \Gamma^i_{jk} v^k$
Covariant_Derivative = np.zeros((N, N)) # 結果 $\nabla_j v^i$

for i in range(N): # $i$ 是上標 (行)
    for j in range(N): # $j$ 是下標 (列)
        
        # 偏導數項 $\frac{\partial v^i}{\partial x^j}$
        term_partial = partial_v_num[i, j]
        
        # 克里斯托費爾項 (求和 $\sum_k \Gamma^i_{jk} v^k$)
        # 注意: $\Gamma^i_{jk}$ 中的 $i$ 是上標，對應 $\Gamma[i][j][k]$
        # $\Gamma^i_{jk} v^k$: einsum('k, k -> ', Gamma[i, j, :], v_num)
        term_christoffel = np.einsum('k,k->', Gamma_num[i, j, :], v_num)
        
        Covariant_Derivative[i, j] = term_partial + term_christoffel

print(f"--- 協變微分 $\\nabla_j v^i$ 數值計算 ($r=2, \\theta=\\pi/4$) ---")
print(f"向量場 $\\mathbf{{v}}$ 數值: {v_num.round(4)}")
print(f"偏導數 $\\frac{{\\partial v^i}}{{\partial x^j}}$:\n{partial_v_num.round(4)}")
print(f"\n協變微分 $\\nabla_j v^i$ (數值結果):\n{Covariant_Derivative.round(4)}")