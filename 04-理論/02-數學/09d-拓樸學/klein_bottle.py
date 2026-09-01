import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm

def plot_klein_bottle():
    """使用參數方程式繪製克萊因瓶（三維浸入模型）。"""
    
    # 參數範圍
    v = np.linspace(0, 2 * np.pi, 100)  # 類似莫比烏斯帶的環繞參數
    u = np.linspace(0, 2 * np.pi, 100)  # 類似莫比烏斯帶的寬度參數 (這裡封閉了)
    u, v = np.meshgrid(u, v)
    
    # 參數設定
    r = 2  # 尺寸參數
    
    # 克萊因瓶的參數方程式 (更複雜的版本，創造自相交)
    
    # 為了程式碼簡潔和可讀性，我們分段處理
    a = 2 / 5
    # 注意：這裡使用了一個稍微不同的參數方程，以獲得更好的視覺效果
    
    x = -2/15 * np.cos(u) * (3 * np.cos(v) - 30 * np.sin(u) + 90 * np.cos(u)**4 * np.sin(u) - 60 * np.cos(u)**6 * np.sin(u) + 5 * np.cos(u) * np.cos(v) * np.sin(u))
    y = -1/15 * np.sin(u) * (3 * np.cos(v) - 3 * np.cos(u)**2 * np.cos(v) - 48 * np.cos(u)**4 * np.cos(v) + 48 * np.cos(u)**6 * np.cos(v) - 60 * np.sin(u) + 5 * np.cos(u) * np.cos(v) * np.sin(u) - 5 * np.cos(u)**3 * np.cos(v) * np.sin(u) - 80 * np.cos(u)**5 * np.cos(v) * np.sin(u) + 80 * np.cos(u)**7 * np.cos(v) * np.sin(u))
    z = 2/15 * (3 + 5 * np.cos(u) * np.sin(u)) * np.sin(v)
    
    # 繪圖
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # 繪製曲面
    ax.plot_surface(x, y, z, 
                    cmap=cm.viridis,  # 使用不同的顏色映射
                    rstride=5, cstride=5,
                    linewidth=0, antialiased=True, alpha=0.9)
    
    # 設定視圖
    ax.set_title('Klein Bottle Projection (R⁴ 浸入 R³, 具有自相交線)')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_aspect('equal')
    plt.show()

# 執行繪製克萊因瓶
plot_klein_bottle()