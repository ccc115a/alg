class Nat:
    def __init__(self, n: int):
        if n < 0:
            raise ValueError("Natural numbers must be non-negative")
        self.n = n

    def __repr__(self):
        return f"Nat({self.n})"

    def __eq__(self, other):
        return isinstance(other, Nat) and self.n == other.n

    def __hash__(self):
        return hash(self.n)

    def __add__(self, other):
        return Nat(self.n + other.n)

    def __mul__(self, other):
        return Nat(self.n * other.n)

    def __sub__(self, other):
        result = self.n - other.n
        return Nat(result if result >= 0 else 0)

    def __le__(self, other):
        return self.n <= other.n

    def __lt__(self, other):
        return self.n < other.n

    def __ge__(self, other):
        return self.n >= other.n

    def __gt__(self, other):
        return self.n > other.n

    def __radd__(self, other):
        return Nat(other.n + self.n) if isinstance(other, Nat) else Nat(other + self.n)

    def __rmul__(self, other):
        return Nat(other * self.n) if isinstance(other, int) else Nat(other.n * self.n)


def nat(n: int) -> Nat:
    return Nat(n)


def zero() -> Nat:
    return Nat(0)


def succ(n: Nat) -> Nat:
    return Nat(n.n + 1)


def pred(n: Nat) -> Nat:
    return Nat(max(0, n.n - 1))


def is_zero(n: Nat) -> bool:
    return n.n == 0


class NatInduction:
    @staticmethod
    def prove(P: callable, n: Nat) -> bool:
        if n.n == 0:
            return P(Nat(0))
        return NatInduction.prove(P, pred(n)) and P(n)


def nat_add(a: Nat, b: Nat) -> Nat:
    return a + b


def nat_mul(a: Nat, b: Nat) -> Nat:
    return a * b


def nat_sub(a: Nat, b: Nat) -> Nat:
    return a - b


def nat_le(a: Nat, b: Nat) -> bool:
    return a <= b


def nat_lt(a: Nat, b: Nat) -> bool:
    return a < b


def nat_eq(a: Nat, b: Nat) -> bool:
    return a == b