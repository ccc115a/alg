from sympy import symbols, Matrix, sin, diff, simplify, pprint
import numpy as np
from math import pi

# 1. 定義符號變數和坐標
# 坐標變數 $x^i$: $x^0=\theta, x^1=\phi$ (球坐標系中的角度)
theta, phi = symbols('theta phi')
a = symbols('a', real=True, positive=True) # 半徑符號 (常數)
coordinates = [theta, phi]
N = 2

print(f"--- 黎曼曲率張量 $R^i_{{jkl}}$ 計算 (球坐標) ---")

# 2. 定義協變度量張量 $g_{ij}$ (來自 4.1 節)
# 2D 球面 (半徑為 $a$) 的度量張量:
g_ij_sym = Matrix([
    [a**2, 0],
    [0, a**2 * sin(theta)**2]
])

# 3. 計算逆變度量張量 $g^{ij}$ (用於提升指標)
g_upper_sym = g_ij_sym.inv().applyfunc(simplify)


# 4. 函數：計算克里斯托費爾符號 $\Gamma^i_{jk}$ (第二類)
def calculate_christoffel_symbols(g_ij, g_upper, coords, N):
    """計算黎曼流形的克里斯托費爾符號 (第二類) $\Gamma^i_{jk}$"""
    
    # 儲存結果：三維陣列 $\Gamma[i][j][k]$
    gamma = np.empty((N, N, N), dtype=object)

    for i in range(N):
        for j in range(N):
            for k in range(N):
                sum_term = 0
                for m in range(N):
                    # $\Gamma_{mjk} = \frac{1}{2} (\partial_k g_{mj} + \partial_j g_{mk} - \partial_m g_{jk})$
                    term1 = diff(g_ij[m, j], coords[k]) # $\partial_k g_{mj}$
                    term2 = diff(g_ij[m, k], coords[j]) # $\partial_j g_{mk}$
                    term3 = diff(g_ij[j, k], coords[m]) # $\partial_m g_{jk}$
                    
                    gamma_mjk = (term1 + term2 - term3) / 2
                    
                    # $\Gamma^i_{jk} = g^{im} \Gamma_{mjk}$
                    sum_term += g_upper[i, m] * gamma_mjk
                
                gamma[i, j, k] = simplify(sum_term)

    return gamma


# 5. 函數：計算黎曼曲率張量 $R^i_{jkl}$
def calculate_riemann_tensor(Gamma, coords, N):
    """計算黎曼曲率張量 $R^i_{jkl}$"""
    
    # 儲存結果：四維陣列 $R[i][j][k][l]$
    R = np.empty((N, N, N, N), dtype=object)

    for i in range(N):
        for j in range(N):
            for k in range(N):
                for l in range(N):
                    # 四項公式: $R^i_{jkl} = \partial_k \Gamma^i_{lj} - \partial_l \Gamma^i_{kj} + \Gamma^m_{lj} \Gamma^i_{mk} - \Gamma^m_{kj} \Gamma^i_{ml}$
                    
                    # 1. 偏導數項 $\partial_k \Gamma^i_{lj} - \partial_l \Gamma^i_{kj}$
                    term_partial = diff(Gamma[i, l, j], coords[k]) - diff(Gamma[i, k, j], coords[l])
                    
                    # 2. 非線性項 (克里斯托費爾符號的乘積) $\Gamma^m_{lj} \Gamma^i_{mk} - \Gamma^m_{kj} \Gamma^i_{ml}$
                    term_nonlinear = 0
                    for m in range(N):
                        term_nonlinear += Gamma[m, l, j] * Gamma[i, m, k] - Gamma[m, k, j] * Gamma[i, m, l]
                        
                    R[i, j, k, l] = simplify(term_partial + term_nonlinear)
                    
    return R

# =========================================================================
# 6. 主程式執行
# =========================================================================

# A. 計算克里斯托費爾符號 (用於輸入曲率計算)
Gamma_symbols = calculate_christoffel_symbols(g_ij_sym, g_upper_sym, coordinates, N)

# B. 計算黎曼曲率張量
Riemann_symbols = calculate_riemann_tensor(Gamma_symbols, coordinates, N)

print("\n--- 黎曼曲率張量 $R^i_{{jkl}}$ 解析解 ---")
# 球面 $R^i_{jkl}$ 只有兩個獨立的非零分量 (例如 $R^{\phi}_{\theta \phi \theta}$)
# 打印所有非零的分量
nonzero_components_found = False
for i in range(N):
    for j in range(N):
        for k in range(N):
            for l in range(N):
                if Riemann_symbols[i, j, k, l] != 0:
                    print(f"R^{i+1}_{{{j+1}{k+1}{l+1}}} = ", end="")
                    pprint(Riemann_symbols[i, j, k, l])
                    nonzero_components_found = True

if not nonzero_components_found:
    print("所有分量均為零 (流形為平坦空間)。")


# C. 計算里奇張量 $R_{jl}$ 和 純量曲率 $R$

# 里奇張量 $R_{jl} = R^k_{jkl}$ (縮並指標 $i$ 和 $k$)
Ricci_symbols = np.empty((N, N), dtype=object)
for j in range(N):
    for l in range(N):
        sum_term = 0
        for k in range(N): # 縮並 $i=k$
             # 注意: $R^i_{jkl}$ 中的 $i$ 是第一個上標
             # $R_{jl} = R^k_{jkl}$ (上標 $i$ 與下標 $k$ 縮並)
            sum_term += Riemann_symbols[k, j, k, l] 
        Ricci_symbols[j, l] = simplify(sum_term)

print("\n--- 里奇張量 $R_{{jl}}$ 解析解 ---")
for j in range(N):
    for l in range(N):
        if Ricci_symbols[j, l] != 0:
            print(f"R_{{{j+1}{l+1}}} = ", end="")
            pprint(Ricci_symbols[j, l])


# 純量曲率 $R = g^{jl} R_{jl}$
Ricci_Scalar_symbol = 0
for j in range(N):
    for l in range(N):
        Ricci_Scalar_symbol += g_upper_sym[j, l] * Ricci_symbols[j, l]
Ricci_Scalar_symbol = simplify(Ricci_Scalar_symbol)

print("\n--- 純量曲率 $R$ 解析解 ---")
pprint(Ricci_Scalar_symbol)


# =========================================================================
# 7. 數值驗證 (在特定點)
# =========================================================================
# 選擇點 P: $\theta = \pi/2$ (赤道), $\phi = 0$。假設半徑 $a=1$。
theta_val, phi_val, a_val = pi/2, 0.0, 1.0

# 數值純量曲率
R_Scalar_num = Ricci_Scalar_symbol.subs({theta: theta_val, a: a_val})
R_Scalar_val = float(R_Scalar_num)

# 理論結果: 對於半徑為 $a$ 的球面，純量曲率 $R$ 應為 $2/a^2$
R_Scalar_theory = 2 / a_val**2

print(f"\n--- 數值驗證 ($\theta=\\pi/2, a=1$) ---")
print(f"數值純量曲率 $R$: {R_Scalar_val:.4f}")
print(f"理論純量曲率 $2/a^2$: {R_Scalar_theory:.4f}")

# 原始的協變導數計算 (保留用於完整性)
# 在該點計算 $\Gamma^i_{jk}$ 的數值
Gamma_num = np.zeros((N, N, N))
for i in range(N):
    for j in range(N):
        for k in range(N):
            Gamma_num[i, j, k] = float(Gamma_symbols[i, j, k].subs({theta: theta_val, a: a_val}))

# 定義一個逆變向量 $v^i$ 及其偏導數 $\partial_j v^i$ 的數值
v_upper = np.array([2.0, 3.0])
partial_v = np.array([
    [0.0, 0.0], # $\partial_{\theta} v^{\theta}, \partial_{\phi} v^{\theta}$
    [1.0, 0.0]  # $\partial_{\theta} v^{\phi}, \partial_{\phi} v^{\phi}$
])

# 協變導數 $\nabla_j v^i = \frac{\partial v^i}{\partial x^j} + \Gamma^i_{jk} v^k$
Covariant_Derivative = np.zeros((N, N)) 
for i in range(N):
    for j in range(N):
        term_partial = partial_v[i, j]
        term_christoffel = np.einsum('k,k->', Gamma_num[i, j, :], v_upper)
        Covariant_Derivative[i, j] = term_partial + term_christoffel

print(f"\n--- 協變導數 $\\nabla_j v^i$ 數值計算 ($\theta=\\pi/2, a=1$) ---")
print(f"向量 $v^i$: {v_upper}")
print(f"偏導數 $\\partial_j v^i$:\n{partial_v}")
print(f"\n協變導數 $\\nabla_j v^i$ (數值結果):\n{Covariant_Derivative.round(4)}")