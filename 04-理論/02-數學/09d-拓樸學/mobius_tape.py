import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm

def plot_mobius_strip():
    """使用參數方程式繪製莫比烏斯帶。"""
    
    # 參數範圍
    u = np.linspace(0, 2 * np.pi, 100)  # 角度 (環繞)
    v = np.linspace(-0.3, 0.3, 30)      # 寬度
    u, v = np.meshgrid(u, v)
    
    # 莫比烏斯帶的參數方程式 (R=1)
    R = 1.0  # 半徑
    
    # 計算 X, Y, Z 坐標
    x = (R + v * np.cos(u / 2)) * np.cos(u)
    y = (R + v * np.cos(u / 2)) * np.sin(u)
    z = v * np.sin(u / 2)
    
    # 繪圖
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # 使用 plot_surface 繪製
    ax.plot_surface(x, y, z, 
                    cmap=cm.coolwarm, 
                    rstride=1, cstride=1,
                    linewidth=0, antialiased=True, alpha=0.9)
    
    # 設定視圖
    ax.set_title('Möbius Strip (可嵌入於 R³)')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_aspect('equal') # 保持比例
    plt.show()

# 執行繪製莫比烏斯帶
plot_mobius_strip()
