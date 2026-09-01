# lean4py

A Python library inspired by Lean's mathlib for formal mathematics.

## Installation

```bash
pip install lean4py
```

For development:

```bash
git clone https://github.com/yourusername/lean4py.git
cd lean4py
pip install -e .
pip install pytest
```

## Quick Start

```python
from lean4py import Prop, implies, and_, Theorem, prove, exact, assume

p, q = Prop('p'), Prop('q')

theorem = prove(
    implies(and_(p, implies(p, q)), q),
    [
        assume('h1', and_(p, implies(p, q))),
        exact(q),
    ]
)
print(theorem)
```

## Features

### Propositional Logic

```python
from lean4py import Prop, implies, and_, or_, not_, iff

p, q = Prop('p'), Prop('q')
formula = implies(p, q)          # p → q
formula = p & q                  # p ∧ q
formula = p | q                  # p ∨ q
formula = ~p                     # ¬p
formula = iff(p, q)              # p ↔ q
```

### Set Theory

```python
from lean4py import Set_from, union, intersection, subset

A = Set_from([1, 2, 3])
B = Set_from([2, 3, 4])

U = A + B         # union
I = A * B         # intersection
S = A <= B        # subset
```

### Algebraic Structures

```python
from lean4py import Group, AbelianGroup, Ring

Z = AbelianGroup('Z', set(range(-100, 101)),
                 lambda a, b: a + b, 0, lambda a: -a)
print(Z.is_abelian_group())  # True
```

## Modules

| Module | Description |
|--------|-------------|
| `lean4py.logic` | Propositional logic, theorems, proofs |
| `lean4py.sets` | Set theory operations |
| `lean4py.algebra` | Algebraic structures |
| `lean4py.nat` | Natural numbers |
| `lean4py.tactics` | Proof tactics |

## Testing

```bash
pytest tests/
```

## Examples

```bash
python examples/01_logic.py
python examples/02_sets.py
python examples/03_algebra.py
```

## License

MIT