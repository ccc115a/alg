import numpy as np

def calculate_line_integral(vector_field_func, path_func, t_range, N=1000):
    """
    計算線積分的通用函數: ∫ F · dr
    
    參數:
    - vector_field_func: 函數，輸入座標 (x, y, ...)，回傳向量 [Fx, Fy, ...]
    - path_func: 函數，輸入參數 t，回傳座標 [x(t), y(t), ...]
    - t_range: tuple (t_start, t_end)
    - N: 切分點數量 (預設 1000，越多越精準)
    
    回傳:
    - 積分值的近似解 (float)
    """
    
    # 1. 產生參數 t 的陣列
    t_vals = np.linspace(t_range[0], t_range[1], N)
    dt = t_vals[1] - t_vals[0]
    
    # 2. 計算路徑上每個點的座標 r(t)
    # 結果是一個 (N, D) 的矩陣，D 是維度
    # 我們使用 list comprehension 來呼叫使用者傳進來的 path_func
    r_vals = np.array([path_func(t) for t in t_vals])
    
    # 3. 計算路徑的切線向量 (速度) dr/dt
    # 使用 numpy 的 gradient 做數值微分，axis=0 代表沿著時間軸微分
    dr_dt = np.gradient(r_vals, dt, axis=0)
    
    # 4. 計算路徑上每個點的力場向量 F(r(t))
    # 注意：使用 *point 將座標解包傳入 (例如 F(*[x,y]) 變成 F(x,y))
    F_vals = np.array([vector_field_func(*point) for point in r_vals])
    
    # 5. 計算被積函數 (點積): F · (dr/dt)
    # 在 axis=1 (空間維度) 上做加總 -> x*dx + y*dy ...
    integrand = np.sum(F_vals * dr_dt, axis=1)
    
    # 6. 執行積分 (使用梯形法 np.trapz 提高精度)
    result = np.trapz(integrand, t_vals)
    
    return result

# ==========================================
# 測試案例 (Test Cases)
# ==========================================

if __name__ == "__main__":
    print("=== 線積分通用函數測試 ===\n")

    # --- 測試 1: 簡單的恆力做功 ---
    # 力場: F = [1, 2] (恆力)
    # 路徑: 從 (0,0) 直線走到 (3,0)
    # 理論值: 力在移動方向分量(1) * 距離(3) = 3
    def field_constant(x, y):
        return [1, 2]
    
    def path_line(t): 
        # t 從 0 到 3，x=t, y=0
        return [t, 0]
    
    res1 = calculate_line_integral(field_constant, path_line, (0, 3))
    print(f"測試 1 (恆力直線):")
    print(f"  計算結果: {res1:.4f}")
    print(f"  理論結果: 3.0000")
    print("-" * 30)

    # --- 測試 2: 圓周運動 (上一題的例子) ---
    # 力場: F = [-y, x]
    # 路徑: 單位圓逆時針 x=cos(t), y=sin(t)
    # 理論值: 2π ≈ 6.28318
    def field_rotation(x, y):
        return [-y, x]
    
    def path_circle(t):
        return [np.cos(t), np.sin(t)]
    
    res2 = calculate_line_integral(field_rotation, path_circle, (0, 2*np.pi))
    print(f"測試 2 (圓周運動):")
    print(f"  計算結果: {res2:.4f}")
    print(f"  理論結果: {2*np.pi:.4f}")
    print("-" * 30)

    # --- 測試 3: 正交運動 (不做功) ---
    # 力場: F = [0, 10] (力向上)
    # 路徑: 水平移動 (t, 0)
    # 力與位移垂直，功應為 0
    def field_vertical(x, y):
        return [0, 10]
    
    res3 = calculate_line_integral(field_vertical, path_line, (0, 5))
    print(f"測試 3 (正交運動):")
    print(f"  計算結果: {res3:.4f}")
    print(f"  理論結果: 0.0000")
    print("-" * 30)

    # --- 測試 4: 3D 螺旋線 ---
    # 力場: F = [z, 0, x]
    # 路徑: 螺旋 x=cos(t), y=sin(t), z=t (t: 0->2pi)
    # 理論計算:
    # r = [cos t, sin t, t]
    # dr = [-sin t, cos t, 1] dt
    # F = [t, 0, cos t]
    # F·dr = -t sin t + 0 + cos t
    # int(cos t - t sin t) dt from 0 to 2pi
    # = [sin t - (-t cos t + sin t)] = [t cos t] | 0->2pi = 2pi
    def field_3d(x, y, z):
        return [z, 0, x]
    
    def path_helix(t):
        return [np.cos(t), np.sin(t), t]
    
    res4 = calculate_line_integral(field_3d, path_helix, (0, 2*np.pi))
    print(f"測試 4 (3D 螺旋線):")
    print(f"  計算結果: {res4:.4f}")
    print(f"  理論結果: {2*np.pi:.4f}")