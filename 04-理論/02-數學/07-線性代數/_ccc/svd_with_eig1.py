import numpy as np
from scipy.linalg import eig
import matplotlib.pyplot as plt

def svd_with_eig(A):
    """
    使用 scipy.linalg.eig 實現 SVD 分解
    
    參數:
    A: 輸入矩陣 (m x n)
    
    返回:
    U: 左奇異向量矩陣 (m x m)
    S: 奇異值數組 (min(m,n),)
    Vt: 右奇異向量矩陣的轉置 (n x n)
    """
    m, n = A.shape
    
    # 計算 A^T A 的特徵值和特徵向量
    ATA = A.T @ A
    eigenvals_V, eigenvecs_V = eig(ATA)
    
    # 計算 A A^T 的特徵值和特徵向量
    AAT = A @ A.T
    eigenvals_U, eigenvecs_U = eig(AAT)
    
    # 處理特徵值（取實部並確保非負）
    eigenvals_V = np.real(eigenvals_V)
    eigenvals_U = np.real(eigenvals_U)
    eigenvals_V = np.maximum(eigenvals_V, 0)  # 避免數值誤差導致的負值
    eigenvals_U = np.maximum(eigenvals_U, 0)
    
    # 處理特徵向量（取實部）
    eigenvecs_V = np.real(eigenvecs_V)
    eigenvecs_U = np.real(eigenvecs_U)
    
    # 計算奇異值
    singular_values_V = np.sqrt(eigenvals_V)
    singular_values_U = np.sqrt(eigenvals_U)
    
    # 按奇異值降序排列
    idx_V = np.argsort(singular_values_V)[::-1]
    idx_U = np.argsort(singular_values_U)[::-1]
    
    singular_values_V = singular_values_V[idx_V]
    singular_values_U = singular_values_U[idx_U]
    eigenvecs_V = eigenvecs_V[:, idx_V]
    eigenvecs_U = eigenvecs_U[:, idx_U]
    
    # 取較小的奇異值集合
    rank = min(m, n)
    S = singular_values_V[:rank]
    
    # 構建 V^T
    Vt = eigenvecs_V.T
    
    # 構建 U
    # 對於 U，我們需要確保維度正確
    U = eigenvecs_U
    
    # 修正 U 的符號以確保 A = U S V^T
    # 通過檢查 A V = U S 來修正符號
    for i in range(rank):
        if S[i] > 1e-10:  # 避免除以接近零的數
            # 計算 A * v_i
            Av = A @ eigenvecs_V[:, i]
            # 期望的 u_i 應該是 Av / s_i
            expected_u = Av / S[i]
            # 檢查符號
            if np.dot(U[:, i], expected_u) < 0:
                U[:, i] = -U[:, i]
    
    return U, S, Vt

# 測試函數
def test_svd():
    """測試 SVD 分解的正確性"""
    # 創建測試矩陣
    np.random.seed(42)
    A = np.random.randn(4, 3)
    
    print("原始矩陣 A:")
    print(A)
    print(f"矩陣形狀: {A.shape}")
    
    # 使用我們的 SVD 實現
    U, S, Vt = svd_with_eig(A)
    
    print(f"\nU 形狀: {U.shape}")
    print(f"S 形狀: {S.shape}")  
    print(f"Vt 形狀: {Vt.shape}")
    
    print("\n奇異值:")
    print(S)
    
    # 重建矩陣
    # 對於重建，我們需要使用適當的維度
    rank = len(S)
    A_reconstructed = U[:, :rank] @ np.diag(S) @ Vt[:rank, :]
    
    print("\n重建矩陣:")
    print(A_reconstructed)
    
    # 計算重建誤差
    reconstruction_error = np.linalg.norm(A - A_reconstructed)
    print(f"\n重建誤差: {reconstruction_error:.2e}")
    
    # 與 numpy 的 SVD 比較
    U_np, S_np, Vt_np = np.linalg.svd(A, full_matrices=True)
    print(f"\nNumPy SVD 奇異值:")
    print(S_np)
    
    print(f"奇異值差異: {np.linalg.norm(S - S_np):.2e}")
    
    return U, S, Vt, A

# 視覺化範例
def visualize_svd_compression():
    """視覺化 SVD 壓縮效果"""
    # 創建一個簡單的圖像矩陣
    x = np.linspace(-2, 2, 50)
    y = np.linspace(-2, 2, 50)
    X, Y = np.meshgrid(x, y)
    
    # 創建一個有趣的圖案
    Z = np.exp(-(X**2 + Y**2)) + 0.5 * np.exp(-((X-1)**2 + (Y-1)**2))
    
    # 進行 SVD 分解
    U, S, Vt = svd_with_eig(Z)
    
    # 不同的近似等級
    ranks = [1, 3, 5, 10]
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    
    # 原始圖像
    im1 = axes[0, 0].imshow(Z, cmap='viridis')
    axes[0, 0].set_title('原始圖像')
    axes[0, 0].axis('off')
    plt.colorbar(im1, ax=axes[0, 0])
    
    # 奇異值圖
    axes[0, 1].plot(S, 'bo-')
    axes[0, 1].set_title('奇異值')
    axes[0, 1].set_xlabel('索引')
    axes[0, 1].set_ylabel('奇異值')
    axes[0, 1].grid(True)
    
    # 累積能量
    cumulative_energy = np.cumsum(S**2) / np.sum(S**2)
    axes[0, 2].plot(cumulative_energy, 'ro-')
    axes[0, 2].set_title('累積能量')
    axes[0, 2].set_xlabel('索引')
    axes[0, 2].set_ylabel('累積能量比例')
    axes[0, 2].grid(True)
    
    # 不同等級的近似
    for i, rank in enumerate(ranks[:3]):
        Z_approx = U[:, :rank] @ np.diag(S[:rank]) @ Vt[:rank, :]
        error = np.linalg.norm(Z - Z_approx, 'fro')
        
        im = axes[1, i].imshow(Z_approx, cmap='viridis')
        axes[1, i].set_title(f'等級-{rank} 近似\n誤差: {error:.3f}')
        axes[1, i].axis('off')
        plt.colorbar(im, ax=axes[1, i])
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    print("=== SVD 分解測試 ===")
    U, S, Vt, A = test_svd()
    
    # print("\n=== SVD 壓縮視覺化 ===")
    # visualize_svd_compression()
    
    # 額外測試：檢驗 U 和 V 的正交性
    print("\n=== 正交性檢驗 ===")
    rank = len(S)
    U_reduced = U[:, :rank]
    Vt_reduced = Vt[:rank, :]
    
    print(f"U^T U 是否接近單位矩陣: {np.allclose(U_reduced.T @ U_reduced, np.eye(rank))}")
    print(f"V V^T 是否接近單位矩陣: {np.allclose(Vt_reduced.T @ Vt_reduced, np.eye(rank))}")
    
    # 檢查 U^T U 的最大偏差
    UTU = U_reduced.T @ U_reduced
    deviation_U = np.max(np.abs(UTU - np.eye(rank)))
    print(f"U^T U 與單位矩陣的最大偏差: {deviation_U:.2e}")
    
    VTV = Vt_reduced.T @ Vt_reduced  
    deviation_V = np.max(np.abs(VTV - np.eye(rank)))
    print(f"V^T V 與單位矩陣的最大偏差: {deviation_V:.2e}")