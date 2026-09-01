import sympy as sp
import numpy as np
import matplotlib.pyplot as plt

def vector_line_integral_demo():
    print("=== 線積分計算示範 (Line Integral) ===")
    print("情境：計算力場 F = [-y, x] 沿著單位圓逆時針路徑所做的功")
    
    # ==========================================
    # Part 1: 符號解 (Exact Solution with SymPy)
    # ==========================================
    t = sp.symbols('t')
    
    # 1. 定義參數化路徑 r(t)
    # 單位圓：x = cos(t), y = sin(t), t 從 0 到 2*pi
    r_x = sp.cos(t)
    r_y = sp.sin(t)
    
    # 2. 定義向量場 F(x, y) = [-y, x]
    # 將路徑 r(t) 代入向量場，變成 F(t)
    F_x = -r_y  # -sin(t)
    F_y = r_x   # cos(t)
    
    # 3. 計算路徑的微分 dr = [dx/dt, dy/dt] * dt
    dr_x = sp.diff(r_x, t) # -sin(t)
    dr_y = sp.diff(r_y, t) # cos(t)
    
    # 4. 計算點積 (Dot Product): F · dr
    #這代表在每一瞬間，力場在移動方向上的分量
    dot_product = F_x * dr_x + F_y * dr_y
    # (-sin(t)) * (-sin(t)) + (cos(t)) * (cos(t)) = sin^2 + cos^2 = 1
    
    # 5. 積分
    work_symbolic = sp.integrate(dot_product, (t, 0, 2*sp.pi))
    
    print(f"\n[符號運算結果]")
    print(f"被積函數 (F · dr/dt): {sp.simplify(dot_product)}")
    print(f"精確積分結果: {work_symbolic}")
    print(f"數值: {float(work_symbolic):.4f}")

    # ==========================================
    # Part 2: 數值解 (Numerical Solution with NumPy)
    # ==========================================
    # 1. 將路徑切分成 1000 個小段 (dt)
    N = 1000
    t_vals = np.linspace(0, 2*np.pi, N)
    dt = t_vals[1] - t_vals[0]
    
    # 2. 計算路徑上每個點的座標
    x_vals = np.cos(t_vals)
    y_vals = np.sin(t_vals)
    
    # 3. 計算路徑上每個點的力場向量 F
    Fx_vals = -y_vals
    Fy_vals = x_vals
    
    # 4. 計算位移向量 dr (dx, dy)
    # 使用 gradient 或 diff 來近似微分
    dx_vals = np.gradient(x_vals) # 注意：這其實是 dx/dn，要乘上間距才精確，但這裡我們直接用累加法
    dy_vals = np.gradient(y_vals)
    
    # 更直觀的物理寫法：黎曼和 (Riemann Sum)
    # Work = sum( F · dr )
    # F · dr = Fx * dx + Fy * dy
    work_numerical = np.sum(Fx_vals * dx_vals + Fy_vals * dy_vals)
    
    # 修正：np.gradient 預設間距是 1，我們需要還原真實間距
    # 實際上 gradient 已經處理了前後差分，但這裡是離散點索引
    # 我們改用簡單的 F dot (dr/dt) * dt
    dx_dt = -np.sin(t_vals)
    dy_dt = np.cos(t_vals)
    dot_prod_vals = Fx_vals * dx_dt + Fy_vals * dy_dt
    
    # 使用梯形積分法 (Trapezoidal rule) 獲得更高精度
    work_numerical = np.trapz(dot_prod_vals, t_vals)

    print(f"\n[數值運算結果]")
    print(f"切分數量: {N}")
    print(f"積分結果: {work_numerical:.4f}")
    
    # ==========================================
    # Part 3: 視覺化 (Visualization)
    # ==========================================
    plt.figure(figsize=(8, 8))
    
    # 畫出力場 (Quiver)
    # 建立網格
    grid_x, grid_y = np.meshgrid(np.linspace(-1.5, 1.5, 20), 
                                 np.linspace(-1.5, 1.5, 20))
    grid_u = -grid_y
    grid_v = grid_x
    plt.quiver(grid_x, grid_y, grid_u, grid_v, color='lightgray', alpha=0.5)
    
    # 畫出路徑 (Circle)
    plt.plot(x_vals, y_vals, 'b-', linewidth=2, label='Path (C)')
    
    # 畫出路徑上的幾個力向量 (紅色箭頭)
    # 每隔 100 點畫一支箭頭，示範該點受到的力
    idx = np.arange(0, N, 100)
    plt.quiver(x_vals[idx], y_vals[idx], 
               Fx_vals[idx], Fy_vals[idx], 
               color='red', scale=15, label='Force F on Path')

    # 畫出移動方向 dr (綠色箭頭)
    plt.quiver(x_vals[idx], y_vals[idx], 
               dx_dt[idx], dy_dt[idx], 
               color='green', scale=15, label='Velocity dr/dt')

    plt.title(f"Line Integral Visualization\nWork = {work_numerical:.2f} (Exact: 2π)", fontsize=14)
    plt.axis('equal')
    plt.legend(loc='upper right')
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    vector_line_integral_demo()