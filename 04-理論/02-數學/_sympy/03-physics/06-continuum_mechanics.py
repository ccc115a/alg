from sympy import symbols, pprint, simplify
from sympy.physics.continuum_mechanics.beam import Beam

def beam_bending_example():
    # 1. 定義符號
    # E: 楊氏模數, I: 慣性矩, L: 長度, x: 位置座標
    E, I, L, x = symbols('E I L x', positive=True)
    # R1, R2: 兩端未知的反作用力
    R1, R2 = symbols('R1 R2')
    # q: 均佈負載大小 (單位長度的力)
    q = symbols('q', positive=True)

    # 2. 建立樑物件 (Beam Object)
    # 定義樑的長度與剛度 E*I
    b = Beam(L, E, I)

    print("--- 1. 設定負載 (Loads) ---")
    # apply_load(value, start, order, end)
    # order 對照表 (奇異函數階數):
    #  -2: 集中力矩 (Moment)
    #  -1: 集中力 (Point Load)
    #   0: 均佈力 (Distributed Load)
    #   1: 線性漸變力 (Ramp Load)
    
    # 施加左端支撐反力 R1 (集中力, order=-1, 位置 0)
    b.apply_load(R1, 0, -1)
    
    # 施加右端支撐反力 R2 (集中力, order=-1, 位置 L)
    b.apply_load(R2, L, -1)
    
    # 施加均佈負載 q (order=0, 從 0 到 L)
    # 注意：SymPy Beam 的正負號慣例通常定義「向上為正」。
    # 因此向下的重力負載設為 -q
    b.apply_load(-q, 0, 0, end=L)

    print("已施加負載與未知反力。")

    # 3. 設定邊界條件 (Boundary Conditions)
    # 簡支樑兩端不會上下移動 -> 撓度 (Deflection) 為 0
    # bc_deflection = [(位置, 值), ...]
    b.bc_deflection.append((0, 0))  # 左端撓度為 0
    b.bc_deflection.append((L, 0))  # 右端撓度為 0
    
    # 若是懸臂樑 (Cantilever)，則會用到 b.bc_slope (斜率邊界條件)

    print("\n--- 2. 求解反作用力 (Solving for Reactions) ---")
    # 這一行會利用靜力平衡方程式 (Sum F = 0, Sum M = 0) 解出 R1, R2
    b.solve_for_reaction_loads(R1, R2)
    
    print(f"左端反力 R1: {b.reaction_loads[R1]}") # 應為 qL/2
    print(f"右端反力 R2: {b.reaction_loads[R2]}") # 應為 qL/2


    print("\n--- 3. 取得結果方程式 ---")
    # 剪力 (Shear Force)
    shear = b.shear_force()
    print("剪力方程式 V(x):")
    pprint(simplify(shear))
    
    # 彎矩 (Bending Moment)
    moment = b.bending_moment()
    print("\n彎矩方程式 M(x):")
    pprint(simplify(moment))
    
    # 撓度 (Deflection)
    deflection = b.deflection()
    print("\n撓度方程式 y(x):")
    pprint(simplify(deflection))
    # 經典公式解應該是: q*x*(L**3 - 2*L*x**2 + x**3) / (24*E*I) (正負號取決於座標系定義)

    
    print("\n--- 4. 計算最大撓度 (Max Deflection) ---")
    # 對於簡支樑均佈載，最大撓度發生在中央 x = L/2
    max_deflection = deflection.subs(x, L/2)
    
    print(f"中央 (x=L/2) 的撓度值:")
    pprint(simplify(max_deflection))
    # 結果應為著名的: -5 * q * L**4 / (384 * E * I)

if __name__ == "__main__":
    beam_bending_example()