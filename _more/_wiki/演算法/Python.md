# Python 程式語言

**標籤**: #Python #程式語言 #資料科學 #演算法 #物件導向
**日期**: 2024-01-15

Python 是一種高階、解釋型的程式語言，由 Guido van Rossum 於 1991 年首次發布。Python 以其簡潔的語法、强大的功能、和廣泛的應用領域，成為最受歡迎的程式語言之一。在演算法實現、資料科學、機器學習、網頁開發等領域都有廣泛應用。

## Python 的發展歷程

### 誕生 (1991)

Guido van Rossum 在荷蘭發布了 Python 的第一個版本。名字來源於英國喜劇團體 Monty Python，而非蛇。

### Python 2 時代 (2000-2020)

Python 2 帶來了很多改進，包括 Unicode 支援、列表推導等。2020 年停止維護。

### Python 3 時代 (2008-現在)

Python 3 是一次重大的語法改進，解決了 Python 2 的許多設計缺陷。目前是主流版本。

### Python 的設計哲學

Python 社群有一句著名的格言：「There should be one—and preferably only one—obvious way to do it」。這體現了 Python 設計的核心原則：簡潔、明確、可讀。

## 基本語法

### 變數與資料類型

```python
# 數值
integer = 42           # 整數
floating = 3.14        # 浮點數
complex_num = 3 + 4j   # 複數

# 字串
name = "Hello"         # 雙引號
message = 'World'      # 單引號
multiline = """多行
字串"""                # 三引號
raw_string = r"raw\nstring"  # 原始字串

# 格式化
formatted = f"{name} {floating:.2f}"  # f-string
formatted = "{} {}".format(name, message)  # format()

# 位元組
byte_data = b"bytes"
```

### 運算子

```python
# 算術
a + b, a - b, a * b, a / b    # 加減乘除
a // b, a % b                  # 整除、取餘
a ** b                        # 次方
divmod(a, b)                  # 商和餘數

# 比較
a == b, a != b, a < b         # 等於、不等於、小於
a <= b, a > b, a >= b         # 小於等於、大於、大於等於

# 邏輯
and, or, not                  # 且、或、反
# 注意：and/or 會返回最後一個評估值

# 位元
a & b, a | b, a ^ b           # AND、OR、XOR
~a, a << b, a >> b            # 反轉、左移、右移
```

### 控制流

```python
# if-elif-else
if condition:
    pass
elif other_condition:
    pass
else:
    pass

# match (Python 3.10+)
def http_status(status):
    match status:
        case 200:
            return "OK"
        case 404:
            return "Not Found"
        case _:
            return "Unknown"

# for 迴圈
for i in range(10):           # 0-9
    pass

for i in range(1, 11):        # 1-10
    pass

for i in range(0, 10, 2):     # 0,2,4,6,8
    pass

# enumerate 和 zip
for i, item in enumerate(items):
    print(i, item)

for a, b in zip(list1, list2):
    print(a, b)

# while 迴圈
while condition:
    pass

# break, continue, pass
for i in range(10):
    if i == 3:
        continue    # 跳過這次
    if i == 7:
        break       # 提前結束
    pass
```

## 資料結構

### 列表 (List)

```python
# 建立
lst = [1, 2, 3]
lst = list(range(10))
lst = [0] * 5              # [0, 0, 0, 0, 0]

# 存取
lst[0]                     # 第一個元素
lst[-1]                    # 最後一個元素

# 切片
lst[1:4]                   # 索引 1 到 3
lst[::2]                   # 間隔 2
lst[::-1]                  # 反向

# 操作
lst.append(4)              # 追加
lst.insert(0, -1)          # 插入
lst.extend([5, 6])        # 擴展
lst.pop()                  # 彈出
lst.remove(4)              # 移除第一個 4
del lst[0]                 # 刪除
lst.clear()                # 清空

# 搜尋
lst.index(3)               # 找到索引
lst.count(3)               # 出現次數
3 in lst                   # 是否存在

# 排序
sorted(lst)               # 返回新排序列表
lst.sort()                 # 原地排序
lst.sort(reverse=True)     # 降序
lst.sort(key=lambda x: x['value'])  # 自訂排序

# 列表推導
squares = [x**2 for x in range(10)]
evens = [x for x in range(20) if x % 2 == 0]
matrix = [[i*j for j in range(3)] for i in range(3)]
```

### 元組 (Tuple)

```python
# 建立
tup = (1, 2, 3)
tup = 1, 2, 3              # 括號可省略
tup = (1,)                 # 單元素元組

# 不可變
# tup[0] = 10  # TypeError

# 操作
x, y, z = tup              # 解包
a, *rest = tup             # 星號解包
tup.index(2)               # 搜尋
tup.count(2)               # 計數

# 用途：多返回值、字典鍵、函式多參數
def func():
    return 1, 2, 3

result = func()  # (1, 2, 3)
```

### 集合 (Set)

```python
# 建立
s = {1, 2, 3}
s = set([1, 2, 3])
s = set()                  # 空集合（不是 {}）

# 操作
s.add(4)                   # 新增
s.remove(4)                # 移除（不存在會報錯）
s.discard(4)               # 移除（不存在不報錯）
s.pop()                    # 彈出任意元素
s.clear()                  # 清空

# 集合運算
s1 | s2                    # 聯集
s1 & s2                    # 交集
s1 - s2                    # 差集
s1 ^ s2                    # 對稱差集

s1.issubset(s2)            # 子集
s1.issuperset(s2)          # 超集

# 集合推導
doubled = {x*2 for x in range(10)}
```

### 字典 (Dictionary)

```python
# 建立
d = {'a': 1, 'b': 2}
d = dict(a=1, b=2)
d = dict(zip(keys, values))
d = {k: v for k, v in pairs}  # 推導

# 操作
d['key']                   # 存取
d.get('key', default)      # 安全取得
d.setdefault('key', [])    # 預設值
d['key'] = value           # 設定
del d['key']               # 刪除
d.pop('key')               # 彈出

# 檢查
'key' in d                 # 鍵是否存在

# 遍歷
for key in d:
    print(key, d[key])

for key, value in d.items():
    print(key, value)

for key in d.keys():
    print(key)

for value in d.values():
    print(value)

# 合併 (Python 3.9+)
d3 = d1 | d2
d1 |= d2                   #原地合併

# 排序
sorted(d.items(), key=lambda x: x[1])  # 按值排序
```

## 函式

### 定義與呼叫

```python
def greet(name, greeting="Hello"):
    """文件字串"""
    return f"{greeting}, {name}!"

# 預設參數
def func(a, b=10, *args, **kwargs):
    # args: 可變位置參數
    # kwargs: 可變關鍵字參數
    pass

# 函式也是物件
func = lambda x: x ** 2
functions = [func, lambda x: x * 2]
```

### 裝飾器

```python
def timer(func):
    def wrapper(*args, **kwargs):
        import time
        start = time.time()
        result = func(*args, **kwargs)
        print(f"執行時間: {time.time() - start}")
        return result
    return wrapper

@timer
def slow_function():
    import time
    time.sleep(1)

# 多個裝飾器
@decorator1
@decorator2
def func():
    pass
```

### 生成器

```python
def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

# 使用
for num in fibonacci(10):
    print(num)

gen = fibonacci(10)
next(gen)  # 取得下一個值
```

### 閉包

```python
def make_counter():
    count = 0
    def counter():
        nonlocal count
        count += 1
        return count
    return counter

c = make_counter()
c()  # 1
c()  # 2
```

## 常用模組

### collections

```python
from collections import deque, Counter, defaultdict, OrderedDict

# deque: 雙端佇列
dq = deque([1, 2, 3])
dq.appendleft(0)
dq.append(4)
dq.popleft()
dq.pop()

# Counter: 計數器
c = Counter(['a', 'b', 'a', 'c', 'a'])
c['a']                    # 3
c.most_common(2)          # [('a', 3), ('b', 1)]

# defaultdict: 預設字典
d = defaultdict(list)
d['key'].append(1)        # 不會報錯

# OrderedDict: 有序字典
od = OrderedDict()
od['a'] = 1
od['b'] = 2
```

### heapq

```python
import heapq

# 最小堆
heap = [3, 1, 4, 1, 5]
heapq.heapify(heap)       # 轉為堆
heapq.heappush(heap, 0)   # 插入
heapq.heappop(heap)       # 彈出最小值
heapq.heappushpop(heap, 2)  # 先push後pop

# 最大堆 (用負數)
max_heap = [-x for x in heap]
heapq.heappush(max_heap, -10)

# nlargest / nsmallest
heapq.nlargest(3, heap)   # 最大的3個
heapq.nsmallest(3, heap)  # 最小的3個
```

### bisect

```python
import bisect

lst = [1, 3, 5, 7, 9]
bisect.bisect_left(lst, 4)   # 2 (插入位置)
bisect.bisect_right(lst, 5) # 3
bisect.insort(lst, 4)       # 插入並保持排序
```

### itertools

```python
import itertools

# product: 笛卡爾積
for a, b in itertools.product([1, 2], [3, 4]):
    # (1,3), (1,4), (2,3), (2,4)
    pass

# permutations: 排列
for p in itertools.permutations([1, 2, 3], 2):
    pass

# combinations: 組合
for c in itertools.combinations([1, 2, 3], 2):
    pass

# chain: 鏈接
for x in itertools.chain([1, 2], [3, 4]):
    pass

# groupby: 分組
for key, group in itertools.groupby([1,1,2,2,1]):
    pass

# cycle: 無限循環
# islice: 切片
```

### functools

```python
from functools import lru_cache, partial, reduce

# lru_cache: 記憶化
@lru_cache(maxsize=128)
def fib(n):
    if n < 2:
        return n
    return fib(n-1) + fib(n-2)

# partial: 偏函式
def power(base, exponent):
    return base ** exponent

square = partial(power, exponent=2)
square(4)  # 16

# reduce: 累積
from functools import reduce
result = reduce(lambda a, b: a + b, [1, 2, 3, 4], 0)  # 10
```

### 匿名算法實現

```python
# 二分搜尋
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1

# 快速排序
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)

# 合併排序
def mergesort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = mergesort(arr[:mid])
    right = mergesort(arr[mid:])
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

# 堆排序
def heapsort(arr):
    import heapq
    heapq.heapify(arr)
    return [heapq.heappop(arr) for _ in range(len(arr))]
```

## 類別與物件

### 定義

```python
class Person:
    # 類別變數
    species = "Homo sapiens"
    
    # 建構函式
    def __init__(self, name, age):
        # 實例變數
        self.name = name
        self.age = age
    
    # 方法
    def greet(self):
        return f"Hello, I'm {self.name}"
    
    # 類別方法
    @classmethod
    def create(cls, name, age):
        return cls(name, age)
    
    # 靜態方法
    @staticmethod
    def validate_age(age):
        return age >= 0
    
    # 魔術方法
    def __str__(self):
        return f"Person({self.name}, {self.age})"
    
    def __repr__(self):
        return f"Person(name='{self.name}', age={self.age})"
    
    def __eq__(self, other):
        return self.name == other.name and self.age == other.age
    
    def __lt__(self, other):
        return self.age < other.age
    
    def __len__(self):
        return self.age
    
    def __call__(self):
        return f"{self.name} says hi!"
```

### 繼承

```python
class Student(Person):
    def __init__(self, name, age, grade):
        super().__init__(name, age)
        self.grade = grade
    
    def greet(self):
        return f"Hi, I'm {self.name} in grade {self.grade}"

# 多重繼承
class Teacher(Person):
    pass

class TeachingAssistant(Student, Teacher):
    pass
```

### 封裝

```python
class BankAccount:
    def __init__(self):
        self._balance = 0      # 單下劃線：受保護
        self.__pin = '1234'    # 雙下劃線：名稱修飾
    
    @property
    def balance(self):
        return self._balance
    
    @balance.setter
    def balance(self, value):
        if value < 0:
            raise ValueError("Balance cannot be negative")
        self._balance = value
```

## 例外處理

```python
try:
    result = 10 / 0
except ZeroDivisionError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"Unexpected: {e}")
else:
    print("No exception")
finally:
    print("Cleanup")

# 自訂例外
class ValidationError(Exception):
    pass

raise ValidationError("Invalid input")
```

## 模組與套件

### import

```python
import math
import random
from collections import deque, Counter
from pathlib import Path as p
import numpy as np  # as 別名
```

### 建立模組

```python
# mymodule.py
def function():
    pass

class MyClass:
    pass

if __name__ == "__main__":
    # 直接執行時的程式碼
    function()
```

## 常用技巧

### 交換變數

```python
a, b = b, a
```

### 切片反轉

```python
lst[::-1]
```

### 計數器

```python
from collections import Counter
c = Counter(input().split())
```

### 函式組合

```python
def compose(f, g):
    return lambda x: f(g(x))
```

### 延遲評估

```python
# 使用生成器避免預先建立大型列表
def get_numbers():
    for i in range(1000000):
        yield i

# 只計算需要的部分
gen = get_numbers()
next(gen)  # 0
next(gen)  # 1
```

## 效能優化

### 時間複雜度

| 操作 | 時間複雜度 |
|------|------------|
| list.append() | O(1) amortized |
| list.pop() | O(1) |
| list.insert(0, x) | O(n) |
| list.pop(0) | O(n) |
| list查找 | O(n) |
| dict.get() | O(1) average |
| set.add() | O(1) average |

### 效能技巧

1. **使用 deque 代替 list 的前端操作**
2. **使用 set 進行成員檢查**
3. **使用生成器代替列表**
4. **使用 numba JIT 編譯**
5. **使用 Cython**
6. **使用 multiprocessing 進行平行運算**

## 相關概念

- [資料結構](資料結構.md) - 了解常見資料結構
- [排序演算法](排序演算法.md) - 了解排序演算法
- [搜尋法](搜尋法.md) - 了解搜尋演算法

---

**參考來源**:
- [Python 官方文檔](https://docs.python.org/3/)
- [Python Cookbook](https://python3-cookbook.readthedocs.io/)
- [Real Python](https://realpython.com/)
