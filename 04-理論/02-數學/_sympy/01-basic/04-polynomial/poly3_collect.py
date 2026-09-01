# 範例 3：合併同類項與係數提取
from sympy import symbols, collect, Poly

def main():
    # 1. 定義符號
    x, y = symbols('x y')

    # 2. 定義一個混合多項式
    # 目標是將其視為關於 x 的多項式
    expr = x*y + x - 3 + 2*x**2 - y*x + x**2
    print(f"原始表達式: {expr}")

    # 3. 合併同類項 (Collect)
    # 將所有含 x 的項合併，係數會變成 y 的函數
    collected_expr = collect(expr, x)
    print(f"針對 x 合併後: {collected_expr}")

    # 4. 使用 Poly 類別提取係數
    # Poly 是 SymPy 處理多項式的專用物件，功能更強大
    p = Poly(expr, x)
    print(f"\n轉為 Poly 物件: {p}")
    
    # 取得所有係數 (依降冪排列)
    coeffs = p.coeffs()
    print(f"係數列表: {coeffs}")
    
    # 取得最高次項係數 (Leading Coefficient)
    print(f"領導係數 (LC): {p.LC()}")

if __name__ == "__main__":
    main()