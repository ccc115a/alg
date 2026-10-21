```
(.venv) ccc@teacherdeiMac cnk % uv run main.py
正確性: 全部與 math.comb 一致

計時:
  DP 1D (O(nk) 時間/O(k) 空間) :     2992.8 us
  DP 2D (O(nk) 時間/O(nk) 空間):     4884.9 us
  階乘公式 (O(n) 用 math)      :       18.8 us

純遞迴 vs DP (小 n 示範重複子問題):
  n= 10 k=  5  遞迴=     0.029 ms  DP=    1.51 us
  n= 15 k=  7  遞迴=     0.754 ms  DP=    3.22 us
  n= 20 k= 10  遞迴=    20.375 ms  DP=    5.09 us
  n= 25 k= 12  遞迴=   567.566 ms  DP=    7.23 us
  n= 28 k= 14  遞迴=  4359.722 ms  DP=    9.17 us
```