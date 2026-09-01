import sympy as sp

def verify_ftc():
    print("=== 驗證微積分基本定理 (FTC) [1D -> 0D] ===")
    
    # 1. 定義變數
    x = sp.symbols('x')
    
    # 2. 定義 0-形式 ω = f(x)
    f = sp.exp(x) * sp.sin(x)  # 選一個稍微複雜的函數
    print(f"1. 形式 ω (0-form) = {f}")
    
    # 3. 計算 dω (1-form)
    # dω = f'(x) dx
    df = sp.diff(f, x)
    print(f"2. 外微分 dω = ({df}) dx")
    
    # 4. 定義流形 M (區間)
    a, b = 0, sp.pi # 積分區間 [0, π]
    print(f"3. 流形 M: 区間 [{a}, {b}]")
    
    # ================= LHS: ∫_M dω (定積分) =================
    # 這裡只有一個變數，不需要 Jacobian 轉換，直接積分
    lhs_value = sp.integrate(df, (x, a, b))
    print(f"4. [LHS] 區間積分結果: {lhs_value}")
    
    # ================= RHS: ∫_∂M ω (邊界求值) =================
    # 邊界 ∂M 是點集 {b} (正向) 和 {a} (負向)
    # ∫_∂M ω = ω(b) - ω(a)
    
    val_b = f.subs(x, b)
    val_a = f.subs(x, a)
    rhs_value = val_b - val_a
    print(f"5. [RHS] 邊界求值 (f(b)-f(a)): {rhs_value}")
    
    print(f"驗證: {lhs_value} == {rhs_value} ? {lhs_value == rhs_value}\n")

verify_ftc()