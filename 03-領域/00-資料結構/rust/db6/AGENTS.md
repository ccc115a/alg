# db6 Agent Instructions

## Build Commands

```bash
cargo build    # Build library
cargo test     # Run tests
./test.sh      # Build + test with output
cargo run      # Run REPL
```

## Architecture

- `src/engine/` — Storage engines: `memory.rs`, `btree/`, `lsm.rs`
- `src/fts/` — FTS (CjkTokenizer, EnglishTokenizer, FtsIndex)
- `src/sql/` — SQL (Parser, Planner, Executor)

## Entry Point

`src/lib.rs` exports:
```rust
pub use engine::{EngineStats, StorageEngine, KvStore, MemoryEngine, BTreeEngine, LsmEngine};
pub use fts::{FtsIndex, CjkTokenizer, FtsTokenizer};
pub use sql::{parse, Executor, ResultSet};
```

## Key Design Notes

- StorageEngine trait uses `where Self: Sized` for `open`/`open_memory` to be dyn compatible
- Memory engine uses BTreeMap to support ORDER BY and range scans
- BTreeEngine uses RwLock for thread safety
- scan() uses `std::collections::Bound` for range queries
- table_id parameter enables multi-table isolation
- batch_put / range_delete for bulk operations

## REPL Commands

```bash
.engine memory|btree|lsm  # Switch engine
.read file.sql            # Execute SQL file
.help                     # Show help
.quit                     # Exit
```

## Git Workflow

`./git.sh <message> <branch>` — commit + push

## Documentation

- [_doc/plan.md](_doc/plan.md) — Full roadmap
- [_doc/v2.1.md](_doc/v2.1.md) — v2.1 完成項目
- [_doc/v2.2.md](_doc/v2.2.md) — v2.2 完成項目
- [_doc/v2.3.md](_doc/v2.3.md) — v2.3 完成項目（範例 + API 統一化）
- [_doc/v2.4.md](_doc/v2.4.md) — v2.4 完成項目（LSM 強化）
- [_doc/v2.5.md](_doc/v2.5.md) — v2.5 完成項目（Memory 模組化）
- [_doc/v2.6.md](_doc/v2.6.md) — v2.6 完成項目（Capability 系統）
- [_doc/v2.7.md](_doc/v2.7.md) — v2.7 完成項目（FTS 強化）