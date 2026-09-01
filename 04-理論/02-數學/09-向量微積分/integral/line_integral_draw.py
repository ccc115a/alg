# --- 檔案名稱: main_plot.py ---
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import line_integral as li  # <--- 引用我們剛寫好的模組

# ==========================================
# 繪圖輔助函數
# ==========================================

def plot_2d_case(ax, field_func, path_func, t_range, title, grid_range):
    """畫出 2D 向量場與路徑"""
    # 1. 計算積分結果 (呼叫模組)
    work = li.calculate_line_integral(field_func, path_func, t_range)
    
    # 2. 準備網格以繪製向量場 (Quiver)
    x = np.linspace(grid_range[0], grid_range[1], 20)
    y = np.linspace(grid_range[2], grid_range[3], 20)
    X, Y = np.meshgrid(x, y)
    
    # 計算網格上的向量
    U, V = np.zeros_like(X), np.zeros_like(Y)
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            vec = field_func(X[i, j], Y[i, j])
            U[i, j] = vec[0]
            V[i, j] = vec[1]
            
    # 3. 準備路徑數據
    t_vals = np.linspace(t_range[0], t_range[1], 200)
    path_points = np.array([path_func(t) for t in t_vals])
    px, py = path_points[:, 0], path_points[:, 1]
    
    # 4. 繪圖
    # 畫向量場 (淡灰色背景)
    ax.quiver(X, Y, U, V, color='gray', alpha=0.3, pivot='mid')
    # 畫路徑
    ax.plot(px, py, 'b-', linewidth=2, label='Path')
    # 畫起點和終點
    ax.plot(px[0], py[0], 'go', label='Start')
    ax.plot(px[-1], py[-1], 'ro', label='End')
    
    ax.set_title(f"{title}\nWork = {work:.4f}", fontsize=11, fontweight='bold')
    ax.grid(True)
    ax.legend(loc='upper right', fontsize=8)
    ax.set_aspect('equal')
    ax.set_xlim(grid_range[0], grid_range[1])
    ax.set_ylim(grid_range[2], grid_range[3])

def plot_3d_case(ax, field_func, path_func, t_range, title):
    """畫出 3D 路徑與沿途的力向量"""
    # 1. 計算積分結果
    work = li.calculate_line_integral(field_func, path_func, t_range)
    
    # 2. 準備路徑數據
    t_vals = np.linspace(t_range[0], t_range[1], 100)
    path_points = np.array([path_func(t) for t in t_vals])
    px, py, pz = path_points[:, 0], path_points[:, 1], path_points[:, 2]
    
    # 3. 繪圖 - 路徑
    ax.plot(px, py, pz, 'b-', linewidth=2, label='Path')
    
    # 4. 繪圖 - 沿途的力場向量 (不畫全場，只畫路徑上的幾個點，不然會太亂)
    skip = 10 # 每隔 10 點畫一個箭頭
    for i in range(0, len(t_vals), skip):
        x, y, z = px[i], py[i], pz[i]
        u, v, w = field_func(x, y, z)
        # 正規化箭頭長度以便觀察
        length = np.sqrt(u**2 + v**2 + w**2)
        if length > 0:
            ax.quiver(x, y, z, u, v, w, length=0.5, normalize=True, color='red', alpha=0.6)
            
    # 假裝畫一個箭頭當作 Legend 用
    ax.plot([],[],[], 'r-', alpha=0.6, label='Force Vectors')

    ax.set_title(f"{title}\nWork = {work:.4f}", fontsize=11, fontweight='bold')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.legend()

# ==========================================
# 定義測試案例與主執行區
# ==========================================

if __name__ == "__main__":
    # 設定畫布
    fig = plt.figure(figsize=(14, 10), constrained_layout=True)
    
    # --- Case 1: 恆力直線 ---
    # F=[1, 2], Path=(t, 0)
    ax1 = fig.add_subplot(2, 2, 1)
    plot_2d_case(
        ax1, 
        field_func=lambda x, y: [1, 2],
        path_func=lambda t: [t, 0],
        t_range=(0, 3),
        title="1. Constant Force (Linear Path)",
        grid_range=(-1, 4, -1, 3) # xmin, xmax, ymin, ymax
    )
    
    # --- Case 2: 旋轉場圓周 ---
    # F=[-y, x], Path=(cos t, sin t)
    ax2 = fig.add_subplot(2, 2, 2)
    plot_2d_case(
        ax2, 
        field_func=lambda x, y: [-y, x],
        path_func=lambda t: [np.cos(t), np.sin(t)],
        t_range=(0, 2*np.pi),
        title="2. Rotation Field (Circular Path)",
        grid_range=(-1.5, 1.5, -1.5, 1.5)
    )
    
    # --- Case 3: 正交運動 (垂直) ---
    # F=[0, 10], Path=(t, 0) -> 力向上，路徑向右
    ax3 = fig.add_subplot(2, 2, 3)
    plot_2d_case(
        ax3, 
        field_func=lambda x, y: [0, 10],
        path_func=lambda t: [t, 0],
        t_range=(0, 5),
        title="3. Vertical Force (Orthogonal Path)",
        grid_range=(-1, 6, -2, 12)
    )
    
    # --- Case 4: 3D 螺旋線 ---
    # F=[z, 0, x], Path=(cos t, sin t, t)
    ax4 = fig.add_subplot(2, 2, 4, projection='3d')
    plot_3d_case(
        ax4,
        field_func=lambda x, y, z: [z, 0, x],
        path_func=lambda t: [np.cos(t), np.sin(t), t],
        t_range=(0, 2*np.pi),
        title="4. 3D Helix Path"
    )

    plt.suptitle("Visualizing Line Integrals (Work = $\int F \cdot dr$)", fontsize=16)
    plt.show()