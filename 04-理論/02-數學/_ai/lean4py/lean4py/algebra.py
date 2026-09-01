from typing import Any, Callable


class AlgebraicStructure:
    def __init__(self, name: str, carrier: set, op: Callable, identity: Any = None, inv: Callable = None):
        self.name = name
        self.carrier = carrier
        self.op = op
        self.identity = identity
        self.inv = inv

    def __repr__(self):
        return f"{self.name}"

    def is_closed(self) -> bool:
        for a in self.carrier:
            for b in self.carrier:
                if self.op(a, b) not in self.carrier:
                    return False
        return True

    def is_associative(self) -> bool:
        for a in self.carrier:
            for b in self.carrier:
                for c in self.carrier:
                    if self.op(self.op(a, b), c) != self.op(a, self.op(b, c)):
                        return False
        return True

    def has_identity(self) -> bool:
        if self.identity is None:
            return False
        for a in self.carrier:
            if self.op(self.identity, a) != a or self.op(a, self.identity) != a:
                return False
        return True

    def has_inverses(self) -> bool:
        if self.inv is None or self.identity is None:
            return False
        for a in self.carrier:
            if self.op(a, self.inv(a)) != self.identity:
                return False
        return True

    def is_abelian(self) -> bool:
        for a in self.carrier:
            for b in self.carrier:
                if self.op(a, b) != self.op(b, a):
                    return False
        return True


class Magma(AlgebraicStructure):
    def __init__(self, name: str, carrier: set, op: Callable):
        super().__init__(name, carrier, op)


class Semigroup(Magma):
    def __init__(self, name: str, carrier: set, op: Callable):
        super().__init__(name, carrier, op)

    def is_semigroup(self) -> bool:
        return self.is_closed() and self.is_associative()


class Monoid(Semigroup):
    def __init__(self, name: str, carrier: set, op: Callable, identity: Any):
        super().__init__(name, carrier, op)
        self.identity = identity

    def is_monoid(self) -> bool:
        return self.is_semigroup() and self.has_identity()


class Group(Monoid):
    def __init__(self, name: str, carrier: set, op: Callable, identity: Any, inv: Callable):
        super().__init__(name, carrier, op, identity)
        self.inv = inv

    def is_group(self) -> bool:
        return self.is_monoid() and self.has_inverses()


class AbelianGroup(Group):
    def __init__(self, name: str, carrier: set, op: Callable, identity: Any, inv: Callable):
        super().__init__(name, carrier, op, identity, inv)

    def is_abelian_group(self) -> bool:
        return self.is_group() and self.is_abelian()


class Ring(AbelianGroup):
    def __init__(self, name: str, carrier: set, add: Callable, add_id: Any, add_inv: Callable,
                 mul: Callable, mul_id: Any = None):
        super().__init__(name, carrier, add, add_id, add_inv)
        self.mul = mul
        self.mul_id = mul_id

    def is_ring(self) -> bool:
        if not self.is_abelian_group():
            return False
        if not self.is_closed_under(self.mul):
            return False
        if not self.is_associative_under(self.mul):
            return False
        return self.is_left_distributive() and self.is_right_distributive()

    def is_closed_under(self, op: Callable) -> bool:
        for a in self.carrier:
            for b in self.carrier:
                if op(a, b) not in self.carrier:
                    return False
        return True

    def is_associative_under(self, op: Callable) -> bool:
        for a in self.carrier:
            for b in self.carrier:
                for c in self.carrier:
                    if op(op(a, b), c) != op(a, op(b, c)):
                        return False
        return True

    def is_left_distributive(self) -> bool:
        for a in self.carrier:
            for b in self.carrier:
                for c in self.carrier:
                    if self.mul(a, self.op(b, c)) != self.op(self.mul(a, b), self.mul(a, c)):
                        return False
        return True

    def is_right_distributive(self) -> bool:
        for a in self.carrier:
            for b in self.carrier:
                for c in self.carrier:
                    if self.mul(self.op(a, b), c) != self.op(self.mul(a, c), self.mul(b, c)):
                        return False
        return True


class Field(Ring):
    def __init__(self, name: str, carrier: set, add: Callable, add_id: Any, add_inv: Callable,
                 mul: Callable, mul_id: Any, mul_inv: Callable):
        super().__init__(name, carrier, add, add_id, add_inv, mul, mul_id)
        self.mul_inv = mul_inv

    def is_field(self) -> bool:
        if not self.is_ring():
            return False
        if self.mul_id is None:
            return False
        for a in self.carrier:
            if a == self.add_id:
                continue
            if self.mul_inv(a) not in self.carrier:
                return False
        return True