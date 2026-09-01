
```
py310) cccimac@cccimacdeiMac general_stoke % python gn_green_theorem.py

=== 驗證格林公式 (Green's Theorem) [2D -> 1D] ===
1. 形式 ω = (-y)dx + (x**2)dy
2. 外微分 dω = (2*x + 1) dx∧dy
3. 流形 M (單位圓盤): x=r*cos(θ), y=r*sin(θ)
4. [LHS] 區域積分結果: pi
5. [RHS] 邊界積分結果: pi
驗證: pi == pi ? True
```
