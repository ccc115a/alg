from sympy import FiniteSet, Union, Intersection, Complement, S

# 1. 建立有限集合
set_a = FiniteSet(1, 2, 3, 4)
set_b = FiniteSet(3, 4, 5, 6)

print(f"集合 A: {set_a}")
print(f"集合 B: {set_b}")

# 2. 聯集 (Union)
u_set = Union(set_a, set_b)
print(f"聯集 (A U B): {u_set}")

# 3. 交集 (Intersection)
i_set = Intersection(set_a, set_b)
print(f"交集 (A n B): {i_set}")

# 4. 差集 (Difference) - 在 A 中但不在 B 中
d_set = set_a - set_b # 或者用 Complement(set_a, set_b)
print(f"差集 (A - B): {d_set}")

# 5. 冪集 (Powerset)
set_c = FiniteSet(1, 2)
print(f"{set_c} 的冪集: {set_c.powerset()}")

from sympy import Interval, S

# 1. 建立區間
# Interval(start, end, left_open=False, right_open=False)
# [1, 5) : 包含 1, 不包含 5
int_1 = Interval(1, 5, right_open=True) 

# (2, 10] : 不包含 2, 包含 10
int_2 = Interval(2, 10, left_open=True)

print(f"\n區間 1: {int_1}")
print(f"區間 2: {int_2}")

# 2. 區間運算
inter_res = Intersection(int_1, int_2)
union_res = Union(int_1, int_2)

print(f"區間交集: {inter_res}") # 應該是 (2, 5)
print(f"區間聯集: {union_res}") # 應該是 [1, 10]

# 3. 檢查元素是否在集合內 (Contains)
print(f"3 是否在區間 1 內? {3 in int_1}")
print(f"5 是否在區間 1 內? {5 in int_1}")

# 4. 特殊集合
# S.Reals (實數), S.Integers (整數), S.Naturals (自然數), S.EmptySet (空集)
real_intersection = Intersection(Interval(-5, 5), S.Integers)
print(f"[-5, 5] 與整數集的交集: {real_intersection}")

from sympy import ConditionSet, Symbol, Eq

x = Symbol('x')

# 定義：所有滿足 x^2 = 4 的實數 x
# ConditionSet(variable, condition, base_set)
sol_set = ConditionSet(x, Eq(x**2, 4), S.Reals)

print(f"\n條件集合表示: {sol_set}")

# 嘗試將其化簡為具體集合 (如果 SymPy 能解出來)
# 注意：ConditionSet 本身是一種延遲求值的表示法，可以用 doit() 嘗試計算，
# 但通常我們會用 sympy.solveset 來直接求解。
from sympy import solveset
solved = solveset(x**2 - 4, x, domain=S.Reals)
print(f"解出來的集合: {solved}")