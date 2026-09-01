import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

# 定義常數 (使用簡化的天文單位)
G = 4 * np.pi**2  # 萬有引力常數，單位為 AU^3 yr^-2 M_sun^-1
M_sun = 1.0       # 太陽質量，單位為 M_sun

# 定義微分方程組
def orbital_ode(t, z):
    """
    z 是狀態向量 [x, y, vx, vy]
    返回 [dx/dt, dy/dt, dvx/dt, dvy/dt]
    """
    x, y, vx, vy = z
    
    r_cubed = (x**2 + y**2)**1.5
    
    # 計算 x 和 y 方向的加速度
    ax = -G * M_sun * x / r_cubed
    ay = -G * M_sun * y / r_cubed
    
    return [vx, vy, ax, ay]

# 設定初始條件 (模擬地球軌道)
# 初始位置：x = 1 AU, y = 0
# 初始速度：vx = 0, vy = 2*pi AU/yr (約為地球公轉速度)
z0 = [1.0, 0.0, 0.0, 2 * np.pi]

# 模擬時間跨度
t_span = (0, 1.0)  # 模擬一年

# 使用 solve_ivp 求解
solution = solve_ivp(
    orbital_ode, 
    t_span, 
    z0, 
    dense_output=True,
    # 設置最大步長，確保軌道平滑
    max_step=0.01
)

# 生成繪圖用的時間點
t_eval = np.linspace(t_span[0], t_span[1], 1000)
# 獲取對應的解
z_sol = solution.sol(t_eval)

# 提取 x 和 y 座標
x_orbit = z_sol[0]
y_orbit = z_sol[1]

# 繪製軌道
plt.figure(figsize=(8, 8))
plt.plot(x_orbit, y_orbit, label='行星軌道')
plt.plot(0, 0, 'o', color='gold', markersize=10, label='太陽')
plt.xlabel('x (AU)')
plt.ylabel('y (AU)')
plt.title('行星軌道模擬 (橢圓軌道)')
plt.grid(True)
plt.axis('equal') # 確保 x-y 軸比例一致，使圓形看起來像圓形
plt.legend()
plt.show()

# 檢查軌道是否為封閉曲線
# 比較起始點和結束點的距離
final_distance_from_start = np.sqrt((x_orbit[-1] - x_orbit[0])**2 + (y_orbit[-1] - y_orbit[0])**2)
print(f"軌道結束點與起始點的距離: {final_distance_from_start:.4f} AU")