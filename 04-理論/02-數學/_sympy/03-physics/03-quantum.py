from sympy import I
from sympy.physics.quantum import Commutator, Dagger, Operator
from sympy.physics.quantum.pauli import SigmaX, SigmaY, SigmaZ
from sympy.physics.quantum import represent

def basic_quantum_algebra():
    print("--- 1. 對易算符 (Commutator) 驗證 ---")
    # 定義包立矩陣算符
    sx = SigmaX()
    sy = SigmaY()
    sz = SigmaZ()

    # 定義對易算符 [sx, sy]
    comm = Commutator(sx, sy)
    
    print(f"符號形式: {comm}")
    
    # 展開對易算符: [A, B] = A*B - B*A
    expanded = comm.doit()
    print(f"展開形式: {expanded}")
    
    # 使用 represent 將算符轉為矩陣形式進行運算
    # 預設基底是 Z 基底 (|0>, |1>)
    # 這裡我們會看到矩陣相乘的結果
    matrix_result = represent(expanded)
    print(f"\n矩陣形式運算結果:\n{matrix_result}")
    
    # 驗證是否等於 2*i*sz
    # 我們也把 2*i*sz 轉成矩陣來對比
    expected = represent(2 * I * sz)
    
    print(f"\n驗證 [Sx, Sy] == 2iSz : {matrix_result == expected}")

if __name__ == "__main__":
    basic_quantum_algebra()