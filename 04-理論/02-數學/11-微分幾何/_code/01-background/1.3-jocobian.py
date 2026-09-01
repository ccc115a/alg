from sympy import symbols, Matrix, sin, cos, diff

# 1. 定義坐標變數
# 舊坐標系 (笛卡爾坐標)： $x^1=x, x^2=y$
x, y = symbols('x y')
old_coords = [x, y]

# 新坐標系 (極坐標)： $u^1=r, u^2=\theta$
r, theta = symbols('r theta')
new_coords = [r, theta]

print("--- 坐標變換：笛卡爾 $(x, y)$ 到 極坐標 $(r, \\theta)$ ---")

# 2. 定義坐標變換公式 $x = x(r, \theta), y = y(r, \theta)$
# 這是從新坐標到舊坐標的映射 $\Phi: \mathbb{R}^n \to \mathbb{R}^n$
x_new = r * cos(theta)
y_new = r * sin(theta)

mapping = Matrix([x_new, y_new])

print(f"變換公式 $x(r, \\theta)$: {x_new}")
print(f"變換公式 $y(r, \\theta)$: {y_new}")
print("\n" + "="*40 + "\n")

# 3. 計算雅可比矩陣 (Jacobian Matrix)
# 雅可比矩陣 $J^i_j = \frac{\partial x^i}{\partial u^j}$ (新坐標到舊坐標的偏導數矩陣)
# $J = \begin{pmatrix} \frac{\partial x}{\partial r} & \frac{\partial x}{\partial \theta} \\ \frac{\partial y}{\partial r} & \frac{\partial y}{\partial \theta} \end{pmatrix}$

# SymPy 的 Jacobian 函數：Jacobian(函數矩陣, 變數列表)
J = mapping.jacobian(new_coords)

print("1. 雅可比矩陣 $J$ (新坐標到舊坐標的導數):\n")
print(J)

# 4. 計算逆雅可比矩陣 (Inverse Jacobian Matrix)
# 逆雅可比矩陣 $J^{-1} = \frac{\partial u^j}{\partial x^i}$
# 這用於將向量分量從舊坐標系變換到新坐標系。

J_inv = J.inv().simplify()

print("\n" + "="*40 + "\n")
print("2. 逆雅可比矩陣 $J^{-1}$ (舊坐標到新坐標的導數):\n")
print(J_inv)

# 5. 雅可比行列式 (Jacobian Determinant)
# 行列式 $|\det(J)|$ 描述了體積元或面積元的伸縮比
det_J = J.det().simplify()

print("\n" + "="*40 + "\n")
print(f"3. 雅可比行列式 $\\det(J)$: {det_J}")