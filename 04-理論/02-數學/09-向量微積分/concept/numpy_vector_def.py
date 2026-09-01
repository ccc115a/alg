import numpy as np

def numerical_gradient(scalar_field, spacing):
    """
    計算數值梯度
    scalar_field: 3D numpy array
    spacing: 網格間距 (dx, dy, dz)
    回傳: [grad_x, grad_y, grad_z]
    """
    # np.gradient 回傳順序對應於 array 的維度順序 (axis 0, axis 1, axis 2)
    # 我們設定 axis 0=x, axis 1=y, axis 2=z
    g = np.gradient(scalar_field, spacing[0], axis=0) # df/dx
    g += np.gradient(scalar_field, spacing[1], axis=1) # df/dy (這行語法錯誤，不能直接加，下一行修正)
    
    # 修正：np.gradient 直接回傳所有維度的梯度列表
    grads = np.gradient(scalar_field, *spacing)
    return grads # [df/dx, df/dy, df/dz]

def numerical_divergence(vector_field, spacing):
    """
    計算數值散度
    vector_field: list of 3D arrays [Fx, Fy, Fz]
    spacing: 網格間距
    回傳: 3D array (純量場)
    """
    Fx, Fy, Fz = vector_field
    dx, dy, dz = spacing
    
    # 散度 = dFx/dx + dFy/dy + dFz/dz
    dFx_dx = np.gradient(Fx, dx, axis=0)
    dFy_dy = np.gradient(Fy, dy, axis=1)
    dFz_dz = np.gradient(Fz, dz, axis=2)
    
    return dFx_dx + dFy_dy + dFz_dz

def numerical_curl(vector_field, spacing):
    """
    計算數值旋度
    vector_field: list of 3D arrays [Fx, Fy, Fz]
    spacing: 網格間距
    回傳: list of 3D arrays [Curl_x, Curl_y, Curl_z]
    """
    Fx, Fy, Fz = vector_field
    dx, dy, dz = spacing
    
    # 旋度計算 (Cross product 邏輯)
    # Curl_x = dFz/dy - dFy/dz
    # Curl_y = dFx/dz - dFz/dx
    # Curl_z = dFy/dx - dFx/dy
    
    dFz_dy = np.gradient(Fz, dy, axis=1)
    dFy_dz = np.gradient(Fy, dz, axis=2)
    curl_x = dFz_dy - dFy_dz
    
    dFx_dz = np.gradient(Fx, dz, axis=2)
    dFz_dx = np.gradient(Fz, dx, axis=0)
    curl_y = dFx_dz - dFz_dx
    
    dFy_dx = np.gradient(Fy, dx, axis=0)
    dFx_dy = np.gradient(Fx, dy, axis=1)
    curl_z = dFy_dx - dFx_dy
    
    return [curl_x, curl_y, curl_z]

# ==========================================
# 測試與驗證區
# ==========================================
if __name__ == "__main__":
    # 1. 建立空間網格 (Grid Generation)
    # 範圍 -2 到 2，每個維度 21 個點 (步長 = 0.2)
    N = 21
    limit = 2.0
    x = np.linspace(-limit, limit, N)
    y = np.linspace(-limit, limit, N)
    z = np.linspace(-limit, limit, N)
    
    # 計算間距 dx, dy, dz
    dx = x[1] - x[0]
    spacing = (dx, dx, dx)
    
    # meshgrid indexing='ij' 很重要！
    # 確保 array[i, j, k] 對應 x[i], y[j], z[k]
    X, Y, Z = np.meshgrid(x, y, z, indexing='ij')

    print(f"網格大小: {N}x{N}x{N}, 間距: {dx:.2f}")
    
    # 選擇一個測試點索引 (中心點)
    mid = N // 2  # x=0, y=0, z=0 的位置
    check_idx = (mid, mid, mid) 
    
    print("\n=== 測試 1: 梯度 (Gradient) ===")
    # 純量場 f = X^2 + Y^2 + Z^2
    # 理論梯度 = [2x, 2y, 2z]
    f = X**2 + Y**2 + Z**2
    grad = numerical_gradient(f, spacing)
    
    # 在 (1, 1, 1) 的位置測試 (索引為 mid+delta)
    test_idx = (mid + 5, mid + 5, mid + 5) # 對應座標約為 (1.0, 1.0, 1.0)
    val_x = X[test_idx]
    
    print(f"座標 x={val_x:.2f} 處:")
    print(f"數值梯度 x分量: {grad[0][test_idx]:.4f} (理論值: {2*val_x:.4f})")
    # 數值解通常會有微小誤差，這是正常的

    print("\n=== 測試 2: 散度 (Divergence) ===")
    # 向量場 F = [X, Y, Z] (向外輻射)
    # 理論散度 = dx/dx + dy/dy + dz/dz = 1 + 1 + 1 = 3
    F_div = [X, Y, Z]
    div_val = numerical_divergence(F_div, spacing)
    
    print(f"中心點散度: {div_val[check_idx]:.4f} (理論值: 3.0000)")
    print(f"平均散度誤差: {np.mean(np.abs(div_val - 3.0)):.6f}")

    print("\n=== 測試 3: 旋度 (Curl) ===")
    # 向量場 F = [-Y, X, 0] (剛體繞 Z 軸旋轉)
    # 理論旋度 = [0, 0, 2]
    F_curl = [-Y, X, np.zeros_like(Z)]
    curl_val = numerical_curl(F_curl, spacing)
    
    cx = curl_val[0][check_idx]
    cy = curl_val[1][check_idx]
    cz = curl_val[2][check_idx]
    
    print(f"中心點旋度: [{cx:.4f}, {cy:.4f}, {cz:.4f}]")
    print(f"理論值旋度: [0.0000, 0.0000, 2.0000]")
