import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

# 定義一組一階微分方程
# y[0] = y, y[1] = dy/dt
def ode_system(t, y):
    dy_dt = y[1]
    d2y_dt2 = -3 * y[1] - 2 * y[0]
    return [dy_dt, d2y_dt2]

# 定義初始條件
y0 = [1, 0] # [y(0), dy/dt(0)]
t_span = (0, 10)

# 使用 solve_ivp 求解
solution = solve_ivp(ode_system, t_span, y0, dense_output=True)

# 生成 t 值並計算對應的 y 和 dy/dt 值
t_eval = np.linspace(t_span[0], t_span[1], 200)
y_sol = solution.sol(t_eval)

# 繪製結果
plt.figure(figsize=(8, 6))
plt.plot(t_eval, y_sol[0], label='y(t)')
plt.plot(t_eval, y_sol[1], label="y'(t)")
plt.xlabel('t')
plt.ylabel('值')
plt.title('二階常微分方程求解')
plt.grid(True)
plt.legend()
plt.show()