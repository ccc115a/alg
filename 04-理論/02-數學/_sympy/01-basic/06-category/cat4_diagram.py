# cat4_diagram.py
from sympy.categories import Object, NamedMorphism, Diagram
# 修正重點 1：匯入 DiagramGrid
from sympy.categories.diagram_drawing import XypicDiagramDrawer, DiagramGrid

def main():
    # 1. 定義物件
    A = Object('A')
    B = Object('B')
    C = Object('C')

    # 2. 定義具名態射
    f = NamedMorphism(A, B, 'f')
    g = NamedMorphism(B, C, 'g')
    h = NamedMorphism(A, C, 'h') 

    # 3. 建立圖 (Diagram)
    d = Diagram([f, g, h])

    # 修正重點 2：建立網格佈局
    # DiagramGrid 會自動決定 A, B, C 在紙上的座標
    grid = DiagramGrid(d)

    # 4. 使用 XypicDrawer 生成 LaTeX 代碼
    drawer = XypicDiagramDrawer()
    
    # 修正重點 3：同時傳入圖和網格
    latex_code = drawer.draw(d, grid)

    print("--- 生成的 LaTeX (Xy-pic) 代碼 ---")
    print(latex_code)
    print("----------------------------------")
    print("提示: 將代碼放入 LaTeX 並使用 \\usepackage[all]{xy}")

if __name__ == "__main__":
    main()