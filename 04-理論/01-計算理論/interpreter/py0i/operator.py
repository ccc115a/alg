"""
operator.py  –  手寫的 operator 模組
只實作 py0i.py 實際用到的函式，語意與標準函式庫完全相同。
完全不 import 標準函式庫的 operator 模組。
"""

# ── 算術 ─────────────────────────────────────────────────────────────────────

def add(a: object, b: object) -> object:
    """a + b"""
    return a + b

def sub(a: object, b: object) -> object:
    """a - b"""
    return a - b

def mul(a: object, b: object) -> object:
    """a * b"""
    return a * b

def truediv(a: object, b: object) -> object:
    """a / b"""
    return a / b

def floordiv(a: object, b: object) -> object:
    """a // b"""
    return a // b

def mod(a: object, b: object) -> object:
    """a % b"""
    return a % b

def pow(a: object, b: object) -> object:
    """a ** b"""
    return a ** b

def matmul(a: object, b: object) -> object:
    """a @ b"""
    return a @ b

def neg(a: object) -> object:
    """-a"""
    return -a

def pos(a: object) -> object:
    """+a"""
    return +a

def abs(a: object) -> object:
    """|a|"""
    return a.__abs__() if hasattr(a, '__abs__') else (a if a >= 0 else -a)

# ── 位元 ─────────────────────────────────────────────────────────────────────

def and_(a: object, b: object) -> object:
    """a & b"""
    return a & b

def or_(a: object, b: object) -> object:
    """a | b"""
    return a | b

def xor(a: object, b: object) -> object:
    """a ^ b"""
    return a ^ b

def invert(a: object) -> object:
    """~a"""
    return ~a

def lshift(a: object, b: object) -> object:
    """a << b"""
    return a << b

def rshift(a: object, b: object) -> object:
    """a >> b"""
    return a >> b

# ── 比較 ─────────────────────────────────────────────────────────────────────

def eq(a: object, b: object) -> bool:
    """a == b"""
    return a == b

def ne(a: object, b: object) -> bool:
    """a != b"""
    return a != b

def lt(a: object, b: object) -> bool:
    """a < b"""
    return a < b

def le(a: object, b: object) -> bool:
    """a <= b"""
    return a <= b

def gt(a: object, b: object) -> bool:
    """a > b"""
    return a > b

def ge(a: object, b: object) -> bool:
    """a >= b"""
    return a >= b

# ── 邏輯 ─────────────────────────────────────────────────────────────────────

def not_(a: object) -> bool:
    """not a"""
    return not a

def truth(a: object) -> bool:
    """bool(a)"""
    return bool(a)

# ── 容器 ─────────────────────────────────────────────────────────────────────

def getitem(a: object, b: object) -> object:
    """a[b]"""
    return a[b]

def setitem(a: object, b: object, c: object) -> None:
    """a[b] = c"""
    a[b] = c

def delitem(a: object, b: object) -> None:
    """del a[b]"""
    del a[b]

def contains(a: object, b: object) -> bool:
    """b in a"""
    return b in a

def concat(a: object, b: object) -> object:
    """a + b  (sequences)"""
    return a + b

def length_hint(obj: object, default: int = 0) -> int:
    """len(obj) with fallback"""
    try:
        return len(obj)
    except TypeError:
        return default

# ── 屬性 ─────────────────────────────────────────────────────────────────────

def attrgetter(name: str) -> object:
    """回傳一個函式，用來取出物件的指定屬性。"""
    def getter(obj: object) -> object:
        return getattr(obj, name)
    return getter

def itemgetter(*keys: object) -> object:
    """回傳一個函式，用來取出物件的指定 key。"""
    if len(keys) == 1:
        k = keys[0]
        def getter(obj):
            return obj[k]
    else:
        def getter(obj):
            return tuple(obj[k] for k in keys)
    return getter

def methodcaller(name: str, *args: object, **kwargs: object) -> object:
    """回傳一個函式，呼叫物件的指定方法。"""
    def caller(obj):
        return getattr(obj, name)(*args, **kwargs)
    return caller

# ── index / is ───────────────────────────────────────────────────────────────

def index(a: object) -> int:
    """a.__index__()"""
    return a.__index__()

def is_(a: object, b: object) -> bool:
    """a is b"""
    return a is b

def is_not(a: object, b: object) -> bool:
    """a is not b"""
    return a is not b
