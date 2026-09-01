from sympy import symbols, pprint, simplify
from sympy.physics.control import TransferFunction, Series, Parallel, Feedback

def control_system_example():
    # 1. 定義符號
    # s: Laplace 變數
    # Kp, Ki: PI 控制器的參數 (比例與積分增益)
    # m, c, k: 物理系統參數 (質量, 阻尼, 彈性係數)
    s, Kp, Ki = symbols('s Kp Ki')
    m, c, k = symbols('m c k', positive=True)

    print("--- 1. 建立轉移函數 (Transfer Functions) ---")
    
    # 建立受控體 (Plant): 一個二階機械系統 (Mass-Spring-Damper)
    # G(s) = 1 / (m*s^2 + c*s + k)
    num_plant = 1
    den_plant = m*s**2 + c*s + k
    G_plant = TransferFunction(num_plant, den_plant, s)
    
    print("受控體 G(s):")
    pprint(G_plant)

    # 建立控制器 (Controller): PI 控制器
    # C(s) = Kp + Ki/s = (Kp*s + Ki) / s
    num_ctrl = Kp*s + Ki
    den_ctrl = s
    C_ctrl = TransferFunction(num_ctrl, den_ctrl, s)
    
    print("\n控制器 C(s):")
    pprint(C_ctrl)


    print("\n--- 2. 系統連接 (Block Diagram Algebra) ---")
    
    # 串聯 (Series): 控制器 -> 受控體
    # L(s) = C(s) * G(s)
    sys_open_loop = Series(C_ctrl, G_plant)
    
    # 並聯 (Feedback): 閉迴路系統
    # 預設為負回授 (Negative Feedback), H(s) = 1 (Unity feedback)
    sys_closed_loop = Feedback(sys_open_loop, TransferFunction(1, 1, s))
    
    print("閉迴路系統 (符號表示):")
    pprint(sys_closed_loop)


    print("\n--- 3. 化簡與求解 (Simplification) ---")
    # 使用 .doit() 執行代數運算，將 Series/Feedback 物件轉為單一 TransferFunction
    TF_closed = sys_closed_loop.doit()
    
    # 進一步化簡表達式
    TF_closed = TF_closed.simplify()
    
    print("閉迴路轉移函數 T(s) = Y(s)/R(s):")
    pprint(TF_closed)
    
    # 應該得到類似: (Ki + Kp*s) / (Ki + s*(k + Kp) + c*s^2 + m*s^3) 的形式


    print("\n--- 4. 數值分析範例 ---")
    # 假設 m=1, c=2, k=1 (一個過阻尼系統)
    # 設計 Kp=10, Ki=5
    values = {m: 1, c: 2, k: 1, Kp: 10, Ki: 5}
    
    TF_numerical = TF_closed.subs(values)
    print(f"代入數值參數 (m=1, c=2, k=1, Kp=10, Ki=5):")
    pprint(TF_numerical)

    print("\n--- 5. 極點與零點分析 (Poles & Zeros) ---")
    # 極點決定系統穩定性 (實部必須小於 0)
    poles = TF_numerical.poles()
    zeros = TF_numerical.zeros()
    
    print(f"系統極點 (Poles): {poles}")
    print(f"系統零點 (Zeros): {zeros}")
    
    # 檢查穩定性
    is_stable = all(complex(p).real < 0 for p in poles)
    print(f"系統是否穩定? {'是 (Stable)' if is_stable else '否 (Unstable)'}")

if __name__ == "__main__":
    control_system_example()