(py310) cccimac@cccimacdeiMac 1dwave % python 1dwave_eq_solve.py 
=== 波方程的 SymPy 求解 ===

1. 波方程的定義:
   ∂²u/∂t² = v² ∂²u/∂x²

2. SymPy 表示的波方程:
   Eq(Derivative(u(x, t), (t, 2)), v**2*Derivative(u(x, t), (x, 2)))

=== 方法一：特徵線方法（d'Alembert 解） ===

3. d'Alembert 通解（行波解）:
   u(x,t) = f(x - vt) + g(x + vt)
   其中 f 和 g 是任意可微函數

4. 正弦波特解示例:
   u(x,t) = A*sin(k*x - omega*t + phi)
   其中 ω = kv（色散關係）

5. 驗證正弦波解滿足波方程:
   ∂²u/∂t² = -A*omega**2*sin(k*x - omega*t + phi)
   v²∂²u/∂x² = -A*k**2*v**2*sin(k*x - omega*t + phi)
   當 ω = kv 時:
   ∂²u/∂t² = -A*k**2*v**2*sin(-k*t*v + k*x + phi)
   v²∂²u/∂x² = -A*k**2*v**2*sin(-k*t*v + k*x + phi)
   等式成立：True

=== 方法二：分離變數法 ===

6. 假設 u(x,t) = X(x)T(t)，代入波方程得到:
   X(x)T''(t) = v²X''(x)T(t)
   分離變數：T''(t)/v²T(t) = X''(x)/X(x) = -k²

7. 求解時間部分 T''(t) + (kv)²T(t) = 0:
   Eq(T(t), C1*sin(t*v*Abs(k)) + C2*cos(k*t*v))

8. 求解空間部分 X''(x) + k²X(x) = 0:
   Eq(X(x), C1*sin(x*Abs(k)) + C2*cos(k*x))

9. 完整的分離變數解:
   u(x,t) = [A·cos(kx) + B·sin(kx)] × [C·cos(kvt) + D·sin(kvt)]
   或展開為:
   u(x,t) = A₁·cos(kx)cos(kvt) + A₂·cos(kx)sin(kvt)
            + A₃·sin(kx)cos(kvt) + A₄·sin(kx)sin(kvt)

=== 常見的波解類型 ===

10. 常見波解示例:

    a) 右行波: u(x,t) = f(x - vt)
       例如: u(x,t) = sin(x - vt)
    b) 左行波: u(x,t) = g(x + vt)
       例如: u(x,t) = cos(x + vt)
    c) 駐波: u(x,t) = A·sin(kx)cos(kvt)
       這是兩個反向傳播波的疊加

11. 邊界條件和初始條件:
    - 固定端: u(0,t) = u(L,t) = 0
    - 自由端: ∂u/∂x|ₓ₌₀ = ∂u/∂x|ₓ₌ₗ = 0
    - 初始位移: u(x,0) = f(x)
    - 初始速度: ∂u/∂t|ₜ₌₀ = g(x)

=== 特殊情況：有界弦的駐波解 ===

12. 長度為 L 的固定端弦的駐波解:
    邊界條件: u(0,t) = u(L,t) = 0
    特征頻率: ωₙ = nπv/L  (n = 1,2,3,...)
    對應波數: kₙ = nπ/L

13. 第 n 個模式的解:
    uₙ(x,t) = Aₙ·sin(nπx/L)cos(nπvt/L)

14. 一般解（所有模式的疊加）:
    u(x,t) = Σ[n=1 to ∞] Aₙ·sin(nπx/L)cos(nπvt/L + φₙ)
    其中 Aₙ 和 φₙ 由初始條件決定

=== 總結 ===

波方程 ∂²u/∂t² = v²∂²u/∂x² 的通解包括:
1. d'Alembert 解: u(x,t) = f(x-vt) + g(x+vt)
2. 行波解: u(x,t) = A·sin(kx ± ωt + φ)，其中 ω = kv
3. 駐波解: u(x,t) = A·sin(kx)cos(ωt + φ)
4. 一般解是以上基本解的線性疊加

具體的解取決於:
- 邊界條件（固定端、自由端等）
- 初始條件（初始位移和速度）
- 波傳播的幾何形狀（一維、二維、三維）