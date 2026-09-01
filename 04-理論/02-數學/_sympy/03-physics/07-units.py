from sympy import pprint
from sympy.physics.units import (
    meter, second, kilogram, newton, watt, joule,
    kilometer, hour, gram, 
    speed_of_light, gravitational_constant, planck,
    convert_to
)
from sympy.physics.units.systems import SI

def units_example():
    print("--- 1. 基本單位運算與換算 ---")
    speed_kmh = 100 * kilometer / hour
    print(f"原始速度: {speed_kmh}")
    
    speed_ms = convert_to(speed_kmh, meter / second)
    print(f"換算成 m/s: {speed_ms}")
    
    # 【修正點 1】：先除以單位 (meter/second) 取得純數值，再轉成 float 進行格式化
    speed_val = float(speed_ms / (meter / second))
    print(f"數值部分: {speed_val:.2f} m/s")


    print("\n--- 2. 使用物理常數進行計算 ---")
    m = 1 * gram
    energy = m * speed_of_light**2
    
    print(f"質量: {m}")
    print(f"能量表達式: {energy}")
    
    energy_joules = convert_to(energy, joule)
    print(f"能量 (焦耳): {energy_joules}")
    
    # 【修正點 2】：先除以單位 (joule) 取得純數值
    energy_val = float(energy_joules / joule)
    print(f"數值: {energy_val:.2e} Joules")


    print("\n--- 3. 複合單位化簡 ---")
    m1 = 50 * kilogram
    m2 = 100 * kilogram
    r = 2 * meter
    G = gravitational_constant
    
    force = G * m1 * m2 / r**2
    print(f"計算出的力 (原始單位): {force}")
    
    force_newton = convert_to(force, newton)
    # 這裡沒有用格式化符號 (:.2f)，直接 print 是可以的，它會印出 "8.34e-8*newton"
    print(f"轉換為牛頓: {force_newton.n()} N") 


    print("\n--- 4. 因次一致性檢查 (Dimensional Analysis) ---")
    expr1 = 10 * meter
    expr2 = 5 * second
    
    print(f"嘗試計算 {expr1} + {expr2} ...")
    
    try:
        result = expr1 + expr2
        print("計算成功:", result)
    except Exception as e:
        print(f"錯誤捕獲 (符合預期): {e}")


    print("\n--- 5. 檢查物理量的因次 ---")
    print(f"Newton 的因次組成: {SI.get_dimensional_expr(newton)}")
    print(f"Watt 的因次組成:   {SI.get_dimensional_expr(watt)}")

if __name__ == "__main__":
    units_example()