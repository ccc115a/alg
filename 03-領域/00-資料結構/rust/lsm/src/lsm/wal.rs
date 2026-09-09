use std::fs::{File, OpenOptions};
use std::io::{Read, Write};
use std::path::Path;

use crate::error::Result;

pub struct Wal {
    path: std::path::PathBuf,
    file: File,
}

impl Wal {
    pub fn create(path: &Path) -> Result<Self> {
        let file = OpenOptions::new()
            .create(true)
            .write(true)
            .append(true)
            .open(path)?;

        Ok(Self {
            path: path.to_path_buf(),
            file,
        })
    }

    pub fn open(path: &Path) -> Result<Self> {
        let file = OpenOptions::new()
            .create(true)
            .write(true)
            .append(true)
            .open(path)?;

        Ok(Self {
            path: path.to_path_buf(),
            file,
        })
    }

    pub fn write(&self, key: &[u8], value: &[u8]) -> Result<()> {
        let mut file = OpenOptions::new()
            .write(true)
            .append(true)
            .open(&self.path)?;

        let len = key.len() as u32;
        file.write_all(&len.to_le_bytes())?;
        file.write_all(key)?;

        let len = value.len() as u32;
        file.write_all(&len.to_le_bytes())?;
        file.write_all(value)?;

        Ok(())
    }

    pub fn recover(&self) -> Result<Vec<(Vec<u8>, Vec<u8>)>> {
        let mut file = File::open(&self.path)?;
        let mut results = Vec::new();

        loop {
            let mut len_buf = [0u8; 4];
            match file.read_exact(&mut len_buf) {
                Ok(_) => {}
                Err(_) => break,
            }

            let key_len = u32::from_le_bytes(len_buf) as usize;
            let mut key = vec![0u8; key_len];
            file.read_exact(&mut key)?;

            let mut len_buf = [0u8; 4];
            file.read_exact(&mut len_buf)?;
            let val_len = u32::from_le_bytes(len_buf) as usize;
            let mut value = vec![0u8; val_len];
            file.read_exact(&mut value)?;

            results.push((key, value));
        }

        Ok(results)
    }

    pub fn clear(&self) -> Result<()> {
        let file = OpenOptions::new()
            .write(true)
            .truncate(true)
            .open(&self.path)?;
        drop(file);
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;

    #[test]
    fn test_wal_write_and_recover() {
        let path = std::env::temp_dir().join("test_wal.log");
        fs::remove_file(&path).ok();

        {
            let wal = Wal::create(&path).unwrap();
            wal.write(b"key1", b"value1").unwrap();
            wal.write(b"key2", b"value2").unwrap();
        }

        {
            let wal = Wal::open(&path).unwrap();
            let data = wal.recover().unwrap();
            assert_eq!(data.len(), 2);
            assert_eq!(&data[0].0, b"key1");
            assert_eq!(&data[0].1, b"value1");
        }

        fs::remove_file(&path).ok();
    }

    #[test]
    fn test_wal_clear() {
        let path = std::env::temp_dir().join("test_wal_clear.log");
        fs::remove_file(&path).ok();

        {
            let wal = Wal::create(&path).unwrap();
            wal.write(b"key1", b"value1").unwrap();
            wal.clear().unwrap();
        }

        {
            let wal = Wal::open(&path).unwrap();
            let data = wal.recover().unwrap();
            assert_eq!(data.len(), 0);
        }

        fs::remove_file(&path).ok();
    }
}