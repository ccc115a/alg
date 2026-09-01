#!/usr/bin/env python3
"""
lean4py example 03: Algebraic Structures
Demonstrates Magma, Semigroup, Monoid, Group, Ring, and Field.
"""

from lean4py import (
    Magma, Semigroup, Monoid, Group, AbelianGroup, Ring, Field,
)


def example_magma():
    print("=== Magma (closed binary operation) ===")
    M = Magma('M', {1, 2, 3}, lambda a, b: ((a + b) % 3) + 1)
    print(f"M = {M}")
    print(f"Carrier: {M.carrier}")
    print(f"Is closed: {M.is_closed()}")
    print()


def example_semigroup():
    print("=== Semigroup (associative magma) ===")
    S = Semigroup('S3', {0, 1, 2}, lambda a, b: (a + b) % 3)
    print(f"S = {S}")
    print(f"Is closed: {S.is_closed()}")
    print(f"Is associative: {S.is_associative()}")
    print()


def example_monoid():
    print("=== Monoid (semigroup + identity) ===")
    M = Monoid('M', {0, 1, 2}, lambda a, b: (a + b) % 3, 0)
    print(f"M = {M}")
    print(f"Identity: {M.identity}")
    print(f"Is monoid: {M.is_monoid()}")
    print()


def example_group():
    print("=== Group (monoid + inverses) ===")
    Z5 = Group('Z5', {0, 1, 2, 3, 4},
               lambda a, b: (a + b) % 5,
               0,
               lambda a: (5 - a) % 5)
    print(f"Z5 = {Z5}")
    print(f"Identity: {Z5.identity}")
    print(f"Is closed: {Z5.is_closed()}")
    print(f"Is associative: {Z5.is_associative()}")
    print(f"Has identity: {Z5.has_identity()}")
    print(f"Has inverses: {Z5.has_inverses()}")
    print(f"Is group: {Z5.is_group()}")
    print()


def example_abelian_group():
    print("=== Abelian Group (commutative group) ===")
    Z = AbelianGroup('Z', set(range(-10, 11)),
                     lambda a, b: a + b, 0, lambda a: -a)
    print(f"Z = {Z}")
    print(f"Is group: {Z.is_group()}")
    print(f"Is abelian: {Z.is_abelian()}")
    print()


def example_ring():
    print("=== Ring ===")
    Z = Ring('Z', set(range(-10, 11)),
             lambda a, b: a + b, 0, lambda a: -a,
             lambda a, b: a * b, 1)
    print(f"Z = {Z}")
    print(f"Is ring: {Z.is_ring()}")
    print()


def example_field():
    print("=== Field ===")
    def add(a, b): return (a[0]*b[1] + b[0]*a[1], a[1]*b[1])
    def neg(a): return (-a[0], a[1])
    def mul(a, b): return (a[0]*b[0], a[1]*b[1])
    def inv(a): return (a[1], a[0]) if a[0] != 0 else None

    Q_carrier = set()
    for num in range(-3, 4):
        for den in range(1, 4):
            Q_carrier.add((num, den))
    Q_carrier.discard((0, 1))

    Q = Field('Q', Q_carrier, add, (0, 1), neg, mul, (1, 1), inv)
    print(f"Q = {Q}")
    print(f"Has identity: {Q.has_identity()}")
    print(f"Is group: {Q.is_group()}")
    print()


def example_algebraic_hierarchy():
    print("=== Algebraic Structure Hierarchy ===")
    structures = [
        Magma('M', {1, 2}, lambda a, b: a * b),
        Semigroup('S', {1, 2}, lambda a, b: a * b),
        Monoid('M', {1, 2}, lambda a, b: a * b, 1),
        Group('G', {1, -1}, lambda a, b: a * b, 1, lambda a: a),
    ]

    for s in structures:
        print(f"{s.name}: closed={s.is_closed()}", end="")
        if hasattr(s, 'is_associative'):
            print(f", associative={s.is_associative()}", end="")
        if hasattr(s, 'has_identity'):
            print(f", has_identity={s.has_identity()}", end="")
        if hasattr(s, 'has_inverses'):
            print(f", has_inverses={s.has_inverses()}", end="")
        print()
    print()


def example_non_abelian():
    print("=== Non-Abelian Group (GL(2, 2)) ===")
    def mat_mul(a, b):
        return [[(a[0][0]*b[0][0] + a[0][1]*b[1][0]) % 2,
                 (a[0][0]*b[0][1] + a[0][1]*b[1][1]) % 2],
                [(a[1][0]*b[0][0] + a[1][1]*b[1][0]) % 2,
                 (a[1][0]*b[0][1] + a[1][1]*b[1][1]) % 2]]

    I = [[1, 0], [0, 1]]
    A = [[1, 1], [0, 1]]
    B = [[1, 0], [1, 1]]
    carrier = {I, A, B}

    G = Group('GL(2,2)', carrier, mat_mul, I, lambda m: m)
    print(f"GL(2,2) = {G}")
    print(f"Is closed: {G.is_closed()}")
    print(f"Is group: {G.is_group()}")
    print(f"Is abelian: {G.is_abelian()}")
    print()


if __name__ == '__main__':
    example_magma()
    example_semigroup()
    example_monoid()
    example_group()
    example_abelian_group()
    example_ring()
    example_field()
    example_algebraic_hierarchy()
    example_non_abelian()
    print("All algebra examples completed!")