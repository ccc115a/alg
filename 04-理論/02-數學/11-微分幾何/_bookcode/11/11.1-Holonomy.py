import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from mpl_toolkits.mplot3d import Axes3D

class SphereTransport:
    def __init__(self):
        print("--- 啟動球面平行移動模擬 ---")

    def christoffel(self, theta):
        """
        計算單位球面的 Christoffel Symbols
        非零分量:
        Γ^theta_phi,phi = -sin(theta)cos(theta)
        Γ^phi_theta,phi = cot(theta)
        """
        # G[k, i, j] 代表 Γ^k_ij
        # index 0: theta, index 1: phi
        G = np.zeros((2, 2, 2))
        
        # 避免 theta=0 的奇異點
        if np.abs(theta) < 1e-5:
            cot_theta = 0 # 簡單處理，或者設大數
        else:
            cot_theta = 1.0 / np.tan(theta)
            
        G[0, 1, 1] = -np.sin(theta) * np.cos(theta)
        G[1, 0, 1] = cot_theta
        G[1, 1, 0] = cot_theta
        return G

    def parallel_transport_ode(self, t, V, path_func):
        """
        平行移動微分方程: dV^k/dt = -Γ^k_ij * (dx^i/dt) * V^j
        """
        # 1. 獲取當前位置與速度
        theta, phi, d_theta, d_phi = path_func(t)
        
        # 2. 獲取 Γ
        G = self.christoffel(theta)
        
        # 3. 準備向量
        velocity = np.array([d_theta, d_phi]) # dx^i/dt
        vector = V                            # V^j
        
        # 4. 計算導數 (使用 einsum)
        # k: 輸出分量, i: 速度指標, j: 向量指標
        dV_dt = -np.einsum('kij,i,j->k', G, velocity, vector)
        
        return dV_dt

    def sph2cart(self, theta, phi, v_theta, v_phi):
        """
        將球面坐標的位置和向量轉換為笛卡兒坐標 (用於繪圖)
        位置: (x, y, z)
        向量: (vx, vy, vz) = Jacobian * (v_theta, v_phi)
        """
        # 位置
        x = np.sin(theta) * np.cos(phi)
        y = np.sin(theta) * np.sin(phi)
        z = np.cos(theta)
        
        # 雅可比矩陣 J = d(x,y,z)/d(theta, phi)
        # J 是一個 3x2 矩陣
        # col 1: d/d_theta
        dx_dth = np.cos(theta) * np.cos(phi)
        dy_dth = np.cos(theta) * np.sin(phi)
        dz_dth = -np.sin(theta)
        
        # col 2: d/d_phi
        dx_dphi = -np.sin(theta) * np.sin(phi)
        dy_dphi = np.sin(theta) * np.cos(phi)
        dz_dphi = 0
        
        # 轉換向量
        vx = dx_dth * v_theta + dx_dphi * v_phi
        vy = dy_dth * v_theta + dy_dphi * v_phi
        vz = dz_dth * v_theta + dz_dphi * v_phi
        
        return np.array([x, y, z]), np.array([vx, vy, vz])

    def run_simulation(self):
        # 定義四段路徑 (構成閉迴路)
        # 為了避免極點奇異性，我們從 theta=0.2 (靠近北極) 開始
        theta_start = 0.2
        
        # Segment 1: 向下 (theta 增加, phi 固定 0)
        def path1(t): # t: 0 -> 1
            th = theta_start + t * (np.pi/2 - theta_start)
            return th, 0, (np.pi/2 - theta_start), 0

        # Segment 2: 向東 (theta 固定 pi/2, phi 增加)
        def path2(t): # t: 0 -> 1
            ph = t * (np.pi/2)
            return np.pi/2, ph, 0, np.pi/2

        # Segment 3: 向上 (theta 減少, phi 固定 pi/2)
        def path3(t): # t: 0 -> 1
            th = np.pi/2 - t * (np.pi/2 - theta_start)
            return th, np.pi/2, -(np.pi/2 - theta_start), 0
            
        # Segment 4: 回到起點 (theta 固定 0.2, phi 減少)
        # 這一步是為了數學上的閉合，讓我們回到 (0.2, 0)
        def path4(t): # t: 0 -> 1
            ph = np.pi/2 - t * (np.pi/2)
            return theta_start, ph, 0, -np.pi/2

        paths = [path1, path2, path3, path4]
        
        # 初始向量: 指向南方 (theta方向)
        # V^theta = 1, V^phi = 0
        current_V = np.array([1.0, 0.0])
        
        # 儲存繪圖數據
        all_positions = []
        all_vectors = []
        
        print("開始路徑積分...")
        
        for p_func in paths:
            # 定義該段的 ODE
            fun = lambda t, y: self.parallel_transport_ode(t, y, p_func)
            
            # 求解
            t_span = (0, 1)
            t_eval = np.linspace(0, 1, 20)
            sol = solve_ivp(fun, t_span, current_V, t_eval=t_eval, rtol=1e-7)
            
            # 記錄數據與更新向量
            for i in range(len(sol.t)):
                th, ph, _, _ = p_func(sol.t[i])
                v_th, v_ph = sol.y[:, i]
                
                pos_cart, vec_cart = self.sph2cart(th, ph, v_th, v_ph)
                all_positions.append(pos_cart)
                all_vectors.append(vec_cart)
            
            # 更新下一段的起始向量
            current_V = sol.y[:, -1]

        # 轉為 array 方便繪圖
        all_positions = np.array(all_positions)
        all_vectors = np.array(all_vectors)
        
        # 視覺化
        self.plot_results(all_positions, all_vectors)

    def plot_results(self, P, V):
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # 1. 畫球體網格
        u = np.linspace(0, 2 * np.pi, 30)
        v = np.linspace(0, np.pi, 20)
        x = np.outer(np.cos(u), np.sin(v))
        y = np.outer(np.sin(u), np.sin(v))
        z = np.outer(np.ones(np.size(u)), np.cos(v))
        ax.plot_surface(x, y, z, color='whitesmoke', alpha=0.3)
        
        # 2. 畫路徑
        ax.plot(P[:,0], P[:,1], P[:,2], 'b-', linewidth=2, label='Path')
        
        # 3. 畫向量 (Quiver)
        # 為了不讓圖太亂，每隔幾個點畫一個箭頭
        step = 4
        # 正規化向量長度以便顯示
        V_norm = V / np.linalg.norm(V, axis=1, keepdims=True) * 0.2
        
        ax.quiver(P[::step,0], P[::step,1], P[::step,2], 
                  V_norm[::step,0], V_norm[::step,1], V_norm[::step,2], 
                  color='r', length=1.0, normalize=False, label='Transported Vector')
        
        # 4. 特寫起點和終點向量
        start_idx = 0
        end_idx = -1
        
        # 起點向量 (綠色)
        ax.quiver(P[start_idx,0], P[start_idx,1], P[start_idx,2],
                  V_norm[start_idx,0], V_norm[start_idx,1], V_norm[start_idx,2],
                  color='green', linewidth=3, arrow_length_ratio=0.3, label='Start Vector')
        
        # 終點向量 (洋紅色) - 應該與起點位置重合，但方向不同
        ax.quiver(P[end_idx,0], P[end_idx,1], P[end_idx,2],
                  V_norm[end_idx,0], V_norm[end_idx,1], V_norm[end_idx,2],
                  color='magenta', linewidth=3, arrow_length_ratio=0.3, label='End Vector')

        ax.set_title("Parallel Transport & Holonomy on Sphere")
        ax.set_box_aspect([1,1,1])
        plt.legend()
        plt.show()
        
        # 數值驗證角度差
        v_start = V[0]
        v_end = V[-1]
        
        # 計算夾角 (在 3D 笛卡兒空間算即可，因為我們已經轉換過了)
        # 注意: 這裡是在同一點 (近似)，所以可以直接用歐氏內積算角度差
        cos_alpha = np.dot(v_start, v_end) / (np.linalg.norm(v_start) * np.linalg.norm(v_end))
        angle_deg = np.degrees(np.arccos(np.clip(cos_alpha, -1, 1)))
        
        print("-" * 30)
        print(f"起始向量 (Cartesian): {v_start}")
        print(f"終點向量 (Cartesian): {v_end}")
        print(f"和樂偏差角度 (Holonomy Angle): {angle_deg:.2f}°")
        print(f"理論預測值 (Area = 1/8 Sphere): 90.00°")
        print("-" * 30)

if __name__ == "__main__":
    sim = SphereTransport()
    sim.run_simulation()