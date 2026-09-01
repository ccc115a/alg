from sympy import symbols, simplify, pprint, N
from sympy.physics.optics import FreeSpace, ThinLens, FlatRefraction
from sympy.physics.optics import lens_makers_formula, mirror_formula
from sympy.physics.optics.gaussopt import BeamParameter, waist2rayleigh

def optics_example():
    # 定義符號
    d1, d2, f, n1, n2 = symbols('d1 d2 f n1 n2', real=True)

    print("--- 1. 射線傳遞矩陣 (ABCD Matrix) ---")
    # 這是幾何光學的核心工具。
    # 假設光線路徑：
    # 1. 經過距離 d1 的自由空間 (Object distance)
    # 2. 通過焦距為 f 的薄透鏡 (Thin Lens)
    # 3. 再經過距離 d2 的自由空間 (Image distance)
    
    # 注意：矩陣乘法順序與光線傳播方向相反 (M_total = Mn * ... * M2 * M1)
    M1 = FreeSpace(d1)
    M2 = ThinLens(f)
    M3 = FreeSpace(d2)
    
    # 總傳輸矩陣
    M_system = M3 * M2 * M1
    
    print("光學系統總矩陣 (ABCD):")
    pprint(M_system)
    
    # 應用：成像條件 (Imaging Condition)
    # 當矩陣的 B 元素 (右上角) 為 0 時，表示從同一點發出的光線會聚在同一點 (成像)
    # M = [[A, B],
    #      [C, D]]
    B_element = M_system[0, 1]
    print("\n成像條件 (令 B = 0):")
    pprint(B_element)
    
    # 如果令 B = 0，其實就是推導出高斯成像公式 (1/p + 1/q = 1/f)
    # d1*(1 - d2/f) + d2 = 0  =>  d1 + d2 = d1*d2/f  =>  1/d2 + 1/d1 = 1/f
    

    print("\n--- 2. 高斯光束 (Gaussian Beams) ---")
    # 用於雷射物理，計算光束腰 (Waist) 與擴散
    # w0: 光束腰半徑 (Beam waist radius)
    # z: 傳播距離
    # wvl: 波長 (wavelength)
    w0, z, wvl = symbols('w0 z lambda', real=True, positive=True)
    
    # 計算瑞利長度 (Rayleigh range) z_r
    # z_r = pi * w0^2 / lambda
    z_r = waist2rayleigh(w0, wvl)
    print(f"瑞利長度 z_r: {z_r}")
    
    # 建立光束參數 q (Complex Beam Parameter)
    # q = z + i * z_r
    p = BeamParameter(wvl, z, w=w0) # 或者直接用 BeamParameter(wvl, z, z_r=z_r)
    
    print(f"光束半徑 w(z) 隨距離的變化公式:")
    # p.w 屬性會回傳光束半徑的表達式
    pprint(p.w)
    
    # 這就是經典公式: w(z) = w0 * sqrt(1 + (z/z_r)^2)


    print("\n--- 3. 經典公式：造鏡者公式 (Lens Maker's Equation) ---")
    # n_lens: 透鏡折射率
    # n_surr: 環境折射率 (surrounding)
    # r1, r2: 曲率半徑
    n_lens, n_surr, r1, r2 = symbols('n_lens n_surr r1 r2')
    
    lens_eq = lens_makers_formula(n_lens, n_surr, r1, r2)
    print("造鏡者公式 (焦距 f 與曲率/折射率的關係):")
    pprint(lens_eq)
    
    print("\n--- 4. 數值範例 (幾何光學) ---")
    # 假設物距 d1=10, 焦距 f=5, 求像距 d2
    # 利用上面的 B_element = 0
    equation_to_solve = B_element.subs({d1: 10, f: 5})
    print(f"代入 d1=10, f=5 後的 B 元素方程式: {equation_to_solve} = 0")
    
    from sympy import solve
    sol = solve(equation_to_solve, d2)
    print(f"解得像距 d2: {sol}")
    # 1/10 + 1/d2 = 1/5 => 1/d2 = 1/10 => d2 = 10

if __name__ == "__main__":
    optics_example()