# 引入必要的 SymPy 函式
from sympy import symbols, Matrix, simplify, eye, cos, sin, Rational
# 假設 dgeom.py 中已包含 christoffel, riemann_tensor, metric_tensor
from dgeom import riemann_tensor, christoffel, metric_tensor

# --------------------------------------------------
#                區塊 A: 閔可夫斯基時空 (狹義相對論)
# --------------------------------------------------

# --- 重新定義符號和度量 (Minkowski Metric) ---
# 使用 (t, x, y, z) 笛卡爾座標
t, x, y, z = symbols('t x y z')
coords_mink = [t, x, y, z]
dim_mink = len(coords_mink)

# 閔可夫斯基協變度規 G_cov (使用 -+++ 慣例, 假設 c=1)
G_cov_mink = Matrix([
    [-1, 0, 0, 0],
    [0, 1, 0, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 1]
])

# 逆變度規 G_cont
G_cont_mink = G_cov_mink.inv()

print("## A. 閔可夫斯基時空 (狹義相對論) 測試 ##")
print(f"G_cov =")
print(G_cov_mink)
print("由於度規是常數矩陣，所有偏導數為 0。")
print("-" * 50)


print("## A.1. Christoffel 符號 (驗證 Christoffel 符號為 0):")
# 計算 Gamma^0_1_1 (t, x, x)
Gamma_t_xx = christoffel(0, 1, 1, G_cont_mink, G_cov_mink, coords_mink)
print(f"Gamma^t_xx = {Gamma_t_xx}")
print("結果：Christoffel 符號為 0，因為度規導數為 0。")
print("-" * 50)


print("## A.2. 黎曼曲率張量 R^rho_{sigma mu nu} (示範):")
# 計算 R^t_{x t x} (rho=0, sigma=1, mu=0, nu=1)
R_t_xtx = riemann_tensor(0, 1, 0, 1, G_cont_mink, G_cov_mink, coords_mink)
print(f"R^t_{{x t x}} = {R_t_xtx}")

# 計算 R^x_{y t z} (rho=1, sigma=2, mu=0, nu=3)
R_x_ytz = riemann_tensor(1, 2, 0, 3, G_cont_mink, G_cov_mink, coords_mink)
print(f"R^x_{{y t z}} = {R_x_ytz}")
print("結論：所有黎曼張量分量為 0，證實時空平坦。")
print("=" * 70)


# --------------------------------------------------
#               區塊 B: 二維歐幾里得平面 (極座標) 測試
# --------------------------------------------------

r, theta = symbols('r theta')
coords_polar = [r, theta] # 0=r, 1=theta
dim_polar = len(coords_polar)

# 舊座標 (x, y) 的函數表示
euclid_funcs = [r * cos(theta), r * sin(theta)]

# 計算協變度規 G_cov (極座標)
G_cov_polar = metric_tensor(euclid_funcs, coords_polar)
G_cont_polar = G_cov_polar.inv() # 逆變度規

print("## B. 二維歐幾里得平面 (極座標) 測試 ##")
print("嵌入座標: x = r cos(theta), y = r sin(theta)")
print(f"G_cov (極座標) =")
print(G_cov_polar) # 預期 [[1, 0], [0, r**2]]
print("-" * 50)


print("## B.1. Christoffel 符號 (驗證 Christoffel 符號不為 0):")
# 計算 Gamma^r_theta_theta (rho=0, mu=1, nu=1)
# 理論值: -r
Gamma_r_tt = christoffel(0, 1, 1, G_cont_polar, G_cov_polar, coords_polar)
print(f"Gamma^r_theta_theta = {simplify(Gamma_r_tt)}")

# 計算 Gamma^theta_r_theta (rho=1, mu=0, nu=1)
# 理論值: 1/r
Gamma_t_rt = christoffel(1, 0, 1, G_cont_polar, G_cov_polar, coords_polar)
print(f"Gamma^theta_r_theta = {simplify(Gamma_t_rt)}")
print("結果：Christoffel 符號不為 0，因為極座標系是彎曲的座標系。")
print("-" * 50)


print("## B.2. 黎曼曲率張量 R^rho_{sigma mu nu} (示範):")
# 坐標索引: r=0, theta=1
# 計算 R^r_{theta r theta} (rho=0, sigma=1, mu=0, nu=1)
# 理論值: 0 (必須為 0)
R_r_trt = riemann_tensor(0, 1, 0, 1, G_cont_polar, G_cov_polar, coords_polar)
print(f"R^r_{{theta r theta}} = {simplify(R_r_trt)}")

# 驗證另一個非對角分量 (應為 0)
# 計算 R^theta_{r theta r} (rho=1, sigma=0, mu=1, nu=0)
R_t_rtr = riemann_tensor(1, 0, 1, 0, G_cont_polar, G_cov_polar, coords_polar)
print(f"R^theta_{{r theta r}} = {simplify(R_t_rtr)}")

print("結論：儘管 Christoffel 符號不為 0，但黎曼曲率張量仍為 0，證實流形本身平坦 (內在曲率為零)。")