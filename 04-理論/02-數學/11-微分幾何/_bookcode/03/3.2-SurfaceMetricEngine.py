import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class SurfaceMetricEngine:
    def __init__(self, u, v, r_exprs):
        """
        初始化曲面度量引擎。
        
        Args:
            u, v: SymPy 符號變數
            r_exprs: 列表 [x(u,v), y(u,v), z(u,v)]
        """
        self.u = u
        self.v = v
        self.r = sp.Matrix(r_exprs)
        
        # 1. 計算切向量 (Tangent Vectors)
        self.r_u = self.r.diff(u)
        self.r_v = self.r.diff(v)
        
        # 2. 計算第一基本形式係數 (Metric Coefficients)
        # E = <r_u, r_u>
        self.E = self.r_u.dot(self.r_u)
        # F = <r_u, r_v>
        self.F = self.r_u.dot(self.r_v)
        # G = <r_v, r_v>
        self.G = self.r_v.dot(self.r_v)
        
        # 3. 計算度量行列式與面積元素 (sqrt(det(g)))
        self.det_g = self.E * self.G - self.F**2
        self.sqrt_det_g = sp.sqrt(self.det_g)

    def print_metric(self):
        """漂亮印出度量張量公式"""
        print("--- 第一基本形式 (First Fundamental Form) ---")
        print(f"切向量 r_u: {self.r_u.T}")
        print(f"切向量 r_v: {self.r_v.T}")
        print("-" * 20)
        print(f"E (g_11) = {sp.simplify(self.E)}")
        print(f"F (g_12) = {sp.simplify(self.F)}")
        print(f"G (g_22) = {sp.simplify(self.G)}")
        print("-" * 20)
        print(f"面積元素 dA = {sp.simplify(self.sqrt_det_g)} du dv")
        print("=" * 40 + "\n")

    def numerical_area(self, u_range, v_range):
        """
        使用數值積分計算曲面面積。
        Integral( sqrt(EG-F^2) du dv )
        """
        # 將符號表達式轉換為 Python 函數 (Lambdify)
        area_func = sp.lambdify((self.u, self.v), self.sqrt_det_g, 'numpy')
        
        # 使用 SciPy 的 dblquad 進行雙重積分，或者簡單網格求和
        # 這裡為了展示清晰，使用簡單的黎曼和 (Riemann Sum)
        u_vals = np.linspace(u_range[0], u_range[1], 100)
        v_vals = np.linspace(v_range[0], v_range[1], 100)
        
        du = u_vals[1] - u_vals[0]
        dv = v_vals[1] - v_vals[0]
        
        # 建立網格
        U, V = np.meshgrid(u_vals, v_vals)
        DA_values = area_func(U, V)
        
        total_area = np.sum(DA_values) * du * dv
        return total_area

    def plot_surface(self, u_range, v_range):
        """繪製 3D 曲面"""
        fx = sp.lambdify((self.u, self.v), self.r[0], 'numpy')
        fy = sp.lambdify((self.u, self.v), self.r[1], 'numpy')
        fz = sp.lambdify((self.u, self.v), self.r[2], 'numpy')
        
        u = np.linspace(u_range[0], u_range[1], 50)
        v = np.linspace(v_range[0], v_range[1], 50)
        U, V = np.meshgrid(u, v)
        
        X = fx(U, V)
        Y = fy(U, V)
        Z = fz(U, V)
        
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # 使用 viridis 顏色映射，alpha 設定透明度
        surf = ax.plot_surface(X, Y, Z, cmap='viridis', edgecolor='none', alpha=0.8)
        
        ax.set_title("Surface Visualization")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        # 保持比例，避免環面看起來像橢圓
        ax.set_box_aspect([np.ptp(X), np.ptp(Y), np.ptp(Z)]) 
        
        plt.show()

# ==========================================
# 主程式執行區
# ==========================================

if __name__ == "__main__":
    sp.init_printing(use_unicode=True)
    
    # 定義符號
    u, v = sp.symbols('u v', real=True)
    R, r = sp.symbols('R r', real=True, positive=True) # R: 大半徑, r: 小半徑
    
    # --- 案例: 環面 (Torus) ---
    # u: 大圓的角度 (0 ~ 2pi)
    # v: 小圓（管子截面）的角度 (0 ~ 2pi)
    print(">>> 分析環面 (Torus) <<<")
    
    x = (R + r * sp.cos(v)) * sp.cos(u)
    y = (R + r * sp.cos(v)) * sp.sin(u)
    z = r * sp.sin(v)
    
    torus_engine = SurfaceMetricEngine(u, v, [x, y, z])
    torus_engine.print_metric()
    
    # --- 數值驗證 ---
    # 設定具體數值: R=3, r=1
    R_val, r_val = 3.0, 1.0
    
    # 我們需要重新初始化一個帶數值的引擎，或者使用 substitute (這裡為了程式簡潔，使用 sub)
    # 替換 R, r 為數值
    metric_subs = torus_engine.sqrt_det_g.subs({R: R_val, r: r_val})
    
    # 建立臨時函數計算面積
    # 理論面積 = (2 * pi * R) * (2 * pi * r) = 4 * pi^2 * R * r
    theoretical_area = 4 * (np.pi**2) * R_val * r_val
    
    # 使用我們的方法計算
    # 這裡我們稍微作弊，因為類別裡面是用 self.sqrt_det_g，我們需要一個有數值的實例
    # 為了方便，我們直接構建數值版本的表達式
    
    # 重建數值版表達式
    x_num = (R_val + r_val * sp.cos(v)) * sp.cos(u)
    y_num = (R_val + r_val * sp.cos(v)) * sp.sin(u)
    z_num = r_val * sp.sin(v)
    
    numeric_engine = SurfaceMetricEngine(u, v, [x_num, y_num, z_num])
    
    print(f"計算數值面積 (R={R_val}, r={r_val})...")
    calc_area = numeric_engine.numerical_area([0, 2*np.pi], [0, 2*np.pi])
    
    print(f"理論面積: {theoretical_area:.4f}")
    print(f"數值積分: {calc_area:.4f}")
    print(f"誤差: {abs(theoretical_area - calc_area):.4e}")
    
    # 繪圖
    print("\n顯示 3D 圖形...")
    numeric_engine.plot_surface([0, 2*np.pi], [0, 2*np.pi])