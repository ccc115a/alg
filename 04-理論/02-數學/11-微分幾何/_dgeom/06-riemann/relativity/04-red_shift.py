import numpy as np

# 假設光速 c 已經在前面的程式中定義，這裡使用一個常數
C_LIGHT = 299792458.0  # m/s

def calculate_gravitational_redshift(r_s, r_e):
    """
    計算從 r_e 處發射的光線到達無限遠處觀測者 (r_R -> infinity) 時的重力紅移。

    輸入:
    r_s: 史瓦西半徑 (m)。
    r_e: 光線發射點的徑向座標 (m)。

    輸出:
    nu_ratio: 頻率比 nu_R / nu_E。
    redshift_z: 紅移參數 z。
    """
    
    if r_e <= r_s:
        return np.nan, np.nan # 在事件視界或內部，無法計算
    
    # 1. 計算頻率比 nu_R / nu_E
    # 公式: nu_R / nu_E = sqrt(1 - r_s / r_E)
    nu_ratio = np.sqrt(1.0 - r_s / r_e)
    
    # 2. 計算紅移參數 z
    # 公式: z = (nu_E - nu_R) / nu_R = (1 / (nu_R / nu_E)) - 1
    redshift_z = (1.0 / nu_ratio) - 1.0
    
    return nu_ratio, redshift_z

# --- 範例執行 ---
R_SCHWARZSCHILD = 3000.0  # 太陽質量的 r_s (3 km)

# 範例 1: 靠近黑洞 (r = 1.01 r_s)
R_EMIT_1 = R_SCHWARZSCHILD * 1.01
nu_ratio_1, z_1 = calculate_gravitational_redshift(R_SCHWARZSCHILD, R_EMIT_1)

print("--- 範例 1: 靠近事件視界 (r = 1.01 r_s) ---")
print(f"發射點 r_E = {R_EMIT_1:.2f} m")
print(f"頻率比 ν_R / ν_E: {nu_ratio_1:.6f}")
print(f"紅移參數 z: {z_1:.6f}")
if nu_ratio_1 < 1.0:
    print("結論: ν_R < ν_E，紅移效應極其顯著。")

print("-" * 40)

# 範例 2: 離黑洞稍遠 (r = 5 r_s)
R_EMIT_2 = R_SCHWARZSCHILD * 5.0
nu_ratio_2, z_2 = calculate_gravitational_redshift(R_SCHWARZSCHILD, R_EMIT_2)

print("--- 範例 2: 遠離事件視界 (r = 5 r_s) ---")
print(f"發射點 r_E = {R_EMIT_2:.2f} m")
print(f"頻率比 ν_R / ν_E: {nu_ratio_2:.6f}")
print(f"紅移參數 z: {z_2:.6f}")
if nu_ratio_2 < 1.0:
    print("結論: 仍有紅移，但效應較弱。")