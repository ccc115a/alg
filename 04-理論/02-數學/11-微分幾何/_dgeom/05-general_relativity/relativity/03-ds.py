import numpy as np

# 定義常數 (使用 SI 單位，讓結果更具體)
C_LIGHT = 299792458.0  # 光速 c (m/s)

## 函數定義：計算史瓦西時空間隔 ds^2
def schwarzschild_ds_squared(M, r_s, r, dt, dr, dtheta, dphi):
    """
    根據史瓦西度量計算時空間隔 ds^2。

    輸入:
    M: 中心物體的質量 (kg)。
    r_s: 史瓦西半徑 (m)。
    r: 觀測點的徑向座標 (m)。
    dt, dr, dtheta, dphi: 座標的微分量。

    輸出:
    ds_squared: 時空間隔的平方 ds^2 (單位是 m^2 或 s^2 的倍數，取決於常數設定)。
    """
    
    # 確保不會除以零或在 r < r_s 處產生數學錯誤 (僅供範例使用，實際黑洞內需複數)
    if r <= r_s:
        # 在事件視界或內部，此簡單公式會失效或結果為無窮，我們只計算 r > r_s 的區域
        return np.nan 

    # 1. 計算史瓦西度量張量的非零對角分量 (r 的函數)
    
    # g_tt: 時間分量
    g_tt = -(1.0 - r_s / r) * C_LIGHT**2 # 為了得到距離單位，乘上 c^2
    
    # g_rr: 徑向分量
    g_rr = 1.0 / (1.0 - r_s / r)
    
    # g_theta_theta 和 g_phi_phi: 角分量
    g_theta_theta = r**2
    g_phi_phi = r**2 * np.sin(dtheta)**2  # 此處的 sin(dtheta) 應該是 sin(theta)，但在微分中我們用 dtheta。
                                          # 為了簡化，假設在赤道平面 (theta = pi/2, sin(theta) = 1)，且 dtheta=0
    
    # 實際計算中，應將 dtheta 和 dphi 設為 0
    if dtheta != 0 or dphi != 0:
        print("警告: 程式僅在赤道平面 (dθ=dφ=0) 情況下準確。")
        
    # 簡化計算：只考慮徑向運動 (dtheta=0, dphi=0)
    
    # 2. 應用 ds^2 = g_{\mu\nu} dx^{\mu} dx^{\nu} 公式
    ds_squared = (g_tt * dt**2) + (g_rr * dr**2)
    
    return ds_squared

## 範例展示：應用於黑洞 (太陽質量)

# 假設中心物體是太陽 (M_sun = 1.989e30 kg, 但我們只需要 r_s)
# 史瓦西黑洞的 r_s 計算 (為了簡化，我們直接給定 r_s 的值)
# 太陽的史瓦西半徑 r_s 約為 3000 公尺 (3 km)
R_SCHWARZSCHILD = 3000.0 # 3 km

# --- 情境 1: 觀測者靜止在黑洞附近 (r = 6 km) ---
print("--- 情境 1: 靜止觀測者的固有時間 (鐘慢) ---")
R_OBSERVER = 6000.0  # 觀測者距離，為 2 r_s
DT = 1.0  # 觀測者測得的時間流逝 (外部座標時間)
DR, DTHETA, DPHI = 0.0, 0.0, 0.0 # 空間座標不變

ds2_static = schwarzschild_ds_squared(None, R_SCHWARZSCHILD, R_OBSERVER, DT, DR, DTHETA, DPHI)

if not np.isnan(ds2_static):
    # 類時間隔，計算固有時間 dτ = sqrt(-ds^2/c^2)
    # 單位轉換：我們在 g_tt 中乘了 c^2，所以 ds^2 的單位是 m^2。
    # dτ^2 = -ds^2 / c^2 (因為我們在 g_tt 中已經包含了 c^2)
    dtau_squared = -ds2_static / C_LIGHT**2
    dtau = np.sqrt(dtau_squared)
    
    # 鐘慢因子 (重力時間膨脹)
    time_dilation_factor = DT / dtau
    
    print(f"觀測點 r = {R_OBSERVER} m (2 r_s)")
    print(f"時空間隔平方 ds^2 = {ds2_static:.2e} m^2")
    print(f"觀測者的固有時間 dτ = {dtau:.6f} 秒")
    print(f"重力時間膨脹因子 (dt/dτ) = {time_dilation_factor:.6f}")
    # 理論值 (1 - r_s/r)^(-1/2) = (1 - 3000/6000)^(-1/2) = (0.5)^(-1/2) = 1.4142

print("-" * 40)

# --- 情境 2: 光線徑向射出 (ds^2 = 0) ---
print("--- 情境 2: 光線運動 (ds^2 = 0) ---")
R_LIGHT = 10000.0 # 觀測點
DT_LIGHT = 1e-6   # 極短的座標時間
# 光速運動必須滿足 ds^2 = 0。我們計算所需的 dr/dt

# 數學上: ds^2 = 0 => (1 - r_s/r) c^2 dt^2 = (1 - r_s/r)^-1 dr^2
# 徑向速度 dr/dt = c * (1 - r_s/r)
V_RADIAL_LIGHT = C_LIGHT * (1.0 - R_SCHWARZSCHILD / R_LIGHT)
DR_LIGHT = V_RADIAL_LIGHT * DT_LIGHT

ds2_light = schwarzschild_ds_squared(None, R_SCHWARZSCHILD, R_LIGHT, DT_LIGHT, DR_LIGHT, DTHETA, DPHI)

print(f"光線觀測點 r = {R_LIGHT} m")
print(f"光線徑向速度 (dr/dt) = {V_RADIAL_LIGHT:.2e} m/s")
print(f"計算得時空間隔平方 ds^2 = {ds2_light:.2e} m^2") # 預期為 0
if np.abs(ds2_light) < 1e-10:
    print("驗證成功: ds^2 近似為零，這是類光路徑的特徵。")
