import sympy as sp
import numpy as np
from scipy.integrate import quad, dblquad

# --- 1. 符號定義 (SymPy) ---

# 座標變量 (假設在 R^3 空間中)
x, y, z = sp.symbols('x y z')
t = sp.Symbol('t') # 曲線參數

# 向量場 F = (P, Q, R)
# 這裡 F(x, y, z) = (-y, x, 0)
P = -y
Q = x
R = 0

# 微分 1-形式: omega = P dx + Q dy + R dz
# omega_expr: 符號表示的 1-形式
omega_expr = P * sp.diff(x, x) + Q * sp.diff(y, y) + R * sp.diff(z, z)
# 註: SymPy 難以直接處理外微分，所以我們通常需要手動或用專門的庫進行計算。

# --- 2. 幾何定義：流形 M^k 和邊界 \partial M^k ---

# 假設流形 S (M^2) 是一個半徑為 r 的圓盤，位於 z=0 平面上。
r_val = 1.0

# 邊界 \partial S (M^1) 是一個圓 (單位圓)
# r(t) = (x(t), y(t), z(t))
def curve_param(t_val):
    """邊界曲線參數化: (cos(t), sin(t), 0), t in [0, 2*pi]"""
    return np.array([r_val * np.cos(t_val), r_val * np.sin(t_val), 0.0])

# --- 3. 數值積分：計算邊界積分 \int_{\partial M} \omega ---

def integrand_omega_boundary(t_val):
    """
    計算線積分 \oint_{\partial S} \mathbf{F} \cdot d\mathbf{r} 的被積函數 F(r(t)) * r'(t)

    F = (-y, x, 0)
    r(t) = (cos(t), sin(t), 0)
    r'(t) = (-sin(t), cos(t), 0)
    F(r(t)) = (-sin(t), cos(t), 0)

    F(r(t)) * r'(t) = (-sin(t))(-sin(t)) + (cos(t))(cos(t)) + (0)(0)
                     = sin^2(t) + cos^2(t) = 1
    """
    # 數值計算：
    r_t = curve_param(t_val)
    dr_dt = np.array([-r_val * np.sin(t_val), r_val * np.cos(t_val), 0.0])
    
    # 向量場 F 在 r(t) 上的值 (使用 r_t[0]=x, r_t[1]=y, r_t[2]=z)
    F_val = np.array([-r_t[1], r_t[0], 0.0])
    
    # 點積 F * r'
    dot_product = np.dot(F_val, dr_dt)
    return dot_product

# 使用 SciPy 的 quad 進行單變量數值積分
# 積分區間 t 從 0 到 2*pi
integral_value_boundary, error_boundary = quad(integrand_omega_boundary, 0, 2 * np.pi)

# --- 4. 輸出結果 (根據斯托克斯定理，這就是 \int_S d\omega 的值) ---

print(f"--- 廣義斯托克斯定理 (k=2) 數值計算 ---")
print(f"向量場 F = (-y, x, 0)")
print(f"邊界 \partial S (圓) 上的線積分 \oint_{{\partial S}} \omega (F \cdot dr):")
print(f"  數值結果: {integral_value_boundary:.6f}")
print(f"  預期值 (2\pi r^2/r * r = 2\pi): {2 * np.pi:.6f}")
print(" ")
print(f"根據廣義斯托克斯定理:")
print(f"\iint_{{S}} d\omega = \oint_{{\partial S}} \omega")
print(f"\iint_{{S}} (\\nabla \\times F) \\cdot dS \\approx {integral_value_boundary:.6f}")