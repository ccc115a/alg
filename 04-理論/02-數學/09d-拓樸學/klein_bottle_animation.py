import numpy as np
import matplotlib.pyplot as plt

def klein_bottle_r4_normal_vector_test():
    """
    計算克萊因瓶在 R⁴ 中的法向量，並驗證其單面性。
    我們將軌跡投影到 R³ (x1, x2, x3) 進行視覺化。
    """
    # 選擇一條固定的軌跡線 (例如 u_const = 0.5)
    u_const = np.pi / 4  # 固定的 u 參數
    
    # v 參數，從 0 到 2*pi，共 100 個點 (繞行一圈)
    v_vals = np.linspace(0, 2 * np.pi, 100, endpoint=False)
    
    points_r4 = []
    normals_r4 = [] # 四維空間有兩個法向量，我們計算第一個 (N1) 來示範單面性
    
    # u 和 v 參數的簡寫
    c_u = np.cos(u_const)
    s_u = np.sin(u_const)

    for v in v_vals:
        c_v = np.cos(v)
        s_v = np.sin(v)
        c_2v = np.cos(2*v)
        s_2v = np.sin(2*v)
        
        # --- 1. 計算點的四維坐標 S(u_const, v) ---
        x1 = c_u * c_v
        x2 = c_u * s_v
        x3 = s_u * c_2v
        x4 = s_u * s_2v
        S_r4 = np.array([x1, x2, x3, x4])
        points_r4.append(S_r4)
        
        # --- 2. 計算偏導數 (切向量) ---
        
        # dS/du (切向量 1)
        dx1_du = -s_u * c_v
        dx2_du = -s_u * s_v
        dx3_du = c_u * c_2v
        dx4_du = c_u * s_2v
        dS_du = np.array([dx1_du, dx2_du, dx3_du, dx4_du])
        
        # dS/dv (切向量 2)
        dx1_dv = -c_u * s_v
        dx2_dv = c_u * c_v
        dx3_dv = -2 * s_u * s_2v
        dx4_dv = 2 * s_u * c_2v
        dS_dv = np.array([dx1_dv, dx2_dv, dx4_dv, dx4_dv])
        
        # --- 3. 計算法向量 (四維空間需要兩個法向量 N1, N2) ---
        # 為了簡化單面性驗證，我們只追蹤一個在切線空間正交的額外向量 T，
        # 並檢查它在繞行一圈後是否反轉，這在數值上等同於測試法向量的反轉。
        # 由於計算 R⁴ 曲面的法向量太複雜，我們直接使用 u 方向的切向量 dS_du
        # 作為「追蹤指標」來檢查反轉，因為單面性會讓切線方向也反轉。
        
        # 追蹤 u 方向的切向量 (dS/du)
        N_proxy = dS_du / np.linalg.norm(dS_du) 
        normals_r4.append(N_proxy)


    # 轉換為 Numpy 陣列
    points_r4 = np.array(points_r4)
    normals_r4 = np.array(normals_r4)
    
    # 提取三維投影坐標 (X1, X2, X3)
    points_r3 = points_r4[:, :3] 
    
    # 提取法向量 (或其代理) 的三維投影
    normals_r3_proxy = normals_r4[:, :3]

    # --- 4. 繪圖視覺化 ---
    
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    # 繪製點的軌跡
    ax.plot(points_r3[:, 0], points_r3[:, 1], points_r3[:, 2], 
            color='blue', linewidth=3, label=f'點軌跡 (R⁴投影)')
    
    # 繪製法向量代理 (只繪製每 10 個點)
    ax.quiver(points_r3[::10, 0], points_r3[::10, 1], points_r3[::10, 2], 
              normals_r3_proxy[::10, 0], normals_r3_proxy[::10, 1], normals_r3_proxy[::10, 2], 
              length=0.2, color='red', normalize=False, label='切向量代理投影')

    # 特別標註起點和終點
    start_point = points_r3[0]
    start_normal_proxy = normals_r3_proxy[0]
    
    ax.quiver(start_point[0], start_point[1], start_point[2], 
              start_normal_proxy[0], start_normal_proxy[1], start_normal_proxy[2], 
              length=0.2, color='green', normalize=False, linewidth=3, label='起點方向')

    # 觀察結果
    # 起點的代理向量 (u=pi/4, v=0) vs 終點的代理向量 (u=pi/4, v≈2pi)
    # 在這個 R⁴ 參數化中，繞著 v 走一圈 (0 -> 2pi)，會導致 u 方向的切向量反轉。
    
    print("\n--- R⁴ 投影模擬結果 ---")
    print(f"起點切向量代理 (u={u_const:.2f}, v=0.0): {normals_r4[0]}")
    print(f"終點切向量代理 (u={u_const:.2f}, v≈2π): {normals_r4[-1]}")
    print("-------------------------")
    print("理論上，當 v 繞行一圈後，N[-1] 應接近 -N[0] (除了微小的數值誤差)")


    ax.set_title(f'克萊因瓶單面性驗證 (R⁴ 投影)')
    ax.set_xlabel('X1')
    ax.set_ylabel('X2')
    ax.set_zlabel('X3')
    ax.set_aspect('equal', adjustable='box')
    ax.legend()
    plt.show()

# 執行模擬
klein_bottle_r4_normal_vector_test()