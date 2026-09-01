import sympy as sp
import numpy as np
import matplotlib.pyplot as plt

# 定义符号变量
t, z, c = sp.symbols('t z c', real=True, positive=True)
k, omega, A, B, phi1, phi2 = sp.symbols('k omega A B phi1 phi2', real=True)

# 定义磁场函数 B(z,t)
# 对于标量情况，我们先求解一个分量
B = sp.Function('B')(z, t)

print("波动方程: ∂²B/∂t² = c²∂²B/∂z²")
print("=" * 50)

# 方法1: 使用分离变量法的一般解
print("\n方法1: 分离变量法的一般解")
print("假设解的形式为: B(z,t) = f(z±ct)")

# 行波解的一般形式
# 向前传播的波: f(z-ct)
# 向后传播的波: g(z+ct)
f = sp.Function('f')
g = sp.Function('g')

# 一般解
general_solution = f(z - c*t) + g(z + c*t)
print(f"一般解: B(z,t) = f(z-ct) + g(z+ct)")

print("\n方法2: 特解 - 平面波解")
print("假设解的形式为: B(z,t) = A*cos(kz - ωt + φ)")

# 特解：平面波
plane_wave = A * sp.cos(k*z - omega*t + phi1)
print(f"平面波解: B(z,t) = A*cos(kz - ωt + φ)")

# 验证平面波解
d2B_dt2 = sp.diff(plane_wave, t, 2)
d2B_dz2 = sp.diff(plane_wave, z, 2)

print(f"\n验证平面波解:")
print(f"∂²B/∂t² = {d2B_dt2}")
print(f"c²∂²B/∂z² = {c**2 * d2B_dz2}")

# 检查是否满足波动方程
wave_eq_check = sp.simplify(d2B_dt2 - c**2 * d2B_dz2)
print(f"\n波动方程检验 (应该为0): {wave_eq_check}")

# 色散关系
dispersion_relation = sp.Eq(omega, c*k)
print(f"色散关系: {dispersion_relation}")

print("\n方法3: 复数形式的解")
# 复数形式的解
I = sp.I
complex_solution = A * sp.exp(I*(k*z - omega*t))
print(f"复数解: B(z,t) = A*exp(i(kz - ωt))")

# 验证复数解
d2B_dt2_complex = sp.diff(complex_solution, t, 2)
d2B_dz2_complex = sp.diff(complex_solution, z, 2)

wave_eq_check_complex = sp.simplify(d2B_dt2_complex - c**2 * d2B_dz2_complex)
print(f"复数解验证 (应该为0): {wave_eq_check_complex}")

print("\n方法4: 使用 SymPy 的 PDE 求解器")
# 定义PDE
pde = sp.Eq(sp.diff(B, t, 2) - c**2 * sp.diff(B, z, 2), 0)
print(f"PDE: {pde}")

# SymPy 的 pdsolve 函数
try:
    pde_solution = sp.pdsolve(pde)
    print(f"SymPy PDE 解: {pde_solution}")
except:
    print("SymPy 无法直接求解此PDE，但我们已经通过其他方法得到了解")

print("\n解的物理意义:")
print("1. 一般解 f(z-ct) + g(z+ct) 表示两个相反方向传播的波")
print("2. f(z-ct): 向+z方向传播的波，速度为c")
print("3. g(z+ct): 向-z方向传播的波，速度为c") 
print("4. 色散关系 ω = ck 表明这是无色散的线性波")

print("\n具体例子:")
print("如果 A=1, k=2π/λ, ω=2πf, φ=0:")
# 具体数值例子
A_val = 1
k_val = 2*sp.pi/sp.Symbol('lambda')
omega_val = 2*sp.pi*sp.Symbol('f')
example_solution = A_val * sp.cos(k_val*z - omega_val*t)
print(f"B(z,t) = cos(2πz/λ - 2πft)")
print(f"其中 f = c/λ (频率), λ 是波长")

# 创建数值求解示例
print("\n" + "="*50)
print("数值示例可视化 (需要 matplotlib)")
print("="*50)

# 数值参数
c_val = 3e8  # 光速
lambda_val = 1  # 波长
f_val = c_val / lambda_val  # 频率
k_val = 2*np.pi/lambda_val
omega_val = 2*np.pi*f_val

# 创建网格
z_vals = np.linspace(-2, 2, 100)
t_vals = np.array([0, 0.25/f_val, 0.5/f_val, 0.75/f_val])

plt.figure(figsize=(12, 8))

for i, t_val in enumerate(t_vals):
    B_vals = np.cos(k_val*z_vals - omega_val*t_val)
    plt.subplot(2, 2, i+1)
    plt.plot(z_vals, B_vals, 'b-', linewidth=2)
    plt.title(f't = {t_val:.2e} s (t = {i*0.25}T)')
    plt.xlabel('z')
    plt.ylabel('B(z,t)')
    plt.grid(True)
    plt.ylim(-1.2, 1.2)

plt.tight_layout()
plt.suptitle('波动方程解的时间演化', y=1.02)
plt.show()

print(f"\n生成了波在不同时刻的空间分布图")