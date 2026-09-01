import sympy as sp

def analyze_coordinate_transform(name, new_vars, trans_funcs):
    """
    計算並分析坐標變換的雅可比矩陣與行列式。
    
    參數:
        name (str): 變換名稱
        new_vars (list): 新坐標系的變數符號 (例如 [r, theta, phi])
        trans_funcs (list): 舊坐標系關於新坐標的函數表達式 (例如 [x(r,..), y(r,..), z(r,..)])
    """
    print(f"--- 分析變換: {name} ---")
    
    # 1. 建構矩陣
    # X 為目標坐標向量 (如 x, y, z)
    # U 為來源坐標向量 (如 r, theta, phi)
    X = sp.Matrix(trans_funcs)
    U = sp.Matrix(new_vars)
    
    print(f"變數向量 U: {U.T}")
    print(f"變換函數 X: {X.T}")
    
    # 2. 計算雅可比矩陣 J (Jacobian Matrix)
    # SymPy 的 jacobian 方法會自動計算所有偏微分
    J = X.jacobian(U)
    
    print("\n[雅可比矩陣 J]:")
    sp.pprint(J) # Pretty print 輸出數學格式
    
    # 3. 計算行列式 (Determinant)
    # 這通常對應到體積元素的縮放因子
    det_J = J.det()
    
    print("\n[行列式 det(J) - 未化簡]:")
    sp.pprint(det_J)
    
    # 4. 化簡行列式
    # 使用 trigsimp 處理三角函數恆等式 (如 sin^2 + cos^2 = 1)
    det_J_simplified = sp.trigsimp(det_J)
    
    print("\n[行列式 det(J) - 化簡後]:")
    sp.pprint(det_J_simplified)
    print("-" * 30 + "\n")

# ==========================================
# 主程式執行區
# ==========================================

if __name__ == "__main__":
    # 設定符號輸出為 Unicode 格式，看起來比較像數學公式
    sp.init_printing(use_unicode=True)
    
    # 定義符號
    # r: 半徑, theta: 極角 (與 z 軸夾角), phi: 方位角 (xy 平面上的角度)
    r, theta, phi = sp.symbols('r theta phi', real=True, positive=True)
    
    # --- 案例 1: 球坐標變換 (Spherical Coordinates) ---
    # x = r sin(theta) cos(phi)
    # y = r sin(theta) sin(phi)
    # z = r cos(theta)
    
    x_expr = r * sp.sin(theta) * sp.cos(phi)
    y_expr = r * sp.sin(theta) * sp.sin(phi)
    z_expr = r * sp.cos(theta)
    
    analyze_coordinate_transform(
        name="球坐標 -> 笛卡兒坐標",
        new_vars=[r, theta, phi],
        trans_funcs=[x_expr, y_expr, z_expr]
    )

    # --- 案例 2: 極坐標變換 (Polar Coordinates - 2D) ---
    # x = r cos(theta)
    # y = r sin(theta)
    
    # 重新定義符號避免混淆
    r_2d, theta_2d = sp.symbols('r theta', real=True)
    
    analyze_coordinate_transform(
        name="極坐標 -> 笛卡兒坐標 (2D)",
        new_vars=[r_2d, theta_2d],
        trans_funcs=[r_2d * sp.cos(theta_2d), r_2d * sp.sin(theta_2d)]
    )