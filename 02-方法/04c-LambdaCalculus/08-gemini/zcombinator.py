# Z Combinator 定義 (適用於 Python)
Z = lambda f: (lambda x: f(lambda v: x(x)(v)))(lambda x: f(lambda v: x(x)(v)))

# 高階階乘邏輯（完全不用函數名稱，把「自己」當作 f 傳進來）
fact_gen = lambda f: lambda n: 1 if n == 0 else n * f(n - 1)

# 生成階乘函數
fact = Z(fact_gen)

print(fact(5))  # 輸出: 120
print(fact(6))  # 輸出: 720