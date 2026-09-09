use std::collections::BTreeMap;

#[derive(Clone, Debug)]
pub enum Value {
    Data(Vec<u8>),
    Tombstone,
}

impl Value {
    pub fn is_data(&self) -> bool {
        matches!(self, Value::Data(_))
    }

    pub fn get_data(&self) -> Option<&Vec<u8>> {
        match self {
            Value::Data(v) => Some(v),
            Value::Tombstone => None,
        }
    }
}

pub struct MemTable {
    map: BTreeMap<Vec<u8>, Value>,
}

impl MemTable {
    pub fn new() -> Self {
        Self {
            map: BTreeMap::new(),
        }
    }

    pub fn put(&mut self, key: Vec<u8>, value: Vec<u8>) {
        self.map.insert(key, Value::Data(value));
    }

    pub fn delete(&mut self, key: Vec<u8>) {
        self.map.insert(key, Value::Tombstone);
    }

    pub fn get(&self, key: &[u8]) -> Option<&Value> {
        self.map.get(key)
    }

    pub fn scan(&self, start: &[u8], end: &[u8]) -> Vec<(Vec<u8>, Vec<u8>)> {
        let start = if start.is_empty() {
            None
        } else {
            Some(start.to_vec())
        };
        let end = if end.is_empty() { None } else { Some(end.to_vec()) };

        match (start, end) {
            (None, None) => self
                .map
                .iter()
                .filter(|(_, v)| v.is_data())
                .map(|(k, v)| (k.clone(), v.get_data().unwrap().clone()))
                .collect(),
            (Some(s), None) => self
                .map
                .range(s..)
                .filter(|(_, v)| v.is_data())
                .map(|(k, v)| (k.clone(), v.get_data().unwrap().clone()))
                .collect(),
            (None, Some(e)) => self
                .map
                .range(..e)
                .filter(|(_, v)| v.is_data())
                .map(|(k, v)| (k.clone(), v.get_data().unwrap().clone()))
                .collect(),
            (Some(s), Some(e)) => self
                .map
                .range(s..e)
                .filter(|(_, v)| v.is_data())
                .map(|(k, v)| (k.clone(), v.get_data().unwrap().clone()))
                .collect(),
        }
    }

    pub fn len(&self) -> usize {
        self.map.len()
    }

    pub fn all_data(&self) -> Vec<(Vec<u8>, Vec<u8>)> {
        self.map
            .iter()
            .filter(|(_, v)| v.is_data())
            .map(|(k, v)| (k.clone(), v.get_data().unwrap().clone()))
            .collect()
    }

    pub fn clear(&mut self) {
        self.map.clear();
    }
}

impl Default for MemTable {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_memtable_put_get() {
        let mut mem = MemTable::new();
        mem.put(b"key1".to_vec(), b"value1".to_vec());
        mem.put(b"key2".to_vec(), b"value2".to_vec());

        assert_eq!(mem.get(b"key1").unwrap().get_data(), Some(&b"value1".to_vec()));
        assert_eq!(mem.get(b"key2").unwrap().get_data(), Some(&b"value2".to_vec()));
    }

    #[test]
    fn test_memtable_delete() {
        let mut mem = MemTable::new();
        mem.put(b"key1".to_vec(), b"value1".to_vec());
        mem.delete(b"key1".to_vec());

        assert!(!mem.get(b"key1").unwrap().is_data());
    }

    #[test]
    fn test_memtable_scan() {
        let mut mem = MemTable::new();
        mem.put(b"a".to_vec(), b"1".to_vec());
        mem.put(b"b".to_vec(), b"2".to_vec());
        mem.put(b"c".to_vec(), b"3".to_vec());

        let results = mem.scan(b"a", b"c");
        assert_eq!(results.len(), 2);
    }

    #[test]
    fn test_memtable_overwrite() {
        let mut mem = MemTable::new();
        mem.put(b"key".to_vec(), b"value1".to_vec());
        mem.put(b"key".to_vec(), b"value2".to_vec());

        assert_eq!(mem.get(b"key").unwrap().get_data(), Some(&b"value2".to_vec()));
    }

    #[test]
    fn test_memtable_len() {
        let mut mem = MemTable::new();
        assert_eq!(mem.len(), 0);
        mem.put(b"a".to_vec(), b"1".to_vec());
        mem.put(b"b".to_vec(), b"2".to_vec());
        assert_eq!(mem.len(), 2);
    }
}