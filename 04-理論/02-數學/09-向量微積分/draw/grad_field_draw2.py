import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm

def plot_gradient_vs_surface():
    # 1. 設定網格
    n = 30 # 稍微增加解析度讓 3D 圖更滑順
    x = np.linspace(-2, 2, n)
    y = np.linspace(-2, 2, n)
    X, Y = np.meshgrid(x, y) # indexing='xy'
    
    dx = x[1] - x[0]
    dy = y[1] - y[0]

    # 定義四個場景
    cases = [
        {
            "title": "1. Linear Slope (斜坡)",
            "func": lambda X, Y: 0.5 * X + 0.5 * Y,
            "desc": "Gradient is constant.\n(Uniform steepness)"
        },
        {
            "title": "2. Gaussian Hill (山丘)",
            "func": lambda X, Y: np.exp(-(X**2 + Y**2)),
            "desc": "Arrows point to the peak.\nZero gradient at top."
        },
        {
            "title": "3. Saddle Point (馬鞍面)",
            "func": lambda X, Y: X**2 - Y**2,
            "desc": "Up along X, Down along Y.\nZero gradient at center."
        },
        {
            "title": "4. Egg Crate (波浪地形)",
            "func": lambda X, Y: np.sin(np.pi*X) * np.sin(np.pi*Y),
            "desc": "Multiple peaks and valleys."
        }
    ]

    # 設定畫布：4 列 (Cases) x 2 行 (2D vs 3D)
    # figsize 高度拉長以容納 4 組圖
    fig = plt.figure(figsize=(14, 20), constrained_layout=True)

    for i, case in enumerate(cases):
        Z = case["func"](X, Y)
        
        # 計算梯度
        grad_y, grad_x = np.gradient(Z, dy, dx)

        # ==========================================
        # 左欄：2D 梯度場 (地圖視角)
        # ==========================================
        ax_2d = fig.add_subplot(4, 2, 2*i + 1)
        
        # 畫背景高度
        cp = ax_2d.contourf(X, Y, Z, levels=25, cmap='viridis')
        fig.colorbar(cp, ax=ax_2d, label='Height')
        
        # 畫等高線 (白色)
        ax_2d.contour(X, Y, Z, levels=15, colors='white', alpha=0.3, linewidths=0.5)
        
        # 畫梯度箭頭
        step = 2
        ax_2d.quiver(X[::step, ::step], Y[::step, ::step], 
                     grad_x[::step, ::step], grad_y[::step, ::step], 
                     color='white', pivot='mid')
        
        ax_2d.set_title(f"{case['title']} - Gradient Field (2D)", fontweight='bold')
        ax_2d.set_xlabel('x')
        ax_2d.set_ylabel('y')
        ax_2d.set_aspect('equal')
        
        # 在圖內加上說明
        ax_2d.text(-1.9, -1.9, case["desc"], color='white', fontsize=10,
                   bbox=dict(facecolor='black', alpha=0.5))

        # ==========================================
        # 右欄：3D 曲面圖 (實體視角)
        # ==========================================
        ax_3d = fig.add_subplot(4, 2, 2*i + 2, projection='3d')
        
        # 畫曲面
        surf = ax_3d.plot_surface(X, Y, Z, cmap='viridis', 
                                  linewidth=0, antialiased=False, alpha=0.9)
        
        # 調整視角 (Elevation 高度角, Azimuth 方位角)
        # 根據不同圖形微調視角，讓特徵更明顯
        if i == 2: # 馬鞍面
            ax_3d.view_init(elev=30, azim=45)
        else:
            ax_3d.view_init(elev=45, azim=-60)
            
        ax_3d.set_title(f"{case['title']} - Surface Topology (3D)", fontweight='bold')
        ax_3d.set_xlabel('x')
        ax_3d.set_ylabel('y')
        ax_3d.set_zlabel('z')
        
        # 加一點顏色對照條
        fig.colorbar(surf, ax=ax_3d, shrink=0.5, aspect=10, label='Height')

    plt.suptitle("Comparison: 2D Gradient Vector Field vs 3D Surface Function", fontsize=16)
    plt.show()

if __name__ == "__main__":
    plot_gradient_vs_surface()