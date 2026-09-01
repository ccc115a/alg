import pytest
from lean4py.logic import (
    Prop, Prop_var, implies, and_, or_, not_, iff,
    Theorem, ProofStep, assume, have, exact, apply, rfl, simp, prove,
)


class TestProp:
    def test_prop_var(self):
        p = Prop('p')
        assert p.name == 'p'
        assert repr(p) == "Prop('p')"

    def test_prop_equality(self):
        p1 = Prop('p')
        p2 = Prop('p')
        p3 = Prop('q')
        assert p1 == p2
        assert p1 != p3

    def test_prop_hash(self):
        p1 = Prop('p')
        p2 = Prop('p')
        assert hash(p1) == hash(p2)


class TestPropOps:
    def test_implies(self):
        p = Prop('p')
        q = Prop('q')
        imp = implies(p, q)
        assert '→' in imp.name
        assert imp.left == p
        assert imp.right == q

    def test_and(self):
        p = Prop('p')
        q = Prop('q')
        a = and_(p, q)
        assert '∧' in a.name
        assert a.left == p
        assert a.right == q

    def test_or(self):
        p = Prop('p')
        q = Prop('q')
        o = or_(p, q)
        assert '∨' in o.name
        assert o.left == p
        assert o.right == q

    def test_not(self):
        p = Prop('p')
        n = not_(p)
        assert '¬' in n.name
        assert n.operand == p

    def test_iff(self):
        p = Prop('p')
        q = Prop('q')
        i = iff(p, q)
        assert '∧' in i.name

    def test_rshift(self):
        p = Prop('p')
        q = Prop('q')
        imp = p >> q
        assert imp.left == p
        assert imp.right == q

    def test_and_op(self):
        p = Prop('p')
        q = Prop('q')
        a = p & q
        assert '∧' in a.name

    def test_or_op(self):
        p = Prop('p')
        q = Prop('q')
        o = p | q
        assert '∨' in o.name

    def test_invert(self):
        p = Prop('p')
        n = ~p
        assert '¬' in n.name


class TestTheorem:
    def test_theorem_init(self):
        p = Prop('p')
        t = Theorem('trivial', p)
        assert t.name == 'trivial'
        assert t.prop == p
        assert t.proof == []

    def test_theorem_with_proof(self):
        p = Prop('p')
        t = Theorem('trivial', p, [rfl()])
        assert len(t.proof) == 1


class TestProofSteps:
    def test_assume(self):
        p = Prop('p')
        step = assume('h', p)
        assert step.tactic == 'assume'
        assert step.args[0] == 'h'
        assert step.args[1] == p

    def test_have(self):
        p = Prop('p')
        step = have('h', p, from_='h1')
        assert step.tactic == 'have'
        assert step.args[0] == 'h'

    def test_exact(self):
        p = Prop('p')
        step = exact(p)
        assert step.tactic == 'exact'

    def test_apply(self):
        step = apply('h1')
        assert step.tactic == 'apply'

    def test_rfl(self):
        step = rfl()
        assert step.tactic == 'rfl'

    def test_simp(self):
        step = simp()
        assert step.tactic == 'simp'


class TestProve:
    def test_prove_creates_theorem(self):
        p = Prop('p')
        t = prove(p, [rfl()])
        assert isinstance(t, Theorem)
        assert t.prop == p