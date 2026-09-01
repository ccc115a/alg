import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

# 確保中文字體能夠正確顯示
plt.rcParams['font.sans-serif'] = ['Noto Sans CJK TC']
plt.rcParams['axes.unicode_minus'] = False

def geodesic_equation_polar(t, y):
    """
    歐幾里得平面在極座標 (r, theta) 下的測地線微分方程系統。
    這是一個將兩個二階 ODEs 轉換成的四個一階 ODEs 系統。
    
    y 向量結構:
    y[0] = r (徑向座標)
    y[1] = theta (角座標)
    y[2] = r_dot (r 的一階導數, dr/dt)
    y[3] = theta_dot (theta 的一階導數, d(theta)/dt)
    
    返回值 dydt 向量結構:
    dydt[0] = dr/dt = r_dot
    dydt[1] = d(theta)/dt = theta_dot
    dydt[2] = d(r_dot)/dt = d^2 r / dt^2 = r * (theta_dot)^2  (來自 Christoffel 項 -Gamma^r_theta_theta * (theta_dot)^2)
    dydt[3] = d(theta_dot)/dt = d^2 theta / dt^2 = - (2/r) * r_dot * theta_dot (來自 Christoffel 項 -2 * Gamma^theta_r_theta * r_dot * theta_dot)
    """
    
    # 提取當前狀態變數
    r = y[0]
    theta = y[1]
    r_dot = y[2]
    theta_dot = y[3]
    
    # 防止 r 接近零時出現數值不穩定或除以零，雖然物理上 r=0 是奇異點。
    if r < 1e-6:
        # 在原點處，我們期望所有加速度都為零 (直線運動)
        r_double_dot = 0.0
        theta_double_dot = 0.0
    else:
        # 計算二階導數 (加速度項)
        
        # 測地線方程 k=r: d^2 r / dt^2 = - Gamma^r_theta_theta * (d(theta)/dt)^2
        # 其中 Gamma^r_theta_theta = -r
        r_double_dot = -(-r) * (theta_dot**2)
        
        # 測地線方程 k=theta: d^2 theta / dt^2 = - 2 * Gamma^theta_r_theta * (dr/dt) * (d(theta)/dt)
        # 其中 Gamma^theta_r_theta = 1/r
        theta_double_dot = -2 * (1.0 / r) * r_dot * theta_dot
        
    # 組裝導數向量
    dydt = [r_dot, theta_dot, r_double_dot, theta_double_dot]
    
    return dydt

# --- 數值求解參數設定 ---

# 1. 初始條件 (t=0)
r0 = 1.0  # 初始徑向位置 (r)
theta0 = 0.0 # 初始角位置 (theta)

# 初始速度向量 (dr/dt, d(theta)/dt)
# 為了讓初始速度大小為 1 (單位速度測地線), 我們選擇一個初始切向角 alpha
alpha = np.pi / 4 # 45度角
r_dot0 = np.cos(alpha) # 初始 dr/dt
theta_dot0 = np.sin(alpha) / r0 # 初始 d(theta)/dt (需除以 r0 確保速度大小正確)

# 初始狀態向量 y0 = [r, theta, r_dot, theta_dot]
y0 = [r0, theta0, r_dot0, theta_dot0]

# 2. 時間範圍 (t 從 0 到 T)
T = 5.0
t_span = (0, T)
t_points = np.linspace(0, T, 100) # 100 個時間點用於輸出

# 3. 數值求解
print("開始數值求解測地線...")
solution = solve_ivp(
    geodesic_equation_polar,
    t_span,
    y0,
    t_eval=t_points,
    method='RK45' # 使用經典的 Runge-Kutta 方法
)

if solution.success:
    print("求解成功。")
    
    # 4. 結果提取與轉換 (極座標 -> 笛卡爾座標)
    r_sol = solution.y[0, :]
    theta_sol = solution.y[1, :]
    
    # 轉換為笛卡爾座標 (X = r cos(theta), Y = r sin(theta))
    x_sol = r_sol * np.cos(theta_sol)
    y_sol = r_sol * np.sin(theta_sol)

    # 5. 繪圖
    plt.figure(figsize=(8, 8))
    
    # 繪製測地線路徑
    plt.plot(x_sol, y_sol, label='計算出的測地線 (極座標方程求解)')
    
    # 標記起點和終點
    plt.plot(x_sol[0], y_sol[0], 'go', label='起點 (t=0)')
    plt.plot(x_sol[-1], y_sol[-1], 'ro', label='終點 (t=T)')
    
    # 繪製理論上的直線 (歐幾里得平面上的測地線應該是直線)
    # 起點 (x0, y0)
    x0_cart = r0 * np.cos(theta0)
    y0_cart = r0 * np.sin(theta0)
    
    # 初始速度向量在笛卡爾座標中的分量
    # x_dot = dr/dt * cos(theta) - r * d(theta)/dt * sin(theta)
    # y_dot = dr/dt * sin(theta) + r * d(theta)/dt * cos(theta)
    x_dot_0 = r_dot0 * np.cos(theta0) - r0 * theta_dot0 * np.sin(theta0)
    y_dot_0 = r_dot0 * np.sin(theta0) + r0 * theta_dot0 * np.cos(theta0)
    
    # 理論直線: (x0 + x_dot_0 * t, y0 + y_dot_0 * t)
    x_line = x0_cart + x_dot_0 * t_points
    y_line = y0_cart + y_dot_0 * t_points
    
    plt.plot(x_line, y_line, 'k--', alpha=0.5, label='理論直線路徑')
    
    plt.title('歐幾里得平面在極座標下的測地線數值求解')
    plt.xlabel('X 座標')
    plt.ylabel('Y 座標')
    plt.axis('equal') # 確保X, Y軸比例一致
    plt.grid(True)
    plt.legend()
    plt.show()

else:
    print(f"求解失敗：{solution.message}")