# 數學原理解說 -- https://gemini.google.com/app/74730454e47a988b
from dgeom.sym import Form, TangentVector, d, ParametricPatch, integrate_form
import sympy as sp

def test_dd_f_is_zero():
    print("\n=== 驗證 d(d(f)) = 0 ===")
    
    # 1. 定義座標與純量場 f
    x, y, z = sp.symbols('x y z')
    coords = [x, y, z]
    
    # 定義一個非線性的純量函數 f
    f_expr = x**3 * sp.sin(y) * z**2
    
    # 0-form (純量場)
    # 注意：在我們的定義中，0-form 的 evaluator 不接受參數，直接回傳表達式
    f_form = Form(0, lambda: f_expr)
    
    print(f"純量場 f = {f_expr}")

    # 2. 計算 d(f) 和 d(d(f))
    df = d(f_form)      # 1-form
    ddf = d(df)         # 2-form
    
    print("已建構 2-form: d(d(f))")

    # 3. 定義兩個一般的符號向量場 U, V
    # 我們使用 undefined functions u_x(x,y,z) 等，代表任意向量場
    # 這樣可以確保測試涵蓋了 [U, V] 非零的一般情況
    
    u_funcs = [sp.Function(name)(x, y, z) for name in ['u_x', 'u_y', 'u_z']]
    v_funcs = [sp.Function(name)(x, y, z) for name in ['v_x', 'v_y', 'v_z']]
    
    U = TangentVector(u_funcs, coords, name="U")
    V = TangentVector(v_funcs, coords, name="V")
    
    print("定義符號向量場 U, V (分量為任意函數，非交換)...")

    # 4. 評估 d(d(f))(U, V)
    # 根據定義：d(df)(U, V) = U(df(V)) - V(df(U)) - df([U, V])
    #                      = U(V(f))  - V(U(f))  - [U, V](f)
    # 這應該要自動化簡為 0
    result = ddf(U, V)
    
    print("正在計算 d(d(f))(U, V) 的符號表達式...")
    simplified_result = sp.simplify(result)
    
    print(f"結果: {simplified_result}")
    
    if simplified_result == 0:
        print("驗證成功: d(d(f)) 恆等於 0")
    else:
        print("驗證失敗: 結果不為 0")
        # 如果失敗，通常是因為表達式太複雜 sympy 沒有完全化簡，
        # 或者 lie_bracket 的實作有錯

def test_stoke_theorem():
    # 定義座標系
    x, y, z = sp.symbols('x y z')
    coords = [x, y, z]

    # 定義一個 1-form: omega = P dx + Q dy + R dz
    # 這裡選用: omega = -y dx + x dy + 0 dz
    # 這是標準的旋轉場
    
    # 建構基本 1-forms
    # dx 是一個 operator: dx(V) = V.x_component
    def dx_op(V): return V.components[0]
    def dy_op(V): return V.components[1]
    def dz_op(V): return V.components[2]
    
    dx = Form(1, dx_op)
    dy = Form(1, dy_op)
    dz = Form(1, dz_op)
    
    # 組合 omega (注意：在 Form 的定義中，我們需要手動定義加法和乘法，
    # 或者直接定義 omega 的 evaluator)
    # 為了簡單起見，我們直接寫 evaluator
    def omega_eval(V):
        return -y * V.components[0] + x * V.components[1]
    
    omega = Form(1, omega_eval)
    
    # 計算 d(omega)
    # 理論上 d(-y dx + x dy) = -dy^dx + dx^dy = dx^dy + dx^dy = 2 dx^dy
    d_omega = d(omega)
    
    # === 測試區域：拋物面 Patch ===
    # z = x^2 + y^2 defined on [-1, 1] x [-1, 1]
    u, v = sp.symbols('u v')
    def paraboloid_map(params):
        uu, vv = params
        return [uu, vv, uu**2 + vv**2]
    
    patch = ParametricPatch([u, v], [(-1, 1), (-1, 1)], paraboloid_map)
    
    print("正在計算面積分 (LHS: int_Omega d_omega)...")
    lhs = integrate_form(d_omega, patch, coords)
    print(f"Area Integral Result: {lhs}")
    
    print("正在計算線積分 (RHS: int_boundary omega)...")
    rhs = 0
    boundaries = patch.get_boundaries()
    for b_domain, sign in boundaries:
        val = integrate_form(omega, b_domain, coords)
        rhs += sign * val
        
    print(f"Boundary Integral Result: {rhs}")
    
    assert sp.simplify(lhs - rhs) == 0
    print("Stokes Theorem Verified!")

if __name__ == "__main__":
    # 執行 d^2 = 0 測試
    test_dd_f_is_zero()
    # 執行 Stokes 定理測試
    test_stoke_theorem()
