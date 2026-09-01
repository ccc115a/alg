import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import bernoulli, binom, poisson



# 設定繪圖風格
plt.style.use('seaborn-v0_8-whitegrid')

plt.rcParams['font.sans-serif'] = ['Heiti TC'] # macOS
plt.rcParams['axes.unicode_minus'] = False 

# 伯努利分佈 (Bernoulli Distribution)
print("--- 伯努利分佈 ---")
p_bernoulli = 0.7  # 成功的機率
# 計算成功 (1) 和失敗 (0) 的機率
print(f"P(X=1): {bernoulli.pmf(1, p_bernoulli):.2f}")
print(f"P(X=0): {bernoulli.pmf(0, p_bernoulli):.2f}")
# 生成 10 個樣本
samples_bernoulli = bernoulli.rvs(p_bernoulli, size=10)
print(f"生成樣本: {samples_bernoulli}")
print("\n")


# 二項式分佈 (Binomial Distribution)
print("--- 二項式分佈 ---")
n_binom = 10  # 試驗次數
p_binom = 0.5  # 成功的機率
# 計算在 10 次試驗中，成功 5 次的機率
print(f"P(X=5): {binom.pmf(5, n_binom, p_binom):.2f}")
# 生成 20 個樣本
samples_binom = binom.rvs(n_binom, p_binom, size=20)
print(f"生成樣本 (20個): {samples_binom}")
# 繪製分佈圖
x_binom = np.arange(0, n_binom + 1)
pmf_binom = binom.pmf(x_binom, n_binom, p_binom)
plt.figure(figsize=(8, 4))
plt.bar(x_binom, pmf_binom, color='skyblue', edgecolor='black')
plt.title('二項式分佈 (n=10, p=0.5)')
plt.xlabel('成功次數')
plt.ylabel('機率')
plt.xticks(x_binom)
plt.show()
print("\n")


# 泊松分佈 (Poisson Distribution)
print("--- 泊松分佈 ---")
mu_poisson = 3  # 平均事件發生次數
# 計算事件發生 2 次的機率
print(f"P(X=2): {poisson.pmf(2, mu_poisson):.2f}")
# 生成 15 個樣本
samples_poisson = poisson.rvs(mu_poisson, size=15)
print(f"生成樣本 (15個): {samples_poisson}")
# 繪製分佈圖
x_poisson = np.arange(0, 10)
pmf_poisson = poisson.pmf(x_poisson, mu_poisson)
plt.figure(figsize=(8, 4))
plt.bar(x_poisson, pmf_poisson, color='lightgreen', edgecolor='black')
plt.title('泊松分佈 (平均值=3)')
plt.xlabel('事件發生次數')
plt.ylabel('機率')
plt.xticks(x_poisson)
plt.show()
print("\n")


# 類別分佈 (Categorical Distribution)
# scipy.stats 沒有直接的 categorical 函數，但可以通過 multinomial 實現
print("--- 類別分佈 ---")
# 假設擲一顆不均勻的六面骰子
p_categorical = [0.1, 0.1, 0.1, 0.2, 0.2, 0.3]
# 從中抽取 10 個樣本 (結果會是索引值)
# 注意：這裡使用 np.random.choice 更直觀
samples_categorical = np.random.choice(a=np.arange(1, 7), p=p_categorical, size=10)
print(f"擲骰子結果 (10次): {samples_categorical}")
print("\n")