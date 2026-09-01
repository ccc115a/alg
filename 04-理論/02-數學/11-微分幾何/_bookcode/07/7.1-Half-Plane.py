import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import quad

class PoincareMetric:
    """
    龐加萊半平面度量計算器 g_ij = (1/y^2) * delta_ij
    """
    def __init__(self):
        pass

    def metric_tensor(self, x, y):
        """返回該點的度量矩陣 g (2x2)"""
        # 雖然我們積分時直接用公式，但寫出來有助理解
        scale = 1.0 / (y**2)
        return np.array([[scale, 0], [0, scale]])

    def compute_length(self, x_func, y_func, dx_func, dy_func, t_range):
        """
        計算路徑的黎曼長度。
        L = ∫ sqrt( g_ij * v^i * v^j ) dt
          = ∫ sqrt( (1/y^2) * ( (dx/dt)^2 + (dy/dt)^2 ) ) dt
          = ∫ (1/y) * sqrt( x'^2 + y'^2 ) dt
        """
        def integrand(t):
            x = x_func(t)
            y = y_func(t)
            dx = dx_func(t)
            dy = dy_func(t)
            
            # 龐加萊長度微元 ds = sqrt(dx^2 + dy^2) / y
            euclidean_speed = np.sqrt(dx**2 + dy**2)
            return euclidean_speed / y

        # 使用 scipy.integrate.quad 進行數值積分
        length, error = quad(integrand, t_range[0], t_range[1])
        return length

def run_poincare_demo():
    print("--- 專案 7.1: 龐加萊半平面與非歐距離 ---")
    
    # 定義兩點 A, B
    # 我們選兩個 y 值較小的點，讓測地線效果更明顯
    p1 = np.array([1.0, 1.0])
    p2 = np.array([5.0, 1.0])
    
    metric = PoincareMetric()
    
    print(f"起點 P1: {p1}")
    print(f"終點 P2: {p2}")
    
    # ==========================================
    # 路徑 1: 歐幾里得直線 (Linear Interpolation)
    # y = 1 (常數)
    # ==========================================
    # 參數化: x(t) = t, y(t) = 1
    # t 從 1 到 5
    path1_x = lambda t: t
    path1_y = lambda t: p1[1] + (p2[1] - p1[1]) * (t - p1[0]) / (p2[0] - p1[0]) # 雖然這裡是常數，寫通用點
    
    # 導數
    path1_dx = lambda t: 1.0
    path1_dy = lambda t: 0.0 # 水平線
    
    # 計算長度
    L_linear = metric.compute_length(path1_x, path1_y, path1_dx, path1_dy, (p1[0], p2[0]))
    
    # ==========================================
    # 路徑 2: 雙曲測地線 (Semicircle)
    # 龐加萊半平面的測地線是圓心在 x 軸上的半圓
    # ==========================================
    # 1. 找圓心 (c, 0) 和半徑 r
    # (x1-c)^2 + y1^2 = r^2
    # (x2-c)^2 + y2^2 = r^2
    # 解得 c = (x2^2 + y2^2 - x1^2 - y1^2) / 2(x2-x1)
    
    mid_numerator = (p2[0]**2 + p2[1]**2) - (p1[0]**2 + p1[1]**2)
    mid_denominator = 2 * (p2[0] - p1[0])
    center_x = mid_numerator / mid_denominator
    radius = np.sqrt((p1[0] - center_x)**2 + p1[1]**2)
    
    print(f"測地線圓心: ({center_x:.2f}, 0), 半徑: {radius:.2f}")
    
    # 2. 參數化半圓
    # x(t) = c + r cos(t), y(t) = r sin(t)
    # 我們需要找出 t 的範圍 (角度 theta)
    # theta = arctan2(y, x-c)
    theta1 = np.arctan2(p1[1], p1[0] - center_x)
    theta2 = np.arctan2(p2[1], p2[0] - center_x)
    
    # 確保角度順序 (從右到左 或 從左到右)
    # 這裡我們用 t 從 theta1 到 theta2
    path2_x = lambda t: center_x + radius * np.cos(t)
    path2_y = lambda t: radius * np.sin(t)
    
    path2_dx = lambda t: -radius * np.sin(t)
    path2_dy = lambda t: radius * np.cos(t)
    
    L_geodesic = metric.compute_length(path2_x, path2_y, path2_dx, path2_dy, (theta1, theta2))
    
    # ==========================================
    # 結果輸出與比較
    # ==========================================
    print("-" * 30)
    print(f"路徑 1 (歐氏直線) 的雙曲長度: {L_linear:.4f}")
    print(f"路徑 2 (半圓測地線) 的雙曲長度: {L_geodesic:.4f}")
    
    if L_geodesic < L_linear:
        print(">>> 驗證成功：彎曲的半圓路徑實際上比直線更短！")
    else:
        print(">>> 發生異常。")
        
    # ==========================================
    # 視覺化
    # ==========================================
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # 1. 畫背景熱圖 (Metric Cost)
    # 顏色越深代表長度權重越大 (1/y)
    grid_x = np.linspace(0, 6, 100)
    grid_y = np.linspace(0.1, 4, 100)
    GX, GY = np.meshgrid(grid_x, grid_y)
    MetricCost = 1.0 / GY 
    
    # 使用 LogNorm 讓顏色分佈更好看
    im = ax.imshow(MetricCost, extent=[0, 6, 0.1, 4], origin='lower', 
                   cmap='Blues', alpha=0.5, aspect='auto')
    plt.colorbar(im, label="Metric Cost (1/y)")
    
    # 2. 畫直線路徑
    t_lin = np.linspace(p1[0], p2[0], 50)
    ax.plot(t_lin, [path1_y(t) for t in t_lin], 'k--', linewidth=2, label=f'Euclidean Line (L={L_linear:.2f})')
    
    # 3. 畫測地線路徑
    t_geo = np.linspace(theta1, theta2, 100)
    ax.plot(path2_x(t_geo), path2_y(t_geo), 'r-', linewidth=3, label=f'Geodesic (L={L_geodesic:.2f})')
    
    # 4. 畫起終點
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], 'ko')
    ax.text(p1[0], p1[1]+0.1, "P1")
    ax.text(p2[0], p2[1]+0.1, "P2")
    
    # 5. 標示 x 軸 (邊界)
    ax.axhline(0, color='black', linewidth=2)
    ax.text(3, 0.05, "Boundary (y=0)", ha='center')
    
    ax.set_title("Poincaré Half-Plane Model: Why Geodesics curve up?")
    ax.set_xlim(0, 6)
    ax.set_ylim(0, 4)
    ax.legend()
    plt.show()

if __name__ == "__main__":
    run_poincare_demo()