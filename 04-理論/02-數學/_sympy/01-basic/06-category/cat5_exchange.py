# cat5_exchange.py
from sympy.categories import Object, NamedMorphism, Diagram, CompositeMorphism

def main():
    A = Object('A')
    B = Object('B')
    C = Object('C')
    D = Object('D')

    # 定義路徑 1: A -> B -> D
    f = NamedMorphism(A, B, 'f')
    k = NamedMorphism(B, D, 'k')
    path1 = k * f

    # 定義路徑 2: A -> C -> D
    g = NamedMorphism(A, C, 'g')
    h = NamedMorphism(C, D, 'h')
    path2 = h * g

    print(f"路徑 1: {path1}")
    print(f"路徑 2: {path2}")

    # 建立一個圖
    diagram = Diagram([f, k, g, h])
    
    # 修正重點：使用 .premises 來查看圖中的態射
    print(f"\n圖中的態射 (Premises): {diagram.premises}")
    
    # 檢查是否為複合態射 (CompositeMorphism)
    print(f"\npath1 是複合態射嗎? {isinstance(path1, CompositeMorphism)}")
    print(f"path1 的組成部分: {path1.components}")

if __name__ == "__main__":
    main()