import numpy as np
import matplotlib.pyplot as plt

def plot_gravitational_vector_field():
    # 1. 設定網格 (Grid)
    # 稍微縮小範圍，讓視覺集中
    x = np.linspace(-2, 2, 20)
    y = np.linspace(-2, 2, 20)
    X, Y = np.meshgrid(x, y)

    # 2. 計算物理量
    # 計算距離 r
    R = np.hypot(X, Y)
    
    # 避免除以零 (處理圓心)
    # 將極接近圓心的點設為遮罩 (Mask)，不進行繪製，避免箭頭無限大
    mask = R > 0.3
    X = X[mask]
    Y = Y[mask]
    R = R[mask]

    GM = 1.0
    
    # 計算向量分量 (U, V)
    # g = -GM / r^3 * vec(r)
    # 這邊直接計算出的 U, V 大小本身就代表強度
    U = -GM * X / R**3
    V = -GM * Y / R**3

    # 計算強度 (Magnitude) 用於顏色映射
    M = np.hypot(U, V)

    # --- 關鍵處理 ---
    # 因為重力場中心強度無限大，若直接畫，外圍箭頭會變成像塵埃一樣看不到。
    # 為了視覺效果，我們設定一個「顯示上限」，超過這個長度的箭頭都以該長度顯示。
    # 這雖然在中心點失真，但能讓外圍場線看得到。
    clip_threshold = 3.0  # 設定最大長度閾值
    
    # 複製一份用來畫圖的 U, V (不影響原始數據計算顏色)
    U_plot = U.copy()
    V_plot = V.copy()
    
    # 如果向量長度超過閾值，將其縮放至閾值長度，但方向不變
    large_vectors = M > clip_threshold
    scale_factor = clip_threshold / M[large_vectors]
    U_plot[large_vectors] *= scale_factor
    V_plot[large_vectors] *= scale_factor

    # 3. 繪圖 (Quiver Plot)
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_facecolor('#f0f0f0') # 淺灰背景

    # Quiver 參數說明：
    # X, Y: 位置
    # U_plot, V_plot: 向量分量 (長度代表強度)
    # M: 依據原始強度上色
    # angles='xy', scale_units='xy', scale=1: 確保箭頭長度與座標軸比例一致 (真實比例)
    q = ax.quiver(X, Y, U_plot, V_plot, M,
                  cmap='plasma_r',      # 顏色表 (反轉，讓強處顏色深)
                  pivot='mid',          # 箭頭中心對準網格點
                  width=0.005,          # 箭頭寬度
                  headwidth=4, 
                  headlength=5)

    # 畫出中心質點
    ax.add_patch(plt.Circle((0, 0), 0.1, color='black', zorder=10))

    # 加入顏色條
    cbar = plt.colorbar(q, ax=ax)
    cbar.set_label('Gravitational Field Strength ($g = GM/r^2$)\n(Arrows clamped at center)', fontsize=12)

    ax.set_title('Gravitational Vector Field\n(Length & Color indicate Strength)', fontsize=14)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_aspect('equal')
    ax.grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    plot_gravitational_vector_field()