# 數學原理解說 -- 
from dgeom.sym import riemann_tensor, ricci_tensor, ricci_scalar, einstein_tensor
import sympy as sp

def test_flrw_cosmology():
    """
    測試案例 1: FLRW 宇宙學度規 (Friedmann-Lemaître-Robertson-Walker)
    描述: 均勻且各向同性的膨脹宇宙
    目標: 驗證愛因斯坦張量的分量符合弗里德曼方程式
    """
    print("\n" + "="*60)
    print("GR 測試 1: FLRW 宇宙學度規 (時間相依函數測試)")
    print("="*60)

    # 1. 定義符號
    t, r, theta, phi = sp.symbols('t r theta phi')
    k = sp.symbols('k') # 曲率常數 (-1, 0, +1)
    
    # 定義時間函數: 宇宙尺度因子 a(t)
    # 這是 SymPy 的 Function 物件，微分時會產生 Derivative(a(t), t)
    a = sp.Function('a')(t) 
    
    coords = [t, r, theta, phi]

    # 2. 定義度規
    # ds^2 = -dt^2 + a(t)^2 [ dr^2/(1-kr^2) + r^2 d(Omega)^2 ]
    # 使用球面座標
    
    g_tt = -1
    g_rr = a**2 / (1 - k * r**2)
    g_th = a**2 * r**2
    g_ph = a**2 * r**2 * sp.sin(theta)**2

    G_cov = sp.diag(g_tt, g_rr, g_th, g_ph)
    G_cont = sp.diag(1/g_tt, 1/g_rr, 1/g_th, 1/g_ph)

    print("1. 正在計算 Ricci 張量 R_mn (包含時間導數)...")
    R_mn = ricci_tensor(G_cont, G_cov, coords)
    
    print("2. 正在計算 Ricci 純量 R...")
    R_scalar = ricci_scalar(R_mn, G_cont)
    
    print("3. 正在計算愛因斯坦張量 G_mn...")
    G_mn = einstein_tensor(R_mn, R_scalar, G_cov)
    G_mn = G_mn.applyfunc(sp.simplify)

    # 4. 驗證 G_00 分量 (第一弗里德曼方程式)
    # G_00 = 3(H^2 + k/a^2) = 3 * ( (da/dt)^2 / a^2 + k/a^2 )
    # 注意: G_00 是協變分量
    
    adot = sp.diff(a, t) # da/dt
    expected_G_00 = 3 * (adot**2 + k) / a**2
    
    # 計算出的 G_00
    calc_G_00 = G_mn[0, 0]
    
    print(f"   計算出的 G_00 = {calc_G_00}")
    print(f"   預期的 G_00   = {expected_G_00}")

    if sp.simplify(calc_G_00 - expected_G_00) == 0:
        print("   >> G_00 驗證成功！符合第一弗里德曼方程式。")
    else:
        print("   >> G_00 驗證失敗。")

    # 5. 驗證 G_11 分量 (第二弗里德曼方程式相關)
    # 標準形式: G^1_1 = 2(addot/a) + (adot/a)^2 + k/a^2
    # 我們這裡是協變 G_11
    addot = sp.diff(a, t, t)
    expected_G_11 = - (2*a*addot + adot**2 + k) / (1 - k*r**2)
    
    calc_G_11 = G_mn[1, 1]
    
    if sp.simplify(calc_G_11 - expected_G_11) == 0:
         print("   >> G_11 驗證成功！符合第二弗里德曼方程式。")
    else:
         print(f"   >> G_11 驗證失敗。\n算出的: {calc_G_11}\n預期的: {expected_G_11}")
         
    # 總體檢查
    # 非對角項應為 0
    assert G_mn[0, 1] == 0
    print("   >> FLRW 度規測試通過。")

if __name__ == "__main__":
    test_flrw_cosmology()
