import sympy as sp

def proof_parallelogram_law():
    print("--- 吳文俊方法：證明平行四邊形恆等式 ---\n")

    # 1. 定義符號
    # u1, u2, u3 是自由參數 (定義 A, B, D 的位置)
    # x1, x2 是從屬變量 (定義 C 的位置)
    u1, u2, u3 = sp.symbols('u1 u2 u3')
    x1, x2 = sp.symbols('x1 x2')

    print("【座標設定】")
    print(f"A = (0, 0)")
    print(f"B = ({u1}, 0)")
    print(f"D = ({u2}, {u3})")
    print(f"C = ({x1}, {x2})  <-- 這是我們要消除的約束點\n")

    # 2. 設定幾何條件 (Hypothesis Set)
    # 條件: ABCD 是平行四邊形 => 向量 AB = 向量 DC
    # 向量 AB = (u1, 0)
    # 向量 DC = (x1 - u2, x2 - u3)
    
    # h1 關聯 x1: x1 - u2 = u1  =>  x1 - u1 - u2 = 0
    h1 = x1 - u1 - u2
    
    # h2 關聯 x2: x2 - u3 = 0
    h2 = x2 - u3
    
    # 在吳氏方法中，特徵集通常是倒序排列的（先列出包含最高序變量的方程）
    # 我們希望依序消除 x2, 然後 x1
    H = [h2, h1] 
    vars_to_eliminate = [x2, x1] # 對應 H 中的方程主變量

    print("【幾何條件 (H)】")
    print(f"h1 (關於 x1): {h1} = 0")
    print(f"h2 (關於 x2): {h2} = 0\n")

    # 3. 設定待證結論 (Conclusion)
    # 證明: AC^2 + BD^2 = 2 * (AB^2 + AD^2)
    # 移項: AC^2 + BD^2 - 2 * (AB^2 + AD^2) = 0
    
    # 距離平方公式 dist_sq(P1, P2) = (x1-x2)^2 + (y1-y2)^2
    AC_sq = (x1 - 0)**2 + (x2 - 0)**2
    BD_sq = (u2 - u1)**2 + (u3 - 0)**2
    AB_sq = (u1 - 0)**2 + (0 - 0)**2
    AD_sq = (u2 - 0)**2 + (u3 - 0)**2
    
    g_expr = AC_sq + BD_sq - 2 * (AB_sq + AD_sq)
    
    # 展開多項式 (這一步很重要，讓 SymPy 整理項次)
    g = sp.expand(g_expr)
    print(f"【待證多項式 (g)】")
    print(f"g = {g} = 0 (尚未代入條件)\n")

    # 4. 執行反覆偽除法 (Successive Pseudo-Division)
    print("【開始代數消元 (偽除法)】")
    
    remainder = g
    
    # 我們依序處理每個變量
    for i, h in enumerate(H):
        var = vars_to_eliminate[i]
        print(f"--> 步驟 {i+1}: 利用條件 '{h}=0' 消除變量 '{var}'")
        
        # 計算偽餘式
        remainder = sp.prem(remainder, h, var)
        print(f"    當前餘式: {remainder}")

    # 5. 判斷結果
    print("\n【最終結果】")
    if remainder == 0:
        print("✅ 證明成功！最終餘式為 0。")
        print("這表示在平行四邊形的條件下，對角線恆等式恆成立。")
    else:
        print(f"❌ 證明失敗。餘式為: {remainder}")

if __name__ == "__main__":
    proof_parallelogram_law()