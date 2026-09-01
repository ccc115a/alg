import numpy as np
import matplotlib.pyplot as plt

def plot_curl_gallery():
    # 1. 設定網格
    n = 25
    x = np.linspace(-2, 2, n)
    y = np.linspace(-2, 2, n)
    X, Y = np.meshgrid(x, y) # indexing='xy'
    
    # 計算網格間距
    dx = x[1] - x[0]
    dy = y[1] - y[0]

    # 設定畫布 (2x2)
    fig, axes = plt.subplots(2, 2, figsize=(12, 10), constrained_layout=True)
    axes = axes.flatten()

    # 定義四個場景
    # 注意：在 2D 平面，正旋度(紅色) = 逆時針(CCW)，負旋度(藍色) = 順時針(CW)
    cases = [
        {
            "title": "1. Rigid Body Rotation (Curl = Constant > 0)",
            "u": -Y,
            "v": X,
            "desc": "F = [-y, x]\nLike a spinning CD.\nConstant CCW rotation everywhere."
        },
        {
            "title": "2. Radial / Explosion (Curl = 0)",
            "u": X,
            "v": Y,
            "desc": "F = [x, y]\nParticles move outward but do not spin.\nIrrotational field."
        },
        {
            "title": "3. Shear Flow (Curl varies with Y)",
            "u": Y**2, # 向右流，但上方流速快，下方流速慢(或反向)
            "v": np.zeros_like(X),
            "desc": "F = [y^2, 0]\nStraight flow, but a paddle wheel would spin!\nCurl = -2y (Color gradient top to bottom)"
        },
        {
            "title": "4. Periodic Vortices (Eddies)",
            "u": np.sin(np.pi * Y),  # 注意這裡跟 y 有關
            "v": np.sin(np.pi * X),  # 注意這裡跟 x 有關
            "desc": "F = [sin(πy), sin(πx)]\nGrid of alternating CW and CCW vortices."
        }
    ]

    for i, case in enumerate(cases):
        ax = axes[i]
        U = case["u"]
        V = case["v"]
        
        # --- 計算旋度 (z分量) ---
        # Curl_z = dV/dx - dU/dy
        dV_dx = np.gradient(V, dx, axis=1)
        dU_dy = np.gradient(U, dy, axis=0)
        curl = dV_dx - dU_dy
        
        # --- 繪圖設定 ---
        # 鎖定顏色範圍對稱，讓白色精確對應到 0
        limit = np.max(np.abs(curl))
        if limit < 1e-5: limit = 1.0 
        
        # 畫背景顏色 (旋度)
        # cmap='bwr' (Blue-White-Red): 藍=順時針, 紅=逆時針
        cp = ax.contourf(X, Y, curl, levels=20, cmap='bwr', vmin=-limit, vmax=limit)
        
        # 畫 Colorbar
        cbar = fig.colorbar(cp, ax=ax)
        cbar.set_label('Curl Value (Red=CCW, Blue=CW)')

        # 畫向量箭頭
        step = 2
        ax.quiver(X[::step, ::step], Y[::step, ::step], 
                  U[::step, ::step], V[::step, ::step], 
                  color='black', pivot='mid')
        
        ax.set_title(case["title"], fontsize=12, fontweight='bold')
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.text(0, -2.8, case["desc"], ha='center', va='top', fontsize=10, 
                bbox=dict(boxstyle="round", alpha=0.1))
        ax.set_aspect('equal')

    plt.suptitle("Comparison of Curl in Different Vector Fields", fontsize=16)
    plt.show()

if __name__ == "__main__":
    plot_curl_gallery()
