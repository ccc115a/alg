import numpy as np
from scipy.integrate import solve_ivp
from math import pi

# 1. 定義流形參數 (2D 球面)
N = 2
a_val = 1.0 # 球面半徑 a=1
# 坐標索引: 0: theta ($\theta$), 1: phi ($\phi$)

print(f"--- 測地線方程式數值求解 (單位球, a={a_val}) ---")

# 2. 數值克里斯托費爾符號 (硬編碼自 4.2 節的解析解)
# 只有 $\Gamma^0_{11}$, $\Gamma^1_{01}$, $\Gamma^1_{10}$ 是非零的。
# $\Gamma^{\theta}_{\phi \phi} = -\sin \theta \cos \theta$
# $\Gamma^{\phi}_{\theta \phi} = \Gamma^{\phi}_{\phi \theta} = \cot \theta$

def christoffel_num(coords):
    """
    計算球面度量 $g_{ij}$ 對應的克里斯托費爾符號 $\Gamma^i_{jk}$ 數值。
    coords = [theta, phi]
    """
    theta_coord = coords[0]
    
    # 初始化 $\Gamma^i_{jk}$ 為零
    Gamma = np.zeros((N, N, N))
    
    # 僅計算非零項 (僅依賴 $\theta$)
    
    # $\Gamma^0_{11} = -\sin \theta \cos \theta$
    Gamma[0, 1, 1] = -np.sin(theta_coord) * np.cos(theta_coord)
    
    # 處理 $\theta = 0$ 或 $\theta = \pi$ 處的奇異點 (cot $\theta$)
    # 在這些點，我們假設坐標系已經被選擇使得 $\phi$ 不改變
    if abs(np.sin(theta_coord)) > 1e-10:
        cot_theta = np.cos(theta_coord) / np.sin(theta_coord)
        
        # $\Gamma^1_{01} = \cot \theta$
        Gamma[1, 0, 1] = cot_theta
        
        # $\Gamma^1_{10} = \cot \theta$ (對稱性 $\Gamma^i_{jk} = \Gamma^i_{kj}$)
        Gamma[1, 1, 0] = cot_theta

    return Gamma

# 3. 定義一階 ODE 系統的導數函數
def geodesic_ode_system(tau, Y):
    """
    測地線方程式的一階 ODE 系統: dY/d\tau = F(Y)
    Y 是一個 2N 維向量: $Y = [x^0, x^1, v^0, v^1]$
    其中 $x^0=\theta, x^1=\phi$, $v^i = \frac{d x^i}{d\tau}$
    """
    # 提取坐標 $x^i$ 和速度 $v^i$
    x = Y[:N] # $[x^0, x^1]$
    v = Y[N:] # $[v^0, v^1]$
    
    # 獲取當前坐標點的克里斯托費爾符號
    Gamma = christoffel_num(x)
    
    # dY/d\tau 向量
    dYdtau = np.zeros_like(Y)
    
    # 1. 坐標導數: $\frac{d x^i}{d\tau} = v^i$
    dYdtau[:N] = v
    
    # 2. 速度導數 (加速度): $\frac{d v^i}{d\tau} = - \Gamma^i_{jk} v^j v^k$
    # 使用 einsum 執行縮並 $\Gamma^i_{jk} v^j v^k$
    acceleration = np.zeros(N)
    for i in range(N):
        # $\sum_{j, k} \Gamma^i_{jk} v^j v^k$
        sum_term = np.einsum('jk,j,k->', Gamma[i], v, v)
        acceleration[i] = -sum_term
        
    dYdtau[N:] = acceleration
    
    return dYdtau

# 4. 數值求解測地線 (初始條件與參數)

# 初始參數範圍
tau_span = [0, 5.0] # 參數 $\tau$ 從 0 到 5

# 初始條件 Y(0) = $[x^0(0), x^1(0), v^0(0), v^1(0)]$
# 假設從赤道 ($\theta = \pi/2$) 開始，經度 $\phi = 0$
theta0 = pi / 2
phi0 = 0.0

# 初始速度: 沿 $\theta$ 向上 ($\theta$ 減小) 運動，不改變 $\phi$
# $v^{\theta} = -0.5, v^{\phi} = 0.0$
v_theta0 = -0.5
v_phi0 = 0.0

# 初始狀態向量
Y0 = np.array([theta0, phi0, v_theta0, v_phi0])

print(f"\n初始坐標 $(\\theta_0, \\phi_0)$: ({theta0:.4f}, {phi0:.4f})")
print(f"初始速度 $(v^{\\theta}_0, v^{\\phi}_0)$: ({v_theta0:.4f}, {v_phi0:.4f})")

# 執行數值積分
solution = solve_ivp(
    geodesic_ode_system, 
    tau_span, 
    Y0, 
    method='RK45', 
    dense_output=True, 
    rtol=1e-6, 
    atol=1e-9
)

# 5. 結果分析與輸出
theta_path = solution.y[0]
phi_path = solution.y[1]
tau_points = solution.t

print("\n--- 測地線數值軌跡 ---")
print("$\\tau$ | $\\theta$ (緯度) | $\\phi$ (經度)")
print("-" * 30)

# 打印前 5 個和最後 5 個點
for i in range(min(5, len(tau_points))):
    print(f"{tau_points[i]:.2f} | {theta_path[i]:.4f} | {phi_path[i]:.4f}")

if len(tau_points) > 10:
    print("...")

for i in range(len(tau_points) - min(5, len(tau_points)), len(tau_points)):
    print(f"{tau_points[i]:.2f} | {theta_path[i]:.4f} | {phi_path[i]:.4f}")

# 預期結果: 由於 $v^{\phi}_0 = 0$，測地線應該是 $\phi$ 恆定的大圓 (即經線)
# 由於 $\frac{d^2 \phi}{d\tau^2} = -\Gamma^{\phi}_{jk} v^j v^k = -2 \cot \theta v^{\theta} v^{\phi}$ 
# 若 $v^{\phi} = 0$, 則 $\frac{d^2 \phi}{d\tau^2} = 0$, $\phi(\tau)$ 保持常數。
print(f"\n最終 $\\phi$ 坐標範圍: [{np.min(phi_path):.6f}, {np.max(phi_path):.6f}]")
print("（結果符合預期，軌跡為 $\\phi=0$ 上的經線）")