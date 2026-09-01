import numpy as np
from numpy.linalg import qr

def eigenvalue_decomposition_qr(A, max_iterations=1000, tolerance=1e-8):
    """
    使用 QR 演算法計算矩陣的特徵值。
    
    參數:
    A (numpy.ndarray): 待計算特徵值的方陣。
    max_iterations (int): 最大迭代次數。
    tolerance (float): 判斷收斂的容忍度。當對角線下方的元素足夠接近零時，即視為收斂。
    
    回傳:
    numpy.ndarray: 矩陣 A 的特徵值陣列 (近似值)。
    """
    # 確保輸入是浮點數矩陣
    A_k = np.array(A, dtype=float)
    n = A_k.shape[0]

    # 檢查是否為方陣
    if A_k.shape[0] != A_k.shape[1]:
        raise ValueError("輸入矩陣必須是方陣才能進行特徵值分解。")

    print(f"--- 開始 QR 演算法 (最大迭代次數: {max_iterations}) ---")
    
    for k in range(max_iterations):
        # 1. QR 分解: A_k = Q_k R_k
        Q_k, R_k = qr(A_k)
        
        # 2. 重構: A_{k+1} = R_k Q_k
        A_next = R_k @ Q_k
        
        # 3. 檢查收斂性
        # 收斂條件通常是檢查下三角部分的元素是否趨近於零。
        # 這裡我們只檢查最下層次對角線下的元素是否足夠小。
        # 這種檢查方式較為簡單，但對於大規模矩陣可能不夠嚴謹。
        off_diagonal_sum = np.sum(np.abs(np.tril(A_next, k=-1)))

        if off_diagonal_sum < tolerance:
            # 矩陣已收斂到上三角形式
            print(f"演算法在第 {k + 1} 次迭代後收斂。")
            A_k = A_next
            break
            
        A_k = A_next

        # 簡單印出進度
        if (k + 1) % 50 == 0:
            print(f"第 {k + 1} 次迭代，非對角線誤差: {off_diagonal_sum:.4e}")

    if k == max_iterations - 1:
        print(f"警告：達到最大迭代次數 {max_iterations}，可能尚未完全收斂。")

    # 特徵值就是最終收斂矩陣的對角線元素
    eigenvalues = np.diag(A_k)
    return eigenvalues

# --- 範例 ---
# 選擇一個簡單的對稱矩陣，已知特徵值為 1, 2, 3
A = np.array([[2, 1, 0],
              [1, 2, 1],
              [0, 1, 2]])

# 執行 QR 演算法
calculated_eigenvalues = eigenvalue_decomposition_qr(A)

print("-" * 50)
print(f"原始矩陣:\n{A}")
print(f"計算得出的特徵值:\n{calculated_eigenvalues}")

# 驗證結果（使用 NumPy 內建函式計算特徵值進行比較）
true_eigenvalues = np.linalg.eigvals(A)
print(f"NumPy 內建函式驗證的特徵值:\n{true_eigenvalues}")
print(f"誤差（計算值 - 真實值）:\n{calculated_eigenvalues - true_eigenvalues}")
