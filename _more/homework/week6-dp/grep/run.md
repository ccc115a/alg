```
(.venv) ccc@teacherdeiMac grep % uv run main.py
正確性驗證 (DP + NFA，語法: 字元/./ *):
  'aa'         'a'          -> False
  'aa'         'a*'         -> True
  'ab'         '.*'         -> True
  'aab'        'c*a*b'      -> True
  'mississippi' 'mis*is*p*.' -> False
  'ab'         '.*c'        -> False
  'aaa'        'a*a'        -> True
  'abab'       'ab*'        -> False
  'abc'        'a.c'        -> True

NFA 額外語法 (| 與 ()):
  'ab'         '(a|b)*'     -> True
  'abc'        '(a|b)*c'    -> True
  'xyz'        '(a|b)*c'    -> False
  'abab'       '(ab)*'      -> True

隨機 fuzz 200 組：
  125 組全部通過

計時 (text=10k, pattern='a*abb')：
  DP   :   20.752 ms
  NFA  :    1.015 ms
```