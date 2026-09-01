import numpy as np
import matplotlib.pyplot as plt

def plot_gradient_gallery():
    # 1. 設定網格
    n = 25
    x = np.linspace(-2, 2, n)
    y = np.linspace(-2, 2, n)
    X, Y = np.meshgrid(x, y) # indexing='xy'
    
    # 計算間距
    dx = x[1] - x[0]
    dy = y[1] - y[0]

    # 設定畫布
    fig, axes = plt.subplots(2, 2, figsize=(12, 10), constrained_layout=True)
    axes = axes.flatten()

    # 定義四個場景
    # 這裡定義的是「純量場 Z (高度)」，我們稍後要算出它的梯度
    cases = [
        {
            "title": "1. Linear Slope (Gradient = Constant)",
            "func": lambda X, Y: 0.5 * X + 0.5 * Y,
            "desc": "f(x,y) = 0.5x + 0.5y\nA flat ramp. Steepness (Gradient) is constant everywhere."
        },
        {
            "title": "2. The Hill (Gaussian Peak)",
            "func": lambda X, Y: np.exp(-(X**2 + Y**2)),
            "desc": "f(x,y) = exp(-x^2 - y^2)\nArrows point to the peak.\nLength = Steepness (Zero at peak & far away)."
        },
        {
            "title": "3. Saddle Point (Minimax)",
            "func": lambda X, Y: X**2 - Y**2,
            "desc": "f(x,y) = x^2 - y^2\nUphill along X, Downhill along Y.\nGradient is zero at the center (0,0)."
        },
        {
            "title": "4. Egg Crate (Periodic Peaks)",
            "func": lambda X, Y: np.sin(np.pi*X) * np.sin(np.pi*Y),
            "desc": "f(x,y) = sin(πx)sin(πy)\nMultiple local maxima and minima.\nArrows swirl from pits to peaks."
        }
    ]

    for i, case in enumerate(cases):
        ax = axes[i]
        
        # 1. 取得純量場 Z (高度)
        Z = case["func"](X, Y)
        
        # 2. 計算梯度
        # np.gradient 回傳 (axis=0的微分, axis=1的微分)
        # 對於 meshgrid='xy'，axis=0 是 y方向 (rows)，axis=1 是 x方向 (cols)
        grad_y, grad_x = np.gradient(Z, dy, dx)
        
        # 3. 畫背景 (純量場的高度)
        # 使用 contourf 畫填色圖
        cp = ax.contourf(X, Y, Z, levels=25, cmap='viridis')
        fig.colorbar(cp, ax=ax, label='Height (Scalar Value)')
        
        # 疊加等高線 (Contour Lines)，讓垂直關係更明顯
        ax.contour(X, Y, Z, levels=15, colors='white', alpha=0.3, linewidths=0.5)

        # 4. 畫梯度向量 (箭頭)
        # 箭頭指向上坡
        step = 2
        ax.quiver(X[::step, ::step], Y[::step, ::step], 
                  grad_x[::step, ::step], grad_y[::step, ::step], 
                  color='white', pivot='mid', scale=None)
        
        ax.set_title(case["title"], fontsize=12, fontweight='bold')
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.text(0, -2.9, case["desc"], ha='center', va='top', fontsize=10, 
                bbox=dict(boxstyle="round", alpha=0.1, facecolor='white'))
        ax.set_aspect('equal')

    plt.suptitle("Visualizing Gradient (∇f) on Different Scalar Fields\nArrows point Uphill, perpendicular to Contour Lines", fontsize=16)
    plt.show()

if __name__ == "__main__":
    plot_gradient_gallery()
    