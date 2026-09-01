import pytest
from lean4py.sets import (
    Set, Set_from, in_, subset, union, intersection, complement,
    difference, cartesian, power_set, empty_set,
)


class TestSet:
    def test_empty_set(self):
        s = Set()
        assert s._elems == set()
        assert repr(s) == "∅"

    def test_set_from_list(self):
        s = Set_from([1, 2, 3])
        assert 1 in s
        assert 2 in s
        assert 3 in s

    def test_set_repr(self):
        s = Set_from([1, 2, 3])
        r = repr(s)
        assert "1" in r and "2" in r and "3" in r

    def test_set_equality(self):
        s1 = Set_from([1, 2, 3])
        s2 = Set_from([3, 2, 1])
        s3 = Set_from([1, 2])
        assert s1 == s2
        assert s1 != s3

    def test_set_hash(self):
        s1 = Set_from([1, 2, 3])
        s2 = Set_from([3, 2, 1])
        assert hash(s1) == hash(s2)


class TestSetOps:
    def test_contains(self):
        s = Set_from([1, 2, 3])
        assert 1 in s
        assert 4 not in s

    def test_union(self):
        A = Set_from([1, 2, 3])
        B = Set_from([2, 3, 4])
        U = union(A, B)
        assert 1 in U and 2 in U and 3 in U and 4 in U
        assert len(U._elems) == 4

    def test_union_add(self):
        A = Set_from([1, 2])
        B = Set_from([2, 3])
        U = A + B
        assert 1 in U and 2 in U and 3 in U

    def test_intersection(self):
        A = Set_from([1, 2, 3])
        B = Set_from([2, 3, 4])
        I = intersection(A, B)
        assert 2 in I and 3 in I
        assert len(I._elems) == 2

    def test_intersection_mul(self):
        A = Set_from([1, 2, 3])
        B = Set_from([2, 3, 4])
        I = A * B
        assert 2 in I and 3 in I

    def test_difference(self):
        A = Set_from([1, 2, 3])
        B = Set_from([2, 3])
        D = difference(A, B)
        assert 1 in D
        assert 2 not in D

    def test_complement(self):
        A = Set_from([1, 2, 3])
        C = complement(A)
        assert isinstance(C, Set)


class TestSetRelations:
    def test_subset_true(self):
        A = Set_from([1, 2])
        B = Set_from([1, 2, 3])
        assert subset(A, B) is True

    def test_subset_false(self):
        A = Set_from([1, 2, 3])
        B = Set_from([1, 2])
        assert subset(A, B) is False

    def test_subset_le(self):
        A = Set_from([1, 2])
        B = Set_from([1, 2, 3])
        assert (A <= B) is True


class TestCartesian:
    def test_cartesian_product(self):
        A = Set_from([1, 2])
        B = Set_from(['a', 'b'])
        C = cartesian(A, B)
        assert (1, 'a') in C
        assert (1, 'b') in C
        assert (2, 'a') in C
        assert (2, 'b') in C
        assert len(C._elems) == 4

    def test_cartesian_empty(self):
        A = Set_from([1, 2])
        B = empty_set()
        C = cartesian(A, B)
        assert len(C._elems) == 0


class TestPowerSet:
    def test_power_set_empty(self):
        E = empty_set()
        P = power_set(E)
        assert len(P._elems) == 1
        assert Set() in P._elems

    def test_power_set_singleton(self):
        S = Set_from([1])
        P = power_set(S)
        assert len(P._elems) == 2

    def test_power_set_two_elements(self):
        S = Set_from([1, 2])
        P = power_set(S)
        assert len(P._elems) == 4


class TestEmptySet:
    def test_empty_set_singleton(self):
        E = empty_set()
        assert len(E._elems) == 0

    def test_empty_set_repr(self):
        E = empty_set()
        assert repr(E) == "∅"


class TestInFunction:
    def test_in_true(self):
        A = Set_from([1, 2, 3])
        assert in_(1, A) is True

    def test_in_false(self):
        A = Set_from([1, 2, 3])
        assert in_(4, A) is False