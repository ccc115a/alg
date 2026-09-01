from sympy import symbols, Function, diff, simplify, Matrix, Expr, Derivative

# 1. 設置空間座標
x, y, z = symbols('x y z')
coords = [x, y, z] # 座標變數
coord_map = {c: i for i, c in enumerate(coords)} # 座標到索引的映射

# 2. 定義純量場 f (用於方向導數)
# f 必須是 (x, y, z) 的函數
f = Function('f')(*coords)

# ==========================================
# 核心類別 1: TangentVector (切向量場)
# ==========================================

class SympyTangentVector:
    """
    用 SymPy 表達式的列表來表示切向量場 V 的分量。
    V = [V1(x,y,z), V2(x,y,z), V3(x,y,z)]
    """
    def __init__(self, components: list[Expr], name="V"):
        # components 是 SymPy 函數或表達式，例如 [x*y, 0, 1]
        self.components = components
        self.dim = len(components)
        self.name = name
        
    def __call__(self, f_scalar_field):
        """
        作用於純量場 f (計算方向導數 L_V(f) = V(f) = V . ∇f)
        
        Args:
            f_scalar_field (sympy expression): 純量場 f。
            
        Returns:
            sympy expression: 結果也是一個純量場 L_V(f)。
        """
        if f_scalar_field.free_symbols.intersection(set(coords)):
            # 確保 f 是關於我們座標的函數
            nabla_f_components = [diff(f_scalar_field, coord) for coord in coords]
            
            # 點積 V . ∇f
            directional_derivative = sum(
                self.components[i] * nabla_f_components[i]
                for i in range(self.dim)
            )
            return directional_derivative
        else:
            # 如果 f 已經是常數，方向導數為 0
            return 0


# ==========================================
# 核心函數 1: Lie Bracket (李括號)
# ==========================================

def lie_bracket(u: SympyTangentVector, v: SympyTangentVector) -> SympyTangentVector:
    """
    計算李括號 [U, V] = U(V) - V(U)
    這裡 U(V) 是指 U 作用於 V 的每個分量上 (方向導數)
    
    [U, V]_i = U(V_i) - V(U_i)
    """
    dim = u.dim
    bracket_components = []
    
    for i in range(dim):
        # 計算 U(V_i)
        # 這裡的 V_i 是一個純量場 (V 的第 i 個分量)
        U_of_Vi = u(v.components[i])
        
        # 計算 V(U_i)
        V_of_Ui = v(u.components[i])
        
        # [U, V]_i = U(V_i) - V(U_i)
        bracket_components.append(simplify(U_of_Vi - V_of_Ui))
        
    return SympyTangentVector(bracket_components, name=f"[{u.name}, {v.name}]")


# ==========================================
# 核心類別 2: DifferentialForm (微分形式)
# ==========================================

class SympyForm:
    """
    微分形式的抽象表示，其值是在點 p 處作用於 k 個切向量的結果。
    op: func(*vectors) -> scalar_field (SymPy Expr)
    """
    def __init__(self, degree, evaluator):
        self.k = degree
        self.op = evaluator # evaluator(*vectors) -> SymPy Expr (純量場)
        
    def __call__(self, *vectors: SympyTangentVector) -> Expr:
        """
        將微分形式作用於 k 個切向量場上，返回一個純量場。
        """
        if len(vectors) != self.k: 
            raise ValueError(f"需要 {self.k} 個向量，但接收到 {len(vectors)} 個。")
        
        # 0-形式的特殊情況：op 本身就是純量場
        if self.k == 0:
            return self.op
        
        return self.op(*vectors)

# ==========================================
# 核心函數 2: Exterior Differential d (外微分)
# 這是 dvector.py 中的 Cartan 公式實現
# ==========================================

def d(omega: SympyForm) -> SympyForm:
    """
    使用 Cartan 公式實現外微分算子 d:
    (dω)(X₀, ..., Xₖ) = Σᵢ (-1)ⁱ Lₓᵢ(ω(X₀, ..., X̂ᵢ, ..., Xₖ))
                      + Σᵢ<ⱼ (-1)ⁱ⁺ʲ ω([Xᵢ, Xⱼ], X₀, ..., X̂ᵢ, ..., X̂ⱼ, ..., Xₖ)
    """
    k = omega.k
    
    def d_omega_evaluator(*vectors: SympyTangentVector) -> Expr:
        """
        返回 dω 作用於 k+1 個向量 (X0...Xk) 上所產生的純量場。
        """
        n = len(vectors) # n = k + 1
        if n != k + 1:
            raise ValueError(f"d(k-form) 作用於 {k+1} 個向量，但接收到 {n} 個。")
        
        total_field = 0 # 總和是一個 SymPy 表達式
        
        # Part A: 李導數項 (Lie Derivative term)
        # Σᵢ (-1)ⁱ Lₓᵢ(ω(X₀, ..., X̂ᵢ, ..., Xₖ))
        for i in range(n):
            Xi = vectors[i]
            others = vectors[:i] + vectors[i+1:] # X̂ᵢ (省略 Xi)
            
            # 1. 內部運算: ω 作用於剩下的 k 個向量上
            inner_scalar_field = omega(*others) 
            
            # 2. 外部運算: Xi 作用於這個純量場上 (李導數 Lₓᵢ)
            val = Xi(inner_scalar_field)
            
            sign = 1 if i % 2 == 0 else -1
            total_field += sign * val

        # Part B: 李括號項 (Lie Bracket term)
        # Σᵢ<ⱼ (-1)ⁱ⁺ʲ ω([Xᵢ, Xⱼ], X₀, ..., X̂ᵢ, ..., X̂ⱼ, ..., Xₖ)
        if n >= 2: # 只有 k >= 1 (即 n >= 2) 時才需要計算此項
            for i in range(n):
                for j in range(i + 1, n):
                    bracket = lie_bracket(vectors[i], vectors[j]) # [Xᵢ, Xⱼ]
                    
                    # 構造新的向量列表 (用 [Xᵢ, Xⱼ] 替換 Xᵢ 和 Xⱼ)
                    others_list = list(vectors)
                    # 移除 j (索引較大)
                    others_list.pop(j)
                    # 移除 i (索引較小)
                    others_list.pop(i) 
                    
                    # 構造最終的 ω 參數列表: [bracket, X₀, ..., X̂ᵢ, ..., X̂ⱼ, ..., Xₖ]
                    omega_args = [bracket] + others_list
                    
                    # 內部運算: ω 作用於 k 個向量上 (其中一個是李括號)
                    val = omega(*omega_args) 
                    
                    sign = (-1)**(i + j)
                    total_field += sign * val
                    
        return simplify(total_field)

    return SympyForm(k + 1, d_omega_evaluator)


# ==========================================
# 範例測試：驗證 d(d f) = 0
# ==========================================

print("--- 測試 d(d f) = 0 (使用 Cartan 公式) ---")

# 1. 定義 0-形式 f (純量場)
test_f = x*y*z**2 # 實際函數
# test_f = Function('f')(x, y, z) # 抽象函數
omega_0 = SympyForm(0, evaluator=test_f) 

# 2. 計算 d f (1-形式)
omega_1 = d(omega_0)

# 3. 計算 d(d f) (2-形式)
omega_2 = d(omega_1)


# 4. 驗證結果：讓 omega_2 作用於三個切向量 X, Y, Z
# 定義三個簡單的切向量場 (SymPyTangentVector)
V_x = SympyTangentVector([1, 0, 0], name="d/dx")
V_y = SympyTangentVector([0, 1, 0], name="d/dy")
V_z = SympyTangentVector([0, 0, 1], name="d/dz")

# 測試 V_x, V_y, V_z 作用於 d(d f)
# 在 R^3 上 d(d f) 作用於 3 個向量，應為 0
result_field = omega_2(V_x, V_y)

print(f"原始 0-形式 f: {omega_0()}")
print(f"d(f) 的結果是 k=1 形式 (抽象): {omega_1.op.__name__}")
print(f"d(d f) 作用於 (d/dx, d/dy, d/dz) 的結果 (純量場): {result_field}")

if result_field == 0:
    print("\n✅ 驗證成功: d(d f) 作用於任何常數切向量場基底，結果為 0。")
else:
    print(f"\n❌ 驗證失敗: d(d f) 結果不為 0。")