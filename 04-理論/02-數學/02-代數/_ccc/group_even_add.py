from group_int_add import IntegerAddGroup
import random

class EvenAddGroup(IntegerAddGroup):

    def include(self, element):
        """
        檢查元素是否屬於整數加法群
        
        Args:
            element: 要檢查的元素
            
        Returns:
            bool: 如果元素是整數則返回 True，否則返回 False
        """
        return isinstance(element, int) and element % 2 == 0

    def random_generate(self, from_=-100, to=100):
        """
        隨機生成一個群中的元素（整數）
        
        Returns:
            int: 隨機生成的整數
        """
        return random.randint(from_, to)*2
