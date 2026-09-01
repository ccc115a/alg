"""algebra - 代數模組，包裝 numpy/sympy 提供一致 API."""

from .matrix import Matrix
from .theorem import (
    closure_axiom,
    associativity,
    identity_element,
    inverse_element,
    commutativity,
    distributivity,
)


class AlgebraicStructure:
    """代數結構基礎類別。"""

    def __init__(self, name: str, carrier: set, op):
        self.name = name
        self.carrier = carrier
        self.op = op

    def is_closed(self) -> bool:
        for a in self.carrier:
            for b in self.carrier:
                if self.op(a, b) not in self.carrier:
                    return False
        return True


class Group(AlgebraicStructure):
    """群結構。"""

    def __init__(self, name: str, carrier: set, op, identity, inverse):
        super().__init__(name, carrier, op)
        self.identity = identity
        self.inverse = inverse

    def is_group(self) -> bool:
        if not self.is_closed():
            return False
        for a in self.carrier:
            if self.op(self.identity, a) != a or self.op(a, self.identity) != a:
                return False
        for a in self.carrier:
            if self.op(a, self.inverse(a)) != self.identity:
                return False
        return True

    def is_abelian(self) -> bool:
        for a in self.carrier:
            for b in self.carrier:
                if a in self.carrier and b in self.carrier:
                    if self.op(a, b) != self.op(b, a):
                        return False
        return True


class Ring(AlgebraicStructure):
    """環結構。"""

    def __init__(self, name: str, carrier: set, add, add_id, add_inv, mul, mul_id=None):
        super().__init__(name, carrier, add)
        self.add = add
        self.add_id = add_id
        self.add_inv = add_inv
        self.mul = mul
        self.mul_id = mul_id

    def is_ring(self) -> bool:
        if not self.is_closed():
            return False
        for a in self.carrier:
            for b in self.carrier:
                for c in self.carrier:
                    if self.mul(self.mul(a, b), c) != self.mul(a, self.mul(b, c)):
                        return False
        if self.mul_id is not None:
            for a in self.carrier:
                if self.mul(self.mul_id, a) != a or self.mul(a, self.mul_id) != a:
                    return False
        return True


class Field(Ring):
    """域結構。"""

    def __init__(self, name: str, carrier: set, add, add_id, add_inv, mul, mul_id, mul_inv):
        super().__init__(name, carrier, add, add_id, add_inv, mul, mul_id)
        self.mul_inv = mul_inv

    def is_field(self) -> bool:
        if not self.is_ring():
            return False
        for a in self.carrier:
            if a != self.add_id and self.mul(a, self.mul_inv(a)) != self.mul_id:
                return False
        return True


class VectorSpace:
    """向量空間。"""

    def __init__(self, name: str, carrier: set, field, add, scalar_mul, zero=None):
        self.name = name
        self.carrier = carrier
        self.field = field.carrier if hasattr(field, "carrier") else field
        self.add = add
        self.scalar_mul = scalar_mul
        self.zero = zero or (0, 0)

    def is_vector_space(self) -> bool:
        for v in self.carrier:
            if self.add(self.zero, v) != v:
                return False
        for a in self.field:
            for v in self.carrier:
                if self.scalar_mul(a, v) not in self.carrier:
                    return False
        return True


__all__ = [
    "Matrix",
    "AlgebraicStructure",
    "Group",
    "Ring",
    "Field",
    "VectorSpace",
    "closure_axiom",
    "associativity",
    "identity_element",
    "inverse_element",
    "commutativity",
    "distributivity",
]