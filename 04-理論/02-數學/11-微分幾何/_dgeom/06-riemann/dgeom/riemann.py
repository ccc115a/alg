import sympy as sp

def metric_tensor(old_coords_funcs, new_params):
    """
    計算由參數函數定義的流形在新參數座標系下的度規張量。

    參數:
    - old_coords_funcs (list of SymPy expressions): 
        一個列表，包含舊座標 (例如 x, y, z) 關於新參數的函數表示。
        例如：[r * sp.cos(theta), r * sp.sin(theta)]
    - new_params (list of SymPy symbols): 
        一個列表，包含新座標或參數 (例如 r, theta) 的 SymPy 符號。
        例如：[r, theta]

    回傳:
    - G_bar (SymPy Matrix): 
        新參數座標系下的度規張量矩陣 G_bar。
    """
    
    # 1. 將舊座標函數表示為 SymPy 矩陣形式 (代表嵌入函數 X)
    X_func_matrix = sp.Matrix(old_coords_funcs)
    
    # 2. 計算雅可比矩陣 J (即 Lambda_inv)
    # J 是 X 相對於新參數 (u) 的偏微分矩陣: J_ik = partial x^i / partial u^k
    # 這裡的 X_func_matrix.jacobian(new_params) 正好計算 J
    J_matrix = X_func_matrix.jacobian(new_params)
    
    # 3. 計算度規張量 G_bar
    # 公式: G_bar = J^T * G_old * J
    # 由於我們假設舊座標系是歐幾里得空間 (G_old = I, 單位矩陣)
    # 所以簡化為: G_bar = J^T * J
    
    J_transpose = J_matrix.transpose()
    G_bar = J_transpose * J_matrix
    
    # 4. 簡化結果
    G_bar_simplified = G_bar.applyfunc(sp.simplify)
    
    return G_bar_simplified

# --- 黎曼曲率張量計算函式 ---
def christoffel(mu, alpha, beta, G_cont, G_cov, coords):
    result = 0
    # **【修正點 1】**: 應使用實際的座標維度
    dim = len(coords)
    for gamma in range(dim): # 將 range(4) 替換為 range(dim)
        term1 = sp.diff(G_cov[gamma, alpha], coords[beta])
        term2 = sp.diff(G_cov[gamma, beta], coords[alpha])
        term3 = sp.diff(G_cov[alpha, beta], coords[gamma])
        # 由於 Christoffel 符號的計算中，上標 mu 決定了係數 g^mu_gamma 的維度
        # 此處的 mu 和 gamma 確實應該在流形維度內
        term = G_cont[mu, gamma] * sp.Rational(1, 2) * (term1 + term2 - term3) # 修正: 加上 sp.Rational(1, 2)
        result += term
    return sp.simplify(result)

# --- 黎曼曲率張量計算函式 ---
def riemann_tensor(rho, sigma, mu, nu, G_cont, G_cov, coords):
    """計算 R^rho_{sigma mu nu}"""
    
    # **【修正點 2】**: 應使用實際的座標維度
    dim = len(coords)

    # 計算第一、二項（導數項）
    Gamma_nu_sigma = christoffel(rho, nu, sigma, G_cont, G_cov, coords)
    term1 = sp.diff(Gamma_nu_sigma, coords[mu])
    
    Gamma_mu_sigma = christoffel(rho, mu, sigma, G_cont, G_cov, coords)
    term2 = sp.diff(Gamma_mu_sigma, coords[nu])
    
    # 計算第三、四項（二次項）
    term3_4 = 0
    # **【修正點 3】**: 執行愛因斯坦求和約定 (Summation over alpha)
    for alpha in range(dim): # 將 range(4) 替換為 range(dim)
        # Note: 這裡不需要再次呼叫 christoffel 函數，應該只呼叫一次並傳入 G_cov, G_cont
        # 但由於我沒有 dgeom 的完整實作，我只能假設您的 christoffel 運作正確。
        
        # 重新命名變數以符合迴圈的 alpha
        Gamma_alpha_mu_sigma = christoffel(alpha, mu, sigma, G_cont, G_cov, coords)
        Gamma_rho_nu_alpha = christoffel(rho, nu, alpha, G_cont, G_cov, coords)
        
        Gamma_alpha_nu_sigma = christoffel(alpha, nu, sigma, G_cont, G_cov, coords)
        Gamma_rho_mu_alpha = christoffel(rho, mu, alpha, G_cont, G_cov, coords)
        
        term3 = Gamma_alpha_mu_sigma * Gamma_rho_nu_alpha
        term4 = Gamma_alpha_nu_sigma * Gamma_rho_mu_alpha
        
        term3_4 += term3 - term4

    return sp.simplify(term1 - term2 + term3_4)