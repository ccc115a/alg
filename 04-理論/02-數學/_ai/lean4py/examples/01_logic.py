#!/usr/bin/env python3
"""
lean4py example 01: Propositional Logic
Demonstrates Prop, logical operators, and theorem proving.
"""

from lean4py import (
    Prop, Prop_var, implies, and_, or_, not_, iff,
    Theorem, prove, assume, have, exact, apply, rfl, simp,
)


def example_propositions():
    print("=== Propositions ===")
    p = Prop('p')
    q = Prop('q')
    r = Prop('r')
    print(f"p = {p}")
    print(f"q = {q}")
    print(f"p → q = {implies(p, q)}")
    print(f"p ∧ q = {p & q}")
    print(f"p ∨ q = {p | q}")
    print(f"¬p = {~p}")
    print(f"p ↔ q = {iff(p, q)}")
    print()


def example_rshift():
    print("=== Right Shift Operator (→) ===")
    p = Prop('p')
    q = Prop('q')
    print(f"p >> q = {p >> q}")
    print()


def example_theorems():
    print("=== Theorems ===")
    p = Prop('p')
    q = Prop('q')

    t1 = Theorem('identity', implies(p, p))
    print(f"Theorem identity: {t1}")

    t2 = Theorem('and_intro',
        implies(and_(p, q), p),
        [assume('h', and_(p, q)), exact(p)])
    print(f"Theorem and_intro: {t2}")

    t3 = Theorem('and_elim_right',
        implies(and_(p, q), q),
        [assume('h', and_(p, q)), exact(q)])
    print(f"Theorem and_elim_right: {t3}")
    print()


def example_prove():
    print("=== Prove Function ===")
    p = Prop('p')
    q = Prop('q')

    theorem = prove(
        implies(and_(p, implies(p, q)), q),
        [
            assume('h1', and_(p, implies(p, q))),
            have('p', p, from_='h1'),
            have('p_implies_q', implies(p, q), from_='h1'),
            apply('p_implies_q'),
            exact(p),
        ]
    )
    print(f"Proved: {theorem}")
    print()


def example_proof_steps():
    print("=== Proof Steps ===")
    p = Prop('p')
    q = Prop('q')

    steps = [
        assume('h', and_(p, q)),
        have('hp', p, from_='h'),
        exact(p),
    ]

    for step in steps:
        print(f"  {step}")
    print()


def example_complex():
    print("=== Complex Logical Formula ===")
    p = Prop('p')
    q = Prop('q')
    r = Prop('r')

    formula = iff(
        and_(p, implies(p, q)),
        implies(and_(p, implies(p, q)), q)
    )
    print(f"(p ∧ (p → q)) ↔ ((p ∧ (p → q)) → q) = {formula}")
    print()


if __name__ == '__main__':
    example_propositions()
    example_rshift()
    example_theorems()
    example_prove()
    example_proof_steps()
    example_complex()
    print("All logic examples completed!")