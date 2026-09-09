use super::node::{Key, Node, Record};
use crate::pager::storage::Storage;

pub struct BPlusTree<S: Storage> {
    order: usize,
    storage: S,
    root: usize,
    size: usize,
}

impl<S: Storage> BPlusTree<S> {
    pub fn new(order: usize, mut storage: S) -> Self {
        assert!(order >= 3, "B+Tree order must be >= 3");
        let root_id = storage.alloc_page();
        storage.write_node(root_id, &Node::new_leaf());
        BPlusTree { order, storage, root: root_id, size: 0 }
    }

    pub fn open(order: usize, storage: S, root: usize, size: usize) -> Self {
        BPlusTree { order, storage, root, size }
    }

    pub fn insert(&mut self, key: Key, value: Vec<u8>) {
        let record = Record { key, value };
        if let Some(split) = self.insert_recursive(self.root, record) {
            let mut new_root = Node::new_internal();
            new_root.keys.push(split.0);
            new_root.children.push(self.root);
            new_root.children.push(split.1);
            let new_root_id = self.storage.alloc_page();
            self.storage.write_node(new_root_id, &new_root);
            self.root = new_root_id;
        }
        self.size += 1;
    }

    pub fn search(&mut self, key: &Key) -> Option<Vec<u8>> {
        let leaf_id = self.find_leaf(self.root, key);
        let leaf = self.storage.read_node(leaf_id);
        leaf.records.into_iter().find(|r| &r.key == key).map(|r| r.value)
    }

    pub fn range_search(&mut self, start: &Key, end: &Key) -> Vec<Record> {
        let mut results = Vec::new();
        let mut idx = self.find_leaf(self.root, start);
        loop {
            let leaf = self.storage.read_node(idx);
            let next = leaf.next_leaf;
            let mut done = false;
            for record in leaf.records {
                if &record.key >= start && &record.key <= end {
                    results.push(record);
                } else if &record.key > end {
                    done = true; break;
                }
            }
            if done { break; }
            match next { Some(n) => idx = n, None => break }
        }
        results
    }

    pub fn delete(&mut self, key: &Key) -> bool {
        let removed = self.delete_recursive(self.root, key);
        if removed {
            self.size -= 1;
            let root_node = self.storage.read_node(self.root);
            if !root_node.is_leaf() && root_node.keys.is_empty() {
                self.root = root_node.children[0];
            }
        }
        removed
    }

    pub fn len(&self) -> usize { self.size }
    pub fn is_empty(&self) -> bool { self.size == 0 }
    pub fn root_page(&self) -> usize { self.root }
    pub fn flush(&mut self) { self.storage.flush(); }

    fn alloc_node(&mut self, node: Node) -> usize {
        let id = self.storage.alloc_page();
        self.storage.write_node(id, &node);
        id
    }

    fn find_leaf(&mut self, mut idx: usize, key: &Key) -> usize {
        loop {
            let node = self.storage.read_node(idx);
            if node.is_leaf() { return idx; }
            let pos = node.keys.partition_point(|k| k <= key);
            idx = node.children[pos];
        }
    }

    fn insert_recursive(&mut self, idx: usize, record: Record) -> Option<(Key, usize)> {
        let node = self.storage.read_node(idx);
        if node.is_leaf() {
            return self.insert_into_leaf(idx, node, record);
        }
        let pos = node.keys.partition_point(|k| k <= &record.key);
        let child_idx = node.children[pos];
        if let Some((mid_key, new_child)) = self.insert_recursive(child_idx, record) {
            let mut node = self.storage.read_node(idx);
            node.keys.insert(pos, mid_key);
            node.children.insert(pos + 1, new_child);
            let full = node.is_full(self.order);
            self.storage.write_node(idx, &node);
            if full { return Some(self.split_internal(idx)); }
        }
        None
    }

    fn insert_into_leaf(&mut self, idx: usize, mut leaf: Node, record: Record) -> Option<(Key, usize)> {
        let pos = leaf.keys.partition_point(|k| k < &record.key);
        if pos < leaf.keys.len() && leaf.keys[pos] == record.key {
            leaf.records[pos] = record;
            self.storage.write_node(idx, &leaf);
            self.size = self.size.saturating_sub(1);
            return None;
        }
        leaf.keys.insert(pos, record.key.clone());
        leaf.records.insert(pos, record);
        let full = leaf.is_full(self.order);
        self.storage.write_node(idx, &leaf);
        if full { return Some(self.split_leaf(idx)); }
        None
    }

    fn split_leaf(&mut self, idx: usize) -> (Key, usize) {
        let mut left = self.storage.read_node(idx);
        let mid = left.keys.len() / 2;
        let right_keys = left.keys.split_off(mid);
        let right_records = left.records.split_off(mid);
        let old_next = left.next_leaf;
        let promote_key = right_keys[0].clone();
        let mut right = Node::new_leaf();
        right.keys = right_keys;
        right.records = right_records;
        let right_id = self.storage.alloc_page();
        right.next_leaf = old_next;
        left.next_leaf = Some(right_id);
        self.storage.write_node(idx, &left);
        self.storage.write_node(right_id, &right);
        (promote_key, right_id)
    }

    fn split_internal(&mut self, idx: usize) -> (Key, usize) {
        let mut left = self.storage.read_node(idx);
        let mid = left.keys.len() / 2;
        let promote_key = left.keys.remove(mid);
        let right_keys = left.keys.split_off(mid);
        let right_children = left.children.split_off(mid + 1);
        let mut right = Node::new_internal();
        right.keys = right_keys;
        right.children = right_children;
        let right_id = self.storage.alloc_page();
        self.storage.write_node(idx, &left);
        self.storage.write_node(right_id, &right);
        (promote_key, right_id)
    }

    fn delete_recursive(&mut self, idx: usize, key: &Key) -> bool {
        let node = self.storage.read_node(idx);
        if node.is_leaf() { return self.delete_from_leaf(idx, node, key); }
        let pos = node.keys.partition_point(|k| k <= key);
        let child_idx = node.children[pos];
        if !self.delete_recursive(child_idx, key) { return false; }
        let min_keys = (self.order - 1) / 2;
        let child = self.storage.read_node(child_idx);
        if child.keys.len() < min_keys { self.rebalance(idx, pos); }
        true
    }

    fn delete_from_leaf(&mut self, idx: usize, mut leaf: Node, key: &Key) -> bool {
        if let Some(pos) = leaf.keys.iter().position(|k| k == key) {
            leaf.keys.remove(pos);
            leaf.records.remove(pos);
            self.storage.write_node(idx, &leaf);
            true
        } else { false }
    }

    fn rebalance(&mut self, parent: usize, pos: usize) {
        let parent_node = self.storage.read_node(parent);
        let n_children = parent_node.children.len();
        let min_keys = (self.order - 1) / 2;
        if pos + 1 < n_children {
            let right_sib = parent_node.children[pos + 1];
            if self.storage.read_node(right_sib).keys.len() > min_keys {
                self.borrow_from_right(parent, pos); return;
            }
        }
        if pos > 0 {
            let left_sib = parent_node.children[pos - 1];
            if self.storage.read_node(left_sib).keys.len() > min_keys {
                self.borrow_from_left(parent, pos); return;
            }
        }
        if pos + 1 < n_children { self.merge(parent, pos); }
        else { self.merge(parent, pos - 1); }
    }

    fn borrow_from_right(&mut self, parent: usize, pos: usize) {
        let mut pn = self.storage.read_node(parent);
        let cid = pn.children[pos];
        let rid = pn.children[pos + 1];
        let mut child = self.storage.read_node(cid);
        let mut right = self.storage.read_node(rid);
        if child.is_leaf() {
            let bk = right.keys.remove(0);
            let br = right.records.remove(0);
            pn.keys[pos] = right.keys[0].clone();
            child.keys.push(bk); child.records.push(br);
        } else {
            let sep = pn.keys[pos].clone();
            let ns = right.keys.remove(0);
            let bc = right.children.remove(0);
            pn.keys[pos] = ns; child.keys.push(sep); child.children.push(bc);
        }
        self.storage.write_node(parent, &pn);
        self.storage.write_node(cid, &child);
        self.storage.write_node(rid, &right);
    }

    fn borrow_from_left(&mut self, parent: usize, pos: usize) {
        let mut pn = self.storage.read_node(parent);
        let cid = pn.children[pos];
        let lid = pn.children[pos - 1];
        let mut child = self.storage.read_node(cid);
        let mut left = self.storage.read_node(lid);
        if child.is_leaf() {
            let lk = left.keys.pop().unwrap();
            let lr = left.records.pop().unwrap();
            pn.keys[pos - 1] = lk.clone();
            child.keys.insert(0, lk); child.records.insert(0, lr);
        } else {
            let sep = pn.keys[pos - 1].clone();
            let ns = left.keys.pop().unwrap();
            let bc = left.children.pop().unwrap();
            pn.keys[pos - 1] = ns; child.keys.insert(0, sep); child.children.insert(0, bc);
        }
        self.storage.write_node(parent, &pn);
        self.storage.write_node(cid, &child);
        self.storage.write_node(lid, &left);
    }

    fn merge(&mut self, parent: usize, left_pos: usize) {
        let mut pn = self.storage.read_node(parent);
        let lid = pn.children[left_pos];
        let rid = pn.children[left_pos + 1];
        let mut left = self.storage.read_node(lid);
        let right = self.storage.read_node(rid);
        if left.is_leaf() {
            left.keys.extend(right.keys); left.records.extend(right.records);
            left.next_leaf = right.next_leaf;
        } else {
            let sep = pn.keys[left_pos].clone();
            left.keys.push(sep); left.keys.extend(right.keys);
            left.children.extend(right.children);
        }
        pn.keys.remove(left_pos); pn.children.remove(left_pos + 1);
        self.storage.write_node(lid, &left);
        self.storage.write_node(parent, &pn);
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::pager::storage::MemoryStorage;

    fn int_key(v: i64) -> Key { Key::Integer(v) }
    fn val(s: &str) -> Vec<u8> { s.as_bytes().to_vec() }
    fn new_tree() -> BPlusTree<MemoryStorage> { BPlusTree::new(4, MemoryStorage::new()) }

    #[test]
    fn test_insert_and_search() {
        let mut tree = new_tree();
        tree.insert(int_key(10), val("Alice"));
        tree.insert(int_key(20), val("Bob"));
        tree.insert(int_key(5),  val("Carol"));
        assert_eq!(tree.search(&int_key(10)), Some(b"Alice".to_vec()));
        assert_eq!(tree.search(&int_key(20)), Some(b"Bob".to_vec()));
        assert_eq!(tree.search(&int_key(5)),  Some(b"Carol".to_vec()));
        assert_eq!(tree.search(&int_key(99)), None);
    }

    #[test]
    fn test_insert_many_triggers_split() {
        let mut tree = new_tree();
        for i in 0..20i64 { tree.insert(int_key(i), val("x")); }
        assert_eq!(tree.len(), 20);
        for i in 0..20i64 { assert!(tree.search(&int_key(i)).is_some(), "key {} missing", i); }
    }

    #[test]
    fn test_range_search() {
        let mut tree = new_tree();
        for i in 1..=10i64 { tree.insert(int_key(i), val("v")); }
        let result = tree.range_search(&int_key(3), &int_key(7));
        let keys: Vec<i64> = result.iter().map(|r| match r.key { Key::Integer(v) => v, _ => panic!() }).collect();
        assert_eq!(keys, vec![3, 4, 5, 6, 7]);
    }

    #[test]
    fn test_delete() {
        let mut tree = new_tree();
        for i in 1..=10i64 { tree.insert(int_key(i), val("v")); }
        assert!(tree.delete(&int_key(5)));
        assert_eq!(tree.search(&int_key(5)), None);
        assert_eq!(tree.len(), 9);
        assert!(!tree.delete(&int_key(99)));
    }

    #[test]
    fn test_update() {
        let mut tree = new_tree();
        tree.insert(int_key(1), val("old"));
        tree.insert(int_key(1), val("new"));
        assert_eq!(tree.search(&int_key(1)), Some(b"new".to_vec()));
        assert_eq!(tree.len(), 1);
    }

    #[test]
    fn test_text_key() {
        let mut tree = new_tree();
        tree.insert(Key::Text("banana".into()), val("fruit"));
        tree.insert(Key::Text("apple".into()),  val("also fruit"));
        assert_eq!(tree.search(&Key::Text("banana".into())), Some(b"fruit".to_vec()));
    }

    #[test]
    fn test_disk_storage_persist() {
        use crate::pager::storage::DiskStorage;
        let path = "/tmp/sql4_btree_test.sql4db";
        let _ = std::fs::remove_file(path);
        let root_page;
        {
            let store = DiskStorage::open(path).unwrap();
            let mut tree = BPlusTree::new(4, store);
            for i in 1..=5i64 { tree.insert(int_key(i), val("persisted")); }
            root_page = tree.root_page();
            tree.flush();
        }
        {
            let store = DiskStorage::open(path).unwrap();
            let mut tree = BPlusTree::open(4, store, root_page, 5);
            for i in 1..=5i64 {
                assert_eq!(tree.search(&int_key(i)), Some(b"persisted".to_vec()), "key {} missing after reopen", i);
            }
        }
        let _ = std::fs::remove_file(path);
    }
}
