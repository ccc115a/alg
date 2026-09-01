import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# --- 1. 定義輸入 z 的範圍 (x 和 y 座標) ---
# 為了避免 |z^3| 增長過快，我們將範圍稍微縮小
x = np.linspace(-1.5, 1.5, 50)
y = np.linspace(-1.5, 1.5, 50)

# 建立 z 平面的網格
X, Y = np.meshgrid(x, y)

# --- 2. 計算函數的模長 (高度 H) ---
# z = X + 1j * Y
# H = |f(z)| = |z^3|
H = (X**2 + Y**2)**(3/2) # 或者直接使用 np.abs((X + 1j*Y)**3)

# --- 3. 繪製 3D 圖形 ---
fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111, projection='3d')

# 繪製曲面
surf = ax.plot_surface(X, Y, H, 
                       cmap='inferno', # 換一個顏色地圖
                       edgecolor='none',
                       alpha=0.9)

# 設定軸標籤和標題
ax.set_xlabel('Real Axis (x)')
ax.set_ylabel('Imaginary Axis (y)')
ax.set_zlabel('Magnitude $|f(z)| = |z^3|$')
ax.set_title('3D Plot of Magnitude for $f(z) = z^3$')

# 加入顏色條
fig.colorbar(surf, shrink=0.5, aspect=5, label='$|z^3|$ value')

plt.show()