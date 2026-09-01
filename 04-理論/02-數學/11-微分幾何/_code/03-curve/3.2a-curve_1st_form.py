from sympy import symbols, Matrix, diff, cos, sin, simplify

# 1. 定義符號變數和曲面參數
u, v = symbols('u v') # 曲面參數
R, r_a = symbols('R r_a', real=True, positive=True) # R: 大半徑, r_a: 小半徑 (這裡用 r_a 避免與 u, v 混淆)

# 2. 定義圓環面 (Torus) 參數化曲面 $\mathbf{r}(u, v)$
# 0 <= u, v <= 2*pi
# $\mathbf{r}(u, v) = ( (R + r \cos v) \cos u, (R + r \cos v) \sin u, r \sin v )$
x = (R + r_a * cos(v)) * cos(u)
y = (R + r_a * cos(v)) * sin(u)
z = r_a * sin(v)

r = Matrix([x, y, z])

print(f"--- 圓環面 (Torus) 的第一基本形式計算 ---")
print(f"曲面 $\\mathbf{{r}}(u, v)$:\n{r.T}")

# 3. 計算曲面切向量 (偏導數)
# $\mathbf{r}_u = \frac{\partial \mathbf{r}}{\partial u}$
r_u = diff(r, u)

# $\mathbf{r}_v = \frac{\partial \mathbf{r}}{\partial v}$
r_v = diff(r, v)

print(f"\n切向量 $\\mathbf{{r}}_u$:\n{r_u.T}")
print(f"\n切向量 $\\mathbf{{r}}_v$:\n{r_v.T}")

# 4. 計算第一基本形式的係數 (度量張量 $g_{ij}$)
# E = g_{11}
E = r_u.dot(r_u)
E = simplify(E)

# F = g_{12} = g_{21}
F = r_u.dot(r_v)
F = simplify(F)

# G = g_{22}
G = r_v.dot(r_v)
G = simplify(G)

print("\n" + "="*50)
print("--- 第一基本形式係數 (度量張量) 解析解 ---")
print(f"E = $\\mathbf{{r}}_u \\cdot \\mathbf{{r}}_u$: {E}")
print(f"F = $\\mathbf{{r}}_u \\cdot \\mathbf{{r}}_v$: {F}")
print(f"G = $\\mathbf{{r}}_v \\cdot \\mathbf{{r}}_v$: {G}")
print("="*50)

# 5. 構建協變度量張量 $g_{ij}$
g_ij = Matrix([[E, F], [F, G]])

# 計算度量張量 $g_{ij}$ 的行列式 $g = \det(g_{ij})$
g_det = g_ij.det()
g_det_simplified = simplify(g_det)

print(f"\n協變度量張量 $g_{{ij}}$:\n{g_ij}")
print(f"\n行列式 $g = \det(g_{{ij}})$: {g_det_simplified}")

# 6. 應用：計算曲面面積元 $dA$
# 曲面面積元 $dA = \sqrt{E G - F^2} \,du\,dv = \sqrt{\det(g_{ij})} \,du\,dv$
dA_term = sqrt(g_det)
dA_simplified = simplify(dA_term)

print(f"\n曲面面積元 $\\sqrt{{\det(g_{{ij}})}}$: {dA_simplified}")