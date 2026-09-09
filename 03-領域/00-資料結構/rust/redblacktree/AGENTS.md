# redblacktree

Red-black tree (LLRB variant). Single crate, no dependencies, edition 2024.

## Commands

```sh
cargo test --lib          # Run all 26 inline tests
cargo test --lib <name>   # Run one test: cargo test --lib test_remove_leaf
cargo run --example basic # Run an example (basic, iterator_demo, stress_test, string_keys)
cargo run -- <command>    # CLI: insert <k> <v>, search <k>, delete <k>, list, min, max, help
```

## Structure

- `src/lib.rs` — `RedBlackTree<K,V>` with full LLRB implementation (insert, remove, iter, etc.)
- `src/main.rs` — stateless CLI demo (each command creates a fresh empty tree)
- `examples/` — 4 examples (basic, iterator_demo, stress_test, string_keys)
- Inline `#[cfg(test)] mod tests` — 26 tests, all pass

## Notes

- `main.rs` binary is a toy: each command constructs a new empty tree, so the CLI is stateless (one-shot insert only). Not a bug, just limited.
