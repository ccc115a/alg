import numpy as np
import matplotlib.pyplot as plt

# 定義複變函數 f(z) = z^2
def f(z):
    return z**2

# --- 定義 z 平面 (輸入/定義域) 的網格 ---
# 實部 x 的範圍和網格線
x_min, x_max = -2.0, 2.0
x_lines = np.linspace(x_min, x_max, 9)  # 9 條垂直線

# 虛部 y 的範圍和網格線
y_min, y_max = -2.0, 2.0
y_lines = np.linspace(y_min, y_max, 9)  # 9 條水平線

# 繪圖點的密度
num_points = 100

# --- 繪圖設定 ---
plt.figure(figsize=(12, 6))

# ----------------------------------------------------
# 1. 繪製 z 平面 (輸入/定義域)
# ----------------------------------------------------
plt.subplot(1, 2, 1) # 1 行 2 列的子圖中的第 1 個
ax1 = plt.gca()
ax1.set_title('$z$ Plane (Domain)')
ax1.set_xlabel('Re($z$) = $x$')
ax1.set_ylabel('Im($z$) = $y$')
ax1.set_xlim(x_min, x_max)
ax1.set_ylim(y_min, y_max)
ax1.axhline(0, color='gray', linestyle='--')
ax1.axvline(0, color='gray', linestyle='--')
ax1.set_aspect('equal', adjustable='box') # 確保 x, y 軸比例一致

# 繪製垂直網格線 (x = constant)
for x in x_lines:
    z = x + 1j * np.linspace(y_min, y_max, num_points)
    ax1.plot(z.real, z.imag, color='blue', alpha=0.7)

# 繪製水平網格線 (y = constant)
for y in y_lines:
    z = np.linspace(x_min, x_max, num_points) + 1j * y
    ax1.plot(z.real, z.imag, color='red', alpha=0.7)

# ----------------------------------------------------
# 2. 繪製 w 平面 (輸出/值域)
# ----------------------------------------------------
plt.subplot(1, 2, 2) # 1 行 2 列的子圖中的第 2 個
ax2 = plt.gca()
ax2.set_title('$w = f(z) = z^2$ Plane (Range)')
ax2.set_xlabel('Re($w$) = $u$')
ax2.set_ylabel('Im($w$) = $v$')
ax2.axhline(0, color='gray', linestyle='--')
ax2.axvline(0, color='gray', linestyle='--')
ax2.set_aspect('equal', adjustable='box') 
# 由於 w=z^2，輸出範圍會擴大，我們設定一個更大的範圍
w_max = max(x_max**2, y_max**2) * 2
ax2.set_xlim(-w_max, w_max)
ax2.set_ylim(-w_max, w_max)


# 將 z 平面上的網格點映射到 w 平面並繪製
# 繪製垂直線的映射 (w = f(x + iy))
for x in x_lines:
    z = x + 1j * np.linspace(y_min, y_max, num_points)
    w = f(z)
    ax2.plot(w.real, w.imag, color='blue', alpha=0.7)

# 繪製水平線的映射 (w = f(x + iy))
for y in y_lines:
    z = np.linspace(x_min, x_max, num_points) + 1j * y
    w = f(z)
    ax2.plot(w.real, w.imag, color='red', alpha=0.7)

# 顯示圖形
plt.tight_layout() # 自動調整子圖間距
plt.show()