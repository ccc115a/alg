from sympy.physics.quantum import Ket, Bra, qapply, Operator


# === 必須先定義 A 和 B ===
A = Operator('A')

# 定義一個狀態 (可以是函數 f)
psi = Ket('psi')

# 定義算子作用
action = A * psi
print(f"算子作用: {action}")

# 如果你有具體的定義，可以使用 qapply 進行運算
# 例如定義一個線性算子 L，使得 L|psi> = 3|psi> (本徵值問題)
from sympy.physics.quantum import Operator
from sympy.physics.quantum.qapply import qapply

class MyEigenOperator(Operator):
    # 定義該算子作用在 Ket 上的行為
    def _apply_operator_Ket(self, ket):
        return 3 * ket

L = MyEigenOperator('L')
result = qapply(L * psi)
print(f"應用自定義算子: {result}")  # 輸出 3*|psi>