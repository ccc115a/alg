import math

class Complex:
    """
    一個自定義的複數類別，不依賴 Python 的內建 complex 型別。
    
    屬性:
    - real (float): 實部 (Re(z))
    - imag (float): 虛部 (Im(z))
    """

    def __init__(self, real=0.0, imag=0.0):
        """
        初始化一個複數 z = real + imag * i。
        """
        self.real = float(real)
        self.imag = float(imag)

    # --- 輸出和表示 ---
    def __str__(self):
        """
        返回複數的可讀字串表示形式。
        """
        if self.imag >= 0:
            return f"{self.real} + {self.imag}i"
        else:
            # 確保負號顯示在虛部數字前
            return f"{self.real} - {-self.imag}i"

    def __repr__(self):
        """
        返回複數的官方字串表示形式。
        """
        return f"Complex({self.real}, {self.imag})"

    # --- 基本運算子重載 (二元運算) ---

    def __add__(self, other):
        """
        加法: (a + bi) + (c + di) = (a + c) + (b + d)i
        """
        if isinstance(other, Complex):
            new_real = self.real + other.real
            new_imag = self.imag + other.imag
        else: # 支援與數字 (float/int) 相加
            new_real = self.real + other
            new_imag = self.imag
        return Complex(new_real, new_imag)

    def __radd__(self, other):
        """
        反射加法，處理數字在左邊的情況: c + z
        """
        return self.__add__(other)

    def __sub__(self, other):
        """
        減法: (a + bi) - (c + di) = (a - c) + (b - d)i
        """
        if isinstance(other, Complex):
            new_real = self.real - other.real
            new_imag = self.imag - other.imag
        else: # 支援與數字 (float/int) 相減
            new_real = self.real - other
            new_imag = self.imag
        return Complex(new_real, new_imag)

    def __rsub__(self, other):
        """
        反射減法，處理數字在左邊的情況: c - z = c + (-z)
        """
        if isinstance(other, (int, float)):
            return Complex(other, 0.0) - self
        return other.__sub__(self) # 假設 other 有一個 sub 方法

    def __mul__(self, other):
        """
        乘法: (a + bi) * (c + di) = (ac - bd) + (ad + bc)i
        """
        if isinstance(other, Complex):
            a, b = self.real, self.imag
            c, d = other.real, other.imag
            new_real = a * c - b * d
            new_imag = a * d + b * c
        else: # 支援與數字 (float/int) 相乘
            new_real = self.real * other
            new_imag = self.imag * other
        return Complex(new_real, new_imag)

    def __rmul__(self, other):
        """
        反射乘法，處理數字在左邊的情況: c * z
        """
        return self.__mul__(other)

    def __truediv__(self, other):
        """
        除法: (a + bi) / (c + di) = ((ac + bd) / (c^2 + d^2)) + ((bc - ad) / (c^2 + d^2))i
        """
        if isinstance(other, Complex):
            c, d = other.real, other.imag
        else:
            c, d = float(other), 0.0

        # 分母: c^2 + d^2
        denominator = c**2 + d**2
        
        # 避免除以零
        if denominator == 0:
            raise ZeroDivisionError("division by zero complex number")

        a, b = self.real, self.imag
        
        new_real = (a * c + b * d) / denominator
        new_imag = (b * c - a * d) / denominator
        
        return Complex(new_real, new_imag)

    def __rtruediv__(self, other):
        """
        反射除法，處理數字在左邊的情況: c / z
        """
        # other / self
        if isinstance(other, (int, float)):
            return Complex(other, 0.0) / self
        return other.__truediv__(self) # 假設 other 有一個 truediv 方法

    # --- 內部輔助方法 (極座標) ---

    def magnitude(self):
        """
        計算複數的模 (magnitude) 或絕對值 |z| = sqrt(real^2 + imag^2)。
        """
        return math.sqrt(self.real**2 + self.imag**2)

    def phase(self):
        """
        計算複數的幅角 (phase) 或角度 arg(z)，範圍 (-pi, pi]。
        使用 math.atan2(y, x)。
        """
        return math.atan2(self.imag, self.real)

    # --- 複雜數學函數 (Exp, Log) ---

    def exp(self):
        """
        計算指數函數 e^z。
        如果 z = x + yi，則 e^z = e^(x + yi) = e^x * e^(yi)
                                   = e^x * (cos(y) + i * sin(y))
        """
        x = self.real
        y = self.imag
        
        # e^x
        r = math.exp(x)
        
        # cos(y) 和 sin(y)
        new_real = r * math.cos(y)
        new_imag = r * math.sin(y)
        
        return Complex(new_real, new_imag)

    def log(self):
        """
        計算自然對數函數 ln(z)。
        ln(z) = ln(|z| * e^(i*arg(z))) = ln(|z|) + i * arg(z)
        """
        # 模 |z|
        r = self.magnitude()
        
        # 幅角 arg(z)
        theta = self.phase()
        
        # ln(|z|)
        if r <= 0:
             # ln(0) 是未定義的，拋出錯誤
            raise ValueError("logarithm of zero or negative magnitude is undefined in this context.")

        new_real = math.log(r)
        
        # i * arg(z)
        new_imag = theta
        
        return Complex(new_real, new_imag)

# --- 測試範例 ---
print("### 複數類別測試 ###")

# 1. 初始化
z1 = Complex(2, 3) # 2 + 3i
z2 = Complex(1, -1) # 1 - 1i
z3 = Complex(4) # 4 + 0i
print(f"z1: {z1} (repr: {repr(z1)})")
print(f"z2: {z2}")
print(f"z3: {z3}")
print("-" * 20)

# 2. 加減乘除
z_add = z1 + z2
z_sub = z1 - z2
z_mul = z1 * z2
z_div = z1 / z2

print(f"z1 + z2 = {z_add}")
print(f"z1 - z2 = {z_sub}")
print(f"z1 * z2 = {z_mul}")
print(f"z1 / z2 = {z_div}")
print("-" * 20)

# 3. 與數字運算
z_num_add = z1 + 5
z_num_mul = z1 * 2.5
z_num_rdiv = 10 / z2 # 反射除法 (rtruediv)

print(f"z1 + 5 = {z_num_add}")
print(f"z1 * 2.5 = {z_num_mul}")
print(f"10 / z2 = {z_num_rdiv}")
print("-" * 20)

# 4. Exp 和 Log
z_exp = z1.exp()
z_log = z1.log()

# Exp(i*pi) = -1 (z = 0 + pi*i)
z_euler = Complex(0, math.pi)
z_euler_exp = z_euler.exp()

print(f"e^z1 = e^({z1}) = {z_exp}")
print(f"ln(z1) = ln({z1}) = {z_log}")
# 預期結果約為 -1 + 0i
print(f"e^(i*pi) = {z_euler_exp} (約等於 -1)") 
print("-" * 20)

# 5. 模和幅角
print(f"|z1| = {z1.magnitude():.4f}")
print(f"arg(z1) = {z1.phase():.4f} 弧度")