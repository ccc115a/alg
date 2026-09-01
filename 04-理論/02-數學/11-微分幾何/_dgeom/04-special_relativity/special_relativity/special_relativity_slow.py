import numpy as np

# 定義光速 C
C = 299792458.0  # 光速 (米/秒)

def lorentz_factor(v: float, c: float = C) -> float:
    """
    計算勞侖茲因子 gamma。
    
    參數:
    v (float): 相對速度 (米/秒)。
    c (float): 光速 (米/秒)。
    
    回傳:
    float: 勞侖茲因子 gamma。
    """
    beta = v / c
    if abs(beta) >= 1:
        # 檢查相對速度是否達到或超過光速
        raise ValueError("相對速度 v 必須嚴格小於光速 c。")
        
    # 計算 gamma = 1 / sqrt(1 - beta^2)
    gamma = 1.0 / np.sqrt(1.0 - beta**2)
    return gamma

def lorentz_boost_matrix(v: float, c: float = C) -> np.ndarray:
    """
    構造沿 x 軸的勞侖茲變換矩陣 Lambda^\mu_\nu。
    
    (此函數維持不變，僅為上下文提供完整性)
    """
    gamma = lorentz_factor(v, c)
    beta = v / c
    
    # 矩陣分量
    term_gb = gamma * beta
    
    Lambda_matrix = np.array([
        [gamma, -term_gb, 0.0, 0.0],
        [-term_gb, gamma, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ])
    
    return Lambda_matrix

def lorentz_transform(x_mu: np.ndarray, v: float, c: float = C) -> np.ndarray:
    """
    執行勞侖茲變換，將事件的四維座標從 S 坐標系轉換到 S' 坐標系。
    
    (此函數維持不變，僅為上下文提供完整性)
    """
    
    # 1. 構造勞侖茲變換矩陣
    Lambda = lorentz_boost_matrix(v, c)
    
    # 2. 執行矩陣乘法: x' = Lambda * x
    x_prime_mu = np.dot(Lambda, x_mu)
    
    return x_prime_mu

# ----------------------------------------------------------------------
#                         新增：尺縮鐘慢函數
# ----------------------------------------------------------------------

def time_dilation(tau: float, v: float, c: float = C) -> float:
    """
    計算時間膨脹（鐘慢）效應：運動時鐘走慢了。
    
    dt = gamma * dtau
    
    參數:
    tau (float): 靜止系 (S') 測量的固有時間 (Proper Time, d\tau)。
    v (float): 相對速度 (米/秒)。
    
    回傳:
    float: 運動系 (S) 測量的時間間隔 (dt)。
    """
    gamma = lorentz_factor(v, c)
    dt = gamma * tau
    return dt

def length_contraction(L0: float, v: float, c: float = C) -> float:
    """
    計算勞侖茲收縮（尺縮）效應：運動方向上的長度收縮。
    
    L = L0 / gamma
    
    參數:
    L0 (float): 靜止系 (S') 測量的固有長度 (Proper Length, L0)。
    v (float): 相對速度 (米/秒)。
    
    回傳:
    float: 運動系 (S) 測量的收縮後長度 (L)。
    """
    gamma = lorentz_factor(v, c)
    L = L0 / gamma
    return L

# ----------------------------------------------------------------------
#                             範例測試
# ----------------------------------------------------------------------

# 1. 設定極高的相對速度 (例如 0.8c)
v_relative = 0.8 * C 
gamma_val = lorentz_factor(v_relative)

print(f"================ 尺縮鐘慢範例 ================")
print(f"設定相對速度 v = {v_relative:.2e} m/s (0.8c)")
print(f"計算勞侖茲因子 gamma = {gamma_val:.4f}\n")

# --- 鐘慢 (Time Dilation) 範例 ---
# 假設太空船 (S' 系) 上的時鐘量得時間間隔 tau = 10 秒
tau_prime = 10.0 # 固有時間 (Proper Time)

# 計算靜止觀察者 (S 系) 測量到的時間 dt
dt_measured = time_dilation(tau_prime, v_relative)

print(f"--- 時間膨脹 (鐘慢) ---")
print(f"太空船上的時間間隔 d\tau = {tau_prime:.2f} s")
print(f"靜止觀察者測量的時間間隔 dt = {dt_measured:.2f} s")
# 預期 dt = 1.6667 * 10 = 16.67 s
print(f"結論: 運動時鐘走慢了。靜止系 S 測量到的時間 {dt_measured:.2f} s 比運動系 S' 的 {tau_prime:.2f} s 更長。")
print("-" * 30)

# --- 尺縮 (Length Contraction) 範例 ---
# 假設一把尺在靜止系 (S' 系) 中測得固有長度 L0 = 100 米
L0_prime = 100.0 # 固有長度 (Proper Length)

# 計算靜止觀察者 (S 系) 測量到的長度 L
L_measured = length_contraction(L0_prime, v_relative)

print(f"--- 勞侖茲收縮 (尺縮) ---")
print(f"靜止尺的固有長度 L0 = {L0_prime:.2f} m")
print(f"運動方向上測量到的長度 L = {L_measured:.2f} m")
# 預期 L = 100 / 1.6667 = 60.00 m
print(f"結論: 運動方向上的長度收縮了。靜止系 S 測量到的長度 {L_measured:.2f} m 比固有長度 {L0_prime:.2f} m 更短。")
print("============================================")