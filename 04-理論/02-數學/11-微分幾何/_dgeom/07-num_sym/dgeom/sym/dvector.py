import sympy as sp
import itertools
from functools import reduce

# ==========================================
# Part 1: 代數與微分運算 (SymPy Version)
# ==========================================

class TangentVector:
    """
    符號切向量場
    components: SymPy 表達式列表/矩陣，例如 [y, -x, 0]
    coords: 定義流形的座標符號，例如 [x, y, z]
    """
    def __init__(self, components, coords, name="V"):
        self.components = sp.Matrix(components) # 轉為直列向量
        self.coords = sp.Matrix(coords)
        self.dim = len(coords)
        self.name = name
        
        if len(self.components) != self.dim:
            raise ValueError("向量維度與座標維度不符")

    def __call__(self, f):
        """
        作用於純量函數 f (SymPy 表達式) -> 方向導數 V(f)
        V(f) = sum v^i * (df/dx^i)
        """
        # 計算梯度 (符號微分)
        grad_f = sp.Matrix([sp.diff(f, var) for var in self.coords])
        # 內積
        res = self.components.dot(grad_f)
        return sp.simplify(res)

    def at(self, point_dict):
        """
        在特定點評估向量數值
        point_dict: {x: 1, y: 2}
        """
        return self.components.subs(point_dict)

def lie_bracket(u, v):
    """
    計算李括號 [u, v] = v.jacobian * u - u.jacobian * v
    這是解析解，無需數值近似
    """
    if u.coords != v.coords:
        raise ValueError("向量場必須定義在相同的座標系")
    
    coords = u.coords
    # 計算 Jacobian 矩陣: J_ij = d(v_i)/d(x_j)
    J_u = u.components.jacobian(coords)
    J_v = v.components.jacobian(coords)
    
    # [u, v] = (v \cdot \nabla) u - (u \cdot \nabla) v
    # 注意：在矩陣乘法表示中，通常寫作 J_v * u - J_u * v
    # J_v 是 v 的導數矩陣，乘上 u 向量代表在 u 方向的變化率
    w_components = J_v * u.components - J_u * v.components
    
    return TangentVector(w_components, coords, name=f"[{u.name},{v.name}]")

class Form:
    """
    k-Form
    k: 階數
    op: 函數，接受 k 個 TangentVector，回傳一個 SymPy 表達式
    """
    def __init__(self, degree, evaluator):
        self.k = degree
        self.op = evaluator 
        
    def __call__(self, *vectors):
        # [修正] 針對 0-form (純量場)
        if self.k == 0: 
            # 如果 op 是函數 (例如 lambda)，執行它以取得表達式
            if callable(self.op):
                return self.op()
            # 如果 op 本身已經是表達式，直接回傳
            return self.op
            
        if len(vectors) != self.k: 
            raise ValueError(f"Need {self.k} vectors, got {len(vectors)}")
        # 這裡回傳的是 SymPy 表達式
        return sp.simplify(self.op(*vectors))

def d(omega):
    """
    外微分算子 (Exterior Derivative)
    使用 Palais 不變量公式 (Invariant Formula)
    """
    k = omega.k
    
    def d_omega_evaluator(*vectors): # vectors: X0...Xk
        total = 0
        n = len(vectors)
        
        # Part A: X_i(omega(...))
        # 這項代表向量場 X_i 作用在 (k-1) form 評估後的純量場上
        for i in range(n):
            X_i = vectors[i]
            others = vectors[:i] + vectors[i+1:]
            
            # omega(*others) 是一個 SymPy 表達式
            scalar_field = omega(*others)
            
            # X_i(scalar_field) 是方向導數
            val = X_i(scalar_field)
            
            term = val if i % 2 == 0 else -val
            total += term
            
        # Part B: omega([X_i, X_j], ...)
        # 使用李括號修正項
        if n >= 2:
            for i in range(n):
                for j in range(i + 1, n):
                    bracket = lie_bracket(vectors[i], vectors[j])
                    others = vectors[:i] + vectors[i+1:j] + vectors[j+1:]
                    
                    val = omega(bracket, *others)
                    
                    sign = (-1)**(i + j)
                    total += sign * val
                    
        return sp.simplify(total)
    
    return Form(k + 1, d_omega_evaluator)


# ==========================================
# Part 2: 區域參數化與積分 (SymPy Version)
# ==========================================

class ParametrizedDomain:
    """
    u_vars: 參數符號列表，如 [u, v]
    u_bounds: 參數範圍，如 [(0, 1), (0, 2*sp.pi)] (數值或符號皆可)
    map_func: 接受 u_vars 符號，回傳物理座標表達式 [x_expr, y_expr, z_expr]
    """
    def __init__(self, u_vars, u_bounds, map_func):
        self.dim = len(u_vars)
        self.u_vars = u_vars
        self.u_bounds = u_bounds
        self.map_func = map_func
        
        # 預計算物理座標表達式
        self.p_exprs = sp.Matrix(map_func(u_vars)) 
        # 假設 map_func 回傳 list 或 Matrix

    def get_tangent_vectors(self, manifold_coords):
        """
        計算參數空間的切向量基底 (Pullback)
        ∂p/∂u_i
        manifold_coords: 用於定義 TangentVector 輸出所在的座標系
        """
        tangents = []
        # Jacobian 矩陣每一行就是一個切向量
        # Jacobian: rows=spatial_dims, cols=param_dims
        J = self.p_exprs.jacobian(self.u_vars)
        
        for i in range(self.dim):
            # 取出第 i 行 (針對第 i 個參數的偏微分)
            vec_components = J.col(i)
            # 必須使用 substitute 將結果中的參數 (u,v) 暫時保留
            # 注意：這裡產生的 TangentVector 內含 u, v 符號，
            # 但它是定義在 manifold_coords (x,y,z) 空間的向量場。
            # 當積分替換變數時，x,y,z 會被換成 u,v 的表達式。
            tangents.append(TangentVector(vec_components, manifold_coords, name=f"d/d{self.u_vars[i]}"))
            
        return tangents

def integrate_form(form, domain, manifold_coords):
    """
    符號積分
    form: k-form
    domain: ParametrizedDomain
    manifold_coords: 定義 form 的空間座標符號 [x, y, z]
    """
    if form.k != domain.dim:
        raise ValueError(f"維度不匹配: Form是{form.k}階, 區域是{domain.dim}維")
    
    # 1. 取得切向量基底 (以參數 u_vars 表示的 x,y,z 分量)
    basis_vectors = domain.get_tangent_vectors(manifold_coords)
    
    # 2. 將 Form 作用於切向量
    # 這會得到一個包含 (x,y,z) 和 (u,v) 混合的表達式，甚至包含導數
    integrand_expr = form(*basis_vectors)
    
    # 3. 變數替換 (Pullback)
    # 將表達式中的 x, y, z 替換為 u, v 的函數
    substitution = dict(zip(manifold_coords, domain.p_exprs))
    integrand_in_uv = integrand_expr.subs(substitution).simplify()
    
    # 4. 執行多重積分
    # 從最後一個變數開始積 (通常順序沒差，除非有相依邊界，這裡假設由 bounds 順序決定)
    result = integrand_in_uv
    
    # 這是為了配合 nquad 的順序習慣，通常是 u1, u2...
    # 但 sympy integrate 是由內而外。
    # 假設 u_vars = [u, v]，bounds = [u_bound, v_bound]
    # 我們依序對 u, 然後對 v 積分
    for param, bounds in zip(domain.u_vars, domain.u_bounds):
        result = sp.integrate(result, (param, bounds[0], bounds[1]))
        
    return result

# ==========================================
# Part 3: 幾何形狀 - 超立方體 (HyperCube)
# ==========================================

# ==========================================
# Part 3: 幾何形狀 - 超立方體 (HyperCube)
# ==========================================

class HyperCube(ParametrizedDomain):
    def __init__(self, u_vars, bounds):
        """
        bounds: [(min, max), ...] 數值或符號
        u_vars: 對應的參數符號 [x, y]
        """
        # Identity map
        def identity_map(u):
            return u
        
        # 初始化父類別，這會建立 self.u_bounds
        super().__init__(u_vars, bounds, identity_map)
        self.manifold_coords = u_vars # 自身就是座標系

    def get_boundaries(self):
        boundaries = []
        dim = self.dim
        
        for i in range(dim):
            # 剩餘參數
            sub_vars = self.u_vars[:i] + self.u_vars[i+1:]
            
            # [修正] 使用 self.u_bounds 而非 self.bounds
            sub_bounds = self.u_bounds[:i] + self.u_bounds[i+1:]
            
            # [修正] 使用 self.u_bounds
            val_min = self.u_bounds[i][0]
            val_max = self.u_bounds[i][1]
            
            # 定義 Min 面映射
            # 必須使用 closure 捕捉變數
            def make_map(insert_idx, fixed_val):
                # 注意：這裡要將 list 轉回 tuple 或 list 以便後續處理，
                # 但 Python list 加法會回傳 list，沒問題
                return lambda u_sub: u_sub[:insert_idx] + [fixed_val] + u_sub[insert_idx:]

            map_min = make_map(i, val_min)
            map_max = make_map(i, val_max)
            
            domain_min = ParametrizedDomain(sub_vars, sub_bounds, map_min)
            domain_max = ParametrizedDomain(sub_vars, sub_bounds, map_max)
            
            # 定向: (-1)^i for Max, (-1)^(i+1) for Min
            sign_base = (-1)**i
            boundaries.append((domain_max, sign_base))
            boundaries.append((domain_min, -1 * sign_base))
            
        return boundaries

class ParametricPatch(HyperCube):
    """
    3D 空間中的曲面 Patch
    """
    def __init__(self, u_vars, u_bounds, map_func_3d):
        # 初始化父類別 (參數空間)
        super().__init__(u_vars, u_bounds)
        self.surface_map = map_func_3d # (u,v) -> (x,y,z)
        
        # 覆蓋 map_func 為 3D 映射
        self.map_func = map_func_3d
        self.p_exprs = sp.Matrix(map_func_3d(u_vars))

    def get_boundaries(self):
        # 取得參數空間的邊界 (線段)
        param_boundaries = super().get_boundaries()
        real_boundaries = []
        
        for domain, sign in param_boundaries:
            # 複合映射: t -> uv -> xyz
            # domain.map_func 是 t -> uv
            # self.surface_map 是 uv -> xyz
            
            def composed_map(t_params, local_map=domain.map_func, surf_map=self.surface_map):
                uv = local_map(t_params)
                xyz = surf_map(uv)
                return xyz
            
            real_domain = ParametrizedDomain(domain.u_vars, domain.u_bounds, composed_map)
            real_boundaries.append((real_domain, sign))
            
        return real_boundaries
