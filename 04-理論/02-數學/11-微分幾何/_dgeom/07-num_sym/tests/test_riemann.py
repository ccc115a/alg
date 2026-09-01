# 數學原理解說 -- 
import sympy as sp
from sympy import symbols, Matrix, simplify, cos, sin, eye

def test_minkowski_spacetime():
    """
    測試案例 A: 閔可夫斯基時空 (狹義相對論)
    驗證: 平坦時空的 Christoffel 符號與黎曼張量皆為 0
    """
    print("\n" + "="*60)
    print("測試案例: test_minkowski_spacetime (閔可夫斯基時空)")
    print("="*60)

    # 1. 定義符號與度規
    t, x, y, z = symbols('t x y z')
    coords = [t, x, y, z]
    
    # 閔可夫斯基協變度規 (-+++)
    G_cov = Matrix([
        [-1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])
    G_cont = G_cov.inv()

    print(f"G_cov (Minkowski) =\n{G_cov}")
    
    # 2. 驗證 Christoffel 符號 (預期為 0)
    # 計算 Gamma^t_xx (rho=0, mu=1, nu=1)
    Gamma_t_xx = christoffel(0, 1, 1, G_cont, G_cov, coords)
    print(f"Gamma^t_xx = {Gamma_t_xx}")
    assert Gamma_t_xx == 0, "Minkowski space should have zero Christoffel symbols"

    # 3. 驗證黎曼曲率張量 (預期為 0)
    # 計算 R^t_{x t x}
    R_t_xtx = riemann_tensor(0, 1, 0, 1, G_cont, G_cov, coords)
    print(f"R^t_{{x t x}} = {R_t_xtx}")
    assert R_t_xtx == 0, "Riemann tensor component should be 0"

    # 計算 R^x_{y t z}
    R_x_ytz = riemann_tensor(1, 2, 0, 3, G_cont, G_cov, coords)
    print(f"R^x_{{y t z}} = {R_x_ytz}")
    assert R_x_ytz == 0, "Riemann tensor component should be 0"
    
    print(">> 驗證成功：閔可夫斯基時空是平坦的。")

def test_polar_plane_geometry():
    """
    測試案例 B: 二維歐幾里得平面 (極座標表示)
    驗證: 
    1. 度規張量計算正確
    2. Christoffel 符號不為 0 (座標系彎曲)
    3. 黎曼張量為 0 (流形本身平坦)
    """
    print("\n" + "="*60)
    print("測試案例: test_polar_plane_geometry (極座標平面)")
    print("="*60)

    # 1. 定義符號與映射
    r, theta = symbols('r theta')
    coords = [r, theta]
    
    # 嵌入映射: (r, theta) -> (x, y)
    euclid_funcs = [r * cos(theta), r * sin(theta)]
    
    # 2. 計算度規
    G_cov = metric_tensor(euclid_funcs, coords)
    G_cont = G_cov.inv()
    
    print("G_cov (Polar) =")
    sp.pretty_print(G_cov)
    
    # 驗證度規是否為對角矩陣 diag(1, r^2)
    expected_g_22 = r**2
    assert simplify(G_cov[1, 1] - expected_g_22) == 0, "Metric component g_theta_theta incorrect"

    # 3. 計算 Christoffel 符號 (預期不為 0)
    # Gamma^r_theta_theta = -r
    Gamma_r_tt = simplify(christoffel(0, 1, 1, G_cont, G_cov, coords))
    print(f"Gamma^r_theta_theta = {Gamma_r_tt}")
    assert Gamma_r_tt != 0, "Polar coordinates should have non-zero Christoffel symbols"

    # Gamma^theta_r_theta = 1/r
    Gamma_t_rt = simplify(christoffel(1, 0, 1, G_cont, G_cov, coords))
    print(f"Gamma^theta_r_theta = {Gamma_t_rt}")

    # 4. 驗證黎曼曲率 (預期為 0)
    # R^r_{theta r theta}
    R_r_trt = simplify(riemann_tensor(0, 1, 0, 1, G_cont, G_cov, coords))
    print(f"R^r_{{theta r theta}} = {R_r_trt}")
    assert R_r_trt == 0, "Euclidean plane must have zero curvature"

    # R^theta_{r theta r}
    R_t_rtr = simplify(riemann_tensor(1, 0, 1, 0, G_cont, G_cov, coords))
    print(f"R^theta_{{r theta r}} = {R_t_rtr}")
    assert R_t_rtr == 0, "Euclidean plane must have zero curvature"

    print(">> 驗證成功：極座標系具有非零 Christoffel 符號，但零曲率。")

def test_sphere_metric():
    """
    測試案例 C: 三維空間中的球面
    驗證: 度規張量計算
    """
    print("\n" + "="*60)
    print("測試案例: test_sphere_metric (球面度規)")
    print("="*60)

    # 1. 定義符號
    theta, phi = symbols('theta phi')
    a = symbols('a', positive=True) # 球半徑
    coords = [theta, phi]

    # 2. 嵌入映射: (theta, phi) -> (x, y, z)
    sphere_funcs = [
        a * sin(theta) * cos(phi), # x
        a * sin(theta) * sin(phi), # y
        a * cos(theta)             # z
    ]

    # 3. 計算度規
    G_sphere = metric_tensor(sphere_funcs, coords)
    
    print("G_cov (Sphere) =")
    sp.pretty_print(G_sphere)
    
    # 4. 驗證標準結果: diag(a^2, a^2 sin^2(theta))
    expected_g_00 = a**2
    expected_g_11 = a**2 * sin(theta)**2
    
    assert simplify(G_sphere[0, 0] - expected_g_00) == 0
    assert simplify(G_sphere[1, 1] - expected_g_11) == 0
    assert simplify(G_sphere[0, 1]) == 0 # 交叉項為 0
    
    print(">> 驗證成功：球面度規符合預期。")

def test_sphere_curvature():
    """
    測試案例 D: 驗證球面的 Ricci 純量
    理論值: R = 2 / a^2
    """
    print("\n" + "="*60)
    print("測試案例: test_sphere_curvature (球面曲率驗證)")
    print("="*60)

    # 1. 定義符號
    theta, phi = sp.symbols('theta phi')
    a = sp.symbols('a', positive=True) # 假設半徑為正
    coords = [theta, phi]

    # 2. 定義球面的度規 (可以直接寫結果，或重新算一次)
    # G_cov = diag(a^2, a^2 sin^2(theta))
    G_cov = sp.Matrix([
        [a**2, 0],
        [0, a**2 * sp.sin(theta)**2]
    ])
    G_cont = G_cov.inv()
    
    print("正在計算 Ricci 張量...")
    # 假設您已經在 riemann.py 加入了 ricci_tensor
    R_mn = ricci_tensor(G_cont, G_cov, coords) 
    # print(f"Ricci Tensor:\n{R_mn}")

    print("正在計算 Ricci 純量...")
    # 假設您已經在 riemann.py 加入了 ricci_scalar
    R_scalar = ricci_scalar(R_mn, G_cont)
    
    print(f"計算結果 R = {R_scalar}")
    
    # 3. 斷言驗證
    expected_R = 2 / a**2
    
    # 使用 simplify 確保代數結構被化簡
    diff = sp.simplify(R_scalar - expected_R)
    
    if diff == 0:
        print(f">> 驗證成功：球面的曲率為 {expected_R}，符合 R = 2K = 2/a^2")
    else:
        print(f">> 驗證失敗：預期 {expected_R}，但得到 {R_scalar}")
    
    assert diff == 0, f"Sphere Ricci scalar should be 2/a^2, got {R_scalar}"

if __name__ == "__main__":
    # 執行所有測試
    test_minkowski_spacetime()
    test_polar_plane_geometry()
    test_sphere_metric()
    test_sphere_curvature()