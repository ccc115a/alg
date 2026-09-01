from sympy import symbols, Matrix, sin, diff, simplify, pprint
import numpy as np
from math import pi

# 1. 定義符號變數和坐標
# 坐標變數 $x^i$: $x^0=\theta, x^1=\phi$ (球坐標系中的角度)
theta, phi = symbols('theta phi')
a = symbols('a', real=True, positive=True) # 半徑符號 (常數)
coordinates = [theta, phi]
N = 2

print(f"--- 協變導數與克里斯托費爾符號 $\\Gamma^i_{{jk}}$ 計算 (球坐標) ---")

# 2. 定義協變度量張量 $g_{ij}$ (來自 4.1 節)
# 2D 球面 (半徑為 $a$) 的度量張量:
g_ij_sym = Matrix([
    [a**2, 0],
    [0, a**2 * sin(theta)**2]
])

# 3. 計算逆變度量張量 $g^{ij}$ (用於提升指標)
g_upper_sym = g_ij_sym.inv().applyfunc(simplify)


# 4. 函數：計算克里斯托費爾符號 $\Gamma^i_{jk}$
def calculate_christoffel_symbols(g_ij, g_upper, coords, N):
    """計算黎曼流形的克里斯托費爾符號 (第二類) $\Gamma^i_{jk}$"""
    
    # 儲存結果：三維陣列 $\Gamma[i][j][k]$
    gamma = np.empty((N, N, N), dtype=object)

    for i in range(N):
        for j in range(N):
            for k in range(N):
                # 1. 計算括號內的三項偏導數 $\frac{\partial g_{mj}}{\partial x^k} + \frac{\partial g_{mk}}{\partial x^j} - \frac{\partial g_{jk}}{\partial x^m}$
                sum_term = 0
                for m in range(N):
                    # 這是克里斯托費爾符號的第一類 $\Gamma_{mjk}$ 的部分
                    # 簡化計算法: $\Gamma_{mjk} = \frac{1}{2} (\partial_k g_{mj} + \partial_j g_{mk} - \partial_m g_{jk})$
                    
                    # $\partial_k g_{mj}$
                    term1 = diff(g_ij[m, j], coords[k])
                    
                    # $\partial_j g_{mk}$
                    term2 = diff(g_ij[m, k], coords[j])
                    
                    # $\partial_m g_{jk}$
                    term3 = diff(g_ij[j, k], coords[m])
                    
                    # 2. 計算 $\Gamma^i_{jk} = g^{im} \Gamma_{mjk}$
                    # $\Gamma_{mjk}$
                    gamma_mjk = (term1 + term2 - term3) / 2
                    
                    # $g^{im} \Gamma_{mjk}$
                    sum_term += g_upper[i, m] * gamma_mjk
                
                gamma[i, j, k] = simplify(sum_term)

    return gamma

# 5. 執行計算並打印結果 (符號解)
Gamma_symbols = calculate_christoffel_symbols(g_ij_sym, g_upper_sym, coordinates, N)

print("\n--- 克里斯托費爾符號 $\\Gamma^i_{{jk}}$ 解析解 ---")
# 打印所有非零的分量
for i in range(N):
    for j in range(N):
        for k in range(N):
            if Gamma_symbols[i, j, k] != 0:
                print(f"\\Gamma^{i+1}_{{{j+1}{k+1}}} = ", end="")
                pprint(Gamma_symbols[i, j, k])
                
print("\n" + "="*70)

# 6. 數值計算協變導數 (在特定點)
# 選擇點 P: $\theta = \pi/2$ (赤道), $\phi = 0$。假設半徑 $a=1$。
theta_val, phi_val, a_val = pi/2, 0.0, 1.0

# 在該點計算 $\Gamma^i_{jk}$ 的數值
Gamma_num = np.zeros((N, N, N))
for i in range(N):
    for j in range(N):
        for k in range(N):
            Gamma_num[i, j, k] = float(Gamma_symbols[i, j, k].subs({theta: theta_val, a: a_val}))

# 定義一個逆變向量 $v^i$ 及其偏導數 $\partial_j v^i$ 的數值
# 假設 $v^i$ 是恆定的 $[2, 3]$ (但 $\partial_j v^i$ 必須為零)
v_upper = np.array([2.0, 3.0])
# 假設在該點的偏導數 $\frac{\partial v^i}{\partial x^j}$ 
# 假設 $v^{\theta} = \phi^2$ 和 $v^{\phi} = \theta$
# $\frac{\partial v^0}{\partial x^0} = 0, \frac{\partial v^0}{\partial x^1} = 2\phi \to 0$
# $\frac{\partial v^1}{\partial x^0} = 1, \frac{\partial v^1}{\partial x^1} = 0$
# 為了簡化，我們假設在該點的偏導數 $\partial_j v^i$ 如下:
partial_v = np.array([
    [0.0, 0.0], # $\partial_{\theta} v^{\theta}, \partial_{\phi} v^{\theta}$
    [1.0, 0.0]  # $\partial_{\theta} v^{\phi}, \partial_{\phi} v^{\phi}$
])


# 7. 計算協變導數 $\nabla_j v^i = \frac{\partial v^i}{\partial x^j} + \Gamma^i_{jk} v^k$
Covariant_Derivative = np.zeros((N, N)) # 結果 $\nabla_j v^i$

for i in range(N):
    for j in range(N):
        # 偏導數項
        term_partial = partial_v[i, j]
        
        # 克里斯托費爾項 (求和 $\sum_k \Gamma^i_{jk} v^k$)
        term_christoffel = np.einsum('k,k->', Gamma_num[i, j, :], v_upper)
        
        Covariant_Derivative[i, j] = term_partial + term_christoffel

print(f"\n--- 協變導數 $\\nabla_j v^i$ 數值計算 ($\theta=\\pi/2, a=1$) ---")
print(f"向量 $v^i$: {v_upper}")
print(f"偏導數 $\\partial_j v^i$:\n{partial_v}")
print(f"\n協變導數 $\\nabla_j v^i$ (數值結果):\n{Covariant_Derivative.round(4)}")