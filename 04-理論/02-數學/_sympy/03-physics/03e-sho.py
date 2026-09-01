from sympy import symbols, integrate, oo, pprint, simplify, sqrt
from sympy.physics.sho import R_nl, E_nl

def sho_3d_example():
    # 1. 定義符號
    # r: 徑向距離
    # nu: 頻率參數 (nu = m*omega / (2*hbar))，控制波函數的寬度
    r, nu = symbols('r nu', real=True, positive=True)
    
    print("--- 1. 三維諧振子徑向波函數 R_nl(r) ---")
    # 取得 n=0, l=0 (基態) 的徑向波函數
    # R_nl(n, l, r, nu)
    psi_00 = R_nl(0, 0, r, nu)
    
    print("基態 (n=0, l=0) 徑向波函數:")
    pprint(psi_00)
    
    # 讓我們看一個激發態，例如 n=0, l=1 (對應 p 軌域類似的形狀)
    psi_01 = R_nl(0, 1, r, nu)
    print("\n激發態 (n=0, l=1) 徑向波函數:")
    pprint(psi_01)


    print("\n--- 2. 能量本徵值 E_nl ---")
    # 3D 諧振子的能量公式: E = hbar * omega * (2*n + l + 3/2)
    # 在 sympy 中，它會輸出與參數 nu 對應的形式
    energy_00 = E_nl(0, 0, nu)
    print(f"基態能量 (n=0, l=0): {energy_00}")
    
    energy_01 = E_nl(0, 1, nu)
    print(f"激發態能量 (n=0, l=1): {energy_01}")


    print("\n--- 3. 驗證歸一化 (Normalization) ---")
    # 三維球座標積分體積元素是 r^2 dr sin(theta) d(theta) d(phi)
    # 因為 R_nl 已經正規化了角度部分，我們只需要對徑向做積分
    # 歸一化條件: Integral |R(r)|^2 * r^2 dr = 1
    
    prob_density = psi_00**2 * r**2
    norm_result = integrate(prob_density, (r, 0, oo))
    
    print(f"基態歸一化積分結果 (應為 1): {simplify(norm_result)}")


    print("\n--- 4. 計算 <r^2> (平均半徑平方) ---")
    # 這常用於估算粒子分佈範圍
    # <r^2> = Integral r^2 * |R(r)|^2 * r^2 dr
    #       = Integral r^4 * |R(r)|^2 dr
    
    r_squared_integrand = r**2 * prob_density
    avg_r2 = integrate(r_squared_integrand, (r, 0, oo))
    
    print(f"基態的 <r^2>: {simplify(avg_r2)}")
    # 理論上 3D 諧振子基態 <r^2> 應該與 1/nu 相關

if __name__ == "__main__":
    sho_3d_example()