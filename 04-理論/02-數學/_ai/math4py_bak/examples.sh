#!/bin/bash
# Run all math4py examples

set -x

cd "$(dirname "$0")"

# Use the same Python that has math4py installed
PYTHON="${VENV_PYTHON:-python}"

# Run geometry examples
echo "=== Running Geometry Examples ==="
for example in examples/geometry/*.py; do
    echo "--- Running $example ---"
    $PYTHON "$example"
    echo ""
done

# Run statistics examples
echo "=== Running Statistics Examples ==="
for example in examples/statistics/*.py; do
    echo "--- Running $example ---"
    $PYTHON "$example"
    echo ""
done

# Run stochastic calculus examples
echo "=== Running Stochastic Calculus Examples ==="
for example in examples/stochastic/calculus/*.py; do
    echo "--- Running $example ---"
    $PYTHON "$example"
    echo ""
done

echo "=== All examples completed ==="
