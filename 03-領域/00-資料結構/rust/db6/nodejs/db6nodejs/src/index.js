import http from 'node:http';
import https from 'node:https';

export class Client {
  constructor(baseUrl, options = {}) {
    this.baseUrl = baseUrl.replace(/\/$/, '');
    this.useWebSocket = options.useWebSocket || false;
    this._ws = null;
    this._wsConnected = false;
    this._wsCallbacks = new Map();
    this._wsMessageId = 0;
  }

  _request(method, path, json) {
    return new Promise((resolve, reject) => {
      const url = new URL(path, this.baseUrl);
      const isHttps = url.protocol === 'https:';
      const lib = isHttps ? https : http;

      const options = {
        method,
        hostname: url.hostname,
        port: url.port || (isHttps ? 443 : 80),
        path: url.pathname + url.search,
        headers: {
          'Content-Type': 'application/json',
        },
      };

      const req = lib.request(options, (res) => {
        let data = '';
        res.on('data', (chunk) => data += chunk);
res.on('end', () => {
          if (res.statusCode >= 400) {
            reject(new Error(`HTTP ${res.statusCode}: ${data}`));
            return;
          }
          const ct = res.headers['content-type'] || '';
          if (ct.includes('application/json')) {
            try {
              resolve(JSON.parse(data));
            } catch {
              resolve({});
            }
          } else {
            resolve(data);
          }
        });
      });

      req.on('error', reject);
      req.setTimeout(30000, () => {
        req.destroy();
        reject(new Error('Request timeout'));
      });

      if (json) {
        req.write(JSON.stringify(json));
      }
      req.end();
    });
  }

  async health() {
    try {
      const resp = await this._request('GET', '/health');
      return resp === 'OK' || resp?.status === 'ok';
    } catch {
      return false;
    }
  }

  async put(tableId, key, value) {
    await this._request('POST', '/kv/put', { table_id: tableId, key, value });
  }

  async get(tableId, key) {
    const result = await this._request('POST', '/kv/get', { table_id: tableId, key });
    return [result.value ?? null, result.found ?? false];
  }

  async delete(tableId, key) {
    await this._request('POST', '/kv/delete', { table_id: tableId, key });
  }

  async batchPut(tableId, items) {
    await this._request('POST', '/kv/batch_put', {
      table_id: tableId,
      pairs: items.map(([k, v]) => ({ key: k, value: v })),
    });
  }

  async scan(tableId, startKey, endKey) {
    const result = await this._request('POST', '/kv/scan', {
      table_id: tableId,
      start: startKey,
      end: endKey,
    });
    return (result.pairs || []).map((p) => [p.key, p.value]);
  }

  async stats() {
    return await this._request('GET', '/kv/stats');
  }

  async rangeDelete(tableId, startKey, endKey) {
    await this._request('POST', '/kv/range_delete', {
      table_id: tableId,
      start: startKey,
      end: endKey,
    });
  }

  async executeSql(sql) {
    return await this._request('POST', '/sql/execute', { sql });
  }

  async ftsInsert(docId, text) {
    await this._request('POST', '/fts/insert', { doc_id: docId, text });
  }

  async ftsSearch(query) {
    const result = await this._request('POST', '/fts/search', { query });
    return result.doc_ids || [];
  }

  async ftsSearchBm25(query) {
    const result = await this._request('POST', '/fts/search_bm25', { query });
    return result.results || [];
  }

  async queueCreate(name) {
    await this._request('POST', '/queue/create', { name });
  }

  async queueEnqueue(name, payload, timeout = 30) {
    return await this._request('POST', '/queue/enqueue', { name, payload, timeout });
  }

  async queueDequeue(name, waitTimeout = 0) {
    return await this._request('POST', '/queue/dequeue', { name, wait_timeout: waitTimeout });
  }

  async queueAck(name, msgId) {
    await this._request('POST', '/queue/ack', { name, msg_id: msgId });
  }

  async queueStats(name) {
    return await this._request('POST', '/queue/stats', { name });
  }

  async queueList() {
    const result = await this._request('GET', '/queue/list');
    return result.queues || [];
  }

  async pubsubPublish(channel, payload) {
    return await this._request('POST', '/pubsub/publish', { channel, payload });
  }

  async close() {
    if (this._ws) {
      this._ws.close();
      this._ws = null;
      this._wsConnected = false;
    }
  }
}

export default Client;