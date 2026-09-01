"""Tests for Vector class."""

import pytest
import math4py.geometry as geom
import numpy as np


class TestVectorCreation:
    def test_create_vector(self):
        v = geom.Vector(1, 2, 3)
        assert v.x == 1
        assert v.y == 2
        assert v.z == 3

    def test_vector_repr(self):
        v = geom.Vector(1, 2, 3)
        assert repr(v) == "Vector(1.0, 2.0, 3.0)"


class TestVectorOperations:
    def test_add(self):
        v1 = geom.Vector(1, 0, 0)
        v2 = geom.Vector(0, 1, 0)
        result = v1 + v2
        assert result == geom.Vector(1, 1, 0)

    def test_sub(self):
        v1 = geom.Vector(1, 1, 0)
        v2 = geom.Vector(0, 1, 0)
        result = v1 - v2
        assert result == geom.Vector(1, 0, 0)

    def test_mul(self):
        v = geom.Vector(1, 2, 3)
        result = v * 2
        assert result == geom.Vector(2, 4, 6)

    def test_rmul(self):
        v = geom.Vector(1, 2, 3)
        result = 2 * v
        assert result == geom.Vector(2, 4, 6)

    def test_div(self):
        v = geom.Vector(2, 4, 6)
        result = v / 2
        assert result == geom.Vector(1, 2, 3)

    def test_neg(self):
        v = geom.Vector(1, 2, 3)
        result = -v
        assert result == geom.Vector(-1, -2, -3)


class TestVectorProducts:
    def test_dot(self):
        v1 = geom.Vector(1, 0, 0)
        v2 = geom.Vector(0, 1, 0)
        assert v1.dot(v2) == 0

    def test_dot_nonzero(self):
        v1 = geom.Vector(1, 2, 3)
        v2 = geom.Vector(1, 1, 1)
        assert v1.dot(v2) == 6

    def test_cross(self):
        v1 = geom.Vector(1, 0, 0)
        v2 = geom.Vector(0, 1, 0)
        result = v1.cross(v2)
        assert result == geom.Vector(0, 0, 1)

    def test_cross_parallel(self):
        v1 = geom.Vector(1, 0, 0)
        v2 = geom.Vector(2, 0, 0)
        assert v1.cross(v2).norm() < 1e-9


class TestVectorMetrics:
    def test_norm(self):
        v = geom.Vector(3, 4, 0)
        assert abs(v.norm() - 5.0) < 1e-9

    def test_normalize(self):
        v = geom.Vector(3, 4, 0)
        u = v.normalize()
        assert abs(u.norm() - 1.0) < 1e-9

    def test_normalize_zero_error(self):
        v = geom.Vector(0, 0, 0)
        with pytest.raises(ValueError):
            v.normalize()

    def test_angle(self):
        v1 = geom.Vector(1, 0, 0)
        v2 = geom.Vector(0, 1, 0)
        angle = v1.angle_to(v2)
        assert abs(angle - np.pi/2) < 1e-9


class TestVectorRelations:
    def test_parallel(self):
        v1 = geom.Vector(1, 0, 0)
        v2 = geom.Vector(2, 0, 0)
        assert v1.is_parallel(v2)

    def test_perpendicular(self):
        v1 = geom.Vector(1, 0, 0)
        v2 = geom.Vector(0, 1, 0)
        assert v1.is_perpendicular(v2)

    def test_equality(self):
        v1 = geom.Vector(1, 2, 3)
        v2 = geom.Vector(1, 2, 3)
        assert v1 == v2