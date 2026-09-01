import math

def vector_line_integral_2d(F_x, F_y, r_x, r_y, t_start, t_end, n_points=1000):
    """
    計算二維向量場沿參數化曲線的線積分
    
    參數:
    F_x, F_y: 向量場的分量函數 F = (F_x(x,y), F_y(x,y))
    r_x, r_y: 參數化曲線 r(t) = (r_x(t), r_y(t))
    t_start, t_end: 參數 t 的起始和結束值
    n_points: 積分的分割點數
    
    返回: ∫ F·dr 的值
    """
    dt = (t_end - t_start) / n_points
    integral = 0.0
    
    for i in range(n_points):
        t = t_start + i * dt
        t_next = t + dt
        
        # 計算曲線上的點
        x = r_x(t)
        y = r_y(t)
        
        # 計算切線向量 dr/dt
        h = dt * 0.01  # 用於數值微分的小步長
        dx_dt = (r_x(t + h) - r_x(t - h)) / (2 * h)
        dy_dt = (r_y(t + h) - r_y(t - h)) / (2 * h)
        
        # 計算向量場在該點的值
        F_x_val = F_x(x, y)
        F_y_val = F_y(x, y)
        
        # 計算點積 F·(dr/dt) * dt
        integral += (F_x_val * dx_dt + F_y_val * dy_dt) * dt
    
    return integral


def vector_line_integral_3d(F_x, F_y, F_z, r_x, r_y, r_z, t_start, t_end, n_points=1000):
    """
    計算三維向量場沿參數化曲線的線積分
    
    參數:
    F_x, F_y, F_z: 向量場的分量函數 F = (F_x(x,y,z), F_y(x,y,z), F_z(x,y,z))
    r_x, r_y, r_z: 參數化曲線 r(t) = (r_x(t), r_y(t), r_z(t))
    t_start, t_end: 參數 t 的起始和結束值
    n_points: 積分的分割點數
    
    返回: ∫ F·dr 的值
    """
    dt = (t_end - t_start) / n_points
    integral = 0.0
    
    for i in range(n_points):
        t = t_start + i * dt
        
        # 計算曲線上的點
        x = r_x(t)
        y = r_y(t)
        z = r_z(t)
        
        # 計算切線向量 dr/dt
        h = dt * 0.01  # 用於數值微分的小步長
        dx_dt = (r_x(t + h) - r_x(t - h)) / (2 * h)
        dy_dt = (r_y(t + h) - r_y(t - h)) / (2 * h)
        dz_dt = (r_z(t + h) - r_z(t - h)) / (2 * h)
        
        # 計算向量場在該點的值
        F_x_val = F_x(x, y, z)
        F_y_val = F_y(x, y, z)
        F_z_val = F_z(x, y, z)
        
        # 計算點積 F·(dr/dt) * dt
        integral += (F_x_val * dx_dt + F_y_val * dy_dt + F_z_val * dz_dt) * dt
    
    return integral


def scalar_line_integral_2d(f, r_x, r_y, t_start, t_end, n_points=1000):
    """
    計算標量函數沿曲線的線積分 (弧長積分)
    
    參數:
    f: 標量函數 f(x,y)
    r_x, r_y: 參數化曲線 r(t) = (r_x(t), r_y(t))
    t_start, t_end: 參數 t 的起始和結束值
    n_points: 積分的分割點數
    
    返回: ∫ f ds 的值
    """
    dt = (t_end - t_start) / n_points
    integral = 0.0
    
    for i in range(n_points):
        t = t_start + i * dt
        
        # 計算曲線上的點
        x = r_x(t)
        y = r_y(t)
        
        # 計算切線向量的模長 |dr/dt|
        h = dt * 0.01
        dx_dt = (r_x(t + h) - r_x(t - h)) / (2 * h)
        dy_dt = (r_y(t + h) - r_y(t - h)) / (2 * h)
        ds_dt = math.sqrt(dx_dt**2 + dy_dt**2)
        
        # 計算標量函數在該點的值
        f_val = f(x, y)
        
        # 積分
        integral += f_val * ds_dt * dt
    
    return integral


def test_vector_line_integrals():
    """
    測試向量線積分函數的正確性
    """
    print("=== 向量線積分測試 ===\n")
    
    # 測試1: 保守向量場的線積分應該與路徑無關
    print("測試1: 保守向量場 F = (y, x) 沿不同路徑的線積分")
    
    # 定義保守向量場 F = (y, x) (勢函數為 φ = xy)
    def F_x_conservative(x, y):
        return y
    
    def F_y_conservative(x, y):
        return x
    
    # 路徑1: 直線從 (0,0) 到 (1,1)
    def path1_x(t):
        return t
    
    def path1_y(t):
        return t
    
    integral1 = vector_line_integral_2d(F_x_conservative, F_y_conservative, 
                                      path1_x, path1_y, 0, 1)
    
    # 路徑2: 先沿x軸到(1,0)，再沿y軸到(1,1)
    def path2_x(t):
        return 1 if t > 1 else t
    
    def path2_y(t):
        return t - 1 if t > 1 else 0
    
    integral2 = vector_line_integral_2d(F_x_conservative, F_y_conservative, 
                                      path2_x, path2_y, 0, 2)
    
    print(f"直線路徑積分值: {integral1:.6f}")
    print(f"折線路徑積分值: {integral2:.6f}")
    print(f"理論值 (φ(1,1) - φ(0,0) = 1×1 - 0×0): 1.000000")
    print(f"差異: {abs(integral1 - 1):.6f}, {abs(integral2 - 1):.6f}\n")
    
    # 測試2: 圓周上的向量場線積分
    print("測試2: 向量場 F = (-y, x) 沿單位圓的線積分")
    
    def F_x_rotation(x, y):
        return -y
    
    def F_y_rotation(x, y):
        return x
    
    # 單位圓的參數化: r(t) = (cos(t), sin(t)), t ∈ [0, 2π]
    def circle_x(t):
        return math.cos(t)
    
    def circle_y(t):
        return math.sin(t)
    
    integral_circle = vector_line_integral_2d(F_x_rotation, F_y_rotation, 
                                            circle_x, circle_y, 0, 2*math.pi)
    
    print(f"圓周積分值: {integral_circle:.6f}")
    print(f"理論值 (2π): {2*math.pi:.6f}")
    print(f"差異: {abs(integral_circle - 2*math.pi):.6f}\n")
    
    # 測試3: 三維螺旋線上的向量場線積分
    print("測試3: 三維向量場 F = (z, x, y) 沿螺旋線的線積分")
    
    def F_x_3d(x, y, z):
        return z
    
    def F_y_3d(x, y, z):
        return x
    
    def F_z_3d(x, y, z):
        return y
    
    # 螺旋線參數化: r(t) = (cos(t), sin(t), t), t ∈ [0, 2π]
    def helix_x(t):
        return math.cos(t)
    
    def helix_y(t):
        return math.sin(t)
    
    def helix_z(t):
        return t
    
    integral_helix = vector_line_integral_3d(F_x_3d, F_y_3d, F_z_3d,
                                           helix_x, helix_y, helix_z, 
                                           0, 2*math.pi)
    
    print(f"螺旋線積分值: {integral_helix:.6f}")
    
    # 測試4: 標量線積分 - 計算曲線的弧長
    print("\n測試4: 標量線積分 - 計算單位圓的弧長")
    
    def unity_function(x, y):
        return 1.0  # f(x,y) = 1，積分結果應為弧長
    
    arc_length = scalar_line_integral_2d(unity_function, circle_x, circle_y, 0, 2*math.pi)
    
    print(f"計算得到的弧長: {arc_length:.6f}")
    print(f"理論弧長 (2π): {2*math.pi:.6f}")
    print(f"差異: {abs(arc_length - 2*math.pi):.6f}\n")
    
    # 測試5: 質量計算 - 密度函數沿曲線的積分
    print("測試5: 質量計算 - 密度函數 ρ(x,y) = x² + y² 沿單位圓")
    
    def density_function(x, y):
        return x**2 + y**2  # 在單位圓上，x² + y² = 1
    
    mass = scalar_line_integral_2d(density_function, circle_x, circle_y, 0, 2*math.pi)
    
    print(f"計算得到的質量: {mass:.6f}")
    print(f"理論值 (1 × 2π): {2*math.pi:.6f}")
    print(f"差異: {abs(mass - 2*math.pi):.6f}\n")


def advanced_examples():
    """
    更多高級應用示例
    """
    print("=== 高級應用示例 ===\n")
    
    # 示例1: 電場做功計算
    print("示例1: 點電荷產生的電場沿直線路徑做功")
    
    # 點電荷在原點，電場 E = k*q/r² * r̂
    # 簡化為 F = (x/(x²+y²)^(3/2), y/(x²+y²)^(3/2))
    def E_x(x, y):
        r_squared = x**2 + y**2
        if r_squared < 1e-10:
            return 0
        return x / (r_squared ** 1.5)
    
    def E_y(x, y):
        r_squared = x**2 + y**2
        if r_squared < 1e-10:
            return 0
        return y / (r_squared ** 1.5)
    
    # 從 (1, 0) 到 (2, 0) 的直線路徑
    def straight_x(t):
        return 1 + t  # t ∈ [0, 1]
    
    def straight_y(t):
        return 0
    
    work = vector_line_integral_2d(E_x, E_y, straight_x, straight_y, 0, 1)
    theoretical_work = 1 - 1/2  # -1/r 在端點的差值
    
    print(f"電場做功: {work:.6f}")
    print(f"理論值: {theoretical_work:.6f}")
    print(f"差異: {abs(work - theoretical_work):.6f}\n")
    
    # 示例2: 流體流量計算
    print("示例2: 流體速度場 v = (-y, x) 通過單位圓的流量")
    
    def v_x(x, y):
        return -y
    
    def v_y(x, y):
        return x
    
    # 使用格林定理驗證：∮ F·dr = ∬ (∂F_y/∂x - ∂F_x/∂y) dA
    # 這裡 ∂F_y/∂x - ∂F_x/∂y = 1 - (-1) = 2
    # 所以積分應該等於 2 × π × 1² = 2π
    
    circulation = vector_line_integral_2d(v_x, v_y, circle_x, circle_y, 0, 2*math.pi)
    
    print(f"流體循環: {circulation:.6f}")
    print(f"格林定理預測值: {2*math.pi:.6f}")
    print(f"差異: {abs(circulation - 2*math.pi):.6f}")


if __name__ == "__main__":
    test_vector_line_integrals()
    advanced_examples()