import sympy as sp
from dgeom.sym import metric_tensor, ricci_tensor, ricci_scalar, einstein_tensor, riemann_tensor

def test_reissner_nordstrom():
    """
    測試案例 1: Reissner-Nordström 黑洞 (帶電黑洞)
    物理意義: 驗證幾何與電磁場的耦合
    目標: 愛因斯坦張量 G_mn 不為 0，但應滿足特定的對稱性結構
    """
    print("\n" + "="*60)
    print("黑洞測試 1: Reissner-Nordström (帶電黑洞)")
    print("="*60)

    # 1. 定義符號
    t, r, theta, phi = sp.symbols('t r theta phi')
    coords = [t, r, theta, phi]
    M, Q = sp.symbols('M Q') # 質量與電荷

    # 2. 定義度規函數
    # f(r) = 1 - 2M/r + Q^2/r^2
    f = 1 - 2*M/r + Q**2/r**2

    # 度規張量 (對角)
    G_cov = sp.diag(-f, 1/f, r**2, r**2 * sp.sin(theta)**2)
    G_cont = sp.diag(1/(-f), f, 1/r**2, 1/(r**2 * sp.sin(theta)**2))

    print("1. 計算愛因斯坦張量 G_mn...")
    R_mn = ricci_tensor(G_cont, G_cov, coords)
    R_scalar = ricci_scalar(R_mn, G_cont)
    G_mn = einstein_tensor(R_mn, R_scalar, G_cov)
    
    # 3. 驗證結構
    # 對於帶電黑洞，G_mn = 8 * pi * T_mn (電磁張量)
    # 理論上 T_t^t = T_r^r = -T_theta^theta = -T_phi^phi (跡為0)
    # 所以混和張量 G^m_n 也應該滿足這個比例，或者我們直接檢查 G_mn 的特定分量
    
    # 理論值 (G_tt 與 G_rr 應該不為 0)
    # G_tt 應該包含 Q^2 的項，但不包含 M (M 只影響真空部分的曲率，被 Ricci 取消了? 不，是非線性疊加)
    # 實際上 G_tt = Q^2 / r^4 * f
    
    print("2. 檢查非零分量 (應包含電荷 Q)...")
    G_mn = G_mn.applyfunc(sp.simplify)
    
    # G_00 (t,t) 分量
    g00 = G_mn[0, 0]
    # G_11 (r,r) 分量
    g11 = G_mn[1, 1]
    
    print(f"   G_tt = {g00}")
    print(f"   G_rr = {g11}")

    # 驗證核心物理性質：
    # 若 Q=0，則應退化為史瓦西真空解 (G=0)
    if g00.subs(Q, 0) == 0 and g11.subs(Q, 0) == 0:
        print("   >> 驗證成功：當 Q=0 時退化為真空解。")
    
    # 驗證 G_tt 與 Q^2 成正比
    # 具體形式通常是: G_tt = - (Q^2 / r^4) * g_tt  (注意 g_tt 是負的)
    check_val = sp.simplify(g00 - (Q**2 / r**4) * f) 
    
    if check_val == 0:
        print("   >> 驗證成功：愛因斯坦張量正確反映了電磁場能量密度 (T ~ E^2 ~ Q^2/r^4)。")
    else:
        print("   >> 驗證細節有誤，請檢查公式。")


def test_kerr_metric():
    """
    測試案例 2: Kerr 黑洞 (旋轉黑洞)
    物理意義: 廣義相對論中最著名的真空解，描述真實宇宙中的黑洞
    挑戰: 非對角度規 (Frame Dragging)，計算極其繁重
    """
    print("\n" + "="*60)
    print("黑洞測試 2: Kerr Metric (旋轉黑洞 - 真空解)")
    print("警告: 此計算涉及大量代數化簡，可能需要 10-30 秒...")
    print("="*60)

    # 1. 定義符號 (Boyer-Lindquist 座標)
    t, r, theta, phi = sp.symbols('t r theta phi')
    coords = [t, r, theta, phi]
    M, a = sp.symbols('M a') # 質量 M, 角動量參數 a = J/M
    
    # 輔助函數
    Sigma = r**2 + a**2 * sp.cos(theta)**2
    Delta = r**2 - 2*M*r + a**2
    
    # 2. 定義度規張量 (注意非對角項 g_t_phi)
    # ds^2 = - (1 - 2Mr/Sigma) dt^2 
    #        - (4Mar sin^2(theta) / Sigma) dt dphi 
    #        + (Sigma / Delta) dr^2 
    #        + Sigma dtheta^2
    #        + ( (r^2 + a^2)^2 - Delta a^2 sin^2(theta) ) / Sigma * sin^2(theta) dphi^2
    
    g_tt = -(1 - 2*M*r/Sigma)
    g_tphi = - (2*M*a*r * sp.sin(theta)**2) / Sigma
    g_rr = Sigma / Delta
    g_thth = Sigma
    
    # g_phiphi 化簡後的形式
    # 這裡直接寫出標準形式
    g_phiphi = ( (r**2 + a**2)**2 - Delta * a**2 * sp.sin(theta)**2 ) / Sigma * sp.sin(theta)**2
    
    # 建立矩陣
    G_cov = sp.Matrix([
        [g_tt,   0,      0,      g_tphi],
        [0,      g_rr,   0,      0     ],
        [0,      0,      g_thth, 0     ],
        [g_tphi, 0,      0,      g_phiphi]
    ])
    
    # 計算逆矩陣 (SymPy 會自動處理，但這一步很花時間)
    print("1. 計算逆變度規 G_cont...")
    G_cont = G_cov.inv()
    G_cont = G_cont.applyfunc(sp.simplify) # 重要：先化簡，否則後面會算死
    
    print("2. 計算 Ricci 張量 (這是一場硬仗)...")
    R_mn = ricci_tensor(G_cont, G_cov, coords)
    
    print("3. 化簡 Ricci 張量...")
    R_mn = R_mn.applyfunc(sp.simplify)
    
    # 驗證真空解 R_mn = 0
    if R_mn == sp.zeros(4, 4):
        print("   >> 驗證成功：Kerr 黑洞是一個真空解 (R_mn = 0)。")
        print("   >> 這證明了您的函式庫能處理非對角項與參考系拖曳效應！")
    else:
        print("   >> 驗證失敗，發現非零項 (可能是化簡不完全):")
        sp.pprint(R_mn)

def test_kretschmann_scalar_schwarzschild():
    """
    額外測試: 計算史瓦西黑洞的 Kretschmann 純量 (曲率平方)
    物理意義: 雖然 Ricci 張量為 0，但時空是彎曲的。Kretschmann 純量可以探測奇異點。
    目標: K = R_abcd R^abcd = 48 M^2 / r^6
    """
    print("\n" + "="*60)
    print("黑洞測試 3: Kretschmann Scalar (史瓦西奇異點探測)")
    print("="*60)
    
    t, r, theta, phi = sp.symbols('t r theta phi')
    M = sp.symbols('M')
    coords = [t, r, theta, phi]
    
    # 史瓦西度規
    f = 1 - 2*M/r
    G_cov = sp.diag(-f, 1/f, r**2, r**2 * sp.sin(theta)**2)
    G_cont = sp.diag(-1/f, f, 1/r**2, 1/(r**2 * sp.sin(theta)**2)) # 手動寫逆矩陣比較快
    
    # 我們需要計算 R_rho_sigma_mu_nu (全協變) 和 R^rho_sigma_mu_nu (全逆變)
    # 但您的 riemann_tensor 回傳的是 R^rho_{sigma mu nu} (一上三下)
    # 我們需要手動縮約
    
    print("1. 計算 Kretschmann 純量 K = R_abcd R^abcd ...")
    
    K = 0
    # 4層迴圈... 4^4 = 256 次計算，對史瓦西來說還可以
    # 為了加速，我們只計算非零分量 (利用對稱性會更好，但這裡暴力算)
    
    # 預先計算所有非零的 R^rho_{sigma mu nu}
    # 這裡我們用一個簡單的策略：直接在迴圈裡算並縮約
    
    # K = R^rho_{sigma mu nu} * R_rho^{sigma mu nu}
    #   = R^rho_{sigma mu nu} * (g_{rho alpha} g^{sigma beta} g^{mu gamma} g^{nu delta} R^alpha_{beta gamma delta})
    # 這太慢了。
    
    # 較快的方法：
    # K = R^rho_{sigma mu nu} * R_{rho}^{sigma mu nu}
    # 我們已經有 riemann_tensor 算出 R^rho_{sigma mu nu} (記為 R_up_down3)
    
    # 我們先算出所有分量存起來 (Memoization)
    R_components = {}
    
    dim = 4
    for rho in range(dim):
        for sigma in range(dim):
            for mu in range(dim):
                for nu in range(dim):
                    # 只有當索引有特定配對時才不為0 (由於高度對稱性)
                    # 簡單過濾：對角度規下，指標通常成對出現
                    val = riemann_tensor(rho, sigma, mu, nu, G_cont, G_cov, coords)
                    if val != 0:
                        R_components[(rho, sigma, mu, nu)] = sp.simplify(val)

    print(f"   非零黎曼分量數量: {len(R_components)}")

    # 進行縮約 K = R^a_bcd R_a^bcd
    # R_a^bcd = g_ae g^bf g^cg g^dh R^e_fgh ... 太複雜
    # 換個方式：K = R^a_{bcd} * R^e_{fgh} * g_ae * g^bf * g^cg * g^dh
    
    # 但因為度規是對角的，g_ae 只有 a=e 時非零，g^bf 只有 b=f 時非零...
    # 所以 K = sum ( (R^a_{bcd})^2 * g_aa * g^bb * g^cc * g^dd ) (沒有愛因斯坦求和，單純累加)
    
    for (a, b, c, d), val in R_components.items():
        # 對角度規分量
        g_aa = G_cov[a, a]
        g_bb = G_cont[b, b]
        g_cc = G_cont[c, c]
        g_dd = G_cont[d, d]
        
        term = val * val * g_aa * g_bb * g_cc * g_dd
        K += term
        
    K = sp.simplify(K)
    print(f"   計算結果 K = {K}")
    
    expected_K = 48 * M**2 / r**6
    print(f"   理論預期 K = {expected_K}")
    
    if sp.simplify(K - expected_K) == 0:
        print("   >> 驗證成功：Kretschmann 純量正確發散於 r=0 (真實奇異點)。")
    else:
        print("   >> 驗證失敗。")

if __name__ == "__main__":
    test_reissner_nordstrom()
    test_kretschmann_scalar_schwarzschild()
    test_kerr_metric() # 把最慢的放最後