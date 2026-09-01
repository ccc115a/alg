"""
special_relativity.py

狹義相對論的微分幾何與物理效應計算套件。
包含勞侖茲因子、時空間隔、勞侖茲變換、尺縮和鐘慢等函數。
"""

import numpy as np

# 定義光速 C
C = 299792458.0  # 光速 (米/秒)

def lorentz_factor(v: float, c: float = C) -> float:
    """
    計算勞侖茲因子 gamma (γ)。
    
    參數:
    v (float): 相對速度 (米/秒)。
    c (float): 光速 (米/秒)。
    
    回傳:
    float: 勞侖茲因子 gamma。
    
    數學公式:
    γ = 1 / sqrt(1 - (v/c)^2)
    """
    beta = v / c
    if abs(beta) >= 1:
        raise ValueError("相對速度 v 必須嚴格小於光速 c。")
        
    gamma = 1.0 / np.sqrt(1.0 - beta**2)
    return gamma

# 閔可夫斯基度規矩陣 \eta_{\mu\nu} (Minkowski Metric)
# 採用 (-1, 1, 1, 1) 符號約定：eta_00 = -1, eta_ii = 1
ETA_MU_NU = np.diag([-1.0, 1.0, 1.0, 1.0])

def calculate_ds_squared(dt: float, dx: float, dy: float, dz: float, c: float = C) -> float:
    """
    使用閔可夫斯基度規計算時空間隔的平方 ds^2。
    
    參數:
    dt (float): 時間變化量 (秒)。
    dx (float): x 軸空間變化量 (米)。
    dy (float): y 軸空間變化量 (米)。
    dz (float): z 軸空間變化量 (米)。
    c (float): 光速 (米/秒)。
    
    回傳:
    float: 時空間隔的平方 ds^2 (米的平方)。
    
    數學公式:
    ds^2 = -(c dt)^2 + dx^2 + dy^2 + dz^2 = dx^\mu \eta_{\mu\nu} dx^\nu
    """
    
    # 構造四維位移向量 dx^\mu = (c*dt, dx, dy, dz)
    dx_mu = np.array([c * dt, dx, dy, dz])
    
    # 計算 ds^2 = dx^T \cdot \eta \cdot dx
    ds_squared = np.dot(dx_mu, np.dot(ETA_MU_NU, dx_mu))
    
    return ds_squared

def lorentz_boost_matrix(v: float, c: float = C) -> np.ndarray:
    """
    構造沿 x 軸的勞侖茲變換矩陣 Lambda^\mu_\nu。
    
    參數:
    v (float): 相對速度 (米/秒)。
    c (float): 光速 (米/秒)。
    
    回傳:
    np.ndarray: 勞侖茲變換矩陣 (4x4)。
    """
    gamma = lorentz_factor(v, c)
    beta = v / c
    
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
    
    參數:
    x_mu (np.ndarray): S 坐標系中的四維座標 (c*t, x, y, z)。
    v (float): S' 相對於 S 沿 x 軸移動的速度 (米/秒)。
    c (float): 光速 (米/秒)。
    
    回傳:
    np.ndarray: S' 坐標系中的四維座標 (c*t', x', y', z')。
    
    數學公式:
    x'^\mu = \Lambda^\mu_{\nu} x^\nu
    """
    
    Lambda = lorentz_boost_matrix(v, c)
    x_prime_mu = np.dot(Lambda, x_mu)
    
    return x_prime_mu

def time_dilation(tau: float, v: float, c: float = C) -> float:
    """
    計算時間膨脹（鐘慢）效應：運動時鐘走慢了。
    
    參數:
    tau (float): 靜止系 (S') 測量的固有時間 (Proper Time, d\tau)。
    v (float): 相對速度 (米/秒)。
    
    回傳:
    float: 運動系 (S) 測量的時間間隔 (dt)。
    
    數學公式:
    dt = γ * dτ
    """
    gamma = lorentz_factor(v, c)
    dt = gamma * tau
    return dt

def length_contraction(L0: float, v: float, c: float = C) -> float:
    """
    計算勞侖茲收縮（尺縮）效應：運動方向上的長度收縮。
    
    參數:
    L0 (float): 靜止系 (S') 測量的固有長度 (Proper Length, L0)。
    v (float): 相對速度 (米/秒)。
    
    回傳:
    float: 運動系 (S) 測量的收縮後長度 (L)。
    
    數學公式:
    L = L0 / γ
    """
    gamma = lorentz_factor(v, c)
    L = L0 / gamma
    return L

# ----------------------------------------------------------------------
# 若直接執行此檔案，則執行一個簡短的測試範例
# ----------------------------------------------------------------------
if __name__ == '__main__':
    # 測試勞侖茲變換
    v_test = 0.6 * C 
    t_event = 1.0
    x_event = 0.0
    
    x_mu_test = np.array([C * t_event, x_event, 0.0, 0.0])
    x_prime_mu_test = lorentz_transform(x_mu_test, v_test)
    gamma_test = lorentz_factor(v_test) # gamma = 1 / sqrt(1 - 0.6^2) = 1.25

    print("--- special_relativity.py 模組測試 ---")
    print(f"相對速度 v = 0.6c, gamma = {gamma_test:.2f}")
    print(f"S 坐標系事件 (ct, x, y, z): {x_mu_test[0]:.2e}, {x_mu_test[1]:.2f}...")
    print(f"S' 坐標系事件 (c*t', x', y', z'): {x_prime_mu_test[0]:.2e}, {x_prime_mu_test[1]:.2f}...")

    # 測試尺縮鐘慢
    tau_test = 10.0 # 固有時間
    L0_test = 100.0 # 固有長度

    dt_measured_test = time_dilation(tau_test, v_test)
    L_measured_test = length_contraction(L0_test, v_test)

    print("\n--- 尺縮鐘慢測試 ---")
    print(f"固有時間 dτ = {tau_test:.2f} s -> 運動系測量 dt = {dt_measured_test:.2f} s")
    print(f"固有長度 L0 = {L0_test:.2f} m -> 運動系測量 L = {L_measured_test:.2f} m")