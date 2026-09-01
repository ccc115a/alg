import sympy as sp

def metric_tensor(old_coords_funcs, new_params):
    """
    計算由參數函數定義的流形在新參數座標系下的度規張量。

    參數:
    - old_coords_funcs (list of SymPy expressions): 
        一個列表，包含舊座標 (例如 x, y, z) 關於新參數的函數表示。
        例如：[r * sp.cos(theta), r * sp.sin(theta)]
    - new_params (list of SymPy symbols): 
        一個列表，包含新座標或參數 (例如 r, theta) 的 SymPy 符號。
        例如：[r, theta]

    回傳:
    - G_bar (SymPy Matrix): 
        新參數座標系下的度規張量矩陣 G_bar。
    """
    
    # 1. 將舊座標函數表示為 SymPy 矩陣形式 (代表嵌入函數 X)
    X_func_matrix = sp.Matrix(old_coords_funcs)
    
    # 2. 計算雅可比矩陣 J (即 Lambda_inv)
    # J 是 X 相對於新參數 (u) 的偏微分矩陣: J_ik = partial x^i / partial u^k
    # 這裡的 X_func_matrix.jacobian(new_params) 正好計算 J
    J_matrix = X_func_matrix.jacobian(new_params)
    
    # 3. 計算度規張量 G_bar
    # 公式: G_bar = J^T * G_old * J
    # 由於我們假設舊座標系是歐幾里得空間 (G_old = I, 單位矩陣)
    # 所以簡化為: G_bar = J^T * J
    
    J_transpose = J_matrix.transpose()
    G_bar = J_transpose * J_matrix
    
    # 4. 簡化結果
    G_bar_simplified = G_bar.applyfunc(sp.simplify)
    
    return G_bar_simplified
