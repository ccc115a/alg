# 引入必要的 SymPy 函式
from sympy import symbols, Matrix, simplify, eye, Sum, N
from dgeom import riemann_tensor, christoffel

# --- 測試程式的開始 ---
# --- 重新定義符號和度量 (Minkowski Metric) ---
# 使用 (t, x, y, z) 笛卡爾座標
t, x, y, z = symbols('t x y z')
coords = [t, x, y, z]
dim = len(coords)

# 閔可夫斯基協變度規 G_cov (使用 -+++ 慣例, 假設 c=1)
G_cov = Matrix([
    [-1, 0, 0, 0],
    [0, 1, 0, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 1]
])

# 逆變度規 G_cont (G_cov 的逆矩陣，在此例中 G_cont = G_cov)
G_cont = G_cov.inv()

print("## 1. 閔可夫斯基時空 (狹義相對論) 的度規:")
print(f"G_cov =")
print(G_cov)
print("由於度規是常數矩陣，其所有偏導數為 0，這導致 Christoffel 符號恆為 0。")
print("-" * 50)


print("## 2. Christoffel 符號 (驗證 Christoffel 符號為 0):")
# 計算 Gamma^0_1_1 (t, x, x)
Gamma_t_xx = christoffel(0, 1, 1, G_cont, G_cov, coords)
print(f"Gamma^t_xx = {Gamma_t_xx}")
print("理論結果：所有 Christoffel 符號 Gamma^rho_munu = 0")
print("-" * 50)


print("## 3. 黎曼曲率張量 R^rho_{sigma mu nu} (示範):")
# 在平坦時空，所有黎曼張量分量應為 0。
# 計算 R^t_{x t x} (rho=0, sigma=1, mu=0, nu=1)
R_t_xtx = riemann_tensor(0, 1, 0, 1, G_cont, G_cov, coords)
print(f"R^t_{{x t x}} = {R_t_xtx}")

# 計算 R^x_{y t z} (rho=1, sigma=2, mu=0, nu=3)
R_x_ytz = riemann_tensor(1, 2, 0, 3, G_cont, G_cov, coords)
print(f"R^x_{{y t z}} = {R_x_ytz}")
print("理論結果：所有黎曼張量分量 R^rho_{sigma mu nu} = 0")
print("-" * 50)

