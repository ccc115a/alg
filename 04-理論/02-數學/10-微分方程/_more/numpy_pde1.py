import numpy as np
import matplotlib.pyplot as plt

# 參數設定
alpha = 0.1
L = 1.0 # 空間長度
T = 0.5 # 總時間
Nx = 50 # 空間點數
Nt = 5000 # 時間點數

# 計算步長
dx = L / (Nx - 1)
dt = T / (Nt - 1)
r = alpha * dt / (dx**2)

# 檢查穩定性條件 (r <= 0.5)
if r > 0.5:
    print("警告: r > 0.5, 數值解可能不穩定！")

# 初始化網格
x = np.linspace(0, L, Nx)
u = np.zeros(Nx)

# 設置初始條件
u[:] = np.sin(np.pi * x)

# 迭代求解
for n in range(0, Nt):
    un = u.copy()
    for i in range(1, Nx - 1):
        u[i] = un[i] + r * (un[i+1] - 2*un[i] + un[i-1])

# 繪製結果
plt.figure(figsize=(8, 6))
plt.plot(x, u, label=f't={T:.2f}')
plt.xlabel('x')
plt.ylabel('u(x,t)')
plt.title('一維熱傳導方程求解 (有限差分法)')
plt.grid(True)
plt.legend()
plt.show()