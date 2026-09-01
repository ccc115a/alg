import pytest
from lean4py.algebra import (
    Magma, Semigroup, Monoid, Group, AbelianGroup, Ring, Field,
)


class TestMagma:
    def test_magma_init(self):
        M = Magma('M', {1, 2, 3}, lambda a, b: (a * b) % 3 + 1)
        assert M.name == 'M'
        assert len(M.carrier) == 3


class TestSemigroup:
    def test_associative_operation(self):
        def add_mod(a, b):
            return (a + b) % 3
        S = Semigroup('S3', {0, 1, 2}, add_mod)
        assert S.is_associative() is True


class TestMonoid:
    def test_monoid_with_identity(self):
        M = Monoid('M', {0, 1, 2}, lambda a, b: (a + b) % 3, 0)
        assert M.has_identity() is True
        assert M.identity == 0


class TestGroup:
    def test_integers_under_addition(self):
        Z = Group('Z5', {0, 1, 2, 3, 4}, lambda a, b: (a + b) % 5, 0, lambda a: (5 - a) % 5)
        assert Z.is_group() is True

    def test_group_is_abelian(self):
        Z5 = Group('Z5', {0, 1, 2, 3, 4}, lambda a, b: (a + b) % 5, 0, lambda a: (5 - a) % 5)
        assert Z5.is_group() is True
        assert Z5.is_abelian() is True


class TestAbelianGroup:
    def test_abelian_group_int_addition(self):
        Z = AbelianGroup('Z5', {0, 1, 2, 3, 4}, lambda a, b: (a + b) % 5, 0, lambda a: (5 - a) % 5)
        assert Z.is_abelian_group() is True


class TestRing:
    def test_ring_integers(self):
        Z = Ring('Z6', {0, 1, 2, 3, 4, 5}, lambda a, b: (a + b) % 6, 0, lambda a: (6 - a) % 6,
                 lambda a, b: (a * b) % 6, 1)
        assert Z.is_ring() is True


class TestField:
    def test_field_rationals(self):
        def add(a, b): return (a[0]*b[1] + b[0]*a[1], a[1]*b[1])
        def neg(a): return (-a[0], a[1])
        def mul(a, b): return (a[0]*b[0], a[1]*b[1])
        def inv(a): return (a[1], a[0]) if a[0] != 0 else None

        Q = Field('Q', set(), add, (0, 1), neg, mul, (1, 1), inv)
        Q.carrier = {(a, b) for a in range(-5, 6) for b in range(1, 6)}
        assert Q.has_identity() is True


class TestAlgebraicProperties:
    def test_magma_closed(self):
        M = Magma('M', {1, 2}, lambda a, b: (a * b) % 2 + 1)
        assert M.is_closed() is True

    def test_magma_not_closed(self):
        M = Magma('M', {1, 2}, lambda a, b: a + b)
        assert M.is_closed() is False

    def test_semigroup_associative(self):
        S = Semigroup('S', {1, 2, 3}, lambda a, b: ((a + b) % 3) + 1)
        assert S.is_associative() is True

    def test_semigroup_not_associative(self):
        def sub(a, b): return a - b
        S = Semigroup('S', {1, 2, 3}, sub)
        assert S.is_associative() is False

    def test_group_has_inverses(self):
        Z = Group('Z', {0, 1, 2, 3, 4}, lambda a, b: (a + b) % 5, 0, lambda a: (5 - a) % 5)
        assert Z.has_inverses() is True

    def test_abelian_check(self):
        Z = AbelianGroup('Z', {1, 2, 3}, lambda a, b: (a + b) % 3, 0, lambda a: (3 - a) % 3)
        assert Z.is_abelian() is True