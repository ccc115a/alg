from sympy.physics.quantum import Dagger, Operator

# === 必須先定義 A 和 B ===
A = Operator('A')
B = Operator('B')

# 計算 A 的伴隨
adj_A = Dagger(A)
print(f"A 的伴隨: {adj_A}")

# 伴隨算子的性質：(AB)† = B† A†
adj_mul = Dagger(A * B)
print(f"(AB)† 展開: {adj_mul}")  # 輸出 Dagger(B) * Dagger(A)