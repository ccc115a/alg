# lean4py AGENTS.md

## Install
```bash
pip install -e .
pip install pytest
```

## Test
```bash
pytest tests/
```

## Key Commands
- `pytest tests/` - Run all tests
- `pytest tests/test_prover.py -v` - Run prover tests only
- `python examples/01_logic.py` - Logic example
- `python examples/02_sets.py` - Sets example
- `python examples/03_algebra.py` - Algebra example

## Structure
- `lean4py/` - Main library (logic, sets, algebra, nat, tactics, prover)
- `tests/` - pytest tests
- `examples/` - Usage examples

## Important Implementation Notes

### tableau_prove bugs fixed (prover.py)
1. `¬(A → B)` expands to `[A, ¬B]` on ONE branch (α-rule), not two branches
2. Negated literals (e.g., `¬p`) should not expand - `else: pass` in `_expand_branch`
3. `_is_complementary` uses `==` not `is` for operand comparison (Prop equality is by name)

### Prop objects
- `Prop('p') == Prop('p')` is True (name-based equality)
- But `Prop('p') is Prop('p')` is False (different objects)
- Use `==` for equality checks in prover logic

## Modules
- `lean4py.logic` - Prop, implies, and_, or_, not_, Theorem, prove
- `lean4py.sets` - Set_from, union, intersection, subset
- `lean4py.algebra` - Group, AbelianGroup, Ring
- `lean4py.nat` - Natural numbers
- `lean4py.tactics` - Proof tactics (intros, cases, split, etc.)
- `lean4py.prover` - tableau_prove, truth_table_prove, is_valid, is_satisfiable
- `lean4py.number_theory` - Integer, gcd, lcm, is_prime, phi, mod_exp, etc. (v0.3)
- `lean4py.linear_algebra` - Vector, Matrix, dot_product, det, rank, etc. (v0.3)