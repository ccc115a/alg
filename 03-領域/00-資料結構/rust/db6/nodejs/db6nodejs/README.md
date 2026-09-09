# db6nodejs

Node.js client for db6 database with REST support.

## Installation

```bash
npm install db6nodejs
```

## Quick Start

```javascript
import { Client } from 'db6nodejs';

// Create client
const db = new Client('http://localhost:50052');

// Health check
await db.health();

// Key-Value operations
await db.put(1, 'key', 'value');
const [value, found] = await db.get(1, 'key');

// Batch operations
await db.batchPut(1, [['k1', 'v1'], ['k2', 'v2']]);
const results = await db.scan(1, 'k', 'k\xff');

// Statistics
const stats = await db.stats();

// Delete
await db.delete(1, 'key');
```

## API Reference

### new Client(baseUrl, options?)

- `baseUrl`: Base URL of db6 server (e.g., 'http://localhost:50052')

### Methods

- `health()` -> Promise<boolean>
- `put(tableId, key, value)` -> Promise<void>
- `get(tableId, key)` -> Promise<[value, found]>
- `delete(tableId, key)` -> Promise<void>
- `batchPut(tableId, items)` -> Promise<void>
- `scan(tableId, startKey, endKey)` -> Promise<Array<[key, value]>>
- `stats()` -> Promise<object>
- `rangeDelete(tableId, startKey, endKey)` -> Promise<void>
- `close()` -> Promise<void>

## License

MIT