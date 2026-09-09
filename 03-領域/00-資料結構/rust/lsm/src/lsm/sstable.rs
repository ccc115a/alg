use std::collections::BTreeMap;
use std::fs::{File, OpenOptions};
use std::io::{Read, Write};
use std::path::Path;

use crate::error::{Error, Result};

pub struct SSTable {
    path: std::path::PathBuf,
    data: BTreeMap<Vec<u8>, Vec<u8>>,
}

impl SSTable {
    pub fn create(path: &Path, data: Vec<(Vec<u8>, Vec<u8>)>) -> Result<Self> {
        let mut ss = Self {
            path: path.to_path_buf(),
            data: BTreeMap::new(),
        };

        for (k, v) in data {
            ss.data.insert(k, v);
        }

        ss.write_to_disk()?;
        Ok(ss)
    }

    pub fn open(path: &Path) -> Result<Self> {
        if !path.exists() {
            return Ok(Self {
                path: path.to_path_buf(),
                data: BTreeMap::new(),
            });
        }

        let mut file = File::open(path)?;
        let mut contents = Vec::new();
        file.read_to_end(&mut contents)?;

        let data: BTreeMap<Vec<u8>, Vec<u8>> =
            match bincode::deserialize(&contents) {
                Ok(d) => d,
                Err(_) => BTreeMap::new(),
            };

        Ok(Self {
            path: path.to_path_buf(),
            data,
        })
    }

    fn write_to_disk(&self) -> Result<()> {
        let mut file = OpenOptions::new()
            .create(true)
            .write(true)
            .truncate(true)
            .open(&self.path)?;

        let data =
            bincode::serialize(&self.data).map_err(|e| Error::Sql(format!("bincode: {:?}", e)))?;

        file.write_all(&data)?;
        Ok(())
    }

    pub fn get(&self, key: &[u8]) -> Option<Vec<u8>> {
        self.data.get(key).cloned()
    }

    pub fn scan(&self, start: &[u8], end: &[u8]) -> Vec<(Vec<u8>, Vec<u8>)> {
        let start = if start.is_empty() {
            None
        } else {
            Some(start.to_vec())
        };
        let end = if end.is_empty() { None } else { Some(end.to_vec()) };

        match (start, end) {
            (None, None) => {
                self.data.iter().map(|(k, v)| (k.clone(), v.clone())).collect()
            }
            (Some(s), None) => self
                .data
                .range(s..)
                .map(|(k, v)| (k.clone(), v.clone()))
                .collect(),
            (None, Some(e)) => self
                .data
                .range(..e)
                .map(|(k, v)| (k.clone(), v.clone()))
                .collect(),
            (Some(s), Some(e)) => self
                .data
                .range(s..e)
                .map(|(k, v)| (k.clone(), v.clone()))
                .collect(),
        }
    }

    pub fn len(&self) -> u64 {
        self.data.len() as u64
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;

    #[test]
    fn test_sstable_create_and_get() {
        let path = std::env::temp_dir().join("test_sstable.sst");
        fs::remove_file(&path).ok();

        let data = vec![
            (b"key1".to_vec(), b"value1".to_vec()),
            (b"key2".to_vec(), b"value2".to_vec()),
        ];
        let ss = SSTable::create(&path, data).unwrap();

        assert_eq!(ss.get(b"key1"), Some(b"value1".to_vec()));
        assert_eq!(ss.get(b"key2"), Some(b"value2".to_vec()));
        assert_eq!(ss.get(b"missing"), None);

        fs::remove_file(&path).ok();
    }

    #[test]
    fn test_sstable_persistence() {
        let path = std::env::temp_dir().join("test_sstable_persist.sst");
        fs::remove_file(&path).ok();

        {
            let data = vec![
                (b"a".to_vec(), b"1".to_vec()),
                (b"b".to_vec(), b"2".to_vec()),
            ];
            SSTable::create(&path, data).unwrap();
        }

        {
            let ss = SSTable::open(&path).unwrap();
            assert_eq!(ss.get(b"a"), Some(b"1".to_vec()));
            assert_eq!(ss.get(b"b"), Some(b"2".to_vec()));
        }

        fs::remove_file(&path).ok();
    }

    #[test]
    fn test_sstable_scan() {
        let path = std::env::temp_dir().join("test_sstable_scan.sst");
        fs::remove_file(&path).ok();

        let data = vec![
            (b"a".to_vec(), b"1".to_vec()),
            (b"b".to_vec(), b"2".to_vec()),
            (b"c".to_vec(), b"3".to_vec()),
        ];
        SSTable::create(&path, data).unwrap();

        let ss = SSTable::open(&path).unwrap();
        let results = ss.scan(b"a", b"c");
        assert_eq!(results.len(), 2);

        fs::remove_file(&path).ok();
    }

    #[test]
    fn test_sstable_len() {
        let path = std::env::temp_dir().join("test_sstable_len.sst");
        fs::remove_file(&path).ok();

        let data = vec![
            (b"a".to_vec(), b"1".to_vec()),
            (b"b".to_vec(), b"2".to_vec()),
        ];
        let ss = SSTable::create(&path, data).unwrap();
        assert_eq!(ss.len(), 2);

        fs::remove_file(&path).ok();
    }
}