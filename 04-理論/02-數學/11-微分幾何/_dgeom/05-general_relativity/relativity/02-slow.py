import numpy as np

# 定義光速 c (SI 單位，方便理解)
C_LIGHT = 299792458.0  # meters per second

## 函式定義：計算洛倫茲因子 (Gamma)
def lorentz_factor(v):
    """
    計算洛倫茲因子 gamma = 1 / sqrt(1 - (v/c)^2)。
    
    輸入:
    v: 物體相對於慣性系的移動速度 (m/s)。
    
    輸出:
    gamma: 洛倫茲因子。
    """
    if v < 0 or v >= C_LIGHT:
        raise ValueError("速度 v 必須在 [0, c) 範圍內。")
        
    # 計算速度與光速的比值平方 (v/c)^2
    v_over_c_squared = (v / C_LIGHT)**2
    
    # 計算 gamma
    gamma = 1.0 / np.sqrt(1.0 - v_over_c_squared)
    
    return gamma

## 範例展示：計算與結果
def demonstrate_sr_effects(v_speed, L0_proper_length, d_tau_proper_time):
    """
    展示給定速度下的尺縮與鐘慢效應。
    """
    
    print(f"\n--- 狹義相對論效應展示 (v = {v_speed / C_LIGHT:.4f} c) ---")
    
    try:
        gamma = lorentz_factor(v_speed)
    except ValueError as e:
        print(f"錯誤: {e}")
        return
        
    print(f"洛倫茲因子 (Gamma, γ): {gamma:.6f}")
    
    # 1. 鐘慢 (Time Dilation)
    # 靜止觀測者測得的時間: dt = gamma * d_tau
    dt_observed_time = gamma * d_tau_proper_time
    
    print("\n[鐘慢 (Time Dilation)]")
    print(f"固有點時間 dτ (靜止時鐘): {d_tau_proper_time:.4e} 秒")
    print(f"觀測者測得時間 dt (運動時鐘): {dt_observed_time:.4e} 秒")
    print(f"dt / dτ = {dt_observed_time / d_tau_proper_time:.6f} (等於 γ)")
    
    # 2. 尺縮 (Length Contraction)
    # 觀測者測得的長度: L = L0 / gamma
    L_observed_length = L0_proper_length / gamma
    
    print("\n[尺縮 (Length Contraction)]")
    print(f"固有長度 L0 (靜止尺長): {L0_proper_length:.4e} 公尺")
    print(f"觀測者測得長度 L (運動尺長): {L_observed_length:.4e} 公尺")
    print(f"L / L0 = {L_observed_length / L0_proper_length:.6f} (等於 1/γ)")
    
    if gamma > 1.0001:
        print("\n結論: γ 顯著大於 1，鐘慢與尺縮效應顯著。")
    else:
        print("\n結論: γ 約等於 1，效應不明顯 (低速近似於牛頓力學)。")


# --- 執行範例 ---

# 範例 1: 低速 (約 1% 光速)
v1 = 0.01 * C_LIGHT
L0_1 = 100.0  # 100 公尺
d_tau_1 = 1.0  # 1 秒
demonstrate_sr_effects(v1, L0_1, d_tau_1)

# 範例 2: 極高速 (約 99.99% 光速)
v2 = 0.9999 * C_LIGHT
L0_2 = 100.0  # 100 公尺
d_tau_2 = 1.0  # 1 秒
demonstrate_sr_effects(v2, L0_2, d_tau_2)