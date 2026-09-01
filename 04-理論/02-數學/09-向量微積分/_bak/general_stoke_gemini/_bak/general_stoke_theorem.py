import numpy as np
from scipy.integrate import quad, dblquad

# --- 1. 定義向量場 F 的分量 P 和 Q ---
def P(x, y):
    """P(x, y) = -y^2"""
    return -y**2

def Q(x, y):
    """Q(x, y) = x^2"""
    return x**2

# --------------------------------------------------------------------
# A. 左邊 (LHS): 封閉路徑線積分 (Circulation)
# --------------------------------------------------------------------

# 路徑 C 由四個片段組成: C1, C2, C3, C4
# C1: (x, 0) from x=0 to x=1
# C2: (1, y) from y=0 to y=1
# C3: (x, 1) from x=1 to x=0 (注意方向)
# C4: (0, y) from y=1 to y=0 (注意方向)

line_integral_lhs = 0

# C1: y=0, dy=0. x goes from 0 to 1.
# P(x,0)dx + Q(x,0)dy = P(x,0)dx = 0
C1_integral = quad(lambda x: P(x, 0) * 1 + Q(x, 0) * 0, 0, 1)[0]
line_integral_lhs += C1_integral

# C2: x=1, dx=0. y goes from 0 to 1.
# P(1,y)dx + Q(1,y)dy = Q(1,y)dy = 1^2 dy
C2_integral = quad(lambda y: P(1, y) * 0 + Q(1, y) * 1, 0, 1)[0]
line_integral_lhs += C2_integral

# C3: y=1, dy=0. x goes from 1 to 0. (注意積分下限 > 上限，代表方向)
# P(x,1)dx + Q(x,1)dy = P(x,1)dx = -1^2 dx
C3_integral = quad(lambda x: P(x, 1) * 1 + Q(x, 1) * 0, 1, 0)[0]
line_integral_lhs += C3_integral

# C4: x=0, dx=0. y goes from 1 to 0.
# P(0,y)dx + Q(0,y)dy = Q(0,y)dy = 0^2 dy
C4_integral = quad(lambda y: P(0, y) * 0 + Q(0, y) * 1, 1, 0)[0]
line_integral_lhs += C4_integral

# --------------------------------------------------------------------
# B. 右邊 (RHS): 區域微分積分 (Curl)
# --------------------------------------------------------------------

# 計算被積函數 (旋度的 k 分量)
# Integrand = dQ/dx - dP/dy
# dQ/dx = d/dx (x^2) = 2x
# dP/dy = d/dy (-y^2) = -2y
# Integrand = 2x - (-2y) = 2x + 2y

def integrand_rhs(y, x):
    """Integrand for the double integral (dQ/dx - dP/dy)"""
    return 2 * x + 2 * y

# 計算雙重積分 over D: 0 <= x <= 1, 0 <= y <= 1
# dblquad(func, a, b, gfun, hfun) -> integral of func(y, x) from x=a to x=b, y=gfun(x) to y=hfun(x)
double_integral_rhs = dblquad(integrand_rhs, 0, 1, lambda x: 0, lambda x: 1)[0]


# --------------------------------------------------------------------
# C. 驗證結果
# --------------------------------------------------------------------

print(f"--- 廣義斯托克斯定理 (格林定理特例) 驗證 ---")
print(f"向量場 F = <-y^2, x^2> 於單位正方形上")
print("-" * 40)
print(f"左邊 (LHS) - 線積分結果 (Circulation): {line_integral_lhs:.10f}")
print(f"右邊 (RHS) - 雙重積分結果 (Curl Flux): {double_integral_rhs:.10f}")
print("-" * 40)

# 判斷是否相等 (考慮浮點數誤差)
if np.isclose(line_integral_lhs, double_integral_rhs):
    print(f"✅ 驗證成功：兩邊數值非常接近，廣義斯托克斯定理成立！")
else:
    print(f"❌ 驗證失敗：兩邊數值不匹配。")