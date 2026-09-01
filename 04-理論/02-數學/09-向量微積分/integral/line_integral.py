# --- 檔案名稱: line_integral.py ---
import numpy as np

def calculate_line_integral(vector_field_func, path_func, t_range, N=1000):
    """
    計算線積分的通用函數: ∫ F · dr
    """
    t_vals = np.linspace(t_range[0], t_range[1], N)
    dt = t_vals[1] - t_vals[0]
    
    # 計算 r(t)
    r_vals = np.array([path_func(t) for t in t_vals])
    
    # 計算 dr/dt (速度向量)
    dr_dt = np.gradient(r_vals, dt, axis=0)
    
    # 計算 F(r(t))
    F_vals = np.array([vector_field_func(*point) for point in r_vals])
    
    # 計算 F · dr/dt
    integrand = np.sum(F_vals * dr_dt, axis=1)
    
    # 積分
    result = np.trapz(integrand, t_vals)
    return result