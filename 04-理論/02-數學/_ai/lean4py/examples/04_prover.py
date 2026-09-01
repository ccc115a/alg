#!/usr/bin/env python3
"""
lean4py example 04:
Automated Theorem Proving and Advanced Tactics (v0.2)
Demonstrates the new prover module and additional tactics.
"""

from lean4py import (
    Prop, implies, and_, or_, not_, iff,
    Prover, truth_table_prove, tableau_prove,
    is_valid, is_satisfiable, find_counterexample,
)
from lean4py.tactics import (
    intros, by_contra, cases, split, left, right,
    use, show, by, sorry, rewrite, induction,
    intro, calc, TacticState,
)

def example_truth_table_prover():
    print("=== Truth Table Prover ===")
    p = Prop('p')
    q = Prop('q')

    print(f"p → p is valid: {truth_table_prove(implies(p, p))}")
    print(f"p ∨ ¬p is valid: {truth_table_prove(or_(p, not_(p)))}")
    print(f"p → q is valid: {truth_table_prove(implies(p, q))}")
    print(f"(p ∧ q) → p is valid: {truth_table_prove(implies(and_(p, q), p))}")
    print()

def example_tableau_prover():
    print("=== Semantic Tableau Prover ===")
    p = Prop('p')
    q = Prop('q')

    print(f"p → p via tableau: {tableau_prove(implies(p, p))}")
    print(f"p ∨ ¬p via tableau: {tableau_prove(or_(p, not_(p)))}")
    print(f"(p ∧ (p → q)) → q via tableau: {tableau_prove(implies(and_(p, implies(p, q)), q))}")
    print()

def example_is_valid():
    print("=== Validity Checking ===")
    p = Prop('p')
    q = Prop('q')

    print(f"p → p is valid: {is_valid(implies(p, p))}")
    print(f"p → q is valid: {is_valid(implies(p, q))}")
    print(f"¬(p ∧ ¬p) is valid: {is_valid(not_(and_(p, not_(p))))}")
    print()

def example_is_satisfiable():
    print("=== Satisfiability Checking ===")
    p = Prop('p')
    q = Prop('q')

    print(f"p is satisfiable: {is_satisfiable(p)}")
    print(f"p ∧ ¬p is satisfiable: {is_satisfiable(and_(p, not_(p)))}")
    print(f"p ∨ q is satisfiable: {is_satisfiable(or_(p, q))}")
    print()

def example_counterexample():
    print("=== Finding Counterexamples ===")
    p = Prop('p')
    q = Prop('q')

    ce = find_counterexample(implies(p, q))
    print(f"Counterexample for p → q: {ce}")
    ce = find_counterexample(implies(p, p))
    print(f"Counterexample for p → p: {ce}")
    print()

def example_prover_class():
    print("=== Using the Prover Class ===")
    prover = Prover()
    p = Prop('p')
    q = Prop('q')

    result = prover.prove(implies(and_(p, implies(p, q)), q))
    print(f"Proved modus ponens: {result is not None}")

    result, ce = prover.prove_with_steps(implies(p, q))
    print(f"p → q provable: {result}, counterexample: {ce}")
    print()

def example_new_tactics():
    print("=== New Tactics (v0.2) ===")

    p = Prop('p')
    q = Prop('q')

    print("intros(['x', 'y']):", intros(['x', 'y']))
    print("by_contra('h', not_(p)):", by_contra('h', not_(p)))
    print("cases('h', [p, q]):", cases('h', [p, q]))
    print("split():", split())
    print("left():", left())
    print("right():", right())
    print("use('x'):", use('x'))
    print("show(p):", show(p))
    print("sorry():", sorry())
    print("rewrite('h', sym=True):", rewrite('h', sym=True))
    print()

def example_tactic_state():
    print("=== TacticState ===")
    state = TacticState()
    p = Prop('p')

    state.add_hypothesis('h1', p)
    print(f"Added h1: {state.get_hypothesis('h1')}")
    print(f"Hypotheses: {list(state.hypotheses.keys())}")
    print()

def example_nested_proof():
    print("=== Nested Proof with 'by' ===")
    p = Prop('p')
    q = Prop('q')

    proof = by([split(), left(), right()])
    print(f"Nested proof: {proof}")
    print()

def example_calc_tactic():
    print("=== Calc Tactic ===")
    proof = calc([sorry()])
    print(f"Calc proof: {proof}")
    print()

if __name__ == '__main__':
    example_truth_table_prover()
    example_tableau_prover()
    example_is_valid()
    example_is_satisfiable()
    example_counterexample()
    example_prover_class()
    example_new_tactics()
    example_tactic_state()
    example_nested_proof()
    example_calc_tactic()
    print("All v0.2 examples completed!")