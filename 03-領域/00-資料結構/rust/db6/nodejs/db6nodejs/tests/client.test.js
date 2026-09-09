import { describe, test, beforeEach, afterEach } from 'node:test';
import assert from 'node:assert';
import { Client } from '../src/index.js';

const DB_URL = 'http://localhost:50052';

describe('db6nodejs', () => {
  let db;

  beforeEach(() => {
    db = new Client(DB_URL);
  });

  afterEach(async () => {
    await db.close();
  });

  test('health', async () => {
    const result = await db.health();
    assert.strictEqual(result, true);
  });

  test('put and get', async () => {
    await db.put(1, 'test_key', 'test_value');
    const [value, found] = await db.get(1, 'test_key');
    assert.strictEqual(found, true);
    assert.strictEqual(value, 'test_value');
  });

  test('delete', async () => {
    await db.put(1, 'delete_key', 'delete_value');
    await db.delete(1, 'delete_key');
    const [, found] = await db.get(1, 'delete_key');
    assert.strictEqual(found, false);
  });

  test('get not found', async () => {
    const [, found] = await db.get(1, 'nonexistent_key');
    assert.strictEqual(found, false);
  });

  test('batch put', async () => {
    await db.batchPut(1, [['batch1', 'v1'], ['batch2', 'v2']]);
    const [v1] = await db.get(1, 'batch1');
    const [v2] = await db.get(1, 'batch2');
    assert.strictEqual(v1, 'v1');
    assert.strictEqual(v2, 'v2');
  });

  test('scan', async () => {
    await db.batchPut(1, [['scan_a', '1'], ['scan_b', '2'], ['scan_c', '3']]);
    const results = await db.scan(1, 'scan_', 'scan_\xff');
    const keys = results.map(([k]) => k).sort();
    assert.ok(keys.includes('scan_a'));
    assert.ok(keys.includes('scan_b'));
    assert.ok(keys.includes('scan_c'));
  });

  test('stats', async () => {
    const stats = await db.stats();
    assert.ok('key_count' in stats);
    assert.ok('engine' in stats);
    assert.ok('size_bytes' in stats);
  });

  test('execute sql', async () => {
    const result = await db.executeSql('SELECT 1 as id, "hello" as name');
    assert.ok(result);
    assert.ok('columns' in result);
    assert.ok('rows' in result);
  });

  test('fts insert and search', async () => {
    await db.ftsInsert(1, 'Hello world');
    await db.ftsInsert(2, '資料庫系統');
    const docIds = await db.ftsSearch('Hello');
    assert.ok(docIds.includes(1));
  });

  test('fts search chinese', async () => {
    await db.ftsInsert(10, '資料庫系統');
    const docIds = await db.ftsSearch('資料庫');
    assert.ok(docIds.includes(10));
  });

  test('fts search bm25', async () => {
    await db.ftsInsert(20, 'hello world database');
    await db.ftsInsert(21, 'hello hello database database');
    const results = await db.ftsSearchBm25('hello database');
    assert.ok(Array.isArray(results));
  });

  test('queue operations', async () => {
    const queueName = 'test_queue_js';
    await db.queueCreate(queueName);
    const result = await db.queueEnqueue(queueName, 'test_payload', 30);
    assert.ok(result);
    assert.ok('msg_id' in result || 'status' in result);
  });

  test('pubsub publish', async () => {
    const result = await db.pubsubPublish('test_channel', 'test_message');
    assert.ok(result);
  });
});