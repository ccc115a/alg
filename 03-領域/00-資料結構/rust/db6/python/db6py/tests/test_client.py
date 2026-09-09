"""pytest for db6py"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from db6py import Client


@pytest.fixture
def db():
    return Client("http://localhost:50052")


class TestHealth:
    def test_health(self, db):
        assert db.health() == True


class TestKVOperations:
    def test_put_get(self, db):
        db.put(1, "test_key", "test_value")
        value, found = db.get(1, "test_key")
        assert found == True
        assert value == "test_value"

    def test_delete(self, db):
        db.put(1, "delete_key", "delete_value")
        db.delete(1, "delete_key")
        _, found = db.get(1, "delete_key")
        assert found == False

    def test_get_not_found(self, db):
        _, found = db.get(1, "nonexistent_key")
        assert found == False


class TestBatchOperations:
    def test_batch_put(self, db):
        db.batch_put(1, [("batch1", "v1"), ("batch2", "v2")])
        v1, _ = db.get(1, "batch1")
        v2, _ = db.get(1, "batch2")
        assert v1 == "v1"
        assert v2 == "v2"

    def test_scan(self, db):
        db.batch_put(1, [("scan_a", "1"), ("scan_b", "2"), ("scan_c", "3")])
        results = db.scan(1, "scan_", "scan_\xff")
        keys = sorted([k for k, v in results])
        assert "scan_a" in keys
        assert "scan_b" in keys
        assert "scan_c" in keys


class TestStats:
    def test_stats(self, db):
        stats = db.stats()
        assert "key_count" in stats
        assert "engine" in stats
        assert "size_bytes" in stats


class TestSql:
    def test_execute_sql(self, db):
        result = db.execute_sql("SELECT 1 as id, 'hello' as name")
        assert result is not None
        assert "columns" in result
        assert "rows" in result


class TestFts:
    def test_fts_insert_search(self, db):
        db.fts_insert(1, "Hello world")
        db.fts_insert(2, "資料庫系統")
        doc_ids = db.fts_search("Hello")
        assert 1 in doc_ids

    def test_fts_search_chinese(self, db):
        db.fts_insert(10, "資料庫系統")
        doc_ids = db.fts_search("資料庫")
        assert 10 in doc_ids

    def test_fts_search_bm25(self, db):
        db.fts_insert(20, "hello world database")
        db.fts_insert(21, "hello hello database database")
        results = db.fts_search_bm25("hello database")
        assert results is not None
        assert isinstance(results, list)


class TestQueue:
    def test_queue_operations(self, db):
        queue_name = "test_queue_py"
        db.queue_create(queue_name)
        result = db.queue_enqueue(queue_name, "test_payload", 30)
        assert result is not None
        assert "msg_id" in result or "status" in result


class TestPubSub:
    def test_pubsub_publish(self, db):
        result = db.pubsub_publish("test_channel", "test_message")
        assert result is not None