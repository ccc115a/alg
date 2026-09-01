# 數學原理解說 -- 
from dgeom.sym import riemann_tensor, ricci_tensor, ricci_scalar, einstein_tensor
import sympy as sp

def test_schwarzschild_de_sitter():
    """
    測試案例 2: 史瓦西-德西特度規 (Schwarzschild-de Sitter)
    描述: 帶有宇宙常數 Lambda 的靜態黑洞
    目標: 驗證 G_mn + Lambda * g_mn = 0 (真空場方程式帶宇宙常數)
    """
    print("\n" + "="*60)
    print("GR 測試 2: Schwarzschild-de Sitter (帶宇宙常數 Lambda)")
    print("="*60)
    
    # 1. 定義符號
    t, r, theta, phi = sp.symbols('t r theta phi')
    coords = [t, r, theta, phi]
    
    # rs = 2GM, L = Lambda (宇宙常數)
    rs, L = sp.symbols('r_s Lambda')
    
    # 定義 Lapse Function f(r)
    # f(r) = 1 - rs/r - (Lambda * r^2) / 3
    f = 1 - rs/r - (L * r**2)/3
    
    # 2. 定義度規
    g_tt = -f
    g_rr = 1/f
    g_th = r**2
    g_ph = r**2 * sp.sin(theta)**2
    
    G_cov = sp.diag(g_tt, g_rr, g_th, g_ph)
    G_cont = sp.diag(1/g_tt, 1/g_rr, 1/g_th, 1/g_ph)
    
    print("1. 計算愛因斯坦張量 (需處理分式化簡)...")
    R_mn = ricci_tensor(G_cont, G_cov, coords)
    R_scalar = ricci_scalar(R_mn, G_cont)
    G_mn = einstein_tensor(R_mn, R_scalar, G_cov)
    
    # 3. 驗證場方程式: G_mn + Lambda * g_mn = 0
    # 這代表 G_mn = -Lambda * g_mn
    
    print("2. 驗證方程式 G_mn + Lambda * g_mn = 0 ...")
    
    # 計算左手邊 (Left Hand Side)
    LHS = G_mn + L * G_cov
    
    # 全面化簡
    LHS = LHS.applyfunc(sp.simplify)
    
    # 印出結果矩陣
    # sp.pprint(LHS)
    
    if LHS == sp.zeros(4, 4):
        print("   >> 驗證成功！此度規滿足帶宇宙常數的愛因斯坦場方程式。")
    else:
        print("   >> 驗證失敗，殘差矩陣如下:")
        sp.pprint(LHS)

if __name__ == "__main__":
    test_schwarzschild_de_sitter()
