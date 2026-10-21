```
(.venv) ccc@teacherdeiMac diff % uv run main.py
正確性驗證：
  OK len=10 edits=4
  OK len=10 edits=10
  OK len=10 edits=8
  OK len=50 edits=34
  OK len=50 edits=28
  OK len=50 edits=28
  OK len=200 edits=118
  OK len=200 edits=120
  OK len=200 edits=118

計時 (n=300, 含大量相同字元):
  LCS DP      :    5.375 ms
  Myers O(ND) :    1.065 ms
  speedup     :     5.05x
```