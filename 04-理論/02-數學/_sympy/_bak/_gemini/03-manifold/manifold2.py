from sympy import symbols, sin, cos, pi, pprint, simplify
from sympy.diffgeom import Manifold, Patch, CoordSystem, LieDerivative

def main():
    print("=== 1. 定義流形與符號 ===")
    m = Manifold('M', 2)
    p = Patch('P', m)
    
    # 定義符號 (建議加上 real=True)
    x, y = symbols('x y', real=True)
    r, theta = symbols('r theta', real=True, positive=True)

    print("=== 2. 定義座標系與轉換關係 ===")
    # 定義直角座標系 (rect 是物件)
    rect = CoordSystem('rect', p, [x, y])
    
    # 定義極座標系
    # 【關鍵修正】
    # Key: ('polar', rect) 
    #   - 'polar': 字串，代表正在建立的這個座標系名稱
    #   - rect:    變數(物件)，代表目標座標系，這樣 SymPy 才能讀取 x, y 的定義
    polar = CoordSystem('polar', p, [r, theta], relations={
        ('polar', rect): ( 
            (r, theta), 
            (r * cos(theta), r * sin(theta)) 
        )
    })

    print(f"座標系建立完成: {rect} <-> {polar}")

    print("\n=== 3. 準備場變數 ===")
    # 取得座標函數與基底
    # 務必使用系統回傳的 func，以確保拓撲連結正確
    x_func, y_func = rect.coord_functions()
    e_x, e_y = rect.base_vectors()
    
    r_func, theta_func = polar.coord_functions()
    
    # 定義向量場 V = y * (∂/∂x)
    V_rect = y_func * e_x
    print(f"直角座標向量場 V: {V_rect}")
    
    # 定義純量場 f = r^2
    f_polar = r_func**2
    print(f"目標純量場 f: {f_polar}")
    
    print("\n=== 4. 計算向量場作用 V(f) ===")
    print("正在計算 LieDerivative(V, f)...")
    
    try:
        # 使用 LieDerivative 進行計算
        # 這次 SymPy 應該能順利透過 rect 物件找到轉換路徑
        result = LieDerivative(V_rect, f_polar)
        
        print("結果 (未化簡):")
        pprint(result)
        
        print("\n結果 (化簡後):")
        final_res = simplify(result)
        pprint(final_res)
        
        print("\n=== 驗證 ===")
        print("V = y ∂/∂x, f = r^2 = x^2 + y^2")
        print("預期結果 (直角): 2xy")
        print("預期結果 (極座標): 2 * (r sin) * (r cos) = r^2 sin(2θ)")
        
    except Exception as e:
        print(f"運算失敗: {e}")
        # 如果還是出錯，印出詳細堆疊以便除錯
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()