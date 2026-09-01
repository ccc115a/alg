from sympy import symbols, simplify
from sympy.physics.vector import ReferenceFrame, dynamicsymbols, time_derivative

def vector_kinematics_example():
    # 1. 定義參考系
    # N: 慣性系 (Ground)
    # A: 轉盤系 (Disc)
    N = ReferenceFrame('N')
    A = ReferenceFrame('A')

    # 2. 定義動態符號 (隨時間變化的變數)
    # theta: 轉盤轉過的角度
    # r: 質點離圓心的距離
    theta, r = dynamicsymbols('theta r')

    # 3. 設定參考系的旋轉關係
    # A 參考系繞著 N 的 Z 軸 (N.z) 旋轉 theta 角度
    A.orient(N, 'Axis', [theta, N.z])
    
    # 你可以查看旋轉矩陣 (Direction Cosine Matrix)
    # print(A.dcm(N)) 

    # 設定 A 在 N 中的角速度 (Angular Velocity)
    # 雖然 orient 之後通常會自動計算，但顯式設定是好習慣，或者我們讓 sympy 自動算
    # 這裡我們讓 sympy 自動處理，因為 orient 已經定義了幾何關係
    
    # 4. 定義位置向量 (Position Vector)
    # 假設原點重合，質點位置 p 僅在 A 參考系的 x 軸上移動
    p_vec = r * A.x

    print(f"位置向量 (在 A 系表示): {p_vec}")

    # 5. 向量運算：點積與叉積 (Dot & Cross Product)
    # 演示：A.x 與 N.y 的點積 (會隨 theta 變化)
    dot_prod = A.x & N.y  # & 符號代表 Dot product
    print(f"A.x dot N.y = {dot_prod}") # 應該是 sin(theta)

    # 6. 運動學：速度計算 (Velocity)
    # 計算 p_vec 在 N 參考系中的時間微分 (即相對於地面的速度)
    # 使用 .dt(ReferenceFrame) 方法
    v_vec = p_vec.dt(N)
    
    print("\n--- 速度向量 (Velocity in N) ---")
    print(f"原始形式: {v_vec}")
    # 結果解釋: r'*A.x (徑向速度) + r*theta'*A.y (切向速度)

    # 7. 運動學：加速度計算 (Acceleration)
    # 再對 N 微分一次
    a_vec = v_vec.dt(N)

    print("\n--- 加速度向量 (Acceleration in N) ---")
    print(f"原始形式: {a_vec}")
    
    # 為了讓結果更易讀，我們通常會整理一下
    # 這裡我們將結果顯示出來，並解釋各項物理意義
    # sympy 的輸出可能會沒有合併同類項，我們手動觀察即可
    
    # 8. 向量基底轉換 (Express)
    # 上面的結果都是用 A.x, A.y 表達的 (因為這是最自然的描述方式)
    # 如果我們硬要把結果轉成用 N.x, N.y 表達：
    v_vec_in_N_basis = v_vec.express(N)
    print("\n--- 速度向量 (轉換到 N 基底表示) ---")
    print(v_vec_in_N_basis)

if __name__ == "__main__":
    vector_kinematics_example()