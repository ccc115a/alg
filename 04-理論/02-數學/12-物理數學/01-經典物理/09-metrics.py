from sympy import I, pprint, eye
from sympy.physics.matrices import msigma, mgamma, minkowski_tensor, mdft

def physics_matrices_example():
    print("--- 1. Pauli 矩陣 (Quantum Spin) ---")
    # msigma(1) -> sigma_x
    # msigma(2) -> sigma_y
    # msigma(3) -> sigma_z
    sx = msigma(1)
    sy = msigma(2)
    sz = msigma(3)

    print("Sigma X:")
    pprint(sx)
    print("\nSigma Y:")
    pprint(sy)
    
    # 驗證對易關係 (Commutation Relation): [Sx, Sy] = 2*i*Sz
    # [A, B] = A*B - B*A
    commutator = sx * sy - sy * sx
    
    print("\n計算 [Sx, Sy]:")
    pprint(commutator)
    
    expected = 2 * I * sz
    print(f"\n驗證是否等於 2*i*Sz: {commutator == expected}")


    print("\n--- 2. Dirac Gamma 矩陣 (Relativistic QM) ---")
    # mgamma(mu) 生成 4x4 的狄拉克矩陣
    # 預設使用標準表示 (Dirac/Standard Representation)
    g0 = mgamma(0)
    g1 = mgamma(1)
    
    print("Gamma 0 (Time component):")
    pprint(g0)
    
    print("\nGamma 1 (Spatial x component):")
    pprint(g1)
    
    # 驗證 Clifford 代數: {gamma^mu, gamma^nu} = 2 * eta^munu * I
    # 當 mu != nu 時，反對易 (Anti-commutator) 應為 0
    # {g0, g1} = g0*g1 + g1*g0
    anti_commutator = g0 * g1 + g1 * g0
    
    print("\n計算反對易 {gamma^0, gamma^1}:")
    pprint(anti_commutator)
    # 結果應為 4x4 的零矩陣


    print("\n--- 3. Minkowski 度規張量 (Special Relativity) ---")
    # 預設簽名 (Signature) 通常是 (+, -, -, -)
    eta = minkowski_tensor
    print("Minkowski Metric (eta):")
    pprint(eta)
    
    # 驗證 gamma^0 * gamma^0 = eta^00 * I = 1 * I
    # 驗證 gamma^1 * gamma^1 = eta^11 * I = -1 * I
    check_g0 = g0 * g0
    print(f"\ngamma^0 * gamma^0 是否為單位矩陣? {check_g0 == eye(4)}")
    
    check_g1 = g1 * g1
    print(f"gamma^1 * gamma^1 是否為負單位矩陣? {check_g1 == -1 * eye(4)}")


    print("\n--- 4. 離散傅立葉變換矩陣 (DFT Matrix) ---")
    # 生成一個 4x4 的 DFT 矩陣
    # 這在量子計算 (Quantum Fourier Transform) 或 離散訊號處理 中很常見
    dft_4 = mdft(4)
    print("4x4 DFT Matrix:")
    pprint(dft_4)
    
    # 驗證性質: DFT 矩陣是 Unitary 的 (在適當歸一化下)
    # 或者簡單驗證 M * M_inverse = I
    is_invertible = dft_4 * dft_4.inv() == eye(4)
    print(f"\n矩陣是否可逆且乘積為 I? {is_invertible}")

if __name__ == "__main__":
    physics_matrices_example()