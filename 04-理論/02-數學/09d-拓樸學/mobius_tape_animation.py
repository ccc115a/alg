import numpy as np
import matplotlib.pyplot as plt

def mobius_strip_normal_vector_test():
    """
    計算並視覺化莫比烏斯帶的法向量，展示其單面性。
    當點環繞一圈 (u: 0 -> 2*pi) 時，法向量將會反轉。
    """
    R = 1.0  # 半徑
    v_const = 0.2 # 選擇一條固定的寬度線 (例如 v=0.2) 進行測試
    
    # u 參數，從 0 到 2*pi，共 100 個點
    u_vals = np.linspace(0, 2 * np.pi, 100, endpoint=False)
    
    # 存儲軌跡點和法向量
    points = []
    normals = []
    
    for u in u_vals:
        # --- 1. 計算點的坐標 S(u, v_const) ---
        cu = np.cos(u)
        su = np.sin(u)
        c2 = np.cos(u / 2)
        s2 = np.sin(u / 2)
        v = v_const
        
        # S(u, v)
        x = (R + v * c2) * cu
        y = (R + v * c2) * su
        z = v * s2
        points.append([x, y, z])
        
        # --- 2. 計算偏導數 (切向量) ---
        
        # dS/du (切向量 1)
        dx_du = (-v/2 * s2) * cu - (R + v * c2) * su
        dy_du = (-v/2 * s2) * su + (R + v * c2) * cu
        dz_du = v / 2 * c2
        dS_du = np.array([dx_du, dy_du, dz_du])
        
        # dS/dv (切向量 2)
        dx_dv = c2 * cu
        dy_dv = c2 * su
        dz_dv = s2
        dS_dv = np.array([dx_dv, dy_dv, dz_dv])
        
        # --- 3. 計算法向量 N = dS/du x dS/dv (叉積) ---
        
        normal = np.cross(dS_du, dS_dv)
        
        # 進行正規化 (確保向量長度一致，方便視覺化)
        normal = normal / np.linalg.norm(normal)
        normals.append(normal)

    # 轉換為 Numpy 陣列
    points = np.array(points)
    normals = np.array(normals)

    # --- 4. 繪圖視覺化 ---
    
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    # 繪製莫比烏斯帶的基本形狀 (簡化繪製，以節省資源)
    u_full = np.linspace(0, 2 * np.pi, 50)
    v_full = np.linspace(-0.3, 0.3, 20)
    u_full, v_full = np.meshgrid(u_full, v_full)
    X = (R + v_full * np.cos(u_full / 2)) * np.cos(u_full)
    Y = (R + v_full * np.cos(u_full / 2)) * np.sin(u_full)
    Z = v_full * np.sin(u_full / 2)
    ax.plot_surface(X, Y, Z, color='lightgray', alpha=0.3, linewidth=0)
    
    # 繪製點的軌跡
    ax.plot(points[:, 0], points[:, 1], points[:, 2], color='blue', linewidth=3, label=f'點軌跡 (v={v_const})')
    
    # 繪製法向量 (只繪製每 10 個點，避免太過擁擠)
    Q = ax.quiver(points[::10, 0], points[::10, 1], points[::10, 2], 
                  normals[::10, 0], normals[::10, 1], normals[::10, 2], 
                  length=0.4, color='red', normalize=False, label='法向量 N')

    # 特別標註起點和終點的法向量
    start_point = points[0]
    start_normal = normals[0]
    end_normal = normals[-1] # 最後一個點的法向量（u 接近 2pi）

    # 顯示開始的法向量
    ax.quiver(start_point[0], start_point[1], start_point[2], 
              start_normal[0], start_normal[1], start_normal[2], 
              length=0.4, color='green', normalize=False, linewidth=3, label='起點法向量')

    # 顯示結束的法向量
    # 注意：由於 u_vals 設置了 endpoint=False，所以最後一個點 (normals[-1]) 非常接近起點 (normals[0])
    # 觀察 normals[-1] 的方向，它應該幾乎和 normals[0] 完全相反。

    ax.set_title('莫比烏斯帶單面性驗證：法向量反轉')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_aspect('equal', adjustable='box')
    ax.legend()
    plt.show()

# 執行模擬
mobius_strip_normal_vector_test()
