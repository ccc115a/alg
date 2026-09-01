import matplotlib.pyplot as plt
import matplotlib.patches as patches

# 設定圖表
fig, ax = plt.subplots(figsize=(8, 6))

# 定義矩形的角點
x0, y0 = 1, 1
dx, dy = 4, 3
x1, y1 = x0 + dx, y0 + dy

# 繪製矩形框 (虛線表示輔助幾何)
rect = patches.Rectangle((x0, y0), dx, dy, linewidth=1, edgecolor='gray', facecolor='#f0f8ff', linestyle='--', alpha=0.5)
ax.add_patch(rect)

# 定義箭頭樣式
arrow_props = dict(facecolor='black', width=0.02, head_width=0.15, length_includes_head=True)

# 1. 繪製路徑 1 (下, x 正向)
plt.arrow(x0, y0, dx, 0, **arrow_props, color='blue')
ax.text(x0 + dx/2, y0 - 0.3, r'Path 1: $F_x \cdot \Delta x$', color='blue', ha='center', fontsize=12, fontweight='bold')
ax.text(x0 + dx/2, y0 + 0.2, r'$y$', color='gray', ha='center', fontsize=10)

# 2. 繪製路徑 2 (右, y 正向)
plt.arrow(x1, y0, 0, dy, **arrow_props, color='red')
ax.text(x1 + 0.2, y0 + dy/2, r'Path 2: $F_y(x+\Delta x) \cdot \Delta y$', color='red', va='center', fontsize=12, fontweight='bold')
ax.text(x1 - 0.5, y0 + dy/2, r'$x+\Delta x$', color='gray', va='center', fontsize=10)

# 3. 繪製路徑 3 (上, x 負向)
plt.arrow(x1, y1, -dx, 0, **arrow_props, color='green')
ax.text(x0 + dx/2, y1 + 0.2, r'Path 3: $-F_x(y+\Delta y) \cdot \Delta x$', color='green', ha='center', fontsize=12, fontweight='bold')
ax.text(x0 + dx/2, y1 - 0.3, r'$y+\Delta y$', color='gray', ha='center', fontsize=10)

# 4. 繪製路徑 4 (左, y 負向)
plt.arrow(x0, y1, 0, -dy, **arrow_props, color='purple')
ax.text(x0 - 0.2, y0 + dy/2, r'Path 4: $-F_y \cdot \Delta y$', color='purple', va='center', ha='right', fontsize=12, fontweight='bold')
ax.text(x0 + 0.2, y0 + dy/2, r'$x$', color='gray', va='center', fontsize=10)

# 繪製中間的旋度符號 (CCW)
arc = patches.Arc((x0 + dx/2, y0 + dy/2), 1, 1, theta1=0, theta2=270, color='black', linewidth=2)
ax.add_patch(arc)
# 手動加一個箭頭頭在弧線上
ax.arrow(x0 + dx/2, y0 + dy/2 - 0.5, 0.01, 0, head_width=0.1, head_length=0.1, fc='k', ec='k')
ax.text(x0 + dx/2, y0 + dy/2, r'Curl $(\nabla \times \mathbf{F})_z$', ha='center', va='center', fontsize=14)

# 設定座標軸範圍與隱藏
ax.set_xlim(0, 7)
ax.set_ylim(0, 5)
ax.set_aspect('equal')
ax.axis('off')

plt.title('Visualization of Curl Calculation (Circulation)', fontsize=16)
plt.tight_layout()
plt.show()