from sympy.physics.quantum import Operator, Commutator

# === 必須先定義 A 和 B ===
A = Operator('A')
B = Operator('B')

# === 現在才能使用 A 和 B ===
# 定義對易子
comm = Commutator(A, B)

print(f"符號表示: {comm}")

# 展開對易子
expanded = comm.doit()
print(f"展開後: {expanded}")