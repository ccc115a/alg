import math
import random
from group import Group

def simplify_rational(rational):
    """
    使用輾轉相除法化簡有理數元組 (numerator, denominator)
    並確保分母為正數。
    """
    numerator, denominator = rational
    if denominator == 0:
        raise ZeroDivisionError("分母不能為零")

    # 確保分母為正數
    if denominator < 0:
        numerator = -numerator
        denominator = -denominator
    
    # 找到最大公因數並化簡
    common_divisor = math.gcd(numerator, denominator)
    return (numerator // common_divisor, denominator // common_divisor)

# --- 有理數加法群 (Q, +) ---

class RationalAddGroup(Group):
    """
    有理數加法群 (Q, +)
    使用元組 (numerator, denominator) 來表示有理數。
    """
    def __init__(self):
        # 單位元素為 0，表示為 (0, 1)
        self._identity = (0, 1)
    
    @property
    def identity(self):
        return self._identity

    def operation(self, a, b):
        """
        有理數加法運算：(a/b) + (c/d) = ((ad + bc), bd)
        """
        if not (self.include(a) and self.include(b)):
            raise TypeError("輸入必須是有理數元組")
        
        num_a, den_a = a
        num_b, den_b = b
        
        new_numerator = num_a * den_b + num_b * den_a
        new_denominator = den_a * den_b
        
        return simplify_rational((new_numerator, new_denominator))

    def inverse(self, val):
        """
        有理數加法逆元（負數）：-a/b = (-a, b)
        """
        if not self.include(val):
            raise TypeError("輸入必須是有理數元組")
        
        return (-val[0], val[1])

    def include(self, element):
        """
        檢查元素是否為有效有理數元組
        """
        return (
            isinstance(element, tuple) and
            len(element) == 2 and
            isinstance(element[0], int) and
            isinstance(element[1], int) and
            element[1] != 0
        )

    def random_generate(self):
        """
        隨機生成一個有理數元組
        """
        numerator = random.randint(-10, 10)
        denominator = random.randint(1, 10)
        return simplify_rational((numerator, denominator))

# --- 有理數乘法群 (Q*, ×) ---

class RationalMulGroup(Group):
    """
    有理數乘法群 (Q*, ×) - 排除零元素
    使用元組 (numerator, denominator) 來表示有理數。
    """
    def __init__(self):
        # 單位元素為 1，表示為 (1, 1)
        self._identity = (1, 1)

    @property
    def identity(self):
        return self._identity

    def operation(self, a, b):
        """
        有理數乘法運算：(a/b) * (c/d) = (ac, bd)
        """
        # if not (self.include(a) and self.include(b)):
        #    raise TypeError("輸入必須是非零有理數元組")
            
        new_numerator = a[0] * b[0]
        new_denominator = a[1] * b[1]
        
        return simplify_rational((new_numerator, new_denominator))

    def inverse(self, val):
        """
        有理數乘法逆元（倒數）：(a/b)⁻¹ = (b, a)
        """
        if not self.include(val):
            raise TypeError("輸入必須是非零有理數元組")
        
        # 檢查分子是否為0
        if val[0] == 0:
            raise ValueError("零沒有乘法逆元")
        
        return simplify_rational((val[1], val[0]))

    def include(self, element):
        """
        檢查元素是否為非零有理數元組
        """
        return self.is_rational(element) and element[0] != 0

    def is_rational(self, element):
        """
        輔助方法：檢查是否為有效的有理數元組
        """
        return (
            isinstance(element, tuple) and
            len(element) == 2 and
            isinstance(element[0], int) and
            isinstance(element[1], int) and
            element[1] != 0
        )
        
    def random_generate(self):
        """
        隨機生成一個非零有理數元組
        """
        numerator = random.choice([i for i in range(-10, 11) if i != 0])
        denominator = random.randint(1, 10)
        return simplify_rational((numerator, denominator))

# --- 有理數體物件 (組合模式) ---

class RationalField:
    """
    一個表示有理數體 Q 的類別，由加法群和乘法群組合而成。
    """
    def __init__(self):
        self.add_group = RationalAddGroup()
        self.mul_group = RationalMulGroup()

    def add(self, a, b):
        """有理數加法"""
        return self.add_group.operation(a, b)

    def subtract(self, a, b):
        """有理數減法 (a - b = a + (-b))"""
        return self.add_group.operation(a, self.add_group.inverse(b))
        
    def multiply(self, a, b):
        """有理數乘法"""
        return self.mul_group.operation(a, b)
    
    def divide(self, a, b):
        """有理數除法 (a ÷ b = a × b⁻¹)"""
        return self.mul_group.operation(a, self.mul_group.inverse(b))
    
    def random_rational(self):
        """隨機生成一個有理數"""
        return self.add_group.random_generate()

    def random_nonzero_rational(self):
        """隨機生成一個非零有理數"""
        return self.mul_group.random_generate()
        
    def additive_inverse(self, val):
        """加法逆元"""
        return self.add_group.inverse(val)
        
    def multiplicative_inverse(self, val):
        """乘法逆元"""
        return self.mul_group.inverse(val)

    @staticmethod
    def _to_string(rational_tuple):
        """輔助方法，將有理數元組轉換為可讀的字串"""
        num, den = rational_tuple
        if den == 1:
            return f"{num}"
        return f"{num}/{den}"


# 範例使用
if __name__ == "__main__":
    # 建立一個有理數體的物件
    Q = RationalField()
    print("--- 測試有理數體 Q ---")
    
    # 加法測試
    a = Q.random_rational()
    b = Q.random_rational()
    add_result = Q.add(a, b)
    print(f"加法: {Q._to_string(a)} + {Q._to_string(b)} = {Q._to_string(add_result)}")
    
    # 減法測試
    sub_result = Q.subtract(a, b)
    print(f"減法: {Q._to_string(a)} - {Q._to_string(b)} = {Q._to_string(sub_result)}")
    
    # 乘法測試
    c = Q.random_nonzero_rational()
    d = Q.random_nonzero_rational()
    mul_result = Q.multiply(c, d)
    print(f"乘法: {Q._to_string(c)} × {Q._to_string(d)} = {Q._to_string(mul_result)}")
    
    # 除法測試
    div_result = Q.divide(c, d)
    print(f"除法: {Q._to_string(c)} ÷ {Q._to_string(d)} = {Q._to_string(div_result)}")

    # 分配律測試 (此測試需要兩個運算)
    e = Q.random_nonzero_rational()
    f = Q.random_rational()
    g = Q.random_rational()
    
    # 檢驗 e × (f + g) = (e × f) + (e × g)
    lhs = Q.multiply(e, Q.add(f, g))
    rhs = Q.add(Q.multiply(e, f), Q.multiply(e, g))
    print(f"\n分配律測試: {Q._to_string(e)} × ({Q._to_string(f)} + {Q._to_string(g)}) = {Q._to_string(lhs)}")
    print(f"({Q._to_string(e)} × {Q._to_string(f)}) + ({Q._to_string(e)} × {Q._to_string(g)}) = {Q._to_string(rhs)}")
    assert lhs == rhs, "分配律測試失敗！"
    print("分配律測試成功！")
    
    # 逆元測試
    print(f"\n逆元測試:")
    test_val = Q.random_nonzero_rational()
    add_inv = Q.additive_inverse(test_val)
    mul_inv = Q.multiplicative_inverse(test_val)
    
    print(f"{Q._to_string(test_val)} 的加法逆元: {Q._to_string(add_inv)}")
    print(f"驗證: {Q._to_string(test_val)} + ({Q._to_string(add_inv)}) = {Q._to_string(Q.add(test_val, add_inv))}")
    
    print(f"{Q._to_string(test_val)} 的乘法逆元: {Q._to_string(mul_inv)}")
    print(f"驗證: {Q._to_string(test_val)} × {Q._to_string(mul_inv)} = {Q._to_string(Q.multiply(test_val, mul_inv))}")