import numpy as np
import matplotlib.pyplot as plt

def plot_vector_calculus_demo():


    # 1. 設定網格 (Grid Setup)
    # 建立 -2 到 2 的空間，切分 20x20 個點
    n = 21
    x = np.linspace(-2, 2, n)
    y = np.linspace(-2, 2, n)
    X, Y = np.meshgrid(x, y)

    # 設定畫布大小
    fig, axes = plt.subplots(1, 3, figsize=(18, 5), constrained_layout=True)
    
    # ==========================================
    # 圖 1: 梯度 (Gradient)
    # 意義：純量場變大的最快方向
    # ==========================================
    ax = axes[0]
    
    # 定義純量場 Z (像是一個小山丘和一個凹谷)
    # Z = X * exp(-X^2 - Y^2)
    Z = X * np.exp(-(X**2 + Y**2))
    
    # 計算梯度 (NumPy 的 gradient 回傳的是 [dZ/dy, dZ/dx] 注意順序)
    # 為了畫圖對應正確，dy 對應 axis 0, dx 對應 axis 1
    dZ_dy, dZ_dx = np.gradient(Z, y[1]-y[0], x[1]-x[0])
    
    # 畫出底圖 (純量場的高度顏色)
    cp = ax.contourf(X, Y, Z, levels=20, cmap='viridis')
    fig.colorbar(cp, ax=ax, label='Scalar Value (Height)')
    
    # 畫出向量場 (箭頭)
    # 箭頭指向上坡方向
    ax.quiver(X, Y, dZ_dx, dZ_dy, color='white', scale=20, width=0.005)
    
    ax.set_title("Gradient (∇f)\nArrows point uphill (Steepest Ascent)", fontsize=14)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_aspect('equal')

    # ==========================================
    # 圖 2: 散度 (Divergence)
    # 意義：流體從一點「湧出」或「匯入」的程度
    # ==========================================
    ax = axes[1]
    
    # 定義向量場 F = [x, y] (這是一個典型的源頭 Source)
    U = X
    V = Y
    
    # 計算散度 (數值近似)
    # div F = dU/dx + dV/dy
    dU_dx = np.gradient(U, x[1]-x[0], axis=1)
    dV_dy = np.gradient(V, y[1]-y[0], axis=0)
    divergence = dU_dx + dV_dy
    
    # 畫出底圖 (散度的大小顏色)
    # 這裡散度應該是常數 2 (因為 dx/dx + dy/dy = 1+1 = 2)
    cp = ax.contourf(X, Y, divergence, levels=20, cmap='coolwarm')
    fig.colorbar(cp, ax=ax, label='Divergence Value')
    
    # 畫出向量場
    ax.quiver(X, Y, U, V, color='black', scale=25, width=0.005)
    
    ax.set_title("Divergence (∇·F)\nPositive: Source (Expanding outward)", fontsize=14)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_aspect('equal')

    # ==========================================
    # 圖 3: 旋度 (Curl)
    # 意義：流體的旋轉強度
    # ==========================================
    ax = axes[2]
    
    # 定義向量場 F = [-y, x] (剛體旋轉)
    U = -Y
    V = X
    
    # 計算 2D 旋度 (數值近似)
    # curl F (z分量) = dV/dx - dU/dy
    dV_dx = np.gradient(V, x[1]-x[0], axis=1)
    dU_dy = np.gradient(U, y[1]-y[0], axis=0)
    curl_z = dV_dx - dU_dy
    
    # 畫出底圖 (旋度的大小顏色)
    # 這裡旋度應該是常數 2
    cp = ax.contourf(X, Y, curl_z, levels=20, cmap='autumn')
    fig.colorbar(cp, ax=ax, label='Curl (Z-component)')
    
    # 畫出向量場
    ax.quiver(X, Y, U, V, color='black', scale=25, width=0.005)
    
    ax.set_title("Curl (∇×F)\nNon-zero: Rotation (Vortex)", fontsize=14)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_aspect('equal')

    # 顯示圖表
    plt.show()

if __name__ == "__main__":
    plot_vector_calculus_demo()
