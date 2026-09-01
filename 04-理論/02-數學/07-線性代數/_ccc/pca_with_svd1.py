import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_blobs

class PCA_SVD:
    def __init__(self, n_components=None):
        """
        使用 SVD 實現的 PCA 類別
        
        Parameters:
        n_components: int, 要保留的主成分數量
        """
        self.n_components = n_components
        self.components_ = None
        self.explained_variance_ = None
        self.explained_variance_ratio_ = None
        self.mean_ = None
        
    def fit(self, X):
        """
        擬合 PCA 模型
        
        Parameters:
        X: array-like, shape (n_samples, n_features)
        """
        # 1. 資料中心化（減去均值）
        self.mean_ = np.mean(X, axis=0)
        X_centered = X - self.mean_
        
        # 2. 使用 SVD 分解中心化後的資料矩陣
        # X_centered = U * S * V^T
        U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)
        
        # 3. 主成分就是 V^T 的行（或 V 的列）
        self.components_ = Vt
        
        # 4. 計算解釋方差
        # 解釋方差 = (奇異值^2) / (n_samples - 1)
        n_samples = X.shape[0]
        self.explained_variance_ = (S ** 2) / (n_samples - 1)
        
        # 5. 計算解釋方差比例
        total_var = np.sum(self.explained_variance_)
        self.explained_variance_ratio_ = self.explained_variance_ / total_var
        
        # 6. 如果指定了 n_components，則只保留前 n 個主成分
        if self.n_components is not None:
            self.components_ = self.components_[:self.n_components]
            self.explained_variance_ = self.explained_variance_[:self.n_components]
            self.explained_variance_ratio_ = self.explained_variance_ratio_[:self.n_components]
        
        return self
    
    def transform(self, X):
        """
        將資料轉換到主成分空間
        
        Parameters:
        X: array-like, shape (n_samples, n_features)
        
        Returns:
        X_transformed: array-like, shape (n_samples, n_components)
        """
        # 中心化資料
        X_centered = X - self.mean_
        
        # 投影到主成分空間
        return np.dot(X_centered, self.components_.T)
    
    def fit_transform(self, X):
        """
        擬合模型並轉換資料
        """
        return self.fit(X).transform(X)
    
    def inverse_transform(self, X_transformed):
        """
        從主成分空間還原到原始空間
        
        Parameters:
        X_transformed: array-like, shape (n_samples, n_components)
        
        Returns:
        X_reconstructed: array-like, shape (n_samples, n_features)
        """
        return np.dot(X_transformed, self.components_) + self.mean_

# 示例使用
if __name__ == "__main__":
    # 生成示例資料
    np.random.seed(42)
    X, y = make_blobs(n_samples=300, centers=4, n_features=4, 
                      random_state=42, cluster_std=2.0)
    
    print("原始資料形狀:", X.shape)
    print("原始資料前5行:")
    print(X[:5])
    
    # 使用我們實現的 PCA
    pca = PCA_SVD(n_components=2)
    X_pca = pca.fit_transform(X)
    
    print(f"\nPCA 後資料形狀: {X_pca.shape}")
    print("PCA 後資料前5行:")
    print(X_pca[:5])
    
    print(f"\n主成分形狀: {pca.components_.shape}")
    print("解釋方差:", pca.explained_variance_)
    print("解釋方差比例:", pca.explained_variance_ratio_)
    print(f"前{pca.n_components}個主成分總解釋方差比例: {np.sum(pca.explained_variance_ratio_):.3f}")
    
    # 資料重建測試
    X_reconstructed = pca.inverse_transform(X_pca)
    reconstruction_error = np.mean((X - X_reconstructed) ** 2)
    print(f"\n重建誤差 (MSE): {reconstruction_error:.6f}")
    
    # 與 sklearn 的 PCA 比較
    from sklearn.decomposition import PCA as SklearnPCA
    
    sklearn_pca = SklearnPCA(n_components=2)
    X_sklearn_pca = sklearn_pca.fit_transform(X)
    
    print(f"\n與 sklearn PCA 比較:")
    print(f"解釋方差比例差異: {np.abs(pca.explained_variance_ratio_ - sklearn_pca.explained_variance_ratio_)}")
    
    # 視覺化（如果是2D資料）
    if X_pca.shape[1] == 2:
        plt.figure(figsize=(12, 4))
        
        # 原始資料的前兩個特徵
        plt.subplot(1, 2, 1)
        plt.scatter(X[:, 0], X[:, 1], c=y, cmap='viridis', alpha=0.7)
        plt.title('原始資料 (前兩個特徵)')
        plt.xlabel('特徵 1')
        plt.ylabel('特徵 2')
        
        # PCA 後的資料
        plt.subplot(1, 2, 2)
        plt.scatter(X_pca[:, 0], X_pca[:, 1], c=y, cmap='viridis', alpha=0.7)
        plt.title('PCA 轉換後的資料')
        plt.xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.2f})')
        plt.ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.2f})')
        
        plt.tight_layout()
        plt.show()
    
    # 顯示所有主成分的解釋方差比例
    pca_full = PCA_SVD()  # 不限制主成分數量
    pca_full.fit(X)
    
    plt.figure(figsize=(10, 4))
    
    plt.subplot(1, 2, 1)
    plt.bar(range(1, len(pca_full.explained_variance_ratio_) + 1), 
            pca_full.explained_variance_ratio_)
    plt.xlabel('主成分')
    plt.ylabel('解釋方差比例')
    plt.title('各主成分的解釋方差比例')
    
    plt.subplot(1, 2, 2)
    cumsum_var = np.cumsum(pca_full.explained_variance_ratio_)
    plt.plot(range(1, len(cumsum_var) + 1), cumsum_var, 'bo-')
    plt.xlabel('主成分數量')
    plt.ylabel('累積解釋方差比例')
    plt.title('累積解釋方差比例')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()