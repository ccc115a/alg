# math4py

A Python library for mathematics - algebra, calculus, geometry and more.

## Modules

- `geometry`: 3D geometry module (points, vectors, lines, planes)

## Installation

```bash
cd math4py
pip install -e .
```

## Usage

```python
import math4py as mp

# Using geometry module
from math4py.geometry import Point, Vector, Line, Plane

p1 = Point(0, 0, 0)
p2 = Point(1, 0, 0)
v = Vector(0, 1, 0)
line = Line(p1, v)
```

## Development

```bash
pip install -e ".[dev]"
pytest
```
