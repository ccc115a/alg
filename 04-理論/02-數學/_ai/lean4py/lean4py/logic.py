from typing import Optional

class Prop:
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"Prop({self.name!r})"

    def __eq__(self, other):
        return isinstance(other, Prop) and self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __rshift__(self, other):
        return implies(self, other)

    def __and__(self, other):
        return and_(self, other)

    def __or__(self, other):
        return or_(self, other)

    def __invert__(self):
        return not_(self)


def Prop_var(name: str) -> Prop:
    return Prop(name)


def implies(a: Prop, b: Prop) -> Prop:
    return _PropBinOp("→", a, b)


def and_(a: Prop, b: Prop) -> Prop:
    return _PropBinOp("∧", a, b)


def or_(a: Prop, b: Prop) -> Prop:
    return _PropBinOp("∨", a, b)


def not_(a: Prop) -> Prop:
    return _PropUnOp("¬", a)


def iff(a: Prop, b: Prop) -> Prop:
    return and_(implies(a, b), implies(b, a))


class _PropBinOp(Prop):
    def __init__(self, op: str, left: Prop, right: Prop):
        super().__init__(f"({left.name} {op} {right.name})")
        self.op = op
        self.left = left
        self.right = right


class _PropUnOp(Prop):
    def __init__(self, op: str, operand: Prop):
        super().__init__(f"{op}{operand.name}")
        self.op = op
        self.operand = operand


class Theorem:
    def __init__(self, name: str, prop: Prop, proof: Optional[list] = None):
        self.name = name
        self.prop = prop
        self.proof = proof or []

    def __repr__(self):
        return f"Theorem({self.name!r}, {self.prop!r})"


class ProofStep:
    def __init__(self, tactic: str, *args):
        self.tactic = tactic
        self.args = args

    def __repr__(self):
        return f"ProofStep({self.tactic!r}, {self.args})"


def assume(name: str, prop: Prop) -> ProofStep:
    return ProofStep("assume", name, prop)


def have(name: str, prop: Prop, from_: Optional[str] = None) -> ProofStep:
    return ProofStep("have", name, prop, from_)


def exact(prop: Prop) -> ProofStep:
    return ProofStep("exact", prop)


def apply(h: str) -> ProofStep:
    return ProofStep("apply", h)


def rfl() -> ProofStep:
    return ProofStep("rfl")


def simp() -> ProofStep:
    return ProofStep("simp")


def prove(prop: Prop, tactics: list) -> Theorem:
    return Theorem(f"proved_{id(prop)}", prop, tactics)