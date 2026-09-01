from sympy import symbols, Matrix

# 定義坐標變數 $r, \theta$
r, theta = symbols('r theta')

# 定義 2D 黎曼度量張量 $g_{ij}$
# 注意： SymPy 矩陣的索引從 (0, 0) 開始對應 $g_{rr}$
g_ij = Matrix([
    [1, 0],
    [0, r**2]
])

# 計算逆度量張量 $g^{ij}$
# 在提升或降低指標時會用到
g_upper = g_ij.inv()

print(f"協變度量張量 $g_{{ij}}$:\n{g_ij}")
print(f"\n逆變度量張量 $g^{{ij}}$:\n{g_upper}")