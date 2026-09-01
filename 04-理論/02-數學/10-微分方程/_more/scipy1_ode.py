import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

# 定義微分方程
# dy/dt = f(t, y)
def ode_system(t, y):
    return -2 * y + 4 * t

# 定義初始條件
y0 = [1]
t_span = (0, 5) # 求解的 t 範圍

# 使用 solve_ivp 求解
solution = solve_ivp(ode_system, t_span, y0, dense_output=True)

# 生成 t 值並計算對應的 y 值
t_eval = np.linspace(t_span[0], t_span[1], 100)
y_sol = solution.sol(t_eval)

# 繪製結果
plt.figure(figsize=(8, 6))
plt.plot(t_eval, y_sol[0], label='y(t)')
plt.xlabel('t')
plt.ylabel('y')
plt.title('一階線性微分方程求解')
plt.grid(True)
plt.legend()
plt.show()