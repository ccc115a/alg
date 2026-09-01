import pytest
import group_axioms
from group_int_add import IntegerAddGroup
from group_even_add import EvenAddGroup
from group_odd_add import OddAddGroup

def test_add_group():
    group_axioms.check_group_axioms(IntegerAddGroup())

def test_even_group():
    group_axioms.check_group_axioms(EvenAddGroup())

"""
def test_odd_group():
    group_axioms.check_group_axioms(OddAddGroup())
"""

"""
import group_even_add
import group_odd_add
import group_fractions_add
import group_fractions_mul
import group_float_add
import group_float_mul
import group_finite_add
import group_finite_mul

def test_add_group():
    group_axioms.check_group_axioms(group_add)

def test_float_add_group():
    group_axioms.check_group_axioms(group_float_add)

def test_float_mul_group():
    group_axioms.check_group_axioms(group_float_mul)

def test_even_group():
    group_axioms.check_group_axioms(group_even_add)

def test_odd_group():
    group_axioms.check_group_axioms(group_odd_add)


def test_fractions_add_group():
    group_axioms.check_group_axioms(group_fractions_add)

def test_fractions_mul_group():
    group_axioms.check_group_axioms(group_fractions_mul)


def test_finite_add_group():
    group_axioms.check_group_axioms(group_finite_add)


def test_finite_mul_group():
    group_axioms.check_group_axioms(group_finite_mul)
"""