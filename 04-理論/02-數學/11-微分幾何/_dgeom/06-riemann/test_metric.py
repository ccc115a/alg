from dgeom import metric_tensor
import sympy as sp
# --- 應用範例 ---

# 1. 定義符號變數
r, theta = sp.symbols('r theta')
phi = sp.symbols('phi')
a = sp.symbols('a', positive=True) # 假設 a 是正數，例如半徑

## 範例 A: 二維空間的極座標變換 (已在前面計算過)
print("## 範例 A: 極座標 (r, theta) 的度規張量 ##")
# 舊座標 (x, y) 的函數表示
polar_funcs = [r * sp.cos(theta), r * sp.sin(theta)]
# 新參數
polar_params = [r, theta]

G_polar = metric_tensor(polar_funcs, polar_params)
sp.pretty_print(G_polar)

print("\n" + "-"*50 + "\n")

## 範例 B: 嵌入在 R^3 中的球面 (半徑為 a)
print("## 範例 B: 球面 (theta, phi) 的度規張量 ##")
# 舊座標 (x, y, z) 關於新參數 (theta, phi) 的函數表示
# theta: 極角 (0 到 pi), phi: 方位角 (0 到 2pi)
sphere_funcs = [
    a * sp.sin(theta) * sp.cos(phi), # x
    a * sp.sin(theta) * sp.sin(phi), # y
    a * sp.cos(theta)                # z
]
# 新參數
sphere_params = [theta, phi]

G_sphere = metric_tensor(sphere_funcs, sphere_params)
sp.pretty_print(G_sphere)