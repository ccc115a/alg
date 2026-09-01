from sympy import symbols, sin, cos, pi, pprint, simplify
from sympy.diffgeom import Manifold, Patch, CoordSystem

def main():
    print("=== 1. 定義流形與符號 (Manifold & Symbols) ===")
    m = Manifold('M', 2)
    p = Patch('P', m)
    
    # 定義符號 (務必加上 real=True, positive=True 幫助簡化)
    x, y = symbols('x y', real=True)
    r, theta = symbols('r theta', real=True, positive=True)

    print(f"流形: {m}")
    print("\n")


    print("=== 2. 定義座標系與轉換關係 (CoordSystems with Relations) ===")
    
    # 3. 定義直角座標系 (名稱為 'rect')
    rect = CoordSystem('rect', p, [x, y])
    
    # 4. 定義極座標系 (名稱為 'polar')
    # 【關鍵修正】 relations 的格式：
    # Key: ('from_name', 'to_name') -> 使用字串名稱
    # Value: ( (來源符號列表), (轉換公式列表) )
    polar = CoordSystem('polar', p, [r, theta], relations={
        ('polar', 'rect'): ( 
            (r, theta), 
            (r * cos(theta), r * sin(theta)) 
        )
    })

    # 顯示座標系資訊
    print(f"座標系 1: {rect} (變數: {rect.coord_functions()})")
    print(f"座標系 2: {polar} (變數: {polar.coord_functions()})")
    print("\n")


    print("=== 3. 座標點變換 (Point Transformation) ===")
    # 在極座標系定義一個點 (r=2, theta=pi/3)
    point_polar = polar.point([2, pi/3])
    print(f"極座標點 (r=2, theta=pi/3)")
    
    # 轉換到直角座標系
    try:
        coords_rect = rect.point_to_coords(point_polar)
        print(f"轉換為直角座標 (x, y):")
        pprint(coords_rect)
    except Exception as e:
        print(f"座標轉換失敗: {e}")
    print("\n")


    print("=== 4. 向量場變換 (Vector Field Transformation) ===")
    # 取得座標系的「座標函數」(BaseScalarField) 與「基底向量」(BaseVectorField)
    # 建議使用系統回傳的函數物件，而非最上面的 symbols
    x_func, y_func = rect.coord_functions()
    e_x, e_y = rect.base_vectors()
    
    r_func, theta_func = polar.coord_functions()
    
    # 定義向量場 V = y * (∂/∂x) (在直角座標系定義)
    V_rect = y_func * e_x
    print("直角座標向量場 V = y * ∂/∂x")
    
    # 定義純量場 f = r^2 (在極座標系定義)
    f_polar = r_func**2
    print("目標純量場 f = r^2")
    
    print("正在計算 V(f) (方向導數)...")
    # SymPy 會自動處理座標轉換：
    # 1. 識別 V_rect 是 rect 系統
    # 2. 識別 f_polar 是 polar 系統
    # 3. 利用 relations 將它們轉換到同一系統進行微分運算
    
    try:
        result = V_rect(f_polar)
        print("結果 (V(f)):")
        pprint(simplify(result))
        
        print("\n驗證說明:")
        print("V = y(∂/∂x)")
        print("f = x^2 + y^2 (= r^2)")
        print("V(f) = y * ∂(x^2 + y^2)/∂x = y * 2x = 2xy")
        print("代回極座標: 2 * (r sin) * (r cos) = r^2 sin(2θ)")
    except Exception as e:
        print(f"向量場運算失敗: {e}")

if __name__ == "__main__":
    main()