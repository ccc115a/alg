import numpy as np

# 定義光速 c
# 為了程式的可讀性和數值穩定性，我們可以使用一個標準值，
# 或者在某些計算中將其設定為 1 (自然單位制)，
# 但在這裡我們使用標準值來保持物理意義。
C = 299792458.0  # 光速 (米/秒)

# 1. 閔可夫斯基度規矩陣 \eta_{\mu\nu} (Minkowski Metric)
# 採用 (-1, 1, 1, 1) 符號約定：eta_00 = -1, eta_ii = 1
eta_mu_nu = np.diag([-1.0, 1.0, 1.0, 1.0])

def calculate_ds_squared(dt: float, dx: float, dy: float, dz: float, c: float = C) -> float:
    """
    使用閔可夫斯基度規計算時空間隔的平方 ds^2。

    參數:
    dt (float): 時間變化量 (秒)。
    dx (float): x 軸空間變化量 (米)。
    dy (float): y 軸空間變化量 (米)。
    dz (float): z 軸空間變化量 (米)。
    c (float): 光速 (米/秒)。預設使用定義的 C。

    回傳:
    float: 時空間隔的平方 ds^2 (米的平方)。
    """
    
    # 構造四維位移向量 dx^\mu = (c*dt, dx, dy, dz)
    # 這裡的 c*dt 就是 x^0 分量
    dx_mu = np.array([c * dt, dx, dy, dz])
    
    # 計算 ds^2 = dx^T \cdot \eta \cdot dx
    # 1. 計算中間結果: \eta \cdot dx
    # np.dot(eta_mu_nu, dx_mu) 得到 \eta_{\mu\nu} dx^\nu
    intermediate_result = np.dot(eta_mu_nu, dx_mu)
    
    # 2. 計算最終結果: dx^T \cdot (\eta \cdot dx)
    # np.dot(dx_mu, intermediate_result) 得到 dx^\mu (\eta_{\mu\nu} dx^\nu)
    ds_squared = np.dot(dx_mu, intermediate_result)
    
    return ds_squared

# --- 範例測試 ---

# 範例 1: 空間位移 (ds^2 > 0，空間類間隔)
# 設 t=0, 位移 (3m, 4m, 0m)。c*dt = 0。
# 預期 ds^2 = 0^2 + 3^2 + 4^2 + 0^2 = 25
ds1 = calculate_ds_squared(dt=0, dx=3, dy=4, dz=0, c=1.0) # 為了簡化計算，這裡暫時將 c 設為 1
print(f"範例 1 (空間類): ds^2 = {ds1} m^2 (預期 25)")


# 範例 2: 時間位移 (ds^2 < 0，時間類間隔)
# 設 x=0, 只有時間位移 dt=1s。c*dt = C。
# 預期 ds^2 = -(C)^2 + 0 + 0 + 0 = -C^2
# 這裡使用實際光速 C
ds2 = calculate_ds_squared(dt=1e-8, dx=0, dy=0, dz=0) # 使用一個極小的 dt 避免數值溢出
# C 是一個很大的數， C^2 ~ 9 * 10^16，我們使用 1e-8 秒來縮小數值
c_dt = C * 1e-8
expected_ds2 = -(c_dt**2)
print(f"\n範例 2 (時間類): 使用 dt=1e-8s, dx=0, dy=0, dz=0")
print(f"計算出的 ds^2 = {ds2:.4e} m^2")
print(f"預期的 ds^2 = {expected_ds2:.4e} m^2")


# 範例 3: 光線 (ds^2 = 0，光類間隔/零間隔)
# 設光線沿 x 軸移動 3m 所需時間。dt = 3m / C
dt_light = 3.0 / C
# 預期 ds^2 = -(C * dt_light)^2 + 3^2 + 0 + 0 = -(3)^2 + 3^2 = 0
ds3 = calculate_ds_squared(dt=dt_light, dx=3.0, dy=0, dz=0)
print(f"\n範例 3 (光類): 光線位移 ds^2 = {ds3:.4e} m^2 (預期接近 0)")