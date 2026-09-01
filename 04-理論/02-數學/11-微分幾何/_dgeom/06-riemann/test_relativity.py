from dgeom import riemann_tensor, ricci_tensor, ricci_scalar, einstein_tensor
from sympy import symbols, Matrix, simplify

# --- 重新定義符號和度量 (Minkowski Metric) ---
# 使用 (t, x, y, z) 笛卡爾座標
t, x, y, z = symbols('t x y z')
coords = [t, x, y, z]

# 閔可夫斯基協變度規 G_cov (使用 -+++ 慣例, 假設 c=1)
G_cov = Matrix([
    [-1, 0, 0, 0],
    [0, 1, 0, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 1]
])

# 逆變度規 G_cont (G_cov 的逆矩陣，在此例中 G_cont = G_cov)
G_cont = G_cov.inv()
# 注意：這裡的度規是常數矩陣，所有偏微分項都為零，這就是平坦時空的特性。

print("## 1. 閔可夫斯基時空 (狹義相對論) 的度規:")
print(f"G_cov =")
print(G_cov)
print("-" * 50)


print("## 2. 黎曼曲率張量 R^rho_{sigma mu nu} (示範):")
# 在平坦時空，所有黎曼張量分量應為 0。
# 計算 R^t_{x t x} (rho=0, sigma=1, mu=0, nu=1)
R_t_xtx = riemann_tensor(0, 1, 0, 1, G_cont, G_cov, coords)
print(f"R^t_{{xtx}} = {R_t_xtx}")

# 計算 R^x_{y t z} (rho=1, sigma=2, mu=0, nu=3)
R_x_ytz = riemann_tensor(1, 2, 0, 3, G_cont, G_cov, coords)
print(f"R^x_{{ytz}} = {R_x_ytz}")
print("理論結果：所有黎曼張量分量 R^rho_{sigma mu nu} = 0")
print("-" * 50)


print("## 3. 里奇張量 R_munu (示範):")
# 里奇張量 R_munu 是黎曼張量的縮並，在平坦時空應為 0。
# 計算 R_tt (mu=0, nu=0)
R_tt = ricci_tensor(0, 0, G_cont, G_cov, coords)
print(f"R_tt = {R_tt}")

# 計算 R_xx (mu=1, nu=1)
R_xx = ricci_tensor(1, 1, G_cont, G_cov, coords)
print(f"R_xx = {R_xx}")
print("理論結果：所有里奇張量分量 R_munu = 0")
print("-" * 50)


print("## 4. 里奇純量 R:")
# 里奇純量 R 是里奇張量的縮並，在平坦時空應為 0。
R_scalar = ricci_scalar(G_cont, G_cov, coords)
print(f"R = {R_scalar}")
print("理論結果：里奇純量 R = 0")
print("-" * 50)


print("## 5. 愛因斯坦張量 G_munu (示範):")
# 愛因斯坦張量 G_munu = R_munu - (1/2) * R * g_munu
# 由於 R_munu = 0 且 R = 0，愛因斯坦張量 G_munu 應為 0。

# 計算 G_tt (mu=0, nu=0)
G_tt = einstein_tensor(0, 0, R_tt, R_scalar, G_cov)
print(f"G_tt = {G_tt}")

# 計算 G_xy (mu=1, nu=2)
# 需要先計算 R_xy，但由於 R_tt 和 R_xx 已經為 0，且時空是對稱的，我們預期 R_xy = 0。
R_xy = ricci_tensor(1, 2, G_cont, G_cov, coords)
G_xy = einstein_tensor(1, 2, R_xy, R_scalar, G_cov)
print(f"G_xy = {G_xy}")
print("理論結果：所有愛因斯坦張量分量 G_munu = 0")
print("-" * 50)

print("結論：由於所有曲率張量均為 0，此時空沒有彎曲，這證實了狹義相對論描述的是平坦時空。")