import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm, uniform, expon

# 設定繪圖風格
plt.style.use('seaborn-v0_8-whitegrid')

plt.rcParams['font.sans-serif'] = ['Heiti TC'] # macOS
plt.rcParams['axes.unicode_minus'] = False 

# 常態分佈 (Normal Distribution)
print("--- 常態分佈 ---")
mu_normal = 0  # 平均數
sigma_normal = 1  # 標準差
# 計算 x=1 時的機率密度
print(f"PDF at x=1: {norm.pdf(1, mu_normal, sigma_normal):.2f}")
# 計算 P(X <= 1.96) 的累積機率
print(f"CDF at x=1.96: {norm.cdf(1.96, mu_normal, sigma_normal):.2f}")
# 生成 1000 個樣本
samples_normal = norm.rvs(mu_normal, sigma_normal, size=1000)
# 繪製分佈圖
x_normal = np.linspace(-4, 4, 100)
pdf_normal = norm.pdf(x_normal, mu_normal, sigma_normal)
plt.figure(figsize=(8, 4))
plt.plot(x_normal, pdf_normal, color='blue', lw=2)
plt.title('標準常態分佈 (μ=0, σ=1)')
plt.xlabel('變數值')
plt.ylabel('機率密度')
plt.show()
print("\n")


# 均勻分佈 (Uniform Distribution)
print("--- 均勻分佈 ---")
a_uniform = 0  # 區間起點
b_uniform = 10  # 區間終點
# 計算 x=5 時的機率密度
print(f"PDF at x=5: {uniform.pdf(5, a_uniform, b_uniform):.2f}")
# 計算 P(X <= 5) 的累積機率
print(f"CDF at x=5: {uniform.cdf(5, a_uniform, b_uniform):.2f}")
# 生成 100 個樣本
samples_uniform = uniform.rvs(a_uniform, b_uniform - a_uniform, size=100)
# 繪製分佈圖
x_uniform = np.linspace(-2, 12, 100)
pdf_uniform = uniform.pdf(x_uniform, a_uniform, b_uniform - a_uniform)
plt.figure(figsize=(8, 4))
plt.plot(x_uniform, pdf_uniform, color='orange', lw=2)
plt.title('均勻分佈 (a=0, b=10)')
plt.xlabel('變數值')
plt.ylabel('機率密度')
plt.show()
print("\n")


# 指數分佈 (Exponential Distribution)
print("--- 指數分佈 ---")
lam_expon = 0.5  # 速率參數 (λ)
# 這裡 scipy 的 scale 參數為 1/λ
scale_expon = 1 / lam_expon
# 計算 x=2 時的機率密度
print(f"PDF at x=2: {expon.pdf(2, scale=scale_expon):.2f}")
# 計算 P(X <= 2) 的累積機率
print(f"CDF at x=2: {expon.cdf(2, scale=scale_expon):.2f}")
# 生成 500 個樣本
samples_expon = expon.rvs(scale=scale_expon, size=500)
# 繪製分佈圖
x_expon = np.linspace(0, 10, 100)
pdf_expon = expon.pdf(x_expon, scale=scale_expon)
plt.figure(figsize=(8, 4))
plt.plot(x_expon, pdf_expon, color='purple', lw=2)
plt.title('指數分佈 (λ=0.5)')
plt.xlabel('時間間隔')
plt.ylabel('機率密度')
plt.show()
print("\n")