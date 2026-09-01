import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D

class CurveAnalyzer:
    """
    曲線分析器：給定參數曲線的座標點，計算 Frenet 標架。
    """
    def __init__(self, r_points):
        # r_points 形狀為 (N, 3)，代表 N 個點的 (x, y, z)
        self.r = r_points
        self.n_points = len(r_points)
        
        # 預先計算標架
        self.T, self.N, self.B = self._compute_frame()

    def _compute_frame(self):
        # 1. 計算切向量 T
        # 使用 numpy.gradient 進行數值微分 (中心差分法)
        # axis=0 表示沿著點的序列方向微分
        dr = np.gradient(self.r, axis=0)
        
        # 計算長度 (使用 linalg.norm)
        dr_norm = np.linalg.norm(dr, axis=1, keepdims=True)
        
        # 避免除以零 (雖然在光滑曲線上不應發生)
        dr_norm[dr_norm == 0] = 1.0 
        
        T = dr / dr_norm
        
        # 2. 計算法向量 N
        # N 是 T 的導數方向 (指向彎曲圓心)
        dT = np.gradient(T, axis=0)
        dT_norm = np.linalg.norm(dT, axis=1, keepdims=True)
        
        # 處理直線情況 (dT 為 0)
        # 這裡簡單處理：若曲率為0，N 保持與上一時刻相同或設為任意垂直向量
        # 為演示簡單，我們假設曲線足夠彎曲
        dT_norm[dT_norm < 1e-6] = 1.0 
        
        N = dT / dT_norm
        
        # 3. 計算副法向量 B
        # B = T x N
        B = np.cross(T, N)
        
        return T, N, B

def run_frenet_animation():
    print("--- 正在生成 Frenet-Serret 標架動畫 ---")
    
    # 1. 定義曲線：螺旋線 (Helix)
    # x = cos(t), y = sin(t), z = t/5
    t = np.linspace(0, 4 * np.pi, 200) # 兩個圓周
    x = np.cos(t)
    y = np.sin(t)
    z = t / 5.0
    
    # 堆疊成 (N, 3) 陣列
    points = np.column_stack([x, y, z])
    
    # 2. 計算標架
    curve = CurveAnalyzer(points)
    
    # 3. 設定繪圖環境
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # 設定坐標軸範圍
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_zlim(0, 3)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title("Frenet-Serret Frame Animation")
    
    # 繪製整條曲線軌跡 (灰色虛線)
    ax.plot(x, y, z, 'k--', alpha=0.3, lw=1)
    
    # 初始化物件：一個點和三個向量箭頭
    # quiver(x, y, z, u, v, w)
    # 我們將只繪製當前的一組 T, N, B
    
    # 因為 quiver 在 3D 動畫更新較麻煩，我們使用 "線段" 來模擬箭頭
    # 每個向量用一條顏色不同的線表示
    line_T, = ax.plot([], [], [], 'r-', lw=3, label='Tangent (T)')
    line_N, = ax.plot([], [], [], 'g-', lw=3, label='Normal (N)')
    line_B, = ax.plot([], [], [], 'b-', lw=3, label='Binormal (B)')
    point_dot, = ax.plot([], [], [], 'ko', markersize=5) # 當前點
    
    ax.legend()

    # 4. 動畫更新函數
    def update(frame_idx):
        # 獲取當前數據
        p = curve.r[frame_idx]   # 當前位置 (x,y,z)
        t_vec = curve.T[frame_idx]
        n_vec = curve.N[frame_idx]
        b_vec = curve.B[frame_idx]
        
        scale = 0.5 # 向量顯示長度縮放
        
        # 更新點的位置
        point_dot.set_data([p[0]], [p[1]]) # x, y
        point_dot.set_3d_properties([p[2]]) # z
        
        # 更新 T 向量 (紅色)
        # 起點 p, 終點 p + t_vec
        line_T.set_data([p[0], p[0] + t_vec[0]*scale], [p[1], p[1] + t_vec[1]*scale])
        line_T.set_3d_properties([p[2], p[2] + t_vec[2]*scale])
        
        # 更新 N 向量 (綠色)
        line_N.set_data([p[0], p[0] + n_vec[0]*scale], [p[1], p[1] + n_vec[1]*scale])
        line_N.set_3d_properties([p[2], p[2] + n_vec[2]*scale])
        
        # 更新 B 向量 (藍色)
        line_B.set_data([p[0], p[0] + b_vec[0]*scale], [p[1], p[1] + b_vec[1]*scale])
        line_B.set_3d_properties([p[2], p[2] + b_vec[2]*scale])
        
        return point_dot, line_T, line_N, line_B

    # 創建動畫
    ani = FuncAnimation(fig, update, frames=len(t), interval=50, blit=False)
    
    # 若在 Jupyter Notebook 中，請使用 %matplotlib notebook 或 jshtml
    # 這裡我們直接顯示視窗
    plt.show()

if __name__ == "__main__":
    run_frenet_animation()