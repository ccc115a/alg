```
(.venv) ccc@teacherdeiMac wordseek % uv run main.py
Boyer-Moore 正確性: OK
fuzzy_search('helo') -> [(1, 'held'), (1, 'hell'), (1, 'hello'), (1, 'help'), (1, 'hero')] ...
Edit distance DP 正確性: OK

精確搜尋 (text=200k, pattern=16):
  Boyer-Moore :    2.225 ms
  str.find    :    0.027 ms

模糊搜尋 (dictionary=22 words, query='helo'):
  edit-dist DP:    0.048 ms / 查詢
```