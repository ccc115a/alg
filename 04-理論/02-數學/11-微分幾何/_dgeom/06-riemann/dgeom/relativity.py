from .riemann import *
import sympy as sp

# --- 里奇張量計算函式 ---
def ricci_tensor(mu, nu, G_cont, G_cov, coords):
    """計算 R_{mu nu}"""
    
    result = 0
    # 執行愛因斯坦求和約定 (Summation over rho from 0 to 3)
    for rho in range(4):
        # 這裡需要計算 R^rho_{mu rho nu}
        R_rho_mu_rho_nu = riemann_tensor(rho, mu, rho, nu, G_cont, G_cov, coords)
        result += R_rho_mu_rho_nu
        
    return sp.simplify(result)


# --- 里奇純量計算函式 ---
def ricci_scalar(G_cont, G_cov, coords):
    """計算 R"""
    
    result = 0
    # 執行雙重愛因斯坦求和約定 (Summation over mu and nu from 0 to 3)
    for mu in range(4):
        for nu in range(4):
            # 只有對角線項 R_munu 可能是非零的
            if G_cov[mu, nu] != 0:
                R_mu_nu = ricci_tensor(mu, nu, G_cont, G_cov, coords)
                result += G_cont[mu, nu] * R_mu_nu
                
    return sp.simplify(result)

# --- 愛因斯坦張量計算函式 ---
def einstein_tensor(mu, nu, R_mu_nu, R_scalar, G_cov):
    """計算 G_{mu nu}"""
    
    # G_{mu nu} = R_{mu nu} - 1/2 * R * g_{mu nu}
    G_mu_nu = R_mu_nu - 0.5 * R_scalar * G_cov[mu, nu]
    
    return sp.simplify(G_mu_nu)