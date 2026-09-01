import numpy as np
import itertools

# ==========================================
# 1. 數值微積分核心
# ==========================================

def partial_derivative(f, p, index, h=1e-5):
    p_arr = np.array(p, dtype=float)
    p_plus = p_arr.copy()
    p_plus[index] += h
    p_minus = p_arr.copy()
    p_minus[index] -= h
    return (f(p_plus) - f(p_minus)) / (2 * h)

def gradient(f, p):
    n = len(p)
    return np.array([partial_derivative(f, p, i) for i in range(n)])

# ==========================================
# 2. 向量場與李括號
# ==========================================

class VectorField:
    def __init__(self, func_of_p, name="V"):
        self.func = func_of_p
        self.name = name
        
    def __call__(self, f):
        """作用於函數 f (方向導數)"""
        def resulting_scalar_field(p):
            v_at_p = np.array(self.func(p), dtype=float)
            grad_f = gradient(f, p)
            return np.dot(grad_f, v_at_p)
        return resulting_scalar_field
    
    def at(self, p):
        return np.array(self.func(p), dtype=float)
    
    def __repr__(self):
        return self.name

def lie_bracket(u, v):
    """計算 [u, v]"""
    def bracket_func(p):
        p = np.array(p, dtype=float)
        h = 1e-5
        u_val = u.at(p)
        v_val = v.at(p)
        # 數值導數 (u·∇)v - (v·∇)u
        term1 = (v.at(p + h * u_val) - v.at(p - h * u_val)) / (2 * h)
        term2 = (u.at(p + h * v_val) - u.at(p - h * v_val)) / (2 * h)
        return term1 - term2
    return VectorField(bracket_func, name=f"[{u.name},{v.name}]")

# ==========================================
# 3. k-form 類別 (關鍵)
# ==========================================

class Form:
    def __init__(self, degree, evaluator):
        """
        degree: 階數 k (0, 1, 2...)
        evaluator: 
           若 k=0: func(p) -> float
           若 k>0: func(v1, ..., vk) -> scalar_field(p)
        """
        self.k = degree
        self.op = evaluator

    def __call__(self, *vectors):
        # 如果是 0-form，不接受向量，直接回傳函數本身
        if self.k == 0:
            if len(vectors) > 0:
                raise ValueError("0-form 不接受向量輸入")
            return self.op
            
        # 驗證輸入數量
        if len(vectors) != self.k:
            raise ValueError(f"{self.k}-form 需要 {self.k} 個向量，但收到 {len(vectors)} 個")
            
        return self.op(*vectors)

# ==========================================
# 4. 通用外微分算子 d (The Palais Formula)
# ==========================================

def d(omega):
    """
    接收一個 k-form，回傳一個 (k+1)-form
    """
    k = omega.k
    
    # 回傳的新函數：接收 k+1 個向量
    def d_omega_evaluator(*vectors):
        # vectors 是一個 tuple，包含 X_0, ..., X_k
        n = len(vectors) # 應該等於 k + 1
        
        # 結果是一個標量場函數 f(p)
        def field_at_p(p):
            total = 0.0
            
            # --- 第一部分：Σ (-1)^i X_i ( ω(..., ^Xi, ...) ) ---
            for i in range(n):
                X_i = vectors[i]
                
                # 建立排除 X_i 的列表
                others = vectors[:i] + vectors[i+1:]
                
                # 計算 ω(others)
                # 注意：如果 ω 是 0-form，others 是空 list，這也沒問題
                inner_scalar_field = omega(*others)
                
                # 讓 X_i 去微分這個標量場: X_i(g)(p)
                val = X_i(inner_scalar_field)(p)
                
                # 加上符號 (-1)^i
                if i % 2 == 1:
                    total -= val
                else:
                    total += val
            
            # --- 第二部分：Σ (-1)^(i+j) ω([Xi, Xj], ...) ---
            # 只有當輸入向量至少有 2 個 (即 k+1 >= 2, k >= 1) 時才有這項
            if n >= 2:
                for i in range(n):
                    for j in range(i + 1, n):
                        X_i = vectors[i]
                        X_j = vectors[j]
                        
                        # 計算 Lie Bracket
                        bracket = lie_bracket(X_i, X_j)
                        
                        # 建立參數列表： [bracket] + others (排除 i, j)
                        others = vectors[:i] + vectors[i+1:j] + vectors[j+1:]
                        args = (bracket,) + others
                        
                        # 計算 ω([Xi, Xj], ...)
                        val = omega(*args)(p)
                        
                        # 加上符號 (-1)^(i+j)
                        sign = (-1)**(i + j)
                        total += sign * val
            
            return total
        return field_at_p

    # 回傳新的 Form 物件，階數 + 1
    return Form(k + 1, d_omega_evaluator)

# ==========================================
# 5. 測試腳本
# ==========================================

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
    v = VectorField(lambda p: [1, 3, 0], name="v")
    
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
    
    u = VectorField(lambda p: [1, 0, 0], name="∂x")
    v = VectorField(lambda p: [0, 1, 0], name="∂y")
    
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
    w = VectorField(lambda p: [0, 0, 1], name="∂z")
    
    # 這裡我們使用稍複雜的變動向量場來確保 Lie Bracket 項有被運算到
    v_complex = VectorField(lambda p: [p[1], p[0], 0], name="V_mix")
    
    val_zero = d2_omega(u, v_complex, w)(p_test)
    print(f"驗證 d^2 = 0")
    print(f"計算 d(dω)(u, v_mix, w): {val_zero:.10f}")
    
    if abs(val_zero) < 1e-4:
        print("✅ 通用算子 d 運作正常，平方性質驗證成功。")
    else:
        print("❌ 驗證失敗。")