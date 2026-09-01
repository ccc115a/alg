import numpy as np
import matplotlib.pyplot as plt

def plot_divergence_gallery():
    # 1. 設定網格
    # 範圍 -2 到 2
    n = 25
    x = np.linspace(-2, 2, n)
    y = np.linspace(-2, 2, n)
    X, Y = np.meshgrid(x, y) # Default indexing='xy'
    
    # 計算網格間距 (用於梯度計算)
    dx = x[1] - x[0]
    dy = y[1] - y[0]

    # 設定畫布 (2x2)
    fig, axes = plt.subplots(2, 2, figsize=(12, 10), constrained_layout=True)
    axes = axes.flatten()

    # 定義四個場景
    # 格式: (標題, U函數, V函數, 說明)
    cases = [
        {
            "title": "1. Uniform Expansion (Div = Constant > 0)",
            "u": X,
            "v": Y,
            "desc": "F = [x, y]\nEvery point expands equally."
        },
        {
            "title": "2. Pure Rotation (Div = 0)",
            "u": -Y,
            "v": X,
            "desc": "F = [-y, x]\nFluid rotates but density never changes.\n(Incompressible)"
        },
        {
            "title": "3. Accelerating Flow (Div varies with X)",
            "u": X**2, # 向右流，速度隨 x 平方增加
            "v": np.zeros_like(Y),
            "desc": "F = [x^2, 0]\nLeft: Decelerating (Traffic Jam/Sink)\nRight: Accelerating (Stretch/Source)"
        },
        {
            "title": "4. Periodic Sources & Sinks",
            "u": np.sin(np.pi * X),
            "v": np.sin(np.pi * Y),
            "desc": "F = [sin(πx), sin(πy)]\nAlternating pockets of expansion and compression."
        }
    ]

    for i, case in enumerate(cases):
        ax = axes[i]
        U = case["u"]
        V = case["v"]
        
        # --- 計算散度 ---
        # divergence = dU/dx + dV/dy
        # 注意: np.gradient 對於 meshgrid='xy'，axis=1 是 x 方向，axis=0 是 y 方向
        dU_dx = np.gradient(U, dx, axis=1)
        dV_dy = np.gradient(V, dy, axis=0)
        div = dU_dx + dV_dy
        
        # --- 繪圖設定 ---
        # 為了讓紅色代表正(Source)，藍色代表負(Sink)，白色代表0
        # 我們需要鎖定顏色範圍，使其對稱
        limit = np.max(np.abs(div))
        if limit < 1e-5: limit = 1.0 # 避免除以 0 或範圍過小
        
        # 畫背景顏色 (散度)
        # cmap='seismic' 是一個優良的紅-白-藍色階
        cp = ax.contourf(X, Y, div, levels=20, cmap='seismic', vmin=-limit, vmax=limit)
        
        # 畫 Colorbar
        cbar = fig.colorbar(cp, ax=ax)
        cbar.set_label('Divergence Value')

        # 畫向量箭頭
        # 稍微稀疏一點，畫起來比較不亂 (每隔 2 點畫一個)
        step = 2
        ax.quiver(X[::step, ::step], Y[::step, ::step], 
                  U[::step, ::step], V[::step, ::step], 
                  color='black', pivot='mid')
        
        ax.set_title(case["title"], fontsize=12, fontweight='bold')
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        # 在圖下方加上說明文字
        ax.text(0, -2.8, case["desc"], ha='center', va='top', fontsize=10, 
                bbox=dict(boxstyle="round", alpha=0.1))
        ax.set_aspect('equal')

    plt.suptitle("Comparison of Divergence in Different Vector Fields", fontsize=16)
    plt.show()

if __name__ == "__main__":
    plot_divergence_gallery()