#!/usr/bin/env python3
"""
lean4py example 02: Set Theory
Demonstrates Set operations, relations, and constructions.
"""

from lean4py import (
    Set, Set_from, empty_set,
    in_, subset, union, intersection, complement, difference,
    cartesian, power_set,
)


def example_basic_sets():
    print("=== Basic Sets ===")
    A = Set_from([1, 2, 3])
    B = Set_from([2, 3, 4])
    E = empty_set()

    print(f"A = {A}")
    print(f"B = {B}")
    print(f"∅ = {E}")
    print()


def example_membership():
    print("=== Membership (∈) ===")
    A = Set_from([1, 2, 3])
    print(f"1 ∈ A: {1 in A}")
    print(f"4 ∈ A: {4 in A}")
    print(f"in_(1, A): {in_(1, A)}")
    print()


def example_union():
    print("=== Union (∪) ===")
    A = Set_from([1, 2, 3])
    B = Set_from([3, 4, 5])
    U = union(A, B)
    print(f"A ∪ B = {U}")
    print(f"A + B = {A + B}")
    print()


def example_intersection():
    print("=== Intersection (∩) ===")
    A = Set_from([1, 2, 3])
    B = Set_from([2, 3, 4])
    I = intersection(A, B)
    print(f"A ∩ B = {I}")
    print(f"A * B = {A * B}")
    print()


def example_difference():
    print("=== Difference (\\) ===")
    A = Set_from([1, 2, 3, 4])
    B = Set_from([3, 4, 5])
    D = difference(A, B)
    print(f"A \\ B = {D}")
    print(f"A - B = {A - B}")
    print()


def example_complement():
    print("=== Complement (~) ===")
    A = Set_from([1, 2, 3])
    C = complement(A)
    print(f"~A = {C}")
    print()


def example_subset():
    print("=== Subset (⊆) ===")
    A = Set_from([1, 2])
    B = Set_from([1, 2, 3])
    C = Set_from([1, 2, 3])

    print(f"{{1,2}} ⊆ {{1,2,3}}: {subset(A, B)}")
    print(f"A ≤ B: {A <= B}")
    print(f"A < B: {A < B}")
    print(f"B ≤ C: {B <= C}")
    print()


def example_cartesian_product():
    print("=== Cartesian Product (×) ===")
    A = Set_from([1, 2])
    B = Set_from(['a', 'b'])
    C = cartesian(A, B)
    print(f"A × B = {C}")
    print()


def example_power_set():
    print("=== Power Set (P) ===")
    E = empty_set()
    P_E = power_set(E)
    print(f"P(∅) = {P_E}")

    S = Set_from([1, 2])
    P_S = power_set(S)
    print(f"P({{1,2}}) = {P_S}")
    print()


def example_set_laws():
    print("=== Set Laws ===")
    A = Set_from([1, 2, 3])
    B = Set_from([2, 3, 4])
    C = Set_from([3, 4, 5])

    Idem = union(A, A)
    print(f"A ∪ A = {Idem} (Idempotent)")

    Comm = union(A, B) == union(B, A)
    print(f"A ∪ B = B ∪ A: {Comm} (Commutative)")

    Assoc = union(union(A, B), C) == union(A, union(B, C))
    print(f"(A ∪ B) ∪ C = A ∪ (B ∪ C): {Assoc} (Associative)")

    Dist = intersection(A, union(B, C)) == union(intersection(A, B), intersection(A, C))
    print(f"A ∩ (B ∪ C) = (A ∩ B) ∪ (A ∩ C): {Dist} (Distributive)")
    print()


def example_complex():
    print("=== Complex Set Expression ===")
    A = Set_from([1, 2, 3])
    B = Set_from([2, 3, 4])
    C = Set_from([3, 4, 5])

    Result = intersection(union(A, B), C)
    print(f"(A ∪ B) ∩ C = {Result}")
    print()


if __name__ == '__main__':
    example_basic_sets()
    example_membership()
    example_union()
    example_intersection()
    example_difference()
    example_complement()
    example_subset()
    example_cartesian_product()
    example_power_set()
    example_set_laws()
    example_complex()
    print("All set theory examples completed!")