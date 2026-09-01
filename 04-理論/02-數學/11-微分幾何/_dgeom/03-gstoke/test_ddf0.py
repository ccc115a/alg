from dgeom import TangentVector, Form, d, HyperCube, integrate_form
import numpy as np

if __name__ == "__main__":
    print("=== 通用外微分 d 測試 ===\n")
    
    # 定義測試點
    p_test = [1.0, 2.0, 3.0] 
    print(f"測試點 p: {p_test}\n")

    # --- 案例 1: 0-form -> 1-form ---
    # f = x^2 y
    def f_func(p): return (p[0]**2) * p[1]
    
    form0 = Form(0, f_func)
    print(f"0-form f = x^2 y")
    print(f"f(p) = {f_func(p_test)}")

    # 計算 df
    form1 = d(form0) # 這是 1-form
    
    # 定義向量 v = (1, 3, 0)
    v = TangentVector(lambda p: [1, 3, 0], name="v")
    
    # df(v) 應該等於 v(f)
    res_df = form1(v)(p_test)
    res_vf = v(form0())(p_test) # form0() 回傳 f 本身
    
    print(f"向量 v = {v.at(p_test)}")
    print(f"df(v) = {res_df:.5f}")
    print(f"v(f)  = {res_vf:.5f}")
    print(f"驗證: {np.isclose(res_df, res_vf)}\n")

    # --- 案例 2: 1-form -> 2-form ---
    # 定義一個 1-form ω = y dx
    # 數學定義：ω(v) = v_x * y
    def omega_func(v):
        def field(p):
            v_val = v.at(p)
            return v_val[0] * p[1] # v_x * y
        return field
    
    omega = Form(1, omega_func)
    
    # 理論計算：
    # ω = y dx
    # dω = dy ∧ dx = - dx ∧ dy
    # 如果我們選 u=(1,0,0) (x方向), v=(0,1,0) (y方向)
    # dω(u, v) 應該是 -1
    
    u = TangentVector(lambda p: [1, 0, 0], name="∂x")
    v = TangentVector(lambda p: [0, 1, 0], name="∂y")
    
    d_omega = d(omega) # 這是 2-form
    
    val = d_omega(u, v)(p_test)
    print(f"1-form ω = y dx")
    print(f"計算 dω(∂x, ∂y) 數值: {val:.5f}")
    print(f"理論值應為 -1.0")
    print(f"驗證: {np.isclose(val, -1.0)}\n")

    # --- 案例 3: 驗證 d^2 = 0 (從 1-form 到 3-form) ---
    # 我們讓上面那個 ω 繼續被微分
    # dω 已經是 2-form 了
    # d(dω) 應該是 3-form，且值為 0
    
    d2_omega = d(d_omega) # 3-form
    
    # 隨便選三個向量
    w = TangentVector(lambda p: [0, 0, 1], name="∂z")
    
    # 這裡我們使用稍複雜的變動向量場來確保 Lie Bracket 項有被運算到
    v_complex = TangentVector(lambda p: [p[1], p[0], 0], name="V_mix")
    
    val_zero = d2_omega(u, v_complex, w)(p_test)
    print(f"驗證 d^2 = 0")
    print(f"計算 d(dω)(u, v_mix, w): {val_zero:.10f}")
    
    if abs(val_zero) < 1e-4:
        print("✅ 通用算子 d 運作正常，平方性質驗證成功。")
    else:
        print("❌ 驗證失敗。")