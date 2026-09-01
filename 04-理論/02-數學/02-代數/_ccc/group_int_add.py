from group import Group
import random

class IntegerAddGroup(Group):
    """
    整數加法群 (ℤ, +)
    
    這是一個無限阿貝爾群，包含所有整數作為元素，
    以加法作為群運算，0作為單位元素。
    """
    
    def __init__(self):
        """初始化整數加法群"""
        self._identity = 0
    
    @property
    def identity(self):
        """
        返回加法群的單位元素
        
        Returns:
            int: 單位元素 0
        """
        return self._identity

    def operation(self, a, b):
        """
        執行群的二元運算（加法）
        
        Args:
            a (int): 第一個整數
            b (int): 第二個整數
            
        Returns:
            int: a + b 的結果
            
        Raises:
            TypeError: 當輸入不是整數時
        """
        if not (isinstance(a, int) and isinstance(b, int)):
            raise TypeError("Both operands must be integers")
        
        return a + b

    def inverse(self, val):
        """
        計算元素的加法逆元（相反數）
        
        Args:
            val (int): 要計算逆元的整數
            
        Returns:
            int: val 的加法逆元 -val
            
        Raises:
            TypeError: 當輸入不是整數時
        """
        if not isinstance(val, int):
            raise TypeError("Input must be an integer")
        
        return -val

    def include(self, element):
        """
        檢查元素是否屬於整數加法群
        
        Args:
            element: 要檢查的元素
            
        Returns:
            bool: 如果元素是整數則返回 True，否則返回 False
        """
        return isinstance(element, int)

    def random_generate(self, from_=-100, to=100):
        """
        隨機生成一個群中的元素（整數）
        
        Returns:
            int: 隨機生成的整數
        """
        return random.randint(from_, to)
