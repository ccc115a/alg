import pytest
import field_axioms
from field_rational import RationalField

def test_rational_field():
    field_axioms.check_field_axioms(RationalField())

"""
from field_finite import FiniteField
def test_finite_field():
    field_axioms.check_field_axioms(FiniteField(7))
"""