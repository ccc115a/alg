from sympy import symbols, Matrix, diff, simplify
import numpy as np

# 1. 定義符號變數和坐標
# 坐標 $x^0=x, x^1=y, x^2=z$
x, y, z = symbols('x y z')
coords = [x, y, z]
N = len(coords)

print(f"--- 第 5 章：外微分與外積 (R^{N}) ---")

# 2. 定義微分形式的係數 (以協變張量表示)

# A. 1 形式 $\omega = \omega_x dx + \omega_y dy + \omega_z dz$
# 選擇一個具體的向量場 (e.g., $\mathbf{F} = (yz, xz, xy)$)
omega_coeffs = Matrix([y * z, x * z, x * y]) 

# B. 另一個 1 形式 $\eta = \eta_x dx + \eta_y dy + \eta_z dz$
# 選擇另一個向量場 (e.g., $\mathbf{G} = (x^2, y^2, z^2)$)
eta_coeffs = Matrix([x**2, y**2, z**2])

print(f"\n1 形式 $\\omega$ 係數 ($\\omega_i$): {omega_coeffs.T}")
print(f"1 形式 $\\eta$ 係數 ($\\eta_j$): {eta_coeffs.T}")
print("-" * 50)


# =========================================================================
# I. 外積 (Wedge Product) $\omega \wedge \eta$
# 結果為 2 形式 $C = C_{ij} dx^i \wedge dx^j$
# $C_{ij} = \frac{1}{2} (\omega_i \eta_j - \omega_j \eta_i)$
# =========================================================================

C_coeffs = np.empty((N, N), dtype=object) # 2 形式係數 $C_{ij}$

print(f"\n--- I. 外積 $\\omega \\wedge \\eta$ (2 形式) ---")

for i in range(N):
    for j in range(N):
        if i < j:
            # 僅計算 $i < j$ 的獨立分量 (因為 $C_{ii}=0$ 且 $C_{ij} = -C_{ji}$)
            # $C_{ij} = (\omega_i \eta_j - \omega_j \eta_i)$ (不含 $1/2$ 因子，因為我們關注基底的係數)
            C_ij = simplify(omega_coeffs[i] * eta_coeffs[j] - omega_coeffs[j] * eta_coeffs[i])
            C_coeffs[i, j] = C_ij
            
            # 打印基底 $dx^i \wedge dx^j$ 的係數
            print(f"係數 $C_{{{i+1}{j+1}}}$ for $dx^{{{i+1}}} \\wedge dx^{{{j+1}}}$: {C_ij}")
        else:
            C_coeffs[i, j] = 0 # 填充對角線和下三角為 0 或反對稱項

# 驗證反對稱性: $C_{12} = -C_{21}$ (這裡 $C_{01}$ 是 $dx \wedge dy$ 的係數)
C_01 = C_coeffs[0, 1]
C_10 = -(omega_coeffs[1] * eta_coeffs[0] - omega_coeffs[0] * eta_coeffs[1])
C_10 = simplify(C_10)

# print(f"\n驗證: $C_{12}$ = {C_01}, $-C_{21}$ = {C_10} (應相等)")
print("-" * 50)


# =========================================================================
# II. 外微分 (Exterior Derivative) $d\omega$
# $d\omega$ 也是一個 2 形式 $D = D_{ij} dx^i \wedge dx^j$
# $D_{ij} = \frac{\partial \omega_j}{\partial x^i} - \frac{\partial \omega_i}{\partial x^j}$
# (這裡 $D_{ij}$ 是 $\mathbf{\nabla} \times \mathbf{F}$ 的係數, $\mathbf{F}$ 是 $\omega$ 對應的向量場)
# =========================================================================

D_coeffs = np.empty((N, N), dtype=object) # 2 形式係數 $D_{ij}$

print(f"\n--- II. 外微分 $d\\omega$ (2 形式) ---")

for i in range(N):
    for j in range(N):
        # 僅計算 $i < j$ 的獨立分量
        if i < j:
            # $\frac{\partial \omega_j}{\partial x^i}$
            term1 = diff(omega_coeffs[j], coords[i])
            
            # $\frac{\partial \omega_i}{\partial x^j}$
            term2 = diff(omega_coeffs[i], coords[j])
            
            # $D_{ij} = \partial_i \omega_j - \partial_j \omega_i$
            D_ij = simplify(term1 - term2)
            D_coeffs[i, j] = D_ij
            
            # 打印基底 $dx^i \wedge dx^j$ 的係數
            print(f"係數 $D_{{{i+1}{j+1}}}$ for $dx^{{{i+1}}} \\wedge dx^{{{j+1}}}$: {D_ij}")
        else:
            D_coeffs[i, j] = 0

# 範例的物理意義 (Curl $\mathbf{F}$):
# 1 形式 $\omega$: $(yz, xz, xy)$
# Curl $\mathbf{F} = (\partial_y F_z - \partial_z F_y, \partial_z F_x - \partial_x F_z, \partial_x F_y - \partial_y F_x)$
# $D_{12}$ (即 $D_{xy}$ 係數): $\partial_x \omega_y - \partial_y \omega_x = \partial_x(xz) - \partial_y(yz) = z - z = 0$
# $D_{01}$ (即 $D_{xy}$ 係數): $\partial_x \omega_y - \partial_y \omega_x$
# $D_{01} \to i=0 (x), j=1 (y)$: $\partial_x \omega_y - \partial_y \omega_x = \partial_x(xz) - \partial_y(yz) = z - z = 0$ (檢查索引定義)
# 修正 SymPy 輸出 (使用 $i=0, j=1$ 匹配 $dx \wedge dy$):
# $dx \wedge dy$ 係數 $D_{xy} = \partial_x \omega_y - \partial_y \omega_x = 0$
# $dx \wedge dz$ 係數 $D_{xz} = \partial_x \omega_z - \partial_z \omega_x = y - y = 0$
# $dy \wedge dz$ 係數 $D_{yz} = \partial_y \omega_z - \partial_z \omega_y = x - x = 0$
# 結果 $d\omega = 0$ (表示 $\omega$ 是**閉形式 (Closed Form)**)
print(f"\n結論: $d\\omega = 0$。因此 $\\omega$ 是一個**閉形式**。")
print("根據**龐加萊引理 (Poincaré Lemma)**，在 $\\mathbb{R}^3$ 中，閉形式是**恰當形式 (Exact Form)**。")
print(f"即 $\\omega$ 可以寫成某個 0 形式 $f$ 的外微分 $\\omega = df$。")
# 驗證 $\omega = df$: $f = xyz$
# $df = \partial_x f dx + \partial_y f dy + \partial_z f dz = yz dx + xz dy + xy dz$
# $df = \omega$. 驗證成功。