import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

class BlackHoleRayTracer:
    def __init__(self, M=1.0):
        self.M = M
        self.rs = 2 * M        # 史瓦西半徑 (Event Horizon)
        self.rp = 3 * M        # 光子層 (Photon Sphere) - 光可以繞圈圈的地方
        print(f"--- 初始化黑洞 (M={M}) ---")
        print(f"  事件視界 r_s = {self.rs}")
        print(f"  光子層   r_p = {self.rp}")

    def geodesic_equations(self, lam, state):
        """
        史瓦西時空中的測地線方程 (Equatorial Plane)
        state = [t, r, phi, dt, dr, dphi]
        """
        t, r, phi, dt, dr, dphi = state
        
        # 為了數值穩定，當 r 非常接近或小於視界時，停止計算導並設為 0
        if r <= self.rs * 1.01:
            return np.zeros(6)

        # 預先計算常用項
        term1 = r - 2 * self.M
        factor = 1.0 / (r * term1) # 1 / (r(r-2M))
        
        # 1. 時間加速度 d2t
        # d/dl ( (1-2M/r) dt ) = 0 => dt/dl = E / (1-2M/r)
        # 這裡我們直接寫二階形式: d2t = - (2M / r(r-2M)) * dr * dt
        d2t = - (2 * self.M * factor) * dr * dt
        
        # 2. 角度加速度 d2phi
        # d/dl ( r^2 dphi ) = 0 => Conservation of Angular Momentum
        # d2phi = - (2/r) * dr * dphi
        d2phi = - (2.0 / r) * dr * dphi
        
        # 3. 徑向加速度 d2r (最複雜的一項)
        # 來自 Euler-Lagrange 方程
        acc_r_part1 = - (self.M * factor) * (dr**2)
        acc_r_part2 = term1 * (dphi**2)
        acc_r_part3 = - (self.M * term1 / (r**3)) * (dt**2)
        
        d2r = acc_r_part1 + acc_r_part2 + acc_r_part3
        
        return [dt, dr, dphi, d2t, d2r, d2phi]

    def shoot_ray(self, start_pos, start_dir, t_len=50):
        """
        發射光線
        Args:
            start_pos: (x, y) 笛卡兒坐標
            start_dir: (vx, vy) 初始方向
        """
        x0, y0 = start_pos
        vx0, vy0 = start_dir
        
        # 1. 坐標轉換 (Cartesian -> Schwarzschild Polar)
        r0 = np.sqrt(x0**2 + y0**2)
        phi0 = np.arctan2(y0, x0)
        
        # 2. 速度轉換 (Cartesian Velocity -> Polar Velocity)
        # v_r = (x v_x + y v_y) / r
        # v_phi = (x v_y - y v_x) / r^2
        dr0 = (x0 * vx0 + y0 * vy0) / r0
        dphi0 = (x0 * vy0 - y0 * vx0) / (r0**2)
        
        # 3. 計算初始 dt (Null Condition: ds^2 = 0)
        # -(1-2M/r)dt^2 + (1-2M/r)^-1 dr^2 + r^2 dphi^2 = 0
        # dt = sqrt( ( (1-2M/r)^-1 dr^2 + r^2 dphi^2 ) / (1-2M/r) )
        g_rr = 1.0 / (1.0 - self.rs / r0)
        metric_factor = 1.0 - self.rs / r0
        
        spatial_part = g_rr * dr0**2 + (r0**2) * dphi0**2
        dt0 = np.sqrt(spatial_part / metric_factor)
        
        # 4. 初始狀態向量
        # [t, r, phi, dt, dr, dphi]
        initial_state = [0, r0, phi0, dt0, dr0, dphi0]
        
        # 5. 數值積分
        # 設一個事件函數來檢測是否掉入黑洞
        def hit_horizon(t, y): return y[1] - self.rs * 1.01
        hit_horizon.terminal = True
        hit_horizon.direction = -1
        
        # 設一個事件函數檢測是否飛太遠 (離開模擬區)
        def escape(t, y): return y[1] - 30.0
        escape.terminal = True
        escape.direction = 1
        
        sol = solve_ivp(self.geodesic_equations, [0, t_len], initial_state, 
                        events=[hit_horizon, escape], rtol=1e-7, atol=1e-9)
        
        return sol

    def visualize_lensing(self, impact_parameters):
        """
        視覺化重力透鏡效應
        impact_parameters: 一系列 y 坐標 (假設光從左邊 x=-15 射入)
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # 1. 繪製黑洞結構
        # 事件視界 (黑色)
        circle_bh = plt.Circle((0, 0), self.rs, color='black', zorder=10, label='Event Horizon')
        ax.add_patch(circle_bh)
        
        # 光子層 (虛線，半徑 3M)
        circle_ph = plt.Circle((0, 0), self.rp, color='orange', fill=False, linestyle='--', label='Photon Sphere')
        ax.add_patch(circle_ph)
        
        print("開始光線追蹤...")
        
        for b in impact_parameters:
            # 初始位置: x = -15, y = b
            # 初始方向: 向右 (1, 0)
            start_pos = [-15, b]
            start_dir = [1, 0]
            
            sol = self.shoot_ray(start_pos, start_dir)
            
            # 轉換回笛卡兒坐標繪圖
            r = sol.y[1]
            phi = sol.y[2]
            x = r * np.cos(phi)
            y = r * np.sin(phi)
            
            # 判斷光線命運
            if r[-1] < self.rs * 1.02:
                # 被捕獲 (掉進黑洞)
                color = 'red'
                alpha = 0.3
            else:
                # 逃逸 (被透鏡偏折)
                color = 'cyan'
                alpha = 0.6
                
            ax.plot(x, y, color=color, alpha=alpha, linewidth=1)

        # 設定圖形屬性
        ax.set_facecolor('black') # 太空背景
        ax.set_xlim(-15, 15)
        ax.set_ylim(-10, 10)
        ax.set_aspect('equal')
        ax.set_title(f"Gravitational Lensing by Schwarzschild Black Hole (M={self.M})")
        ax.set_xlabel("X (Units of M)")
        ax.set_ylabel("Y (Units of M)")
        
        # 加一個圖例說明
        from matplotlib.lines import Line2D
        custom_lines = [Line2D([0], [0], color='cyan', lw=2),
                        Line2D([0], [0], color='red', lw=2),
                        circle_bh, circle_ph]
        ax.legend(custom_lines, ['Scattered Ray', 'Captured Ray', 'Event Horizon (2M)', 'Photon Sphere (3M)'], 
                  loc='upper right')
        
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    # 設定黑洞質量 M=1 (則 rs=2, rp=3)
    tracer = BlackHoleRayTracer(M=1.0)
    
    # 產生一系列撞擊參數 b
    # 密集地測試臨界區域 (b 約為 5.2M 左右是臨界值)
    # b < 5.196 (3*sqrt(3)/2 * rs) 會掉進去
    b_values = np.concatenate([
        np.linspace(0, 4.0, 10),    # 肯定掉進去
        np.linspace(4.1, 6.0, 40),  # 臨界區域 (最有趣的部分)
        np.linspace(6.1, 10.0, 10)  # 輕微偏折
    ])
    
    # 對稱地加上負的 b
    b_all = np.concatenate([b_values, -b_values])
    
    tracer.visualize_lensing(b_all)