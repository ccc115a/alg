# cat1_obj.py
from sympy.categories import Object, Morphism, NamedMorphism

def main():
    # 1. 定義物件 (Objects)
    A = Object('A')
    B = Object('B')
    
    print(f"物件 A: {A}")
    print(f"物件 B: {B}")

    # 2. 定義具名態射 (NamedMorphism) f: A -> B
    # NamedMorphism(domain, codomain, name)
    f = NamedMorphism(A, B, 'f')

    print(f"\n態射 f: {f}")
    print(f"定義域 (Domain): {f.domain}")
    print(f"對應域 (Codomain): {f.codomain}")

    # 3. 檢查態射的類型
    # NamedMorphism 是 Morphism 的子類別
    print(f"f 是態射嗎? {isinstance(f, Morphism)}")

if __name__ == "__main__":
    main()