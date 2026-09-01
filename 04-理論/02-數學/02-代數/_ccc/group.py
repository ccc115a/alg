from abc import ABC, abstractmethod

class Group(ABC):
    """
    群的抽象基類。
    定義了群所需的基本運算和屬性，但不提供具體實作。
    """
    @property
    @abstractmethod
    def identity(self):
        """單位元素（Identity element）。"""
        pass

    @abstractmethod
    def operation(self, a, b):
        """群的二元運算。"""
        pass

    @abstractmethod
    def inverse(self, val):
        """反元素。"""
        pass

    @abstractmethod
    def include(self, element):
        """檢查元素是否屬於群。"""
        pass
