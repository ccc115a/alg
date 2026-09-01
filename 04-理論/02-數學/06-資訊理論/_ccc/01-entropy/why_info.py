import numpy as np

p = 0.2
print(f'p^10={p**10:.4e} \np^100={p**100:.4e} \np^1000={p**1000:.4e} \np^10000={p**10000:.4e}')

print('-'*40)
print('採用資訊量 log2(1/p) 來表示')
print(f'log2(p)={np.log2(p)}')
print(f'10000*log2(p)={10000*np.log2(p)}')
print(f'log2(p**10000)={np.log2(p**10000)}')
