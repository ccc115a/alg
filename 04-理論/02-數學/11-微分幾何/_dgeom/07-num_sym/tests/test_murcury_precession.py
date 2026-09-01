import sympy as sp
# 我們只需要 metric_tensor 來驗證度規結構，實際推導使用守恆律
from dgeom.sym import metric_tensor

def test_mercury_precession():
    print("\n" + "="*60)
    print("廣義相對論測試: 水星近日點進動 (Effective Potential Method)")
    print("目標: 從有效位能推導出 GR 的力修正項 (-3ML^2/r^4)")
    print("="*60)

    # 1. 定義符號
    # t, r, phi (赤道面 theta=pi/2)
    t, r, phi = sp.symbols('t r phi')
    # M: 質量, E: 能量, L: 角動量
    M, E, L = sp.symbols('M E L')
    
    # 2. 定義史瓦西度規分量
    # ds^2 = g_tt dt^2 + g_rr dr^2 + g_pp dphi^2 = -1 (對於有質量粒子)
    f = 1 - 2*M/r
    g_tt = -f
    g_rr = 1/f
    g_pp = r**2  # 在赤道面 sin(theta)=1
    
    # 3. 引入守恆量與四維速度條件
    # u^t = dt/dtau, u^r = dr/dtau, u^phi = dphi/dtau
    # 能量守恆: u_t = g_tt * u^t = -E  =>  u^t = -E / g_tt = E/f
    # 角動量守恆: u_phi = g_pp * u^phi = L  =>  u^phi = L / g_pp = L/r^2
    
    u_t_upper = E / f
    u_phi_upper = L / r**2
    
    # 4. 利用歸一化條件推導徑向方程式
    # g_mn u^m u^n = -1
    # g_tt(u^t)^2 + g_rr(u^r)^2 + g_pp(u^phi)^2 = -1
    
    # 代入分量:
    # -(1-2M/r)(E/f)^2 + (1-2M/r)^(-1)(dr/dtau)^2 + r^2(L/r^2)^2 = -1
    # -E^2/f + (1/f)(dr/dtau)^2 + L^2/r^2 = -1
    
    # 同乘 f = (1-2M/r):
    # -E^2 + (dr/dtau)^2 + (L^2/r^2)(1-2M/r) = -(1-2M/r)
    # (dr/dtau)^2 = E^2 - (1 - 2M/r)(1 + L^2/r^2)
    
    # 5. 定義有效位能 V_eff
    # 動能項 (1/2)(dr/dtau)^2 + V_eff = 常數
    # 上式除以 2: (1/2)(dr/dtau)^2 + (1/2)(1 - 2M/r)(1 + L^2/r^2) = E^2/2
    
    V_eff = sp.Rational(1, 2) * (1 - 2*M/r) * (1 + L**2/r**2)
    
    print(f"1. 有效位能 V_eff = {V_eff}")
    
    # 6. 計算徑向力 F_r
    # 力 F = - d(V_eff) / dr
    F_r = -sp.diff(V_eff, r)
    F_r = sp.simplify(F_r)
    
    print(f"2. 徑向力 F_r (精確值) = {F_r}")
    
    # 7. 展開與係數提取
    print("3. 分析修正項 (使用級數展開)...")
    
    # 使用 sp.series 在 r -> infinity 處展開，取到 r^-4 項
    F_series = sp.series(F_r, r, sp.oo, n=5)
    print(f"   級數展開結果 = {F_series}")
    
    # 提取係數 (使用 removeO 去除高階小量)
    F_poly = F_series.removeO()
    
    coeff_grav = F_poly.coeff(1/r**2)
    coeff_centrifugal = F_poly.coeff(1/r**3)
    coeff_correction = F_poly.coeff(1/r**4)
    
    print(f"   [r^-2] 牛頓重力項係數: {coeff_grav} (應為 -M)")
    print(f"   [r^-3] 離心力項係數:   {coeff_centrifugal} (應為 L^2)")
    print(f"   [r^-4] GR修正項係數:   {coeff_correction} (應為 -3*M*L^2)")
    
    # 8. 驗證
    # 注意: coeff 有時會回傳包含 1.0 的浮點數，使用 simplify 比較最安全
    assert sp.simplify(coeff_grav - (-M)) == 0
    assert sp.simplify(coeff_centrifugal - L**2) == 0
    assert sp.simplify(coeff_correction - (-3*M*L**2)) == 0
    
    print("\n>> 驗證成功！")
    print("   成功從史瓦西度規推導出有效位能修正項。")
    print("   正是這個 -3ML^2/r^4 的力導致了水星軌道的近日點進動。")

if __name__ == "__main__":
    test_mercury_precession()