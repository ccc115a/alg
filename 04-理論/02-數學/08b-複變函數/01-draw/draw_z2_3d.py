import numpy as np
import matplotlib.pyplot as plt
# 匯入 3D 繪圖模組
from mpl_toolkits.mplot3d import Axes3D

# --- 1. 定義輸入 z 的範圍 (x 和 y 座標) ---
# 建立 x 和 y 軸的等差數列
x = np.linspace(-2, 2, 50)
y = np.linspace(-2, 2, 50)

# 建立一個網格 (Grid) 來表示 z 平面
X, Y = np.meshgrid(x, y)

# --- 2. 計算函數的模長 (高度 H) ---
# 複變函數 f(z) = z^2
# 我們計算模長 H = |f(z)| = x^2 + y^2
H = X**2 + Y**2

# --- 3. 繪製 3D 圖形 ---
fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111, projection='3d')

# 繪製曲面
surf = ax.plot_surface(X, Y, H, 
                       cmap='viridis', # 設定顏色地圖
                       edgecolor='none',
                       alpha=0.8)

# 設定軸標籤和標題
ax.set_xlabel('Real Axis (x)')
ax.set_ylabel('Imaginary Axis (y)')
ax.set_zlabel('Magnitude $|f(z)| = |z^2|$')
ax.set_title('3D Plot of Magnitude for $f(z) = z^2$')

# 加入顏色條
fig.colorbar(surf, shrink=0.5, aspect=5, label='$|z^2|$ value')

plt.show()