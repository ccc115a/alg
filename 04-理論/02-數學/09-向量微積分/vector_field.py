def gradient_2d(f, x, y, h=1e-6):
    """
    計算二維標量場的梯度
    
    參數:
    f: 標量函數 f(x, y)
    x, y: 計算點的座標
    h: 數值微分的步長
    
    返回: [df/dx, df/dy]
    """
    df_dx = (f(x + h, y) - f(x - h, y)) / (2 * h)
    df_dy = (f(x, y + h) - f(x, y - h)) / (2 * h)
    return [df_dx, df_dy]


def gradient_3d(f, x, y, z, h=1e-6):
    """
    計算三維標量場的梯度
    
    參數:
    f: 標量函數 f(x, y, z)
    x, y, z: 計算點的座標
    h: 數值微分的步長
    
    返回: [df/dx, df/dy, df/dz]
    """
    df_dx = (f(x + h, y, z) - f(x - h, y, z)) / (2 * h)
    df_dy = (f(x, y + h, z) - f(x, y - h, z)) / (2 * h)
    df_dz = (f(x, y, z + h) - f(x, y, z - h)) / (2 * h)
    return [df_dx, df_dy, df_dz]


def divergence_2d(fx, fy, x, y, h=1e-6):
    """
    計算二維向量場的散度
    
    參數:
    fx, fy: 向量場的分量函數 F = (fx(x,y), fy(x,y))
    x, y: 計算點的座標
    h: 數值微分的步長
    
    返回: div F = ∂fx/∂x + ∂fy/∂y
    """
    dfx_dx = (fx(x + h, y) - fx(x - h, y)) / (2 * h)
    dfy_dy = (fy(x, y + h) - fy(x, y - h)) / (2 * h)
    return dfx_dx + dfy_dy


def divergence_3d(fx, fy, fz, x, y, z, h=1e-6):
    """
    計算三維向量場的散度
    
    參數:
    fx, fy, fz: 向量場的分量函數 F = (fx(x,y,z), fy(x,y,z), fz(x,y,z))
    x, y, z: 計算點的座標
    h: 數值微分的步長
    
    返回: div F = ∂fx/∂x + ∂fy/∂y + ∂fz/∂z
    """
    dfx_dx = (fx(x + h, y, z) - fx(x - h, y, z)) / (2 * h)
    dfy_dy = (fy(x, y + h, z) - fy(x, y - h, z)) / (2 * h)
    dfz_dz = (fz(x, y, z + h) - fz(x, y, z - h)) / (2 * h)
    return dfx_dx + dfy_dy + dfz_dz


def curl_2d(fx, fy, x, y, h=1e-6):
    """
    計算二維向量場的旋度 (z分量)
    
    參數:
    fx, fy: 向量場的分量函數 F = (fx(x,y), fy(x,y))
    x, y: 計算點的座標
    h: 數值微分的步長
    
    返回: curl F 的 z 分量 = ∂fy/∂x - ∂fx/∂y
    """
    dfy_dx = (fy(x + h, y) - fy(x - h, y)) / (2 * h)
    dfx_dy = (fx(x, y + h) - fx(x, y - h)) / (2 * h)
    return dfy_dx - dfx_dy


def curl_3d(fx, fy, fz, x, y, z, h=1e-6):
    """
    計算三維向量場的旋度
    
    參數:
    fx, fy, fz: 向量場的分量函數 F = (fx(x,y,z), fy(x,y,z), fz(x,y,z))
    x, y, z: 計算點的座標
    h: 數值微分的步長
    
    返回: [curl_x, curl_y, curl_z]
    curl_x = ∂fz/∂y - ∂fy/∂z
    curl_y = ∂fx/∂z - ∂fz/∂x
    curl_z = ∂fy/∂x - ∂fx/∂y
    """
    # curl_x = ∂fz/∂y - ∂fy/∂z
    dfz_dy = (fz(x, y + h, z) - fz(x, y - h, z)) / (2 * h)
    dfy_dz = (fy(x, y, z + h) - fy(x, y, z - h)) / (2 * h)
    curl_x = dfz_dy - dfy_dz
    
    # curl_y = ∂fx/∂z - ∂fz/∂x
    dfx_dz = (fx(x, y, z + h) - fx(x, y, z - h)) / (2 * h)
    dfz_dx = (fz(x + h, y, z) - fz(x - h, y, z)) / (2 * h)
    curl_y = dfx_dz - dfz_dx
    
    # curl_z = ∂fy/∂x - ∂fx/∂y
    dfy_dx = (fy(x + h, y, z) - fy(x - h, y, z)) / (2 * h)
    dfx_dy = (fx(x, y + h, z) - fx(x, y - h, z)) / (2 * h)
    curl_z = dfy_dx - dfx_dy
    
    return [curl_x, curl_y, curl_z]


def laplacian_2d(f, x, y, h=1e-6):
    """
    計算二維標量場的拉普拉斯算子
    
    參數:
    f: 標量函數 f(x, y)
    x, y: 計算點的座標
    h: 數值微分的步長
    
    返回: ∇²f = ∂²f/∂x² + ∂²f/∂y²
    """
    # 計算二階偏微分 ∂²f/∂x²
    d2f_dx2 = (f(x + h, y) - 2 * f(x, y) + f(x - h, y)) / (h ** 2)
    
    # 計算二階偏微分 ∂²f/∂y²
    d2f_dy2 = (f(x, y + h) - 2 * f(x, y) + f(x, y - h)) / (h ** 2)
    
    return d2f_dx2 + d2f_dy2


def laplacian_3d(f, x, y, z, h=1e-6):
    """
    計算三維標量場的拉普拉斯算子
    
    參數:
    f: 標量函數 f(x, y, z)
    x, y, z: 計算點的座標
    h: 數值微分的步長
    
    返回: ∇²f = ∂²f/∂x² + ∂²f/∂y² + ∂²f/∂z²
    """
    # 計算二階偏微分 ∂²f/∂x²
    d2f_dx2 = (f(x + h, y, z) - 2 * f(x, y, z) + f(x - h, y, z)) / (h ** 2)
    
    # 計算二階偏微分 ∂²f/∂y²
    d2f_dy2 = (f(x, y + h, z) - 2 * f(x, y, z) + f(x, y - h, z)) / (h ** 2)
    
    # 計算二階偏微分 ∂²f/∂z²
    d2f_dz2 = (f(x, y, z + h) - 2 * f(x, y, z) + f(x, y, z - h)) / (h ** 2)
    
    return d2f_dx2 + d2f_dy2 + d2f_dz2


# 示例使用函數
def example_usage():
    """
    示例：如何使用這些函數
    """
    import math
    
    print("=== 向量微分算子計算示例 ===\n")
    
    # 示例1: 計算標量場 f(x,y) = x² + y² 在點 (1, 2) 的梯度
    def f1(x, y):
        return x**2 + y**2
    
    grad = gradient_2d(f1, 1, 2)
    print(f"標量場 f(x,y) = x² + y² 在點 (1, 2) 的梯度: {grad}")
    print(f"理論值: [2, 4]\n")
    
    # 示例2: 計算向量場 F = (x, y) 在點 (1, 1) 的散度
    def fx(x, y):
        return x
    
    def fy(x, y):
        return y
    
    div = divergence_2d(fx, fy, 1, 1)
    print(f"向量場 F = (x, y) 在點 (1, 1) 的散度: {div}")
    print(f"理論值: 2\n")
    
    # 示例3: 計算向量場 F = (-y, x) 在點 (1, 1) 的旋度
    def fx_rot(x, y):
        return -y
    
    def fy_rot(x, y):
        return x
    
    curl = curl_2d(fx_rot, fy_rot, 1, 1)
    print(f"向量場 F = (-y, x) 在點 (1, 1) 的旋度 (z分量): {curl}")
    print(f"理論值: 2\n")
    
    # 示例4: 計算標量場 f(x,y) = x² + y² 在點 (1, 1) 的拉普拉斯
    lapl = laplacian_2d(f1, 1, 1)
    print(f"標量場 f(x,y) = x² + y² 在點 (1, 1) 的拉普拉斯: {lapl}")
    print(f"理論值: 4\n")
    
    # 示例5: 三維函數 f(x,y,z) = x² + y² + z² 的梯度
    def f3d(x, y, z):
        return x**2 + y**2 + z**2
    
    grad_3d = gradient_3d(f3d, 1, 2, 3)
    print(f"三維標量場 f(x,y,z) = x² + y² + z² 在點 (1, 2, 3) 的梯度: {grad_3d}")
    print(f"理論值: [2, 4, 6]")


# 執行示例
if __name__ == "__main__":
    example_usage()