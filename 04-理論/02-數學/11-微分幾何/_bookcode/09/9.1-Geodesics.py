import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from mpl_toolkits.mplot3d import Axes3D

class RiemannianAutoPilot:
    def __init__(self, coords, metric_matrix):
        """
        初始化黎曼幾何導航系統。
        
        Args:
            coords: 坐標變數列表 (如 [theta, phi])
            metric_matrix: 度量張量 g_ij (SymPy Matrix)
        """
        self.coords = coords
        self.dim = len(coords)
        self.g = metric_matrix
        self.g_inv = self.g.inv() # 逆度量 g^ij
        
        print(f"--- 初始化黎曼流形 (Dim={self.dim}) ---")
        print("計算克里斯托費爾符號 (Christoffel Symbols)...")
        self.Gamma = self._compute_christoffel()
        
        print("生成測地線演化函數 (Geodesic Evolution Functions)...")
        self.evolution_func = self._generate_numeric_func()

    def _compute_christoffel(self):
        """
        符號計算: Γ^k_ij
        """
        # 初始化 3D 陣列 (列表的列表的列表)
        Gamma = [[[sp.Integer(0) for _ in range(self.dim)] 
                  for _ in range(self.dim)] 
                 for _ in range(self.dim)]
        
        # 遍歷所有指標 k, i, j
        for k in range(self.dim):
            for i in range(self.dim):
                for j in range(self.dim):
                    sum_term = sp.Integer(0)
                    # 對指標 m 求和
                    for m in range(self.dim):
                        # 公式: 1/2 * g^km * (dg_mj/dx^i + dg_im/dx^j - dg_ij/dx^m)
                        term = 0.5 * self.g_inv[k, m] * (
                            self.g[m, j].diff(self.coords[i]) +
                            self.g[i, m].diff(self.coords[j]) -
                            self.g[i, j].diff(self.coords[m])
                        )
                        sum_term += term
                    
                    Gamma[k][i][j] = sp.simplify(sum_term)
                    
                    # 若非零，印出來看看
                    if Gamma[k][i][j] != 0:
                        print(f"  Γ^{self.coords[k]}_{self.coords[i]}{self.coords[j]} = {Gamma[k][i][j]}")
        
        return Gamma

    def _generate_numeric_func(self):
        """
        將符號表達式轉換為可供 scipy.solve_ivp 使用的 Python 函數。
        目標: y' = f(t, y)
        狀態向量 y = [x^0, x^1, ..., v^0, v^1, ...]
        """
        # 定義符號變數：位置 x 和 速度 v
        x_sym = sp.symbols(f'x:{self.dim}') # x0, x1, ...
        v_sym = sp.symbols(f'v:{self.dim}') # v0, v1, ...
        
        # 構建加速度表達式 a^k = -Γ^k_ij * v^i * v^j
        acc_exprs = []
        for k in range(self.dim):
            acc_k = sp.Integer(0)
            for i in range(self.dim):
                for j in range(self.dim):
                    # 注意: 我們需要將 Gamma 中的坐標符號替換為通用的 x_sym
                    # 因為 Gamma 裡面存的是 theta, phi，但這裡我們用 x0, x1
                    gamma_val = self.Gamma[k][i][j]
                    # 替換坐標變數
                    subs_dict = {self.coords[d]: x_sym[d] for d in range(self.dim)}
                    gamma_val = gamma_val.subs(subs_dict)
                    
                    acc_k -= gamma_val * v_sym[i] * v_sym[j]
            acc_exprs.append(acc_k)
            
        # 現在我們有完整的導數列表: [v0, v1, a0, a1]
        derivs = list(v_sym) + acc_exprs
        
        # 使用 lambdify 編譯成快速函數
        # 輸入參數展開為: (x0, x1, v0, v1)
        args = list(x_sym) + list(v_sym)
        func_fast = sp.lambdify(args, derivs, modules='numpy')
        
        def ode_system(t, y):
            # y 是一個陣列，我們需要把它拆開傳給 func_fast
            return func_fast(*y)
            
        return ode_system

    def solve_geodesic(self, start_pos, start_vel, t_span, steps=500):
        """
        求解測地線。
        """
        y0 = list(start_pos) + list(start_vel)
        t_eval = np.linspace(t_span[0], t_span[1], steps)
        
        sol = solve_ivp(self.evolution_func, t_span, y0, t_eval=t_eval, rtol=1e-8)
        return sol

# ==========================================
# 實作案例：球面幾何 (S^2)
# ==========================================

def run_sphere_geodesic():
    # 1. 定義度量
    print("\n>>> 設定流形：單位球面 S^2 <<<")
    theta, phi = sp.symbols('theta phi', real=True)
    # 球坐標度量: diag(1, sin^2(theta))
    # 注意: theta 是極角 (0~pi), phi 是方位角
    metric = sp.Matrix([
        [1, 0],
        [0, sp.sin(theta)**2]
    ])
    
    # 2. 初始化導航系統
    autopilot = RiemannianAutoPilot([theta, phi], metric)
    
    # 3. 設定初始條件
    # 從赤道 (theta=pi/2, phi=0) 出發
    # 初始速度: 向東北方發射 (d_theta < 0 為向北, d_phi > 0 為向東)
    # 注意: 在球面上，phi 方向的實際速度 v_phi 需要乘上 sin(theta) 才是物理速度
    start_pos = [np.pi/2, 0.0]
    start_vel = [-0.5, 1.0] 
    
    print(f"\n[模擬開始]")
    print(f"  起點: (θ={start_pos[0]:.2f}, φ={start_pos[1]:.2f})")
    print(f"  初速: (v_θ={start_vel[0]:.2f}, v_φ={start_vel[1]:.2f})")
    
    # 4. 求解 ODE
    # 模擬足夠長的時間，看能不能繞一圈回來
    sol = autopilot.solve_geodesic(start_pos, start_vel, t_span=(0, 15))
    
    # 提取結果
    theta_traj = sol.y[0]
    phi_traj = sol.y[1]
    
    # 5. 視覺化 (轉回 3D 笛卡兒坐標繪圖)
    print("正在繪製 3D 軌跡...")
    
    # 球面參數化 (用於畫球體)
    u = np.linspace(0, 2 * np.pi, 50)
    v = np.linspace(0, np.pi, 50)
    x_sphere = np.outer(np.cos(u), np.sin(v))
    y_sphere = np.outer(np.sin(u), np.sin(v))
    z_sphere = np.outer(np.ones(np.size(u)), np.cos(v))

    # 軌跡參數化
    x_path = np.sin(theta_traj) * np.cos(phi_traj)
    y_path = np.sin(theta_traj) * np.sin(phi_traj)
    z_path = np.cos(theta_traj)

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # 畫球
    ax.plot_wireframe(x_sphere, y_sphere, z_sphere, color='gray', alpha=0.1)
    
    # 畫軌跡
    ax.plot(x_path, y_path, z_path, 'r-', linewidth=2, label='Geodesic')
    
    # 標示起點
    ax.scatter([x_path[0]], [y_path[0]], [z_path[0]], color='blue', s=50, label='Start')
    
    ax.set_title("Geodesic Simulation on Sphere")
    ax.legend()
    
    # 保持比例
    ax.set_box_aspect([1,1,1])
    plt.show()

if __name__ == "__main__":
    run_sphere_geodesic()
