import sympy as sp
from diff_form import DifferentialForm

# ==============================================================================
# 輔助函式：漂亮印出微分形式
# ==============================================================================
def pretty_print(form: DifferentialForm, label: str):
    terms = []
    # 根據維度產生變數符號，以便顯示
    vars_ = [sp.symbols(f'x{i}') for i in range(form.dim)]
    
    # 將 data 排序以便輸出順序固定
    sorted_items = sorted(form.data.items(), key=lambda x: x[0])
    
    for indices, expr in sorted_items:
        # 簡化表達式，如果為 0 就不顯示
        simp_expr = sp.simplify(expr)
        if simp_expr == 0:
            continue
            
        dx_str = " ^ ".join([f"dx{i}" for i in indices])
        terms.append(f"({simp_expr}) {dx_str}")
    
    result = " + ".join(terms) if terms else "0"
    print(f"[{label}] (Dim={form.dim}, Degree={form.degree}):")
    print(f"  {result}")
    print("-" * 60)

# ==============================================================================
# 驗證邏輯：檢查形式是否為 0
# ==============================================================================
def is_zero_form(form: DifferentialForm) -> bool:
    """檢查微分形式的所有係數是否經化簡後均為 0"""
    if not form.data:
        return True
    for expr in form.data.values():
        if sp.simplify(expr) != 0:
            return False
    return True

def run_test_case(case_num, dim, degree, data, description):
    print(f"=== 測試案例 {case_num}: {description} ===")
    
    # 1. 建立初始形式 omega
    omega = DifferentialForm(dim, degree, data)
    pretty_print(omega, "Original (omega)")
    
    # 2. 計算第一次外微分 d(omega)
    d_omega = omega.exterior_derivative()
    pretty_print(d_omega, "First derivative (d omega)")
    
    # 3. 計算第二次外微分 d(d(omega))
    dd_omega = d_omega.exterior_derivative()
    pretty_print(dd_omega, "Second derivative (d^2 omega)")
    
    # 4. 驗證結果
    if is_zero_form(dd_omega):
        print(f"✅ 測試通過: d^2 = 0\n\n")
    else:
        print(f"❌ 測試失敗: d^2 != 0\n\n")

# ==============================================================================
# 主程式
# ==============================================================================
if __name__ == "__main__":
    # 定義符號以便建構測試資料
    # 假設最大用到 x0, x1, x2, x3
    x0, x1, x2, x3 = sp.symbols('x0 x1 x2 x3')

    # --------------------------------------------------------------------------
    # 案例 1: 3D 空間中的 0-form (纯量場)
    # 驗證：d(f) 是梯度，d(d(f)) 也就是 curl(grad f) 應為 0
    # --------------------------------------------------------------------------
    # f = x0^2 * x1 + sin(x2)
    # data key 為空 tuple () 代表 0-form
    data_case1 = {
        (): x0**2 * x1 + sp.sin(x2)
    }
    run_test_case(1, 3, 0, data_case1, "3D Scalar Field (0-form)")

    # --------------------------------------------------------------------------
    # 案例 2: 3D 空間中的 1-form
    # 驗證：d(omega) 類似旋度，d(d(omega)) 也就是 div(curl F) 應為 0
    # --------------------------------------------------------------------------
    # omega = (x1) dx0 + (x2*x0) dx1 + (x0^2) dx2
    data_case2 = {
        (0,): x1,
        (1,): x2 * x0,
        (2,): x0**2
    }
    run_test_case(2, 3, 1, data_case2, "3D Vector Field (1-form)")

    # --------------------------------------------------------------------------
    # 案例 3: 4D 空間中的 2-form
    # 驗證：高維度下的 d^2 = 0
    # --------------------------------------------------------------------------
    # omega = x0*x3 dx0^dx1 + e^x2 dx2^dx3
    data_case3 = {
        (0, 1): x0 * x3,
        (2, 3): sp.exp(x2)
    }
    run_test_case(3, 4, 2, data_case3, "4D Tensor Field (2-form)")
