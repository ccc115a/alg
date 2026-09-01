

```
(py310) cccimac@cccimacdeiMac general_stoke % python gn_div_theorem.py
=== 驗證高斯散度定理 (Gauss Divergence Theorem) [3D -> 2D] ===
1. 形式 ω (2-form):
   F = (x**2, y**2, z**2)
   ω = (x**2)dy∧dz + (y**2)dz∧dx + (z**2)dx∧dy
2. 外微分 dω (散度) = (2*x + 2*y + 2*z) dx∧dy∧dz
3. 流形 M: 單位立方體 [0,1] x [0,1] x [0,1]
4. [LHS] 體積積分 (散度總和): 3
5. [RHS] 邊界積分 (6個面):
   - Face x=1 (+x): 1
   - Face x=0 (-x): 0
   - Face y=1 (+y): 1
   - Face y=0 (-y): 0
   - Face z=1 (+z): 1
   - Face z=0 (-z): 0
   [RHS] 總通量: 3
---------------------------------------------------------
驗證結果: 3 == 3 ? True
```
