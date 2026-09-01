from sympy import sqrt
from sympy.physics.quantum import qapply, represent
from sympy.physics.quantum.qubit import Qubit
from sympy.physics.quantum.gate import H, CNOT

def quantum_circuit_example():
    print("\n--- 2. 量子電路與貝爾態 (Bell State) ---")
    
    # 1. 定義初始狀態 |00>
    # Qubit('00') 代表兩個 qubit，都在 0 態
    psi_0 = Qubit('00')
    print(f"初始狀態: {psi_0}")

    # 2. 步驟一：對第一個 Qubit (最右邊那個，索引為 0) 施加 Hadamard Gate
    # H(0) 代表對第 0 號 qubit 作用
    # 數學上： |00> -> |0> * ( |0> + |1> )/sqrt(2)
    step1_op = H(0)
    psi_1 = qapply(step1_op * psi_0)
    
    print(f"H 閘作用後: {psi_1}")
    
    # 3. 步驟二：施加 CNOT Gate (控制反轉)
    # CNOT(0, 1) 代表：第 0 號是控制位 (Control)，第 1 號是目標位 (Target)
    # 注意：SymPy 的 CNOT 定義順序可能與某些教科書不同，需看文件確認
    # 在 SymPy 中 CNOT(control, target)
    step2_op = CNOT(0, 1)
    
    # 將算符作用在目前的狀態 psi_1 上
    psi_final = qapply(step2_op * psi_1)
    
    print(f"CNOT 閘作用後 (最終狀態): {psi_final}")
    
    # 4. 矩陣表示 (Matrix Representation)
    # 將最終的 Bra-Ket 符號轉成 4x1 的行向量 (Column Vector)
    # 對應基底順序為 |00>, |01>, |10>, |11>
    vec_final = represent(psi_final)
    print("\n最終狀態向量 (Vector Form):")
    print(vec_final)
    
    # 你應該會看到:
    # [1/sqrt(2)] -> 對應 |00>
    # [0]
    # [0]
    # [1/sqrt(2)] -> 對應 |11>
    # 這就是標準的糾纏態

if __name__ == "__main__":
    quantum_circuit_example()