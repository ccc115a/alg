from sympy import Function, dsolve, Eq, symbols, cos

# 定義符號變數
theta = symbols('theta')
u = Function('u')
GM = symbols('GM', positive=True) # 萬有引力常數*太陽質量，設為正數
h = symbols('h', positive=True)   # 單位質量的角動量，設為正數

# 建立微分方程
# 我們要解的是 u'' + u = GM/h^2
equation = Eq(u(theta).diff(theta, 2) + u(theta), GM / h**2)

# 使用 dsolve 求解微分方程
solution = dsolve(equation, u(theta))

# 顯示通解
print(f"微分方程: {equation}")
print(f"軌道方程的通解: {solution}")

# 處理通解，使其形式更清晰
# 通解中的常數 C1 和 C2 實際上對應於我們推導中的 A 和 phi
# 為了證明其為橢圓形式，我們需要將通解轉換為我們熟悉的極坐標形式
# 通解一般形式為 u(theta) = C1*sin(theta) + C2*cos(theta) + GM/h^2
# 可以用 C*cos(theta-phi) 來替換 C1*sin + C2*cos
# SymPy 的輸出已經是這個標準形式，我們只是驗證

# 解的 rhs (右側) 部分為我們需要的表達式
rhs_solution = solution.rhs

# 將解轉換為我們所知的圓錐曲線形式
# 我們可以手動替換一下變數名稱來對應物理意義
# 假設 C1 已經是我們方程中的 A*cos(phi)
# 假設 C2 已經是我們方程中的 -A*sin(phi)
# 在這裡，我們主要展示的是方程的形式
print("\n--- 進一步分析 ---")
print("通解的結構為：")
print("u(theta) = (一個常數) * cos(theta) + (另一個常數) * sin(theta) + (常數項)")
print("\n根據三角恆等式，前兩項可合併為 A*cos(theta - phi)")
print(f"因此，解的形式為：u(theta) = A*cos(theta - phi) + GM/h^2")
print("由於 u = 1/r，我們得到：")
print("1/r = A*cos(theta - phi) + GM/h^2")
print("\n這就是圓錐曲線的極坐標方程，當離心率 e < 1 時，軌道為橢圓。")