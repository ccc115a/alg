import numpy as np
import matplotlib.pyplot as plt

def plot_varying_fields():
    # 設定網格
    x = np.linspace(-3, 3, 30)
    y = np.linspace(-3, 3, 30)
    X, Y = np.meshgrid(x, y)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # ==========================================
    # 範例 1: 散度會變化的場
    # F = [sin(x), sin(y)]
    # 散度 = cos(x) + cos(y) -> 會有波峰(紅)與波谷(藍)
    # ==========================================
    ax = axes[0]
    U = np.sin(X)
    V = np.sin(Y)
    
    # 計算散度
    spacing = x[1] - x[0]
    dU_dx = np.gradient(U, spacing, axis=1)
    dV_dy = np.gradient(V, spacing, axis=0)
    divergence = dU_dx + dV_dy
    
    # 畫背景顏色 (散度大小)
    # cmap='bwr' 是 Blue-White-Red (藍-白-紅)，適合看正負值
    cp = ax.contourf(X, Y, divergence, levels=20, cmap='bwr')
    fig.colorbar(cp, ax=ax, label='Divergence Value')
    
    # 畫箭頭
    ax.quiver(X, Y, U, V, color='black')
    ax.set_title("Divergence Map\nRed=Source (Out), Blue=Sink (In)")

    # ==========================================
    # 範例 2: 旋度會變化的場 (剪切流)
    # F = [y^2, 0] (越上面流速越快，產生旋轉)
    # 旋度 = -2y -> 跟 y 有關，上面負旋轉，下面正旋轉
    # ==========================================
    ax = axes[1]
    U = Y**2 * np.sign(Y) # 讓流場稍微複雜一點
    V = np.zeros_like(Y)
    
    # 計算旋度
    # curl = dV/dx - dU/dy
    dV_dx = np.gradient(V, spacing, axis=1)
    dU_dy = np.gradient(U, spacing, axis=0)
    curl = dV_dx - dU_dy
    
    # 畫背景顏色
    cp = ax.contourf(X, Y, curl, levels=20, cmap='bwr')
    fig.colorbar(cp, ax=ax, label='Curl Value')
    
    # 畫箭頭
    ax.quiver(X, Y, U, V, color='black')
    ax.set_title("Curl Map\nColor shows Rotation Strength")

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    plot_varying_fields()