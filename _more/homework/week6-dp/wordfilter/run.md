```
(.venv) ccc@teacherdeiMac wordfilter % uv run main.py
精確匹配一致性: OK (共 4 命中)
模糊匹配: OK [(2, '敏感詞', 1)]

海量詞過濾 (2007 詞, text=50k):
  Aho-Corasick :    5.389 ms
  命中數       : 750

trie+DP 模糊 (7 詞, text=300, k=1):    0.795 ms
```