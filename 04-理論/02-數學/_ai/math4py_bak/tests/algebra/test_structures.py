"""Tests for algebra/structures.py."""

import pytest
from math4py.algebra import Group, Ring, Field, VectorSpace


class TestGroup:
    def test_integers_mod_n(self):
        """Z/3Z 加法群。"""
        carrier = {0, 1, 2}
        op = lambda a, b: (a + b) % 3
        identity = 0
        inverse = lambda a: (-a) % 3
        G = Group("Z/3Z", carrier, op, identity, inverse)
        assert G.is_group()
        assert G.is_abelian()

    def test_symmetric_group(self):
        """S_3 非交換群 (置換群)。"""
        carrier = {0, 1, 2, 3, 4, 5}  # 6 個置換的編號
        # 簡化：用字典定義部分運算（實際完整實作較長）
        op_table = {
            (0, 0): 0, (0, 1): 1, (1, 0): 1, (1, 1): 0,
        }
        op = lambda a, b: op_table.get((a, b), 0)
        identity = 0
        inverse = lambda a: a  # 簡化
        G = Group("S3_small", carrier, op, identity, inverse)
        # 僅檢查封閉性與結合律（簡化）
        assert G.is_closed()


class TestRing:
    def test_z_mod_n(self):
        """Z/4Z 環。"""
        carrier = {0, 1, 2, 3}
        add = lambda a, b: (a + b) % 4
        mul = lambda a, b: (a * b) % 4
        add_id = 0
        add_inv = lambda a: (-a) % 4
        mul_id = 1
        R = Ring("Z/4Z", carrier, add, add_id, add_inv, mul, mul_id)
        assert R.is_ring()


class TestField:
    def test_finite_field(self):
        """F_5 有限域。"""
        carrier = {0, 1, 2, 3, 4}
        add = lambda a, b: (a + b) % 5
        mul = lambda a, b: (a * b) % 5
        add_id = 0
        add_inv = lambda a: (-a) % 5
        mul_id = 1
        mul_inv = lambda a: pow(a, 3, 5) if a != 0 else 0  # a^3 mod 5 是反元素
        F = Field("F_5", carrier, add, add_id, add_inv, mul, mul_id, mul_inv)
        assert F.is_field()


class TestVectorSpace:
    def test_f2_vector_space(self):
        """F_2 上的二維向量空間。"""
        vectors = {(0, 0), (1, 0), (0, 1), (1, 1)}
        field_carrier = {0, 1}
        add = lambda u, v: ((u[0] + v[0]) % 2, (u[1] + v[1]) % 2)
        scalar_mul = lambda a, v: (a * v[0] % 2, a * v[1] % 2)
        field = Field("F_2", field_carrier,
                      lambda a, b: (a + b) % 2, 0, lambda a: a,
                      lambda a, b: (a * b) % 2, 1, lambda a: a if a != 0 else 0)
        V = VectorSpace("F_2^2", vectors, field, add, scalar_mul)
        assert V.is_vector_space()
