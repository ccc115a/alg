import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import sympy as sp

# 設定中文字體
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

print("=== 波方程解的數值可視化 ===")
print()

# 參數設定
L = 10.0      # 區域長度
v = 2.0       # 波速
A = 1.0       # 振幅
x = np.linspace(0, L, 200)
t_vals = np.linspace(0, 5, 50)

fig, axes = plt.subplots(2, 2, figsize=(15, 12))
fig.suptitle('波方程的不同解類型', fontsize=16, fontweight='bold')

# 1. 右行波解 u = A*sin(x - vt)
ax1 = axes[0, 0]
for i, t in enumerate(t_vals[::10]):
    u_right = A * np.sin(x - v*t)
    alpha = 0.3 + 0.7 * i / (len(t_vals[::10]) - 1)
    ax1.plot(x, u_right, alpha=alpha, color='red', 
             label=f't={t:.1f}' if i == len(t_vals[::10])-1 else '')
ax1.set_title('右行波: u(x,t) = sin(x - vt)')
ax1.set_xlabel('位置 x')
ax1.set_ylabel('振幅 u')
ax1.grid(True, alpha=0.3)
ax1.set_ylim(-1.5, 1.5)

# 2. 左行波解 u = A*sin(x + vt)
ax2 = axes[0, 1]
for i, t in enumerate(t_vals[::10]):
    u_left = A * np.sin(x + v*t)
    alpha = 0.3 + 0.7 * i / (len(t_vals[::10]) - 1)
    ax2.plot(x, u_left, alpha=alpha, color='blue',
             label=f't={t:.1f}' if i == len(t_vals[::10])-1 else '')
ax2.set_title('左行波: u(x,t) = sin(x + vt)')
ax2.set_xlabel('位置 x')
ax2.set_ylabel('振幅 u')
ax2.grid(True, alpha=0.3)
ax2.set_ylim(-1.5, 1.5)

# 3. 駐波解（第一模式）u = A*sin(πx/L)*cos(πvt/L)
ax3 = axes[1, 0]
for i, t in enumerate(t_vals[::10]):
    u_standing = A * np.sin(np.pi*x/L) * np.cos(np.pi*v*t/L)
    alpha = 0.3 + 0.7 * i / (len(t_vals[::10]) - 1)
    ax3.plot(x, u_standing, alpha=alpha, color='green',
             label=f't={t:.1f}' if i == len(t_vals[::10])-1 else '')
ax3.set_title('駐波（第一模式）: u(x,t) = sin(πx/L)cos(πvt/L)')
ax3.set_xlabel('位置 x')
ax3.set_ylabel('振幅 u')
ax3.grid(True, alpha=0.3)
ax3.set_ylim(-1.5, 1.5)
# 標記節點
nodes = [0, L/2, L]
for node in nodes:
    ax3.axvline(x=node, color='red', linestyle='--', alpha=0.5)
ax3.text(L/4, 1.2, '反節點', ha='center', fontsize=10)
ax3.text(L/2, -1.2, '節點', ha='center', fontsize=10)

# 4. 疊加解（行波 + 駐波）
ax4 = axes[1, 1]
for i, t in enumerate(t_vals[::10]):
    u_traveling = 0.5 * A * np.sin(x - v*t)  # 行波分量
    u_standing = 0.5 * A * np.sin(2*np.pi*x/L) * np.cos(2*np.pi*v*t/L)  # 駐波分量
    u_combined = u_traveling + u_standing
    alpha = 0.3 + 0.7 * i / (len(t_vals[::10]) - 1)
    ax4.plot(x, u_combined, alpha=alpha, color='purple',
             label=f't={t:.1f}' if i == len(t_vals[::10])-1 else '')
ax4.set_title('疊加解: 行波 + 駐波')
ax4.set_xlabel('位置 x')
ax4.set_ylabel('振幅 u')
ax4.grid(True, alpha=0.3)
ax4.set_ylim(-1.5, 1.5)

plt.tight_layout()
plt.show()

print()
print("=== 波的頻率和波長關係 ===")
print()

# 色散關係分析
fig2, (ax5, ax6) = plt.subplots(1, 2, figsize=(15, 6))

# 波數 k 與頻率 ω 的關係 (ω = vk)
k_vals = np.linspace(0, 5, 100)
omega_vals = v * k_vals

ax5.plot(k_vals, omega_vals, 'b-', linewidth=2, label='ω = vk')
ax5.set_xlabel('波數 k (1/m)')
ax5.set_ylabel('角頻率 ω (rad/s)')
ax5.set_title(f'色散關係 (v = {v} m/s)')
ax5.grid(True, alpha=0.3)
ax5.legend()

# 波長與頻率的關係 (λ = 2π/k, f = ω/2π)
wavelength = 2*np.pi / k_vals[1:]  # 避免除零
frequency = omega_vals[1:] / (2*np.pi)

ax6.loglog(frequency, wavelength, 'r-', linewidth=2, label='λ = v/f')
ax6.set_xlabel('頻率 f (Hz)')
ax6.set_ylabel('波長 λ (m)')
ax6.set_title(f'波長與頻率關係 (v = {v} m/s)')
ax6.grid(True, alpha=0.3)
ax6.legend()

plt.tight_layout()
plt.show()

print()
print("=== 有界弦的本征模式 ===")
print()

# 有界弦的前幾個模式
fig3, axes3 = plt.subplots(2, 2, figsize=(15, 10))
fig3.suptitle(f'長度 L={L} 的固定端弦的本征模式', fontsize=16)

x_string = np.linspace(0, L, 200)
modes = [1, 2, 3, 4]

for i, n in enumerate(modes):
    ax = axes3[i//2, i%2]
    
    # 空間部分（包絡）
    spatial_part = np.sin(n * np.pi * x_string / L)
    ax.plot(x_string, spatial_part, 'b-', linewidth=2, 
            label=f'sin({n}πx/L)')
    
    # 時間演化（幾個時刻）
    for j, t in enumerate([0, 0.25, 0.5, 0.75]):
        temporal_part = np.cos(n * np.pi * v * t / L)
        u_mode = spatial_part * temporal_part
        alpha = 0.4 + 0.6 * (1 - j/3)
        ax.plot(x_string, u_mode, '--', alpha=alpha, 
                color=f'C{j+1}', linewidth=1)
    
    ax.set_title(f'第 {n} 模式: f₁ × {n} = {n*v/(2*L):.2f} Hz')
    ax.set_xlabel('位置 x')
    ax.set_ylabel('振幅 u')
    ax.grid(True, alpha=0.3)
    ax.set_ylim(-1.2, 1.2)
    
    # 標記節點
    for node_pos in range(n+1):
        node_x = node_pos * L / n
        ax.axvline(x=node_x, color='red', linestyle=':', alpha=0.5)

plt.tight_layout()
plt.show()

print("圖形說明:")
print("- 實線：空間包絡 sin(nπx/L)")
print("- 虛線：不同時刻的波形")
print("- 紅色虛線：節點位置")
print(f"- 基頻 f₁ = v/(2L) = {v/(2*L):.3f} Hz")
print()

print("=== 關鍵公式總結 ===")
print()
print("1. 波方程: ∂²u/∂t² = v²∂²u/∂x²")
print()
print("2. d'Alembert 通解: u(x,t) = f(x-vt) + g(x+vt)")
print()
print("3. 行波解: u(x,t) = A sin(kx - ωt + φ)")
print("   色散關係: ω = vk")
print("   波長: λ = 2π/k")
print("   頻率: f = ω/(2π) = v/λ")
print()
print("4. 有界弦駐波解:")
print("   uₙ(x,t) = Aₙ sin(nπx/L) cos(nπvt/L + φₙ)")
print("   本征頻率: fₙ = nv/(2L)")
print("   波長: λₙ = 2L/n")
print()
print("5. 一般解是所有本征模式的線性疊加")
print("   u(x,t) = Σ Aₙ sin(nπx/L) cos(nπvt/L + φₙ)")