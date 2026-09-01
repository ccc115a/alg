# cat2_composition.py
from sympy.categories import Object, Morphism, NamedMorphism

def main():
    # 1. 定義三個物件
    A = Object('A')
    B = Object('B')
    C = Object('C')

    # 2. 定義兩個具名態射
    # 使用 NamedMorphism 來指定名稱 'f' 和 'g'
    f = NamedMorphism(A, B, 'f') # f: A -> B
    g = NamedMorphism(B, C, 'g') # g: B -> C

    print(f"態射 f: {f}")
    print(f"態射 g: {g}")

    # 3. 合成態射 (Composition)
    # 數學寫法通常是 g ∘ f，程式碼寫成 g * f
    # 這代表 "先執行 f，再執行 g"
    composite = g * f

    print(f"\n合成態射 (g ∘ f): {composite}")
    print(f"合成後的定義域: {composite.domain}")
    print(f"合成後的對應域: {composite.codomain}")

    # 4. 錯誤處理
    # 如果嘗試合成不匹配的態射 (例如 f * g)，SymPy 會報錯
    try:
        # A->B 接著 B->C，但 f*g 意味著先 g (B->C) 再 f (A->B)，
        # 除非 C = A，否則定義域不匹配
        invalid = f * g 
    except ValueError as e:
        print(f"\n錯誤測試 (預期發生): {e}")

if __name__ == "__main__":
    main()