from sympy import symbols
from sympy.ntheory import isprime, factorint, prime, primepi, nextprime, prevprime

# 1. 質數判定 (Primality Test)
n = 2027
print(f"{n} 是質數嗎? {isprime(n)}") # True

# 2. 生成質數
# 尋找第 100 個質數 (從 2 開始數)
p_100 = prime(100)
print(f"第 100 個質數: {p_100}")

# 計算 100 以內有多少個質數 (Prime Counting Function, pi(x))
count = primepi(100)
print(f"100 以內的質數數量: {count}")

# 尋找鄰近質數
print(f"50 之後的下一個質數: {nextprime(50)}")
print(f"50 之前的上一個質數: {prevprime(50)}")

# 3. 整數分解 (Integer Factorization)
number_to_factor = 315
# 回傳格式為字典: {質因數: 次方數, ...}
# 315 = 3^2 * 5^1 * 7^1
factors = factorint(number_to_factor)
print(f"{number_to_factor} 的質因數分解: {factors}")

# 視覺化輸出 (Visual Style)
from sympy import Mul, Pow
expr = Mul(*[Pow(p, e) for p, e in factors.items()])
print(f"數學式表示: {expr}")

from sympy.ntheory import totient, reduced_totient, primitive_root, discrete_log, n_order
from sympy import mod_inverse

# 1. 歐拉函數 (Euler's Totient Function, phi)
# 計算小於 10 且與 10 互質的正整數個數 (1, 3, 7, 9)
phi = totient(10)
print(f"phi(10) = {phi}")

# 2. 模反元素 (Modular Inverse)
# 尋找 x，使得 3 * x ≡ 1 (mod 11)
# 3 * 4 = 12 ≡ 1 (mod 11)，所以 x = 4
inv = mod_inverse(3, 11)
print(f"3 在 mod 11 下的模反元素: {inv}")

# 3. 原根 (Primitive Root)
# 找出 17 的最小原根
g = primitive_root(17)
print(f"17 的最小原根: {g}")

# 4. 階 (Multiplicative Order)
# 計算 3 在 mod 10 下的階 (即 3^k ≡ 1 (mod 10) 的最小 k)
order = n_order(3, 10)
print(f"Order of 3 mod 10: {order}")

# 5. 離散對數 (Discrete Logarithm)
# 解 2^x ≡ 13 (mod 19)
base = 2
target = 13
modulus = 19
x = discrete_log(modulus, target, base)
print(f"離散對數 log_{base}({target}) mod {modulus} = {x}")
# 驗證: 2**x % 19 應該等於 13

from sympy.ntheory import divisors, divisor_count, primerange
from sympy.functions.combinatorial.numbers import divisor_sigma
n = 24

# 1. 列出所有正因數
divs = divisors(n)
print(f"{n} 的所有因數: {divs}")

# 2. 因數個數與總和
count = divisor_count(n)
total_sum = divisor_sigma(n) # sigma_1 (因數和)
print(f"{n} 的因數個數: {count}")
print(f"{n} 的因數總和: {total_sum}")

# 3. 範圍質數生成 (Sieve)
# primerange(start, end) 生成 [start, end) 區間內的質數
print("10 到 30 之間的質數: ", list(primerange(10, 30)))

from sympy.ntheory.modular import solve_congruence
from sympy.ntheory import binomial_coefficients
from sympy.functions.combinatorial.numbers import legendre_symbol
from sympy import binomial, factorial

# 1. 求解同餘方程組 (Chinese Remainder Theorem)
# 尋找 x 使得:
# x ≡ 2 (mod 3)
# x ≡ 3 (mod 5)
# x ≡ 2 (mod 7)
# 輸入格式: (餘數, 模數)
res = solve_congruence((2, 3), (3, 5), (2, 7))
print(f"同餘方程組的解: x ≡ {res[0]} (mod {res[1]})")

# 2. 勒讓德符號 (Legendre Symbol)
# 判斷 a 是否為 p 的二次剩餘 (即 x^2 ≡ a (mod p) 是否有解)
# 1: 有解, -1: 無解, 0: a是p的倍數
a = 2
p = 7
ls = legendre_symbol(a, p)
print(f"Legendre symbol ({a}/{p}) = {ls} (2 是 mod 7 的二次剩餘嗎? {ls==1})")

# 3. 組合數學相關 (雖然主要在 functions 但數論常數)
print(f"C(5, 2) = {binomial(5, 2)}")
print(f"5! = {factorial(5)}")
