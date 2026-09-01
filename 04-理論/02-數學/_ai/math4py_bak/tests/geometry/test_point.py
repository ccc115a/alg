"""Tests for Point class."""

import pytest
import math4py.geometry as geom


class TestPointCreation:
    def test_create_point(self):
        p = geom.Point(1, 2, 3)
        assert p.x == 1
        assert p.y == 2
        assert p.z == 3

    def test_point_repr(self):
        p = geom.Point(1, 2, 3)
        assert repr(p) == "Point(1.0, 2.0, 3.0)"


class TestPointOperations:
    def test_add_vector(self):
        p = geom.Point(1, 2, 3)
        v = geom.Vector(1, 0, 0)
        result = p + v
        assert result == geom.Point(2, 2, 3)

    def test_sub_point(self):
        p1 = geom.Point(2, 2, 2)
        p2 = geom.Point(1, 1, 1)
        result = p1 - p2
        assert result == geom.Vector(1, 1, 1)

    def test_sub_vector(self):
        p = geom.Point(2, 2, 2)
        v = geom.Vector(1, 0, 0)
        result = p - v
        assert result == geom.Point(1, 2, 2)


class TestPointMethods:
    def test_distance_to(self):
        p1 = geom.Point(0, 0, 0)
        p2 = geom.Point(3, 4, 0)
        assert abs(p1.distance_to(p2) - 5.0) < 1e-9

    def test_to_vector(self):
        p = geom.Point(1, 2, 3)
        v = p.to_vector()
        assert v == geom.Vector(1, 2, 3)

    def test_equality(self):
        p1 = geom.Point(1, 2, 3)
        p2 = geom.Point(1, 2, 3)
        assert p1 == p2