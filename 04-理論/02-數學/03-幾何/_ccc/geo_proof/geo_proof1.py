import sympy as sp

def wus_method_demo():
    print("--- 吳文俊方法 (Wu's Method) 幾何證明演示 ---\n")

    # 1. 定義符號
    # x, y 是變量 (C點座標)
    # r 是參數 (半徑)
    x, y, r = sp.symbols('x y r')

    # 2. 設定幾何條件 (Hypothesis Set)
    # 條件: 點 C(x, y) 在以原點為圓心、半徑為 r 的圓上
    # 方程: x^2 + y^2 - r^2 = 0
    # 我們將其視為關於主變量 y 的多項式
    h1 = x**2 + y**2 - r**2
    
    # 假設集列表 (在此例中只有一個條件，且已是三角形式)
    # 注意：在更複雜的證明中，這裡會有多個方程，且需要根據變量順序排列
    H = [h1]
    
    print(f"1. 幾何條件 (Hypothesis): {h1} = 0")

    # 3. 設定待證結論 (Conclusion)
    # 結論: 向量 CA 與 向量 CB 垂直 (內積為 0)
    # A = (-r, 0), B = (r, 0), C = (x, y)
    # Vector CA = (-r - x, -y)
    # Vector CB = (r - x, -y)
    # Dot Product = (-r - x)*(r - x) + (-y)*(-y)
    g_expr = (-r - x) * (r - x) + (-y) * (-y)
    
    # 展開多項式
    g = sp.expand(g_expr)
    print(f"2. 待證結論 (Conclusion Polynomial g): {g} = 0")

    # 4. 執行反覆偽除法 (Successive Pseudo-Division)
    # 目標: 計算 prem(g, h1, y)
    # 如果餘數為 0，則證明成立
    
    print("\n3. 開始執行偽除法 (Pseudo-Division)...")
    
    # 當前餘式初始化為結論多項式
    remainder = g
    
    # 對特徵集中的每個條件進行偽除 (逆序，從最高級變量開始消除)
    # 這裡我們的主變量是 y
    for h in reversed(H):
        # sp.prem(被除式, 除式, 變量) 計算偽餘式
        print(f"   正在對變量 y 進行除法: prem({remainder}, {h})")
        remainder = sp.prem(remainder, h, y)

    print(f"\n4. 最終餘式 (Final Remainder): {remainder}")

    # 5. 判斷結果
    if remainder == 0:
        print("\n✅ 證明成功！餘式為 0，定理成立。")
    else:
        print("\n❌ 證明失敗。餘式不為 0。")

if __name__ == "__main__":
    wus_method_demo()