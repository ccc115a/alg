import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# 設定 Matplotlib 支援中文的字型
# 'SimHei' 是 Windows 系統常見的中文黑體字型
# 'Microsoft JhengHei' 適用於繁體中文
# 'WenQuanYi Zen Hei' 適用於 Linux
# plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] # Windows
plt.rcParams['font.sans-serif'] = ['Heiti TC'] # macOS

# 解決負號'-'顯示為方塊的問題
plt.rcParams['axes.unicode_minus'] = False 

# 1. 產生一個簡單的、有相關性的資料集
# 我們產生一個 100x2 的資料，這兩個特徵是高度相關的
np.random.seed(42)
x = np.random.randn(100) * 10 + 5
y = 2 * x + np.random.randn(100) * 5
data = np.vstack((x, y)).T

print("原始資料維度:", data.shape)
print("原始資料（前 5 行）:")
print(data[:5, :])
print("-" * 30)

# 2. 資料標準化
# PCA 對資料尺度敏感，因此必須進行標準化
scaler = StandardScaler()
scaled_data = scaler.fit_transform(data)

print("標準化後資料維度:", scaled_data.shape)
print("標準化後資料（前 5 行）:")
print(scaled_data[:5, :])
print("-" * 30)

# 3. 執行 PCA
# 設定 n_components=1，表示我們想將資料降為 1 個主成分
pca = PCA(n_components=1)
pca.fit(scaled_data)

# 取得主成分的資訊
print(f"主成分的特徵向量（方向）:\n{pca.components_}")
print(f"每個主成分的變異比率:\n{pca.explained_variance_ratio_}")
print("-" * 30)

# 4. 進行資料降維（投影）
# 使用 transform() 方法將資料投影到主成分上
reduced_data = pca.transform(scaled_data)

print("降維後資料維度:", reduced_data.shape)
print("降維後資料（前 5 行）:")
print(reduced_data[:5, :])
print("-" * 30)

# 5. 可視化原始資料和主成分方向
plt.figure(figsize=(10, 6))
plt.scatter(scaled_data[:, 0], scaled_data[:, 1], alpha=0.7, label='Original Scaled Data')

# 繪製第一個主成分（特徵向量）
component_1 = pca.components_[0]
plt.quiver(0, 0, component_1[0], component_1[1], angles='xy', scale_units='xy', scale=0.5, color='r', label='Principal Component 1')

plt.xlabel("Feature 1 (Scaled)")
plt.ylabel("Feature 2 (Scaled)")
plt.title("PCA: 原始資料與主成分")
plt.axis('equal')
plt.grid(True)
plt.legend()
plt.show()