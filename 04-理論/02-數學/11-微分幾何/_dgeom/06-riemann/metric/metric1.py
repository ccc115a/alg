import sympy as sp
import numpy as np

# 1. 定義符號變數
r, theta = sp.symbols('r theta')
x_sym, y_sym = sp.symbols('x y')

# 2. 定義笛卡爾座標 (舊座標 x^k) 與極座標 (新座標 bar_x^i) 的關係
# 舊座標 (x1, x2) = (x, y)
# 新座標 (bar_x1, bar_x2) = (r, theta)
# x = x(r, theta), y = y(r, theta)
x_func = r * sp.cos(theta)
y_func = r * sp.sin(theta)

# 3. 定義舊座標下的度規張量 G (歐幾里得空間, 單位矩陣)
G_matrix = sp.Matrix([[1, 0], [0, 1]])

# 4. 計算逆雅可比矩陣 (J_inv)
# J_inv = 變換矩陣 Lambda_inv (從新座標到舊座標的分量)
# J_inv 分量: J_inv[i, k] = partial x_k / partial bar_x_i
# (i 是新座標 (r, theta), k 是舊座標 (x, y))

# 雅可比矩陣 J 是 (partial bar_x_i / partial x_k)
# 但我們需要 (partial x_k / partial bar_x_i)，這裡我們直接計算它
# SymPy 的 Jacobian 函式可以幫我們計算
# 這裡我們計算 (x, y) 相對於 (r, theta) 的偏微分矩陣，這正是我們需要的 Lambda_inv
Lambda_inv = sp.Matrix([x_func, y_func]).jacobian([r, theta])

print("### 逆雅可比矩陣 Lambda_inv (partial(x, y) / partial(r, theta)) ###")
sp.pretty_print(Lambda_inv)
print("------------------------------------------------------------------")

# 5. 計算新座標下的度規張量 G_bar
# G_bar = (Lambda_inv)^T * G * Lambda_inv
Lambda_inv_T = Lambda_inv.transpose()
G_bar = Lambda_inv_T * G_matrix * Lambda_inv

# 6. 簡化結果並輸出
G_bar_simplified = G_bar.applyfunc(sp.simplify)

print("### 極座標下的度規張量 G_bar ###")
sp.pretty_print(G_bar_simplified)