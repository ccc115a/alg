from sympy import symbols, simplify, trigsimp
from sympy.physics.mechanics import (
    ReferenceFrame, Point, Particle, KanesMethod, 
    dynamicsymbols, inertia, kinetic_energy, potential_energy
)

def simple_pendulum_example():
    # 1. 定義物理常數
    m, g, l = symbols('m g l')
    
    # 2. 定義動態符號
    theta = dynamicsymbols('theta')
    
    # 【修正點】: 定義一個獨立的符號 'omega' 來代表角速度
    # 不要使用 dynamicsymbols('theta', 1)，那樣會導致方程式變成恆等式 0=0
    omega = dynamicsymbols('omega') 

    # 3. 建立參考系
    N = ReferenceFrame('N')
    A = ReferenceFrame('A')
    
    # 設定 A 相對於 N 的旋轉
    A.orient(N, 'Axis', [theta, N.z])
    
    # 【修正點】: 設定角速度時使用新的變數 omega
    A.set_ang_vel(N, omega * N.z)

    # 4. 定義幾何位置與速度
    O = Point('O')
    O.set_vel(N, 0)

    P = O.locatenew('P', l * A.x)
    
    # P 點速度計算
    P.v2pt_theory(O, N, A)

    # 5. 定義慣性物體
    Pa = Particle('Pa', P, m)

    # 6. 定義外力
    gravitational_force = (P, m * g * N.x)
    forces = [gravitational_force]

    # 7. 使用凱恩方法
    # q_ind: 廣義座標 [theta]
    # u_ind: 廣義速度 [omega]
    # kd_eqs: 運動學微分方程 [theta的微分 - omega = 0] -> 即 theta_dot = omega
    KM = KanesMethod(N, q_ind=[theta], u_ind=[omega], kd_eqs=[theta.diff() - omega])
    
    # 計算
    fr, frstar = KM.kanes_equations([Pa], forces)

    # 8. 整理並顯示結果
    print("--- 運動方程式 (Equation of Motion) ---")
    eom = fr + frstar
    eom_simplified = trigsimp(eom[0]) 
    
    # 這裡顯示的會包含 omega 的微分 (omega')，即角加速度
    print(f"方程式: {eom_simplified} = 0")
    
    print("\n--- 對角加速度 (omega_dot) 求解 ---")
    mass_matrix = KM.mass_matrix
    forcing_vector = KM.forcing
    
    rhs = mass_matrix.inv() * forcing_vector
    print(f"角加速度 (omega') = {simplify(rhs[0])}")
    
    # 驗證: omega' 就是 theta''
    # 結果應為 -g*sin(theta)/l

if __name__ == "__main__":
    simple_pendulum_example()