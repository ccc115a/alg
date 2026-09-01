import math

class RationalNumber:
    """
    表示一個有理數，並重載運算子來呼叫 RationalField 的運算函數。
    """
    def __init__(self, field, numerator, denominator=1):
        if not isinstance(numerator, int) or not isinstance(denominator, int):
            raise TypeError("Numerator and denominator must be integers.")
        if denominator == 0:
            raise ValueError("Denominator cannot be zero.")

        # 每個 RationalNumber 物件都與其所屬的 field 綁定
        self.field = field
        
        # 約分
        common_divisor = math.gcd(numerator, denominator)
        self.numerator = numerator // common_divisor
        self.denominator = denominator // common_divisor

        # 確保分母為正
        if self.denominator < 0:
            self.numerator = -self.numerator
            self.denominator = -self.denominator

    def __repr__(self):
        if self.denominator == 1:
            return f"{self.numerator}"
        return f"{self.numerator}/{self.denominator}"

    def __eq__(self, other):
        if isinstance(other, RationalNumber):
            return self.numerator == other.numerator and self.denominator == other.denominator
        if isinstance(other, int):
            return self.numerator == other and self.denominator == 1
        return False

    def __add__(self, other):
        """
        加法運算 (+)，直接呼叫 field.add()。
        """
        if isinstance(other, RationalNumber):
            if self.field != other.field:
                raise ValueError("Cannot operate on numbers from different fields.")
            return self.field.add(self, other)
        
        if isinstance(other, int):
            return self.field.add(self, self.field.element(other))
            
        raise TypeError(f"Unsupported operand type(s) for +: '{type(self).__name__}' and '{type(other).__name__}'")

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        """
        減法運算 (-)，直接呼叫 field.substract()。
        """
        if isinstance(other, RationalNumber):
            if self.field != other.field:
                raise ValueError("Cannot operate on numbers from different fields.")
            return self.field.substract(self, other)
            
        if isinstance(other, int):
            return self.field.substract(self, self.field.element(other))

        raise TypeError(f"Unsupported operand type(s) for -: '{type(self).__name__}' and '{type(other).__name__}'")
    
    def __rsub__(self, other):
        # 為了處理 rsub，我們需要先將左邊的運算元轉為 RationalNumber
        return self.field.substract(self.field.element(other), self)

    def __mul__(self, other):
        """
        乘法運算 (*)，直接呼叫 field.multiply()。
        """
        if isinstance(other, RationalNumber):
            if self.field != other.field:
                raise ValueError("Cannot operate on numbers from different fields.")
            return self.field.multiply(self, other)
            
        if isinstance(other, int):
            return self.field.multiply(self, self.field.element(other))
            
        raise TypeError(f"Unsupported operand type(s) for *: '{type(self).__name__}' and '{type(other).__name__}'")

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        """
        除法運算 (/)，直接呼叫 field.divide()。
        """
        if isinstance(other, RationalNumber):
            if self.field != other.field:
                raise ValueError("Cannot operate on numbers from different fields.")
            return self.field.divide(self, other)
            
        if isinstance(other, int):
            return self.field.divide(self, self.field.element(other))
            
        raise TypeError(f"Unsupported operand type(s) for /: '{type(self).__name__}' and '{type(other).__name__}'")

    def __rtruediv__(self, other):
        return self.field.divide(self.field.element(other), self)

# --- 有理數體 ---

class RationalField:
    """
    一個表示有理數體 Q 的類別，包含主要的運算邏輯。
    """
    def __init__(self):
        self._identity = RationalNumber(self, 0)
    
    @property
    def identity(self):
        return self._identity

    def element(self, numerator, denominator=1):
        """
        工廠方法，用於創建 RationalNumber 物件並與當前 field 綁定。
        """
        return RationalNumber(self, numerator, denominator)

    def add(self, a, b):
        """
        加法邏輯
        """
        new_numerator = a.numerator * b.denominator + b.numerator * a.denominator
        new_denominator = a.denominator * b.denominator
        return self.element(new_numerator, new_denominator)

    def substract(self, a, b):
        """
        減法邏輯
        """
        new_numerator = a.numerator * b.denominator - b.numerator * a.denominator
        new_denominator = a.denominator * b.denominator
        return self.element(new_numerator, new_denominator)
        
    def multiply(self, a, b):
        """
        乘法邏輯
        """
        new_numerator = a.numerator * b.numerator
        new_denominator = a.denominator * b.denominator
        return self.element(new_numerator, new_denominator)
    
    def divide(self, a, b):
        """
        除法邏輯
        """
        if b.numerator == 0:
            raise ZeroDivisionError("Cannot divide by zero.")
        new_numerator = a.numerator * b.denominator
        new_denominator = a.denominator * b.numerator
        return self.element(new_numerator, new_denominator)


# 範例使用
if __name__ == "__main__":
    Q = RationalField()
    
    # 使用 element 工廠方法來創建有理數物件
    a = Q.element(1, 2)  # 1/2
    b = Q.element(3, 4)  # 3/4
    c = Q.element(5)     # 5
    
    print("--- 測試運算子重載與函數呼叫 ---")
    print(f"a = {a}")
    print(f"b = {b}")

    # 加法測試
    add_result = a + b
    print(f"加法: {a} + {b} = {add_result}")  # 1/2 + 3/4 = 5/4
    
    # 減法測試
    sub_result = a - b
    print(f"減法: {a} - {b} = {sub_result}")  # 1/2 - 3/4 = -1/4
    
    # 乘法測試
    mul_result = a * b
    print(f"乘法: {a} * {b} = {mul_result}")  # 1/2 * 3/4 = 3/8
    
    # 除法測試
    div_result = a / b
    print(f"除法: {a} / {b} = {div_result}")  # 1/2 / 3/4 = 4/6 = 2/3

    # 測試與整數的混合運算
    print("\n--- 測試與整數的混合運算 ---")
    d = a + 1
    e = 2 * b
    f = 1 / a
    print(f"{a} + 1 = {d}")  # 1/2 + 1 = 3/2
    print(f"2 * {b} = {e}")  # 2 * 3/4 = 6/4 = 3/2
    print(f"1 / {a} = {f}")   # 1 / (1/2) = 2