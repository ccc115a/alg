"""db6py client with REST and WebSocket support"""

import json
import requests
from typing import List, Tuple, Optional, Dict, Any

from db6py.exceptions import ConnectionError, RequestError


class Client:
    """Synchronous db6 client with REST support"""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def _request(self, method: str, path: str, json: Optional[Dict] = None) -> Any:
        """Make REST request to db6 server"""
        url = f"{self.base_url}{path}"
        try:
            resp = requests.request(method, url, json=json, timeout=30)
            resp.raise_for_status()
            return resp.json() if resp.text else {}
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(f"Failed to connect to {self.base_url}") from e
        except requests.exceptions.RequestException as e:
            raise RequestError(f"Request failed: {e}") from e

    def health(self) -> bool:
        """Check if db6 server is healthy"""
        try:
            resp = requests.get(f"{self.base_url}/health", timeout=5)
            return resp.text == "OK"
        except Exception:
            return False

    def put(self, table_id: int, key: str, value: str) -> None:
        """Put a key-value pair"""
        self._request("POST", "/kv/put", {"table_id": table_id, "key": key, "value": value})

    def get(self, table_id: int, key: str) -> Tuple[Optional[str], bool]:
        """Get a value by key. Returns (value, found)"""
        result = self._request("POST", "/kv/get", {"table_id": table_id, "key": key})
        return result.get("value"), result.get("found", False)

    def delete(self, table_id: int, key: str) -> None:
        """Delete a key"""
        self._request("POST", "/kv/delete", {"table_id": table_id, "key": key})

    def batch_put(self, table_id: int, items: List[Tuple[str, str]]) -> None:
        """Batch put key-value pairs"""
        self._request("POST", "/kv/batch_put", {
            "table_id": table_id,
            "pairs": [{"key": k, "value": v} for k, v in items]
        })

    def scan(self, table_id: int, start_key: str, end_key: str) -> List[Tuple[str, str]]:
        """Scan keys in range [start_key, end_key]"""
        result = self._request("POST", "/kv/scan", {"table_id": table_id, "start": start_key, "end": end_key})
        return [(item["key"], item["value"]) for item in result.get("pairs", [])]

    def stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        return self._request("GET", "/kv/stats")

    def range_delete(self, table_id: int, start_key: str, end_key: str) -> None:
        """Delete all keys in range [start_key, end_key]"""
        self._request("POST", "/kv/range_delete", {"table_id": table_id, "start": start_key, "end": end_key})

    def execute_sql(self, sql: str) -> Dict[str, Any]:
        """Execute SQL query"""
        return self._request("POST", "/sql/execute", {"sql": sql})

    def fts_insert(self, doc_id: int, text: str) -> None:
        """Insert document into FTS index"""
        self._request("POST", "/fts/insert", {"doc_id": doc_id, "text": text})

    def fts_search(self, query: str) -> List[int]:
        """Search FTS index, returns list of doc_ids"""
        result = self._request("POST", "/fts/search", {"query": query})
        return result.get("doc_ids", [])

    def fts_search_bm25(self, query: str) -> List[Dict[str, Any]]:
        """Search FTS index with BM25 scoring"""
        result = self._request("POST", "/fts/search_bm25", {"query": query})
        return result.get("results", [])

    def queue_create(self, name: str) -> None:
        """Create a message queue"""
        self._request("POST", "/queue/create", {"name": name})

    def queue_enqueue(self, name: str, payload: str, timeout: int = 30) -> Dict[str, Any]:
        """Enqueue a message, returns msg_id"""
        return self._request("POST", "/queue/enqueue", {"name": name, "payload": payload, "timeout": timeout})

    def queue_dequeue(self, name: str, wait_timeout: int = 0) -> Optional[Dict[str, Any]]:
        """Dequeue a message"""
        return self._request("POST", "/queue/dequeue", {"name": name, "wait_timeout": wait_timeout})

    def queue_ack(self, name: str, msg_id: str) -> None:
        """Acknowledge a message"""
        self._request("POST", "/queue/ack", {"name": name, "msg_id": msg_id})

    def queue_stats(self, name: str) -> Dict[str, Any]:
        """Get queue statistics"""
        return self._request("POST", "/queue/stats", {"name": name})

    def queue_list(self) -> List[str]:
        """List all queues"""
        result = self._request("GET", "/queue/list")
        return result.get("queues", [])

    def pubsub_publish(self, channel: str, payload: str) -> Dict[str, Any]:
        """Publish to a PubSub channel"""
        return self._request("POST", "/pubsub/publish", {"channel": channel, "payload": payload})