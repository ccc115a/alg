from sympy import symbols, S
from sympy.logic.boolalg import And, Or, Not, Implies, Equivalent, to_cnf, to_dnf, simplify_logic

# 1. 定義布林變數
x, y, z = symbols('x y z')

# 2. 建立邏輯表達式
# 表達式: (x 且 y) 或 (非 x 且 z)
expr1 = Or(And(x, y), And(Not(x), z))

print(f"原始表達式: {expr1}")

# 3. 邏輯代入 (Substitution)
# 假設 x 為真 (True), y 為假 (False)
result = expr1.subs({x: True, y: False})
print(f"代入 x=True, y=False 後的結果: {result}")

# 4. 邏輯化簡 (simplify_logic)
# 例子：De Morgan 定律測試 -> not (x or y) == (not x and not y)
expr2 = Not(Or(x, y))
simplified_expr2 = simplify_logic(expr2)
print(f"De Morgan 化簡前: {expr2}")
print(f"De Morgan 化簡後: {simplified_expr2}")

# 5. 轉換形式
# CNF (合取範式) 和 DNF (析取範式)
expr3 = Equivalent(x, y) # x 若且唯若 y
print(f"等價表達式: {expr3}")
print(f"CNF 形式: {to_cnf(expr3)}")
print(f"DNF 形式: {to_dnf(expr3)}")

from sympy.logic.inference import satisfiable
from sympy.logic.boolalg import truth_table

# 1. 可滿足性檢查 (SAT Solver)
# 檢查是否存在變數組合讓表達式為 True
expr_sat = And(x, Or(y, Not(z)))
models = satisfiable(expr_sat)
print(f"\n表達式 {expr_sat} 的解: {models}")
# 如果返回 False 代表矛盾(無解)，返回字典代表一組解

# 2. 產生真值表 (Truth Table)
print(f"\n{expr_sat} 的真值表:")
print(f"{'x':<5} {'y':<5} {'z':<5} {'Result':<5}")
table = truth_table(expr_sat, [x, y, z])
for t in table:
    # t 是一個 tuple，包含輸入值 list 和結果 bool
    inputs = [str(i) for i in t[0]]
    res = str(t[1])
    print(f"{inputs[0]:<5} {inputs[1]:<5} {inputs[2]:<5} {res:<5}")

