from sympy import symbols, integrate, oo, pprint, simplify
from sympy.physics.hydrogen import R_nl, Psi_nlm

def hydrogen_wavefunction_example():
    # 1. 定義符號
    # r: 半徑, Z: 原子序 (氫 Z=1, 氦離子 Z=2...)
    r, Z = symbols('r Z', real=True, positive=True)
    # theta, phi 用於完整的波函數
    theta, phi = symbols('theta phi', real=True)

    print("--- 1. 徑向波函數 R_nl(r) ---")
    # 取得 n=1, l=0 (1s 軌域) 的徑向波函數
    # 函數簽名: R_nl(n, l, r, Z)
    psi_1s_radial = R_nl(1, 0, r, Z)
    
    print("1s 軌域 (n=1, l=0):")
    pprint(psi_1s_radial)
    # 結果應為: 2 * sqrt(Z**3) * exp(-Z*r)
    # 注意：SymPy 預設使用 atomic units (Bohr radius a0 = 1)

    print("\n2p 軌域 (n=2, l=1):")
    psi_2p_radial = R_nl(2, 1, r, Z)
    pprint(psi_2p_radial)


    print("\n--- 2. 驗證歸一化 (Normalization) ---")
    # 量子力學規定：全空間找到電子的機率為 1
    # 徑向積分公式: Integral |R(r)|^2 * r^2 dr = 1
    
    # 我們驗證 1s 軌域
    prob_density = psi_1s_radial**2 * r**2
    normalization = integrate(prob_density, (r, 0, oo)) # 從 0 積到無窮大 (oo)
    
    print(f"1s 軌域歸一化積分結果: {simplify(normalization)}")
    # 結果應該是 1


    print("\n--- 3. 計算期望值 <r> (平均半徑) ---")
    # 我們想知道在 1s 態時，電子平均離原子核多遠
    # 公式: <r> = Integral r * |R(r)|^2 * r^2 dr
    #           = Integral r^3 * |R(r)|^2 dr
    
    expectation_integrand = r * prob_density
    avg_radius = integrate(expectation_integrand, (r, 0, oo))
    
    print(f"1s 態的平均半徑 <r>: {simplify(avg_radius)}")
    # 對於氫原子 (Z=1)，結果應為 1.5 (即 1.5 倍波耳半徑 a0)
    # 公式解應為: 3 / (2*Z)


    print("\n--- 4. 完整的空間波函數 Psi_nlm ---")
    # 包含角度部分 (Spherical Harmonics)
    # 函數簽名: Psi_nlm(n, l, m, r, phi, theta, Z)
    # 讓我們看一個有角度變化的軌域，例如 2p (n=2, l=1, m=0)
    
    psi_2p_full = Psi_nlm(2, 1, 0, r, phi, theta, Z)
    print("2p (m=0) 完整波函數:")
    pprint(psi_2p_full)
    # 你會看到它包含了 cos(theta) 項，這反映了 p 軌域的方向性

if __name__ == "__main__":
    hydrogen_wavefunction_example()