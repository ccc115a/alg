# db6

[![Crates.io][crates-badge]][crates-url]
[![MIT licensed][mit-badge]][mit-url]


[crates-badge]: https://img.shields.io/crates/v/db6.svg
[crates-url]: https://crates.io/crates/db6
[mit-badge]: https://img.shields.io/badge/license-MIT-blue.svg
[mit-url]: https://github.com/cccrust/db6

Unified database with pluggable storage engines (Memory / BTree / LSM).

- **KV**: Key-Value store
- **SQL**: Parser + Planner + Executor
- **FTS**: Full-Text Search with BM25 ranking
- **Msgq**: Message Queue (sync & async)

## Installation

```bash
cargo add db6
```

## Quick Start

```bash
cargo build
cargo test
cargo run
```

## Storage Engines

| Engine | Backend | Features | Use Case |
|--------|---------|----------|----------|
| Memory | BTreeMap (in-memory) | ORDER BY, range scan | Prototyping, cache |
| BTree | Disk BTree | Full transactions, persistence | General purpose |
| LSM | LSM-tree | Bloom filter, WAL, high write throughput | Write-heavy workloads |

## Key-Value API

```rust
use db6::{KvEngine, KvStore};

let engine = KvEngine::new("memory")?;
engine.put(1, b"key", b"value")?;
let val = engine.get(1, b"key")?;
engine.delete(1, b"key")?;
```

## SQL

```rust
use db6::{parse, Executor, ResultSet};

let stmts = parse("SELECT * FROM users WHERE age > 18")?;
let mut exec = Executor::new(engine);
let result = exec.execute(&stmts[0])?;
```

## Fluent Query API

```rust
use db6::Db;

let mut db = Db::new("memory")?;
let rows = db.select("name, email")
    .from("users")
    .filter("age > 18")
    .execute()?;
```

## Full-Text Search

```rust
use db6::{FtsIndex, FtsTokenizer, CjkTokenizer};

let mut index = FtsIndex::new(engine);
index.insert(1, "database system")?;
let results = index.search("data")?;
let ranked = index.search_bm25("data")?;
```

## Message Queue

```rust
use db6::msgq::Msgq;

let msgq = Msgq::new("memory")?;
let mut queue = msgq.queue("tasks");
queue.enqueue(b"work".to_vec(), 30)?;
let msg = queue.dequeue(0)?;
queue.ack(&msg.unwrap().id)?;
```

## Publish

```bash
./pub.sh <new_version>
# e.g. ./pub.sh 4.14.0
```

## Version History

| Phase | Version | Features |
|-------|---------|----------|
| v0.x | 0.x | StorageEngine trait + 3 engines |
| v1.0+ | 1.x | FTS (inverted index + BM25) |
| v2.0+ | 2.x | SQL (parser, planner, executor) |
| v3.0+ | 3.x | Fluent API + LSM enhancements |
| v4.0+ | 4.x | Message Queue (sync + async) |

## Related Projects

- [btree6](https://github.com/cccrust/btree6)
- [lsm5](https://github.com/cccrust/lsm5)
- [sp6](https://github.com/cccrust/sp6)

## License

MIT
