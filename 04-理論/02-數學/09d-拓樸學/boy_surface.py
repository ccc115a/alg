import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm

def plot_boys_surface():
    """使用參數方程式繪製 Boy's Surface (R P² 的浸入)。"""
    
    # 參數範圍
    # v: 從 0 到 pi (控制球面緯度)
    # u: 從 0 到 2*pi (控制球面經度)
    v_vals = np.linspace(0.001, np.pi, 60) 
    u_vals = np.linspace(0, 2 * np.pi, 60)
    u, v = np.meshgrid(u_vals, v_vals)
    
    # --- 1. 計算複數函式 Z1, Z2, Z3 ---
    
    # 常數項
    w = (u / 3.0) + np.pi/2 # 調整 u 的範圍和相位
    
    # 複數定義
    # Z1 = -i * exp(i*v) * cos(w) * sin(w)
    Z1_real = np.sin(v) * np.cos(w) * np.sin(w)
    Z1_imag = -np.cos(v) * np.cos(w) * np.sin(w)
    
    # Z2 = -i * exp(i*v) * cos(w - 2pi/3) * sin(w - 2pi/3)
    w_2 = w - 2 * np.pi / 3
    Z2_real = np.sin(v) * np.cos(w_2) * np.sin(w_2)
    Z2_imag = -np.cos(v) * np.cos(w_2) * np.sin(w_2)

    # Z3 = -i * exp(i*v) * cos(w + 2pi/3) * sin(w + 2pi/3)
    w_3 = w + 2 * np.pi / 3
    Z3_real = np.sin(v) * np.cos(w_3) * np.sin(w_3)
    Z3_imag = -np.cos(v) * np.cos(w_3) * np.sin(w_3)
    
    # --- 2. 應用主方程式 (計算 x, y, z 坐標) ---
    
    # 簡化 Z * (1 - Z_next * Z_prev)
    
    # --- X 坐標 (與 g1 相關) ---
    # Im( Z1 * (1 - Z2*Z3) )
    Z2Z3_real = Z2_real * Z3_real - Z2_imag * Z3_imag
    Z2Z3_imag = Z2_real * Z3_imag + Z2_imag * Z3_real
    
    Term1_real = Z1_real * (1 - Z2Z3_real) - Z1_imag * (-Z2Z3_imag)
    Term1_imag = Z1_real * (-Z2Z3_imag) + Z1_imag * (1 - Z2Z3_real)
    
    X = (3.0/2.0) * Term1_imag # 取虛部 Im()
    
    # --- Y 坐標 (與 g2 相關) ---
    # Im( Z2 * (1 - Z3*Z1) )
    Z3Z1_real = Z3_real * Z1_real - Z3_imag * Z1_imag
    Z3Z1_imag = Z3_real * Z1_imag + Z3_imag * Z1_real
    
    Term2_real = Z2_real * (1 - Z3Z1_real) - Z2_imag * (-Z3Z1_imag)
    Term2_imag = Z2_real * (-Z3Z1_imag) + Z2_imag * (1 - Z3Z1_real)
    
    Y = (3.0/2.0) * Term2_imag
    
    # --- Z 坐標 (與 g3 相關) ---
    # Im( Z3 * (1 - Z1*Z2) )
    Z1Z2_real = Z1_real * Z2_real - Z1_imag * Z2_imag
    Z1Z2_imag = Z1_real * Z2_imag + Z1_imag * Z2_real
    
    Term3_real = Z3_real * (1 - Z1Z2_real) - Z3_imag * (-Z1Z2_imag)
    Term3_imag = Z3_real * (-Z1Z2_imag) + Z3_imag * (1 - Z1Z2_real)
    
    Z = (3.0/2.0) * Term3_imag
    
    # --- 3. 繪圖 ---
    
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # 使用 plot_surface 繪製
    ax.plot_surface(X, Y, Z, 
                    cmap=cm.PuBuGn, 
                    rstride=1, cstride=1,
                    linewidth=0, antialiased=True, alpha=0.9)
    
    # 設定視圖
    ax.set_title("Boy's Surface (實射影平面 R P² 的浸入)")
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_aspect('equal')
    ax.view_init(elev=20, azim=45) # 設置一個好的視角
    plt.show()

# 執行繪製 Boy's Surface
plot_boys_surface()