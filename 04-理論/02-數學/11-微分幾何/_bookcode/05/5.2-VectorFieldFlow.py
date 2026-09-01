import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

class VectorFieldFlow:
    def __init__(self, vector_field_func):
        """
        初始化向量場流分析器
        Args:
            vector_field_func: 函數 f(t, y) -> [u, v]
        """
        self.field = vector_field_func

    def solve_trajectory(self, start_point, t_span, t_eval=None):
        """計算單條積分曲線"""
        sol = solve_ivp(self.field, t_span, start_point, t_eval=t_eval, rtol=1e-6)
        return sol.y

    def evolve_shape(self, initial_shape, t_end, steps=50):
        """
        演化一個形狀（點的集合）。
        這展示了流形上的區域變換 Φ_t(U)
        """
        transformed_shapes = []
        t_eval = np.linspace(0, t_end, steps)
        
        # initial_shape 形狀為 (2, N)
        num_points = initial_shape.shape[1]
        
        # 儲存每個時間點的形狀
        # 我們需要對形狀上的每個點單獨求解 ODE
        # 為了效率，這部分可以向量化，但為了清晰，我們用迴圈
        all_trajectories = []
        
        for i in range(num_points):
            start = initial_shape[:, i]
            traj = self.solve_trajectory(start, (0, t_end), t_eval)
            all_trajectories.append(traj)
            
        return t_eval, np.array(all_trajectories)

# ==========================================
# 定義向量場
# ==========================================

def complex_flow_field(t, state):
    x, y = state
    # 定義一個非線性場：包含渦旋與鞍點
    # dx/dt = sin(y)
    # dy/dt = cos(x)
    # 這是 Hamiltonian 系統 H = -cos(y) - sin(x) 的流
    u = np.sin(y)
    v = np.cos(x) 
    return [u, v]

def run_flow_demo():
    print("--- 專案 5.2: 向量場的流 (Geometric Flow) ---")
    
    flow_solver = VectorFieldFlow(complex_flow_field)
    
    # 1. 準備繪圖背景 (流線圖)
    x = np.linspace(-5, 5, 20)
    y = np.linspace(-5, 5, 20)
    X, Y = np.meshgrid(x, y)
    # 計算網格上的向量
    # 注意: streamplot 需要 grid 形式的 u, v
    U = np.zeros_like(X)
    V = np.zeros_like(Y)
    for i in range(len(x)):
        for j in range(len(y)):
            vec = complex_flow_field(0, [X[i,j], Y[i,j]])
            U[i,j] = vec[0]
            V[i,j] = vec[1]
            
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # 繪製背景流線 (灰色)
    st = ax.streamplot(X, Y, U, V, color='lightgray', density=1.5, linewidth=1)
    
    # 2. 模擬積分曲線 (粒子軌跡)
    # 選幾個隨機起始點
    start_points = [
        [0.1, 0.1],   # 在中心附近
        [2.0, 2.0],   # 另一個區域
        [-1.5, 1.5],  # 鞍點附近
        [0.0, 3.14]   # 特殊點
    ]
    
    colors = ['r', 'g', 'b', 'orange']
    t_max = 10
    
    print(f"計算 {len(start_points)} 條積分曲線...")
    for idx, p0 in enumerate(start_points):
        # 求解 ODE
        traj = flow_solver.solve_trajectory(p0, (0, t_max), t_eval=np.linspace(0, t_max, 200))
        
        # 繪製軌跡
        ax.plot(traj[0], traj[1], color=colors[idx], linewidth=2, label=f'Path {idx+1}')
        # 標示起點
        ax.plot(p0[0], p0[1], 'o', color=colors[idx])
        # 標示終點 (箭頭)
        ax.arrow(traj[0, -2], traj[1, -2], 
                 traj[0, -1] - traj[0, -2], traj[1, -1] - traj[1, -2], 
                 head_width=0.2, color=colors[idx])

    # 3. 幾何變形演示 (Evolution of a Circle)
    # 這展示了流形上的 "Lie Dragging"
    print("計算幾何形狀變形 (Circle Evolution)...")
    
    # 定義一個小圓
    theta = np.linspace(0, 2*np.pi, 30)
    center = np.array([-1.5, -1.5]) # 選一個有趣的區域
    radius = 0.4
    circle_x = center[0] + radius * np.cos(theta)
    circle_y = center[1] + radius * np.sin(theta)
    initial_shape = np.vstack([circle_x, circle_y])
    
    # 演化形狀
    t_eval, evolved_data = flow_solver.evolve_shape(initial_shape, t_end=4.0, steps=5)
    
    # 繪製演化過程中的形狀
    # evolved_data shape: (num_points, 2, time_steps)
    # 我們需要轉置一下方便取用
    
    num_steps = len(t_eval)
    # 使用漸層色繪製圓圈的變形
    circle_colors = plt.cm.viridis(np.linspace(0, 1, num_steps))
    
    for t_idx in range(num_steps):
        # 取出該時間點的所有點座標
        shape_at_t_x = evolved_data[:, 0, t_idx]
        shape_at_t_y = evolved_data[:, 1, t_idx]
        
        # 封閉圖形
        shape_at_t_x = np.append(shape_at_t_x, shape_at_t_x[0])
        shape_at_t_y = np.append(shape_at_t_y, shape_at_t_y[0])
        
        label = 'Evolving Volume' if t_idx == 0 else None
        ax.plot(shape_at_t_x, shape_at_t_y, '-', color=circle_colors[t_idx], alpha=0.8, linewidth=2)
        
        # 填色 (只填開始和結束)
        if t_idx == 0:
            ax.fill(shape_at_t_x, shape_at_t_y, color=circle_colors[t_idx], alpha=0.3)
            ax.text(center[0], center[1]-0.6, "t=0", color=circle_colors[t_idx], fontweight='bold')
        elif t_idx == num_steps - 1:
            ax.fill(shape_at_t_x, shape_at_t_y, color=circle_colors[t_idx], alpha=0.5)
            # 計算質心以便標示
            mean_x, mean_y = np.mean(shape_at_t_x), np.mean(shape_at_t_y)
            ax.text(mean_x, mean_y-0.6, f"t={t_eval[-1]:.1f}", color=circle_colors[t_idx], fontweight='bold')

    ax.set_title("Flow of Vector Field: $\dot{x}=\sin(y), \dot{y}=\cos(x)$")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_xlim(-5, 5)
    ax.set_ylim(-5, 5)
    ax.set_aspect('equal')
    ax.grid(True, linestyle=':')
    ax.legend(loc='upper right')
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    run_flow_demo()