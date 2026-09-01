# cat3_identity.py
from sympy.categories import Object, NamedMorphism, IdentityMorphism

def main():
    A = Object('A')
    B = Object('B')
    
    # 使用 NamedMorphism
    f = NamedMorphism(A, B, 'f')

    # 1. 定義恆等態射
    id_A = IdentityMorphism(A)
    id_B = IdentityMorphism(B)

    print(f"態射 f: {f}")
    print(f"恆等態射 id_A: {id_A}")
    print(f"恆等態射 id_B: {id_B}")

    # 2. 驗證 f ∘ id_A = f
    res1 = f * id_A
    print(f"\n計算 f * id_A: {res1}")
    print(f"是否等於 f? {res1 == f}")

    # 3. 驗證 id_B ∘ f = f
    res2 = id_B * f
    print(f"計算 id_B * f: {res2}")
    print(f"是否等於 f? {res2 == f}")

if __name__ == "__main__":
    main()