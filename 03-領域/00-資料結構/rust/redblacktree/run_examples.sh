#!/bin/bash
set -x

for ex in basic iterator_demo stress_test string_keys; do
  cargo run --example "$ex"
done
