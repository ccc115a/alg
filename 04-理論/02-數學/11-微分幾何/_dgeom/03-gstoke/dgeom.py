import numpy as np
from scipy import integrate
import itertools

# ==========================================
# Part 1: 通用外微分算子 d (沿用上一版核心)
# ==========================================

def partial_derivative(f, p, index, h=1e-5):
    p_arr = np.array(p, dtype=float)
    p_plus = p_arr.copy(); p_plus[index] += h
    p_minus = p_arr.copy(); p_minus[index] -= h
    return (f(p_plus) - f(p_minus)) / (2 * h)

def gradient(f, p):
    return np.array([partial_derivative(f, p, i) for i in range(len(p))])

class TangentVector:
    def __init__(self, func_of_p, name="V"):
        self.func = func_of_p # func(p) -> array
        self.name = name
    def __call__(self, f): # 作用於函數 (方向導數)
        def resulting_scalar_field(p):
            return np.dot(gradient(f, p), self.func(p))
        return resulting_scalar_field
    def at(self, p): return np.array(self.func(p), dtype=float)

def lie_bracket(u, v):
    def bracket_func(p):
        h = 1e-5; p = np.array(p)
        u_val = u.at(p); v_val = v.at(p)
        term1 = (v.at(p + h * u_val) - v.at(p - h * u_val)) / (2 * h)
        term2 = (u.at(p + h * v_val) - u.at(p - h * v_val)) / (2 * h)
        return term1 - term2
    return TangentVector(bracket_func)

class Form:
    def __init__(self, degree, evaluator):
        self.k = degree
        self.op = evaluator # func(vectors)(p)
    def __call__(self, *vectors):
        if self.k == 0: return self.op
        if len(vectors) != self.k: raise ValueError(f"Need {self.k} vectors")
        return self.op(*vectors)

def d(omega):
    k = omega.k
    def d_omega_evaluator(*vectors): # vectors: X0...Xk
        def field_at_p(p):
            total = 0.0
            n = len(vectors)
            # Part A: Derivatives
            for i in range(n):
                X_i = vectors[i]
                others = vectors[:i] + vectors[i+1:]
                val = X_i(omega(*others))(p)
                total += val if i % 2 == 0 else -val
            # Part B: Lie Brackets
            if n >= 2:
                for i in range(n):
                    for j in range(i + 1, n):
                        bracket = lie_bracket(vectors[i], vectors[j])
                        others = vectors[:i] + vectors[i+1:j] + vectors[j+1:]
                        val = omega(bracket, *others)(p)
                        sign = (-1)**(i + j)
                        total += sign * val
            return total
        return field_at_p
    return Form(k + 1, d_omega_evaluator)

# ==========================================
# Part 2: 區域參數化與積分 (新增部分)
# ==========================================

class ParametrizedDomain:
    """
    代表一個 k 維區域，映射自參數空間 u_bounds
    map_func: u -> p (將參數座標 u 映射到物理空間 p)
    """
    def __init__(self, dim, u_bounds, map_func):
        self.dim = dim
        self.u_bounds = u_bounds # e.g. [(0,1), (0,1)]
        self.map_func = map_func

    def get_tangent_vectors(self, u_params):
        """
        計算該點的切向量基底 (Jacobian columns)
        即 ∂p/∂u1, ∂p/∂u2 ...
        """
        u = np.array(u_params, dtype=float)
        p_curr = self.map_func(u)
        dim_phys = len(p_curr)
        tangents = []
        h = 1e-5
        
        for i in range(self.dim):
            u_next = u.copy()
            u_next[i] += h
            p_next = self.map_func(u_next)
            # 數值微分計算切向量
            vec = (p_next - p_curr) / h
            tangents.append(vec)
            
        return tangents

def integrate_form(form, domain):
    """
    對 k-form 進行數值積分
    ∫_Ω ω = ∫ ω(∂p/∂u1, ..., ∂p/∂uk) du1...duk
    """
    if form.k != domain.dim:
        raise ValueError(f"維度不匹配: Form是{form.k}階, 區域是{domain.dim}維")
    
    # 定義被積函數 (Integrand)
    # scipy.integrate.nquad 傳入的參數是 (u1, u2, ...)
    def integrand(*u_args):
        u_params = list(u_args)
        
        # 1. 取得該參數點在流形上的位置 p
        p = domain.map_func(u_params)
        
        # 2. 計算該點的自然切向量基底 (Pullback)
        # 這些切向量代表了參數網格的變形
        basis_vectors_data = domain.get_tangent_vectors(u_params)
        
        # 3. 將數據轉為我們系統的 TangentVector 物件
        # 注意：這裡我們建立的是「局部常數」向量，因為我們只在當下這點評估
        basis_vector_fields = [TangentVector(lambda _, v=v_data: v) for v_data in basis_vectors_data]
        
        # 4. 讓 Form 吃掉這些切向量，並在點 p 評估
        val = form(*basis_vector_fields)(p)
        return val

    # 執行數值積分
    result, error = integrate.nquad(integrand, domain.u_bounds)
    return result

# ==========================================
# Part 3: 幾何形狀 - 超立方體 (HyperCube)
# ==========================================

class HyperCube(ParametrizedDomain):
    """
    一個簡單的 N 維方塊，可以自動產生邊界
    """
    def __init__(self, bounds):
        # bounds: [(x_min, x_max), (y_min, y_max), ...]
        self.bounds = bounds
        dim = len(bounds)
        
        # 自身的映射函數就是 Identity (假設它就在 R^N 空間中)
        def identity_map(u):
            return np.array(u)
            
        super().__init__(dim, bounds, identity_map)

    def get_boundaries(self):
        """
        回傳邊界列表: list of (Domain, sign)
        根據 Stokes 定理的邊界定向規則:
        ∂([0,1]^k) = Σ (-1)^(i-1) (Face_i_max - Face_i_min)
        """
        boundaries = []
        
        for i in range(self.dim):
            # 針對第 i 個維度，產生兩個面 (min 和 max)
            
            # 剩餘的參數範圍 (排除第 i 維)
            sub_bounds = self.bounds[:i] + self.bounds[i+1:]
            
            # 定義 min 面 (u_i = min)
            def face_map_min(u_sub, idx=i, val=self.bounds[i][0]):
                # u_sub 是 k-1 維參數，插入到第 idx 位置
                res = list(u_sub)
                res.insert(idx, val)
                return np.array(res)
            
            # 定義 max 面 (u_i = max)
            def face_map_max(u_sub, idx=i, val=self.bounds[i][1]):
                res = list(u_sub)
                res.insert(idx, val)
                return np.array(res)
            
            # 建立 Domain 物件
            domain_min = ParametrizedDomain(self.dim-1, sub_bounds, face_map_min)
            domain_max = ParametrizedDomain(self.dim-1, sub_bounds, face_map_max)
            
            # 定向符號 (Orientation)
            # Face_max 的符號是 (-1)^(i)  <-- 注意程式索引從0開始，公式通常從1
            # Face_min 的符號是 (-1)^(i+1)
            # 讓我們對齊標準公式： (-1)^(k-1) * (Integration along outward normal)
            # 在參數空間中，標準定向是 sum (-1)^(i) [Face_u_i=1 - Face_u_i=0] (i從0開始算)
            
            sign_base = (-1)**i
            boundaries.append((domain_max, sign_base))       # Max 面
            boundaries.append((domain_min, -1 * sign_base))  # Min 面
            
        return boundaries


# ==========================================
# 輔助工具：建立參數化曲面 (用於古典史托克定理)
# ==========================================
class ParametricPatch(HyperCube):
    """
    這是一個「彎曲」的超立方體。
    繼承 HyperCube，但覆寫 get_boundaries 以確保邊界積分是在 3D 空間進行。
    """
    def __init__(self, u_bounds, map_func_3d):
        # 初始化父類別
        super().__init__(u_bounds)
        # 將自身的映射函數設為 3D 映射
        self.map_func = map_func_3d

    def get_boundaries(self):
        # 1. 先呼叫父類別，取得「參數空間」中的邊界
        # 這些 boundaries 的 map_func 只會輸出 (u, v)
        param_boundaries = super().get_boundaries()
        
        real_boundaries = []
        
        for domain, sign in param_boundaries:
            # 2. 定義一個「複合映射函數」
            # 輸入: 邊界參數 t
            # 輸出: 3D 座標 (x, y, z)
            # 邏輯: t -> (u, v) -> (x, y, z)
            
            # 使用預設參數 (local_map=domain.map_func) 來捕捉閉包中的變數
            def composed_map_func(t_params, local_map=domain.map_func, surface_map=self.map_func):
                # 第一步：算出參數空間座標 (u, v)
                uv = local_map(t_params)
                # 第二步：映射到 3D 物理空間
                xyz = surface_map(uv)
                return xyz
            
            # 3. 建立一個新的 Domain 物件，使用複合映射
            real_domain = ParametrizedDomain(domain.dim, domain.u_bounds, composed_map_func)
            real_boundaries.append((real_domain, sign))
            
        return real_boundaries

