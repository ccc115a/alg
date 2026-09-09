# db6py

Python client for db6 database with REST and WebSocket support.

## Installation

```bash
pip install db6py
```

With WebSocket support:

```bash
pip install db6py[websocket]
```

## Quick Start

```python
from db6py import Client

# Create client (REST)
db = Client("http://localhost:50052")

# Or use WebSocket
db = Client("http://localhost:50052", use_websocket=True)

# Health check
db.health()

# Key-Value operations
db.put(1, "key", "value")
value, found = db.get(1, "key")

# Batch operations
db.batch_put(1, [("k1", "v1"), ("k2", "v2")])
results = db.scan(1, "k", "k\xff")

# Statistics
stats = db.stats()

# Delete
db.delete(1, "key")
```

## API Reference

### Client(base_url, use_websocket=False)

- `health()` -> bool
- `put(table_id, key, value)` -> None
- `get(table_id, key)` -> (value, found)
- `delete(table_id, key)` -> None
- `batch_put(table_id, items)` -> None
- `scan(table_id, start_key, end_key)` -> [(key, value), ...]
- `stats()` -> dict

## License

MIT