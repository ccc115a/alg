import numpy as np
from collections import Counter

def solve_ode_general(coefficients):
    """
    求解常係數齊次線性常微分方程的通解。
    
    參數:
        coefficients (list 或 array): 
            微分方程的係數 [a_n, a_{n-1}, ..., a_0]。
            例如: 對於 y'' - 4y' + 4y = 0，輸入 [1, -4, 4]。
            
    回傳:
        str: 微分方程的通解。
    """
    if not coefficients or coefficients[0] == 0:
        return "錯誤：係數列表必須提供且最高階係數不能為零。"

    # 1. 求解特徵方程的根
    # numpy.roots 輸入為 [a_n, ..., a_0]，輸出為 n 個根 (可能為複數)
    roots = np.roots(coefficients)
    
    # 2. 統計根的重數
    # 由於浮點數誤差，需要進行四捨五入或設置一個容忍度
    # 這裡採用簡單的四捨五入到一定小數位數來分組
    rounded_roots = np.round(roots, decimals=8)
    # rounded_roots = np.round(roots, decimals=4)
    root_counts = Counter(rounded_roots)
    
    # 3. 處理根的類型並構建基礎解
    solution_terms = []
    
    # 用一個集合來追蹤已經處理過的根，避免重複處理複數共軛對
    processed_roots = set()

    for r_rounded, multiplicity in root_counts.items():
        # 取得未四捨五入的精確根值 (雖然可能還是浮點數近似)
        # 由於 numpy.roots 返回的順序不定，這裡直接用四捨五入後的值來查找
        # 更好的方法是使用一個容忍度去分組，但為簡潔性，這裡直接用 r_rounded
        r = roots[rounded_roots == r_rounded][0] # 取得這個分組中的一個根代表
        
        if r in processed_roots:
            continue
        
        # 判斷是否為實數根 (虛部接近於零)
        if np.isclose(r.imag, 0):
            # 實數根
            lambda_val = r.real
            
            for k in range(multiplicity):
                # 實數重根: y_k(x) = x^k * exp(lambda * x)
                term = f"e^({lambda_val}x)"
                if k > 0:
                    # x^k 的部分
                    x_power = f"x^{k}" if k > 1 else "x"
                    term = f"{x_power}{term}"
                
                solution_terms.append(term)
                
        else:
            # 複數根: r = alpha + i*beta
            alpha = r.real
            beta = r.imag
            
            # 複數根總是成對出現，我們只需要處理 alpha + i*beta
            # 其共軛根 alpha - i*beta 的處理將被這個迴圈跳過 (因為它們一起貢獻解)
            processed_roots.add(r_rounded) # 標記自己
            
            # 找到共軛根的四捨五入值
            r_conjugate_rounded = np.round(r.conjugate(), decimals=8)
            processed_roots.add(r_conjugate_rounded) # 標記共軛根
            
            # 複數根的重數m
            m = multiplicity 
            
            for k in range(m):
                # 複數重根: e^(alpha*x) * [x^k * cos(beta*x) 與 x^k * sin(beta*x)]
                x_power_prefix = f"x^{k}" if k > 1 else ("x" if k == 1 else "")

                # cos 項
                term_cos = f"e^({alpha}x){x_power_prefix}cos({abs(beta)}x)"
                solution_terms.append(term_cos)
                
                # sin 項
                term_sin = f"e^({alpha}x){x_power_prefix}sin({abs(beta)}x)"
                solution_terms.append(term_sin)
                
    # 4. 組合通解
    # y_h(x) = C_1*y_1 + C_2*y_2 + ... + C_n*y_n
    final_solution = " + ".join([f"C_{i+1}{y}" for i, y in enumerate(solution_terms)])
    
    return f"y(x) = {final_solution}"

# 範例測試 (1): 實數單根: y'' - 3y' + 2y = 0  特徵方程: lambda^2 - 3lambda + 2 = 0, 根: 1, 2
# 預期解: C_1e^(1x) + C_2e^(2x)
print("--- 實數單根範例 ---")
coeffs1 = [1, -3, 2]
print(f"方程係數: {coeffs1}")
print(solve_ode_general(coeffs1))

# 範例測試 (2): 實數重根: y'' - 4y' + 4y = 0  特徵方程: lambda^2 - 4lambda + 4 = 0, 根: 2, 2
# 預期解: C_1e^(2x) + C_2xe^(2x)
print("\n--- 實數重根範例 ---")
coeffs2 = [1, -4, 4]
print(f"方程係數: {coeffs2}")
print(solve_ode_general(coeffs2))

# 範例測試 (3): 複數共軛根: y'' + 4y = 0  特徵方程: lambda^2 + 4 = 0, 根: 2i, -2i (alpha=0, beta=2)
# 預期解: C_1cos(2x) + C_2sin(2x)
print("\n--- 複數共軛根範例 ---")
coeffs3 = [1, 0, 4]
print(f"方程係數: {coeffs3}")
print(solve_ode_general(coeffs3))

# 範例測試 (4): 複數重根 (二重): (D^2 + 1)^2 y = 0  特徵方程: (lambda^2 + 1)^2 = 0, 根: i, i, -i, -i (alpha=0, beta=1, m=2)
# 預期解: C_1cos(1x) + C_2sin(1x) + C_3xcos(1x) + C_4xsin(1x)
print("\n--- 複數重根範例 ---")
coeffs4 = [1, 0, 2, 0, 1]
print(f"方程係數: {coeffs4}")
print(solve_ode_general(coeffs4))

# 範例測試 (5): 高階重根: y''' - 6y'' + 12y' - 8y = 0  特徵方程: (lambda - 2)^3 = 0, 根: 2, 2, 2
# 預期解: C_1e^(2x) + C_2xe^(2x) + C_3x^2e^(2x)
print("\n--- 高階重根範例 ---")
coeffs5 = [1, -6, 12, -8]
print(f"方程係數: {coeffs5}")
print(solve_ode_general(coeffs5))