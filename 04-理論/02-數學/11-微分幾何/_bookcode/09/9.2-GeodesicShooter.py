import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from mpl_toolkits.mplot3d import Axes3D

class GeodesicShooter:
    def __init__(self, name, coords, metric, embedding_func):
        """
        初始化射擊遊戲引擎。
        
        Args:
            name (str): 曲面名稱
            coords (list): 符號變數列表 [u, v]
            metric (Matrix): 2x2 度量張量 g_ij
            embedding_func (callable): 將 (u, v) 映射到 (x, y, z) 的函數，用於繪圖
        """
        self.name = name
        self.coords = coords
        self.g = metric
        self.embedding_func = embedding_func
        self.dim = len(coords)
        
        print(f"--- 初始化引擎: {self.name} ---")
        print("1. 符號推導: 計算克里斯托費爾符號與測地線方程...")
        self.acc_funcs = self._derive_equations()
        print("2. 引擎就緒。")

    def _derive_equations(self):
        """
        使用 SymPy 自動推導加速度方程: a^k = - Γ^k_ij * v^i * v^j
        返回: 可快速執行的 Python 函數列表
        """
        g_inv = self.g.inv()
        
        # 定義速度符號
        vel_syms = sp.symbols(f'v:{self.dim}') # v0, v1
        
        acc_exprs = []
        
        # 計算 Γ^k_ij 並直接組合成加速度表達式
        for k in range(self.dim):
            acc_k = sp.Integer(0)
            for i in range(self.dim):
                for j in range(self.dim):
                    # Γ^k_ij 公式
                    gamma_term = sp.Integer(0)
                    for l in range(self.dim):
                        gamma_term += 0.5 * g_inv[k, l] * (
                            self.g[l, j].diff(self.coords[i]) +
                            self.g[i, l].diff(self.coords[j]) -
                            self.g[i, j].diff(self.coords[l])
                        )
                    
                    # 累加到加速度: -Γ * v^i * v^j
                    acc_k -= gamma_term * vel_syms[i] * vel_syms[j]
            
            acc_exprs.append(sp.simplify(acc_k))
        
        # 將符號表達式編譯成 NumPy 函數
        # 輸入參數順序: (u, v, du, dv)
        args = list(self.coords) + list(vel_syms)
        fast_funcs = [sp.lambdify(args, expr, modules='numpy') for expr in acc_exprs]
        
        return fast_funcs

    def shoot(self, start_uv, start_vel, t_span=(0, 20), steps=1000):
        """
        發射粒子！
        Args:
            start_uv: 起始坐標 [u0, v0]
            start_vel: 初始速度 [du0, dv0]
            t_span: 時間範圍
        """
        # 定義 ODE 系統: dy/dt = f(t, y)
        # y = [u, v, du, dv]
        def ode_system(t, state):
            u, v, du, dv = state
            
            # 計算加速度 (二階導數)
            # 注意: 如果分母為零 (如球面的極點)，這裡會報錯，需避開奇異點
            d2u = self.acc_funcs[0](u, v, du, dv)
            d2v = self.acc_funcs[1](u, v, du, dv)
            
            return [du, dv, d2u, d2v]
        
        y0 = list(start_uv) + list(start_vel)
        t_eval = np.linspace(t_span[0], t_span[1], steps)
        
        print(f"正在模擬軌跡 (t={t_span})...")
        sol = solve_ivp(ode_system, t_span, y0, t_eval=t_eval, rtol=1e-6)
        return sol

    def visualize(self, solutions, grid_range):
        """
        3D 視覺化
        Args:
            solutions: 軌跡列表 (由 shoot 返回的 sol 物件)
            grid_range: [[u_min, u_max], [v_min, v_max]]
        """
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        # 1. 繪製曲面網格 (Wireframe)
        u_vals = np.linspace(grid_range[0][0], grid_range[0][1], 40)
        v_vals = np.linspace(grid_range[1][0], grid_range[1][1], 40)
        U, V = np.meshgrid(u_vals, v_vals)
        
        # 使用 embedding_func 將 UV 轉為 XYZ
        X, Y, Z = self.embedding_func(U, V)
        
        ax.plot_surface(X, Y, Z, color='whitesmoke', alpha=0.6, edgecolor='lightgray')
        
        # 2. 繪製所有軌跡
        colors = ['r', 'b', 'g', 'm', 'orange']
        
        for idx, sol in enumerate(solutions):
            u_traj = sol.y[0]
            v_traj = sol.y[1]
            
            # 將軌跡轉為 3D 坐標
            traj_X, traj_Y, traj_Z = self.embedding_func(u_traj, v_traj)
            
            c = colors[idx % len(colors)]
            ax.plot(traj_X, traj_Y, traj_Z, color=c, linewidth=2, label=f'Shot {idx+1}')
            
            # 標示起點
            ax.scatter([traj_X[0]], [traj_Y[0]], [traj_Z[0]], color=c, s=50)
            
            # 標示終點箭頭
            ax.text(traj_X[-1], traj_Y[-1], traj_Z[-1], f"End", fontsize=8)

        ax.set_title(f"Geodesic Shooter on {self.name}")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        
        # 調整比例
        max_range = np.array([X.max()-X.min(), Y.max()-Y.min(), Z.max()-Z.min()]).max() / 2.0
        mid_x = (X.max()+X.min()) * 0.5
        mid_y = (Y.max()+Y.min()) * 0.5
        mid_z = (Z.max()+Z.min()) * 0.5
        ax.set_xlim(mid_x - max_range, mid_x + max_range)
        ax.set_ylim(mid_y - max_range, mid_y + max_range)
        ax.set_zlim(mid_z - max_range, mid_z + max_range)
        
        plt.legend()
        plt.show()

# ==========================================
# 關卡 1: 球面 (Sphere)
# ==========================================
def level_1_sphere():
    # 定義符號: theta (極角), phi (方位角)
    theta, phi = sp.symbols('theta phi', real=True)
    
    # 度量: diag(1, sin^2(theta))  (半徑 R=1)
    metric = sp.Matrix([
        [1, 0],
        [0, sp.sin(theta)**2]
    ])
    
    # 嵌入函數 (Spherical -> Cartesian)
    def sphere_embedding(th, ph):
        x = np.sin(th) * np.cos(ph)
        y = np.sin(th) * np.sin(ph)
        z = np.cos(th)
        return x, y, z
    
    game = GeodesicShooter("Unit Sphere", [theta, phi], metric, sphere_embedding)
    
    # 發射！
    # 避開 theta=0 (北極) 以免分母為零
    # 從赤道 (pi/2) 發射
    shots = []
    
    # Shot 1: 沿赤道發射 (向東) -> 應該是大圓
    shots.append(game.shoot(start_uv=[np.pi/2, 0], start_vel=[0, 1.0], t_span=(0, 7)))
    
    # Shot 2: 向東北方 45度發射 -> 應該也是大圓，但傾斜
    shots.append(game.shoot(start_uv=[np.pi/2, 0], start_vel=[-0.5, 0.5], t_span=(0, 7)))
    
    # 視覺化
    # theta 範圍 0.1~pi-0.1, phi 範圍 0~2pi
    game.visualize(shots, [[0.1, np.pi-0.1], [0, 2*np.pi]])

# ==========================================
# 關卡 2: 環面 (Torus) - 最好玩的部分
# ==========================================
def level_2_torus():
    # 定義符號
    u, v = sp.symbols('u v', real=True)
    # R: 主半徑, r: 管半徑
    R, r = 3.0, 1.0
    
    # 度量: diag((R+r cos v)^2, r^2)
    # 這裡直接代入數值 R=3, r=1 以簡化計算
    metric = sp.Matrix([
        [(R + r*sp.cos(v))**2, 0],
        [0, r**2]
    ])
    
    # 嵌入函數
    def torus_embedding(u_val, v_val):
        x = (R + r*np.cos(v_val)) * np.cos(u_val)
        y = (R + r*np.cos(v_val)) * np.sin(u_val)
        z = r * np.sin(v_val)
        return x, y, z
    
    game = GeodesicShooter("Torus (R=3, r=1)", [u, v], metric, torus_embedding)
    
    shots = []
    
    # Shot 1: 外側赤道 (v=0)，沿著大圓方向發射
    # 這是測地線嗎？是的，因為它是對稱軸。
    shots.append(game.shoot(start_uv=[0, 0], start_vel=[0.5, 0], t_span=(0, 15)))
    
    # Shot 2: 準週期軌道 (Quasi-periodic)
    # 給它一個斜率。它會在環面上繞來繞去，看起來像是在繞線圈。
    # 初始位置: 外側
    # 速度: u方向(繞大圈)快，v方向(繞管子)慢
    shots.append(game.shoot(start_uv=[0, 0], start_vel=[0.8, 1.5], t_span=(0, 40)))
    
    # Shot 3: 內側不穩定軌道
    # 在內側 (v=pi) 發射。幾何上這像馬鞍面。
    # 如果完全沿著赤道是穩定的，但稍微偏一點就會發散震盪。
    shots.append(game.shoot(start_uv=[0, np.pi], start_vel=[0.5, 0.1], t_span=(0, 20)))
    
    # 視覺化
    game.visualize(shots, [[0, 2*np.pi], [0, 2*np.pi]])

if __name__ == "__main__":
    print("=== 選擇關卡 ===")
    print("1. 球面 (驗證大圓)")
    print("2. 環面 (觀察複雜軌道)")
    # 這裡我們先執行環面，因為它比較有趣
    level_2_torus() 
    # 若要執行球面，請註解掉上面，改跑 level_1_sphere()