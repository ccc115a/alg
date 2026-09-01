import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.datasets import make_blobs, load_iris, load_wine
from sklearn.preprocessing import StandardScaler
import pandas as pd
import seaborn as sns

# 設定 Matplotlib 支援中文的字型
# 'SimHei' 是 Windows 系統常見的中文黑體字型
# 'Microsoft JhengHei' 適用於繁體中文
# 'WenQuanYi Zen Hei' 適用於 Linux
# plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] # Windows
plt.rcParams['font.sans-serif'] = ['Heiti TC'] # macOS

# 解決負號'-'顯示為方塊的問題
plt.rcParams['axes.unicode_minus'] = False 

class PCAAnalyzer:
    def __init__(self, n_components=None, standardize=True):
        """
        PCA 分析器類別
        
        Parameters:
        n_components: int or float, 要保留的主成分數量或方差比例
        standardize: bool, 是否標準化資料
        """
        self.n_components = n_components
        self.standardize = standardize
        self.pca = None
        self.scaler = None
        self.feature_names = None
        
    def fit_transform(self, X, feature_names=None):
        """
        擬合 PCA 模型並轉換資料
        
        Parameters:
        X: array-like, shape (n_samples, n_features)
        feature_names: list, 特徵名稱
        
        Returns:
        X_pca: 轉換後的資料
        """
        self.feature_names = feature_names
        
        # 資料標準化
        if self.standardize:
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
        else:
            X_scaled = X
            
        # PCA 轉換
        self.pca = PCA(n_components=self.n_components)
        X_pca = self.pca.fit_transform(X_scaled)
        
        return X_pca
    
    def get_summary(self):
        """取得 PCA 分析摘要"""
        if self.pca is None:
            return "請先執行 fit_transform"
        
        summary = {
            'n_components': self.pca.n_components_,
            'explained_variance': self.pca.explained_variance_,
            'explained_variance_ratio': self.pca.explained_variance_ratio_,
            'cumulative_variance_ratio': np.cumsum(self.pca.explained_variance_ratio_),
            'components': self.pca.components_
        }
        return summary
    
    def plot_explained_variance(self, figsize=(12, 5)):
        """繪製解釋方差圖"""
        if self.pca is None:
            print("請先執行 fit_transform")
            return
            
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        
        # 個別解釋方差
        n_components = len(self.pca.explained_variance_ratio_)
        ax1.bar(range(1, n_components + 1), self.pca.explained_variance_ratio_)
        ax1.set_xlabel('主成分')
        ax1.set_ylabel('解釋方差比例')
        ax1.set_title('各主成分的解釋方差比例')
        ax1.grid(True, alpha=0.3)
        
        # 累積解釋方差
        cumsum_var = np.cumsum(self.pca.explained_variance_ratio_)
        ax2.plot(range(1, n_components + 1), cumsum_var, 'bo-', linewidth=2, markersize=8)
        ax2.axhline(y=0.95, color='r', linestyle='--', alpha=0.7, label='95% 方差線')
        ax2.axhline(y=0.90, color='orange', linestyle='--', alpha=0.7, label='90% 方差線')
        ax2.set_xlabel('主成分數量')
        ax2.set_ylabel('累積解釋方差比例')
        ax2.set_title('累積解釋方差比例')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 標註重要資訊
        for i, ratio in enumerate(cumsum_var):
            if ratio >= 0.95:
                ax2.annotate(f'95% at PC{i+1}', 
                           xy=(i+1, ratio), xytext=(i+1, ratio-0.1),
                           arrowprops=dict(arrowstyle='->'))
                break
        
        plt.tight_layout()
        plt.show()
    
    def plot_components_heatmap(self, figsize=(10, 6)):
        """繪製主成分載荷熱力圖"""
        if self.pca is None:
            print("請先執行 fit_transform")
            return
            
        plt.figure(figsize=figsize)
        
        # 準備資料
        components_df = pd.DataFrame(
            self.pca.components_.T,
            columns=[f'PC{i+1}' for i in range(self.pca.n_components_)],
            index=self.feature_names if self.feature_names else [f'Feature {i+1}' for i in range(self.pca.components_.shape[1])]
        )
        
        # 繪製熱力圖
        sns.heatmap(components_df, annot=True, cmap='coolwarm', center=0,
                   fmt='.3f', square=True, cbar_kws={'label': '載荷值'})
        plt.title('主成分載荷熱力圖')
        plt.xlabel('主成分')
        plt.ylabel('原始特徵')
        plt.tight_layout()
        plt.show()
        
        return components_df

def comprehensive_pca_analysis():
    """綜合 PCA 分析示例"""
    
    print("=" * 60)
    print("綜合 PCA 分析示例")
    print("=" * 60)
    
    # 1. 使用鳶尾花資料集
    print("\n1. 鳶尾花資料集分析")
    print("-" * 30)
    
    iris = load_iris()
    X_iris, y_iris = iris.data, iris.target
    feature_names_iris = iris.feature_names
    
    pca_iris = PCAAnalyzer(n_components=4, standardize=True)
    X_iris_pca = pca_iris.fit_transform(X_iris, feature_names_iris)
    
    summary = pca_iris.get_summary()
    print(f"原始資料形狀: {X_iris.shape}")
    print(f"PCA 後形狀: {X_iris_pca.shape}")
    print(f"解釋方差比例: {summary['explained_variance_ratio']}")
    print(f"累積解釋方差比例: {summary['cumulative_variance_ratio']}")
    
    # 視覺化
    pca_iris.plot_explained_variance()
    components_df = pca_iris.plot_components_heatmap()
    
    # 2D 視覺化
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 2, 1)
    scatter = plt.scatter(X_iris_pca[:, 0], X_iris_pca[:, 1], c=y_iris, cmap='viridis')
    plt.xlabel(f'PC1 ({summary["explained_variance_ratio"][0]:.3f})')
    plt.ylabel(f'PC2 ({summary["explained_variance_ratio"][1]:.3f})')
    plt.title('鳶尾花資料 PCA 視覺化')
    plt.colorbar(scatter)
    
    plt.subplot(1, 2, 2)
    # 使用不同標記區分類別
    colors = ['red', 'green', 'blue']
    labels = iris.target_names
    for i, (color, label) in enumerate(zip(colors, labels)):
        plt.scatter(X_iris_pca[y_iris == i, 0], X_iris_pca[y_iris == i, 1], 
                   c=color, label=label, alpha=0.7)
    plt.xlabel(f'PC1 ({summary["explained_variance_ratio"][0]:.3f})')
    plt.ylabel(f'PC2 ({summary["explained_variance_ratio"][1]:.3f})')
    plt.title('鳶尾花資料 PCA（按類別分色）')
    plt.legend()
    
    plt.tight_layout()
    plt.show()
    
    # 2. 使用葡萄酒資料集
    print("\n2. 葡萄酒資料集分析")
    print("-" * 30)
    
    wine = load_wine()
    X_wine, y_wine = wine.data, wine.target
    feature_names_wine = wine.feature_names
    
    # 自動選擇主成分數量（保留 95% 方差）
    pca_wine = PCAAnalyzer(n_components=0.95, standardize=True)
    X_wine_pca = pca_wine.fit_transform(X_wine, feature_names_wine)
    
    summary_wine = pca_wine.get_summary()
    print(f"原始資料形狀: {X_wine.shape}")
    print(f"PCA 後形狀 (95% 方差): {X_wine_pca.shape}")
    print(f"保留的主成分數量: {summary_wine['n_components']}")
    print(f"累積解釋方差比例: {summary_wine['cumulative_variance_ratio'][-1]:.3f}")
    
    pca_wine.plot_explained_variance()
    pca_wine.plot_components_heatmap(figsize=(12, 8))
    
    # 3. 生成高維資料進行降維
    print("\n3. 高維資料降維分析")
    print("-" * 30)
    
    # 生成 100 維的資料
    np.random.seed(42)
    n_samples, n_features = 500, 100
    X_high_dim = np.random.randn(n_samples, n_features)
    # 添加一些結構
    X_high_dim[:, :5] += np.random.randn(n_samples, 5) * 3
    y_synthetic = np.random.randint(0, 3, n_samples)
    
    pca_high_dim = PCAAnalyzer(n_components=0.90, standardize=True)
    X_high_dim_pca = pca_high_dim.fit_transform(X_high_dim)
    
    summary_high = pca_high_dim.get_summary()
    print(f"原始資料形狀: {X_high_dim.shape}")
    print(f"PCA 後形狀 (90% 方差): {X_high_dim_pca.shape}")
    print(f"降維比例: {X_high_dim_pca.shape[1] / X_high_dim.shape[1]:.3f}")
    
    pca_high_dim.plot_explained_variance()
    
    # 4. 比較標準化前後的差異
    print("\n4. 標準化對 PCA 的影響")
    print("-" * 30)
    
    # 創建不同尺度的資料
    np.random.seed(42)
    X_mixed_scale = np.random.randn(200, 4)
    X_mixed_scale[:, 0] *= 1000  # 第一個特徵放大 1000 倍
    X_mixed_scale[:, 1] *= 100   # 第二個特徵放大 100 倍
    
    pca_no_std = PCAAnalyzer(n_components=4, standardize=False)
    pca_with_std = PCAAnalyzer(n_components=4, standardize=True)
    
    X_no_std_pca = pca_no_std.fit_transform(X_mixed_scale)
    X_with_std_pca = pca_with_std.fit_transform(X_mixed_scale)
    
    print("不標準化的解釋方差比例:", pca_no_std.get_summary()['explained_variance_ratio'])
    print("標準化後的解釋方差比例:", pca_with_std.get_summary()['explained_variance_ratio'])
    
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 2, 1)
    plt.bar(range(1, 5), pca_no_std.get_summary()['explained_variance_ratio'])
    plt.title('不標準化的解釋方差比例')
    plt.xlabel('主成分')
    plt.ylabel('解釋方差比例')
    
    plt.subplot(1, 2, 2)
    plt.bar(range(1, 5), pca_with_std.get_summary()['explained_variance_ratio'])
    plt.title('標準化後的解釋方差比例')
    plt.xlabel('主成分')
    plt.ylabel('解釋方差比例')
    
    plt.tight_layout()
    plt.show()
    
    # 5. PCA 用於資料壓縮和重建
    print("\n5. PCA 資料壓縮和重建")
    print("-" * 30)
    
    pca_compress = PCA(n_components=2)
    X_iris_compressed = pca_compress.fit_transform(StandardScaler().fit_transform(X_iris))
    X_iris_reconstructed = pca_compress.inverse_transform(X_iris_compressed)
    X_iris_reconstructed = StandardScaler().fit(X_iris).inverse_transform(X_iris_reconstructed)
    
    reconstruction_error = np.mean((X_iris - X_iris_reconstructed) ** 2)
    print(f"重建誤差 (MSE): {reconstruction_error:.6f}")
    print(f"壓縮比例: {X_iris_compressed.shape[1] / X_iris.shape[1]:.2f}")
    print(f"保留的方差比例: {np.sum(pca_compress.explained_variance_ratio_):.3f}")
    
    return {
        'iris_pca': pca_iris,
        'wine_pca': pca_wine,
        'high_dim_pca': pca_high_dim
    }

# 執行綜合分析
if __name__ == "__main__":
    results = comprehensive_pca_analysis()
    
    print("\n" + "=" * 60)
    print("分析完成！")
    print("=" * 60)