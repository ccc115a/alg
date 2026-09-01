import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def stereographic_projection_north(x, y, z):
    """ 從北極 (0,0,1) 投影到 z=0 平面 """
    # 公式: X = x / (1-z), Y = y / (1-z)
    # 注意避免除以零 (z=1)
    denom = 1 - z
    # 使用遮罩處理奇異點 (為了繪圖穩定)
    safe_denom = np.where(np.abs(denom) < 1e-6, np.nan, denom)
    return x / safe_denom, y / safe_denom

def stereographic_projection_south(x, y, z):
    """ 從南極 (0,0,-1) 投影到 z=0 平面 """
    # 公式: U = x / (1+z), V = y / (1+z)
    denom = 1 + z
    safe_denom = np.where(np.abs(denom) < 1e-6, np.nan, denom)
    return x / safe_denom, y / safe_denom

def run_atlas_demo():
    print("--- 流形圖冊演示：立體投影 ---")
    
    # 1. 定義流形上的一條路徑 (大圓)
    # 參數 t: 0 -> 2pi
    t = np.linspace(0, 2 * np.pi, 200)
    
    # 路徑：一個傾斜的大圓，確保它同時經過北半球和南半球
    # 透過旋轉矩陣讓圓傾斜
    angle = np.pi / 4 # 傾斜 45 度
    x_raw = np.cos(t)
    y_raw = np.sin(t)
    z_raw = np.zeros_like(t)
    
    # 繞 X 軸旋轉
    x = x_raw
    y = y_raw * np.cos(angle) - z_raw * np.sin(angle)
    z = y_raw * np.sin(angle) + z_raw * np.cos(angle)
    
    # 2. 計算兩張地圖上的坐標
    u_n, v_n = stereographic_projection_north(x, y, z)
    u_s, v_s = stereographic_projection_south(x, y, z)
    
    # 3. 視覺化
    fig = plt.figure(figsize=(15, 5))
    
    # --- 子圖 1: 3D 球面與路徑 ---
    ax3d = fig.add_subplot(132, projection='3d')
    # 繪製參考球面 (網格)
    u_grid = np.linspace(0, 2 * np.pi, 30)
    v_grid = np.linspace(0, np.pi, 20)
    xs = np.outer(np.cos(u_grid), np.sin(v_grid))
    ys = np.outer(np.sin(u_grid), np.sin(v_grid))
    zs = np.outer(np.ones(np.size(u_grid)), np.cos(v_grid))
    ax3d.plot_wireframe(xs, ys, zs, color='gray', alpha=0.1)
    
    # 繪製路徑
    ax3d.plot(x, y, z, 'r-', linewidth=3, label='Path on Manifold')
    # 標示北極南極
    ax3d.scatter([0], [0], [1], color='black', s=50, label='N')
    ax3d.scatter([0], [0], [-1], color='black', s=50, label='S')
    ax3d.set_title("Manifold M (Sphere)")
    ax3d.axis('off')

    # --- 子圖 2: 北極投影圖 (Chart 1) ---
    ax_n = fig.add_subplot(131)
    ax_n.plot(u_n, v_n, 'b-', linewidth=2)
    ax_n.set_title("Chart 1: North Projection\n(Undefined at N)")
    ax_n.set_xlabel("X")
    ax_n.set_ylabel("Y")
    ax_n.grid(True)
    ax_n.set_xlim(-3, 3)
    ax_n.set_ylim(-3, 3)
    ax_n.set_aspect('equal')
    # 標示：當路徑經過北極附近時，這裡會趨向無限大

    # --- 子圖 3: 南極投影圖 (Chart 2) ---
    ax_s = fig.add_subplot(133)
    ax_s.plot(u_s, v_s, 'g-', linewidth=2)
    ax_s.set_title("Chart 2: South Projection\n(Undefined at S)")
    ax_s.set_xlabel("U")
    ax_s.set_ylabel("V")
    ax_s.grid(True)
    ax_s.set_xlim(-3, 3)
    ax_s.set_ylim(-3, 3)
    ax_s.set_aspect('equal')
    
    plt.tight_layout()
    plt.show()

    # 4. 驗證過渡函數 (Transition Function)
    # 對於重疊區域 (赤道 z=0)，兩者關係應為倒數關係 (複平面上的 z -> 1/z_bar)
    # 在實數坐標下： (u, v) = (x/(x^2+y^2), y/(x^2+y^2))
    
    print("驗證過渡函數 (Transition Check):")
    # 選一個非赤道、非極點的索引
    idx = 10 
    X, Y = u_n[idx], v_n[idx]
    U, V = u_s[idx], v_s[idx]
    
    # 計算轉換
    denom_trans = X**2 + Y**2
    U_calc = X / denom_trans
    V_calc = Y / denom_trans
    
    print(f"點索引 {idx}:")
    print(f"  Chart N 坐標: ({X:.4f}, {Y:.4f})")
    print(f"  Chart S 坐標: ({U:.4f}, {V:.4f})")
    print(f"  由 N 算 S : ({U_calc:.4f}, {V_calc:.4f})")
    print(f"  誤差: {abs(U-U_calc) + abs(V-V_calc):.4e}")

if __name__ == "__main__":
    run_atlas_demo()