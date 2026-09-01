import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# --- 1. 定義輸入 z 的範圍 (x 和 y 座標) ---
# 建立 x 和 y 軸的等差數列
x = np.linspace(-2, 2, 50)
y = np.linspace(-2, 2, 50)

# 建立 z 平面的網格 (Grid)
X, Y = np.meshgrid(x, y)

# --- 2. 計算實數部分 (高度 Z) ---
# 複變函數 f(z) = z^3
# 實數部分 u(x, y) = Re(z^3) = x^3 - 3xy^2
Z = X**3 - 3 * X * Y**2

# --- 3. 繪製 3D 曲面圖形 ---
fig = plt.figure(figsize=(5, 5))
# 使用 add_subplot(projection='3d') 啟用 3D 繪圖
ax = fig.add_subplot(111, projection='3d')

# 繪製曲面
surf = ax.plot_surface(X, Y, Z, 
                       cmap='coolwarm',  # 'coolwarm' 顏色地圖常用於顯示正負值差異
                       edgecolor='none',
                       alpha=0.9)

# 設定軸標籤和標題
ax.set_xlabel('Real Axis (x)')
ax.set_ylabel('Imaginary Axis (y)')
ax.set_zlabel('Real Part $\\text{Re}(z^3)$')
ax.set_title('3D Plot of $\\text{Re}(f(z)) = x^3 - 3xy^2$')

# 調整 Z 軸的視角以獲得更好的可視性
ax.view_init(elev=30, azim=45)

# 加入顏色條 (Colorbar)
fig.colorbar(surf, shrink=0.5, aspect=5, label='Value of $\\text{Re}(z^3)$')

plt.show()