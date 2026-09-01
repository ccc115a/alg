import sympy as sp
from itertools import permutations

class DifferentialForm:
    """
    實作微分形式的代數運算類別。
    屬性:
        dim (int): 空間維度
        coeffs (dict): 儲存形式的係數。
                       Key 是 tuple (例如 (0, 2) 代表 dx^0 ^ dx^2)
                       Value 是 SymPy 表達式 (係數函數)
    """
    def __init__(self, dim, coeffs=None):
        self.dim = dim
        self.coeffs = coeffs if coeffs else {}

    def __repr__(self):
        """漂亮打印微分形式"""
        if not self.coeffs:
            return "0"
        
        terms = []
        # 定義坐標字串，方便顯示 (x, y, z, ...)
        coord_names = ["x", "y", "z", "w"]
        dx_names = [f"d{coord_names[i]}" if i < 4 else f"dx{i}" for i in range(self.dim)]
        
        for indices, expr in self.coeffs.items():
            # 忽略係數為 0 的項
            if expr == 0:
                continue
            
            basis_str = " ^ ".join([dx_names[i] for i in indices])
            if basis_str:
                terms.append(f"({expr}) * {basis_str}")
            else:
                terms.append(f"({expr})") # 0-form
                
        return " + ".join(terms) if terms else "0"

    def __add__(self, other):
        """形式加法"""
        if self.dim != other.dim:
            raise ValueError("維度不匹配")
        
        new_coeffs = self.coeffs.copy()
        for indices, val in other.coeffs.items():
            if indices in new_coeffs:
                new_coeffs[indices] = sp.simplify(new_coeffs[indices] + val)
            else:
                new_coeffs[indices] = val
                
        # 清理係數為 0 的項
        new_coeffs = {k: v for k, v in new_coeffs.items() if v != 0}
        return DifferentialForm(self.dim, new_coeffs)

    def wedge(self, other):
        """
        外積運算 (Wedge Product)
        核心邏輯：處理反交換律與排序
        """
        if self.dim != other.dim:
            raise ValueError("維度不匹配")

        new_coeffs = {}

        for idx1, val1 in self.coeffs.items():
            for idx2, val2 in other.coeffs.items():
                
                # 合併指標 (例如 (0,) 和 (1,) 變成 (0, 1))
                combined_idx = list(idx1 + idx2)
                
                # 規則 1: 如果有重複指標，結果為 0 (dx ^ dx = 0)
                if len(set(combined_idx)) != len(combined_idx):
                    continue
                
                # 規則 2: 排序指標並計算符號變換
                # 我們使用冒泡排序來計算交換次數 (Sign signature)
                sign = 1
                sorted_idx = combined_idx[:]
                # 簡單的排序並計算逆序數
                for i in range(len(sorted_idx)):
                    for j in range(0, len(sorted_idx)-i-1):
                        if sorted_idx[j] > sorted_idx[j+1]:
                            sorted_idx[j], sorted_idx[j+1] = sorted_idx[j+1], sorted_idx[j]
                            sign *= -1
                
                final_idx = tuple(sorted_idx)
                
                # 計算新係數
                term_val = val1 * val2 * sign
                
                if final_idx in new_coeffs:
                    new_coeffs[final_idx] += term_val
                else:
                    new_coeffs[final_idx] = term_val
                    
        # 化簡
        for k in new_coeffs:
            new_coeffs[k] = sp.simplify(new_coeffs[k])
        new_coeffs = {k: v for k, v in new_coeffs.items() if v != 0}
            
        return DifferentialForm(self.dim, new_coeffs)

    def d(self, coord_vars):
        """
        外微分運算 (Exterior Derivative)
        d(f dx^I) = Σ (∂f/∂x^k) dx^k ^ dx^I
        """
        if len(coord_vars) != self.dim:
            raise ValueError("坐標變數數量與維度不符")
            
        result = DifferentialForm(self.dim, {})
        
        for indices, func in self.coeffs.items():
            # 對每個係數函數 f 進行微分
            # df = Σ (∂f/∂x^k) dx^k
            
            for k, var in enumerate(coord_vars):
                # 計算偏導
                partial_deriv = sp.diff(func, var)
                
                if partial_deriv == 0:
                    continue
                
                # 構造 1-form: (∂f/∂x^k) dx^k
                # 注意 key 是 tuple (k,)
                df_k = DifferentialForm(self.dim, {(k,): partial_deriv})
                
                # 構造原本的基底部分: 1 * dx^I
                original_basis = DifferentialForm(self.dim, {indices: sp.Integer(1)})
                
                # 運算: d(term) = df_k ^ original_basis
                term_d = df_k.wedge(original_basis)
                
                result = result + term_d
                
        return result

# ==========================================
# 驗證與測試區
# ==========================================

def run_exterior_algebra_demo():
    print("--- 專案 5.1: 外代數計算機 ---")
    
    # 1. 初始化符號
    # R^3 空間
    x, y, z = sp.symbols('x y z', real=True)
    coords = [x, y, z]
    dim = 3
    
    # 建立基底 1-forms: dx, dy, dz
    # 內部表示: dx -> {(0,): 1}, dy -> {(1,): 1}, dz -> {(2,): 1}
    dx = DifferentialForm(dim, {(0,): sp.Integer(1)})
    dy = DifferentialForm(dim, {(1,): sp.Integer(1)})
    dz = DifferentialForm(dim, {(2,): sp.Integer(1)})
    
    print(f"基底: dx, dy, dz defined in R^{dim}")

    # ----------------------------------------
    # 2. 驗證外積規則 (Wedge Product Rules)
    # ----------------------------------------
    print("\n[測試 1] 外積反交換律")
    w1 = dx.wedge(dy)
    w2 = dy.wedge(dx)
    
    print(f"  dx ^ dy = {w1}")
    print(f"  dy ^ dx = {w2}")
    
    # 驗證 w1 + w2 = 0
    check_zero = w1 + w2
    print(f"  驗證和為 0: {check_zero}")
    
    print("\n[測試 2] 重複基底")
    w3 = dx.wedge(dx)
    print(f"  dx ^ dx = {w3}")  # 應為 0

    # ----------------------------------------
    # 3. 驗證外微分 (Exterior Derivative)
    # ----------------------------------------
    print("\n[測試 3] 計算 dω")
    # 定義一個 1-form: ω = P dx + Q dy + R dz
    # 這是我們之前 Stokes 定理用過的場 (-y dx + x dy)
    # 這裡我們用更復雜一點的： ω = z*x dx + x*y dy
    
    omega = DifferentialForm(dim, {
        (0,): z * x,  # coeff of dx
        (1,): x * y   # coeff of dy
    })
    
    print(f"  原始形式 ω = {omega}")
    
    d_omega = omega.d(coords)
    print(f"  外微分 dω  = {d_omega}")
    # 手算驗證:
    # d(zx dx) = (z dx + x dz) ^ dx = x dz^dx = -x dx^dz
    # d(xy dy) = (y dx + x dy) ^ dy = y dx^dy
    # 結果應為: y dx^dy - x dx^dz (程式顯示順序可能不同)

    # ----------------------------------------
    # 4. 驗證 d^2 = 0
    # ----------------------------------------
    print("\n[測試 4] 驗證 d^2 = 0 (Nilpotency)")
    
    # 我們定義一個任意的 0-form (純量函數) f
    f_func = sp.sin(x) * sp.cos(y) * sp.exp(z)
    f_form = DifferentialForm(dim, {(): f_func}) # 空 tuple 代表 0-form
    
    print(f"  函數 f = {f_form}")
    
    df = f_form.d(coords)
    print(f"  一階微分 df = {df}")
    
    ddf = df.d(coords)
    print(f"  二階微分 d(df) = {ddf}")
    
    if len(ddf.coeffs) == 0:
        print("  >>> 驗證成功！ d^2 f = 0")
    else:
        print("  >>> 驗證失敗！")

    print("\n[測試 5] 驗證 d^2 ω = 0 (對於 1-form)")
    # 使用剛才的 d_omega (它是一個 2-form)
    # 再微分一次應該要變 3-form 且值為 0
    
    dd_omega = d_omega.d(coords)
    print(f"  d(dω) = {dd_omega}")
    
    if len(dd_omega.coeffs) == 0:
        print("  >>> 驗證成功！ d^2 ω = 0")
    else:
        print("  >>> 驗證失敗！")

if __name__ == "__main__":
    run_exterior_algebra_demo()