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
    
    參數:
    v (float): 相對速度 (米/秒)。
    c (float): 光速 (米/秒)。
    
    回傳:
    np.ndarray: 勞侖茲變換矩陣 (4x4)。
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
    
    參數:
    x_mu (np.ndarray): S 坐標系中的四維座標 (ct, x, y, z)。
    v (float): S' 相對於 S 沿 x 軸移動的速度 (米/秒)。
    c (float): 光速 (米/秒)。
    
    回傳:
    np.ndarray: S' 坐標系中的四維座標 (c*t', x', y', z')。
    """
    
    # 1. 構造勞侖茲變換矩陣
    Lambda = lorentz_boost_matrix(v, c)
    
    # 2. 執行矩陣乘法: x' = Lambda * x
    # 這裡的 x_mu 必須是四維向量 (4,)
    x_prime_mu = np.dot(Lambda, x_mu)
    
    return x_prime_mu

# --- 範例測試 ---

# 1. 定義一個事件的四維座標 (ct, x, y, z)
# 假設一個事件發生在 t=1秒, 空間座標 (x, y, z) = (100m, 0m, 0m)
t = 1.0
x = 100.0
y = 0.0
z = 0.0
x_mu = np.array([C * t, x, y, z])

print(f"--- 原始 S 坐標系中的事件 (ct, x, y, z) ---")
print(f"ct: {x_mu[0]:.4e} m")
print(f"x: {x_mu[1]:.2f} m")
print(f"y: {x_mu[2]:.2f} m")
print(f"z: {x_mu[3]:.2f} m")

# 2. 定義相對速度
# 設 S' 相對於 S 沿 x 軸以 0.5c 的速度移動
v_relative = 0.5 * C 

# 3. 構造勞侖茲變換矩陣並計算 gamma
gamma_val = lorentz_factor(v_relative)
print(f"\n--- 勞侖茲參數 ---")
print(f"相對速度 v = {v_relative:.2e} m/s ({0.5}c)")
print(f"勞侖茲因子 gamma = {gamma_val:.4f}")

Lambda = lorentz_boost_matrix(v_relative)
print("\n勞侖茲變換矩陣 Lambda:")
# 為了清晰顯示，我們只取前兩列（包含非零項）
print(Lambda[:, :2])


# 4. 執行變換
x_prime_mu = lorentz_transform(x_mu, v_relative)

# 5. 輸出 S' 坐標系中的結果
ct_prime = x_prime_mu[0]
t_prime = ct_prime / C
x_prime = x_prime_mu[1]
y_prime = x_prime_mu[2]
z_prime = x_prime_mu[3]

print(f"\n--- 變換後的 S' 坐標系中的事件 (c*t', x', y', z') ---")
print(f"c*t': {ct_prime:.4e} m")
print(f"x': {x_prime:.2f} m")
print(f"y': {y_prime:.2f} m")
print(f"z': {z_prime:.2f} m")
print(f"-------------------------------------------------------")
print(f"變換後的實際時間 t': {t_prime:.4e} s")