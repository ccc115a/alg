import pytest
from lean4py.number_theory import (
    Integer, int_, zero, one, gcd, lcm, bezout_identity,
    is_prime, prime_factors, phi, mod_exp, mod_inverse,
    divides, coprime, chinese_remainder, fundamental_theorem_of_arithmetic,
    IntegerInduction
)

class TestInteger:
    def test_integer_init(self):
        i = Integer(5)
        assert i.n == 5

    def test_integer_negative(self):
        i = Integer(-3)
        assert i.n == -3

    def test_integer_equality(self):
        assert Integer(5) == Integer(5)
        assert Integer(5) != Integer(3)

    def test_integer_add(self):
        assert Integer(2) + Integer(3) == Integer(5)
        assert Integer(-2) + Integer(3) == Integer(1)

    def test_integer_sub(self):
        assert Integer(5) - Integer(3) == Integer(2)
        assert Integer(3) - Integer(5) == Integer(-2)

    def test_integer_mul(self):
        assert Integer(3) * Integer(4) == Integer(12)

    def test_integer_neg(self):
        assert -Integer(5) == Integer(-5)

    def test_integer_abs(self):
        assert abs(Integer(-5)) == Integer(5)
        assert abs(Integer(5)) == Integer(5)

    def test_integer_comparison(self):
        assert Integer(3) < Integer(5)
        assert Integer(5) > Integer(3)
        assert Integer(3) <= Integer(3)
        assert Integer(3) >= Integer(3)

    def test_is_zero_positive_negative(self):
        assert Integer(0).is_zero == True
        assert Integer(1).is_positive == True
        assert Integer(-1).is_negative == True

class TestGcdLcm:
    def test_gcd_positive(self):
        assert gcd(Integer(12), Integer(18)) == Integer(6)
        assert gcd(Integer(7), Integer(5)) == Integer(1)

    def test_gcd_negative(self):
        assert gcd(Integer(-12), Integer(18)) == Integer(6)
        assert gcd(Integer(12), Integer(-18)) == Integer(6)

    def test_lcm_positive(self):
        assert lcm(Integer(4), Integer(6)) == Integer(12)

    def test_lcm_zero(self):
        assert lcm(Integer(0), Integer(5)) == Integer(0)
        assert lcm(Integer(3), Integer(0)) == Integer(0)

class TestBezoutIdentity:
    def test_bezout(self):
        x, y, d = bezout_identity(Integer(12), Integer(18))
        assert 12 * x.n + 18 * y.n == d.n
        assert d == Integer(6)

    def test_bezout_coprime(self):
        x, y, d = bezout_identity(Integer(35), Integer(15))
        assert d == Integer(5)

class TestPrime:
    def test_is_prime(self):
        assert is_prime(Integer(2)) == True
        assert is_prime(Integer(17)) == True
        assert is_prime(Integer(15)) == False
        assert is_prime(Integer(0)) == False
        assert is_prime(Integer(1)) == False
        assert is_prime(Integer(-5)) == False

    def test_prime_factors(self):
        assert prime_factors(Integer(12)) == [Integer(2), Integer(2), Integer(3)]
        assert prime_factors(Integer(7)) == [Integer(7)]
        assert prime_factors(Integer(1)) == []
        assert prime_factors(Integer(0)) == []

class TestEulerPhi:
    def test_phi(self):
        assert phi(Integer(1)) == Integer(1)
        assert phi(Integer(2)) == Integer(1)
        assert phi(Integer(10)) == Integer(4)
        assert phi(Integer(12)) == Integer(4)
        assert phi(Integer(7)) == Integer(6)

class TestModExp:
    def test_mod_exp(self):
        assert mod_exp(Integer(2), Integer(10), Integer(1024)) == Integer(0)
        assert mod_exp(Integer(2), Integer(3), Integer(7)) == Integer(1)
        assert mod_exp(Integer(3), Integer(4), Integer(10)) == Integer(1)

    def test_mod_exp_large(self):
        result = mod_exp(Integer(7), Integer(234), Integer(100))
        assert 0 <= result.n < 100

    def test_mod_exp_zero_mod(self):
        with pytest.raises(ValueError):
            mod_exp(Integer(2), Integer(10), Integer(0))

    def test_mod_exp_negative_exp(self):
        with pytest.raises(ValueError):
            mod_exp(Integer(2), Integer(-1), Integer(10))

class TestModInverse:
    def test_mod_inverse(self):
        inv = mod_inverse(Integer(3), Integer(11))
        assert inv is not None
        assert (3 * inv.n) % 11 == 1

    def test_mod_inverse_no_inverse(self):
        inv = mod_inverse(Integer(2), Integer(4))
        assert inv is None

class TestCoprime:
    def test_coprime(self):
        assert coprime(Integer(7), Integer(11)) == True
        assert coprime(Integer(12), Integer(18)) == False

class TestChineseRemainder:
    def test_chinese_remainder(self):
        result = chinese_remainder(Integer(2), Integer(3), Integer(3), Integer(5))
        assert result is not None
        assert result.n % 3 == 2
        assert result.n % 5 == 3

class TestDivisibility:
    def test_divides(self):
        assert divides(Integer(3), Integer(12)) == True
        assert divides(Integer(5), Integer(12)) == False
        assert divides(Integer(0), Integer(0)) == True
        assert divides(Integer(3), Integer(0)) == True

class TestIntegerInduction:
    def test_prove_sum(self):
        P = lambda k: k.n >= 0
        assert IntegerInduction.prove(P, Integer(10)) == True

    def test_strong_induction(self):
        P = lambda k: k.n >= 0
        assert IntegerInduction.prove_by_strong(P, Integer(100)) == True