from sympy import symbols, Matrix, diag, diff, simplify

# 定義座標符號 (t, r, theta, phi)
t, r, theta, phi = symbols('t r theta phi')
# 質量 M 和史瓦西半徑 rs
M = symbols('M') 
rs = 2 * M # 史瓦西半徑 rs = 2GM/c^2 (這裡我們假設 G=c=1)

# 將座標組合成列表
coords = [t, r, theta, phi]

# 定義史瓦西度量張量 g_{\mu\nu} (covariant metric)
# f(r) = 1 - rs/r
f = 1 - rs/r

g_tt = -f
g_rr = 1/f
g_theta_theta = r**2
g_phi_phi = r**2 * simplify(symbols('sin(theta)')**2) # 使用 simplify 來處理 sin(theta)

# 建立 4x4 的度量矩陣 G_cov
G_cov = Matrix([
    [g_tt, 0, 0, 0],
    [0, g_rr, 0, 0],
    [0, 0, g_theta_theta, 0],
    [0, 0, 0, g_phi_phi]
])

print("## 1. 協變度量張量 g_munu:")
print(G_cov)
print("-" * 30)

# 計算反變度量張量 g^{\mu\nu} (contravariant metric)
G_cont = G_cov.inv()

print("## 2. 反變度量張量 g^munu:")
print(G_cont)
print("-" * 30)

# 函式：計算克里斯托費爾符號
def christoffel(mu, alpha, beta, G_cont, G_cov, coords):
    """計算 Gamma^mu_{alpha beta}"""
    
    # 初始化總和為 0
    result = 0
    
    # 執行愛因斯坦求和約定 (Summation over gamma from 0 to 3)
    for gamma in range(4):
        
        # 計算三個偏導數項
        term1 = diff(G_cov[gamma, alpha], coords[beta])
        term2 = diff(G_cov[gamma, beta], coords[alpha])
        term3 = diff(G_cov[alpha, beta], coords[gamma])
        
        # 計算總項: g^{\mu\gamma} * 1/2 * (term1 + term2 - term3)
        term = G_cont[mu, gamma] * 0.5 * (term1 + term2 - term3)
        
        result += term
        
    return simplify(result)

# 計算並列印部分克里斯托費爾符號（由於總共有 4^3 = 64 個分量，只示範幾個）
print("## 3. 克里斯托費爾符號 Gamma^mu_{alpha beta} (部分):")

# 示範 1: Gamma^r_tt (mu=1, alpha=0, beta=0)
# 這是描述時間分量 (t) 變化對徑向加速度 (r) 的貢獻
Gamma_r_tt = christoffel(1, 0, 0, G_cont, G_cov, coords)
print(f"Gamma^r_tt = {Gamma_r_tt}")

# 示範 2: Gamma^t_tr (mu=0, alpha=0, beta=1)
# 這是描述徑向分量 (r) 變化對時間分量 (t) 變化的貢獻
Gamma_t_tr = christoffel(0, 0, 1, G_cont, G_cov, coords)
print(f"Gamma^t_tr = {Gamma_t_tr}")

# 示範 3: Gamma^r_rr (mu=1, alpha=1, beta=1)
Gamma_r_rr = christoffel(1, 1, 1, G_cont, G_cov, coords)
print(f"Gamma^r_rr = {Gamma_r_rr}")

# 示範 4: Gamma^theta_phi_phi (mu=2, alpha=3, beta=3)
# 這是描述角動量在 theta 軸上的幾何效應
Gamma_theta_phi_phi = christoffel(2, 3, 3, G_cont, G_cov, coords)
print(f"Gamma^theta_phi_phi = {Gamma_theta_phi_phi}")
print("-" * 30)

