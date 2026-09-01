from sympy import S, pprint
from sympy.physics.wigner import clebsch_gordan, wigner_3j, wigner_6j, racah

def angular_momentum_coupling():
    # 注意：在 SymPy 中計算 Wigner 符號時，強烈建議使用 S(1)/2
    # 來表示分數，而不要用 0.5。因為 0.5 是浮點數，會導致無法進行精確的根號簡化。
    j1 = S(1)/2
    j2 = S(1)/2
    
    print("--- 1. Clebsch-Gordan 係數 (CG Coefficients) ---")
    # 物理意義：<j1 m1, j2 m2 | J M>
    # 範例：計算兩個自旋 1/2 粒子耦合成 J=1, M=0 的係數
    # 狀態：第一顆上(m1=1/2)，第二顆下(m2=-1/2)
    m1 = S(1)/2
    m2 = -S(1)/2
    J = 1
    M = 0
    
    cg = clebsch_gordan(j1, j2, J, m1, m2, M)
    
    print(f"計算 CG 係數 < {j1} {m1}, {j2} {m2} | {J} {M} > :")
    pprint(cg)
    # 結果應該是 sqrt(2)/2，代表機率是 (sqrt(2)/2)^2 = 1/2
    
    
    print("\n--- 2. Wigner 3j 符號 ---")
    # 3j 符號是 CG 係數的更對稱形式，常用於原子光譜計算
    # 格式: ( j1  j2  j3 )
    #       ( m1  m2  m3 )
    # 注意：3j 符號的 m3 通常對應 -M
    j3 = 1
    m3 = 0
    
    wj3 = wigner_3j(j1, j2, j3, m1, m2, m3)
    
    print("Wigner 3j symbol:")
    pprint(wj3)


    print("\n--- 3. Wigner 6j 符號 ---")
    # 6j 符號用於處理三個角動量的耦合 (Recoupling)
    # 常用於計算矩陣元
    # 隨便取一組滿足三角不等式的整數例子:
    # {1  2  3}
    # {2  1  2}
    
    w6 = wigner_6j(1, 2, 3, 2, 1, 2)
    print("Wigner 6j symbol:")
    pprint(w6)


    print("\n--- 4. 驗證選擇定則 (Selection Rules) ---")
    # 物理規則：如果 m1 + m2 != M，則 CG 係數必為 0
    # 讓我們試一個不合法的量子數組合
    wrong_cg = clebsch_gordan(j1, j2, J, S(1)/2, S(1)/2, 0) # 1/2 + 1/2 = 1 != 0
    print(f"不合法的量子數 (m1+m2 != M) 結果: {wrong_cg}")

if __name__ == "__main__":
    angular_momentum_coupling()