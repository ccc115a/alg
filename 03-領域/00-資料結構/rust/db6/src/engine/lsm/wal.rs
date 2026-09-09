//! WAL — Write-Ahead Log
//!
//! WAL is the reliability guarantee mechanism for LSM-Tree. Following ARIES algorithm principles,
//! data must be written to WAL before being written to MemTable.
//!
//! On crash, data not yet flushed to SSTable can be recovered from WAL on restart.
//!
//! ## Log format
//!
//! Each log entry is stored in TLV (Type-Length-Value) format:
//! ```text
//! [key_len: u32][key: key_len bytes][value_len: u32][value: value_len bytes]
//! ```

use std::fs::{File, OpenOptions};
use std::io::{Read, Write};
use std::path::Path;

use crate::error::Result;

/// WAL structure
///
/// Each LSM engine instance corresponds to one `wal.log` file.
pub struct Wal {
    /// WAL file path
    path: std::path::PathBuf,
    /// File handle
    file: File,
}

impl Wal {
    /// Create a new WAL (append mode)
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

    /// Open an existing WAL
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

    /// Write a log entry
    ///
    /// Format: `[key_len:4bytes][key][value_len:4bytes][value]`
    pub fn write(&self, key: &[u8], value: &[u8]) -> Result<()> {
        let mut file = OpenOptions::new()
            .write(true)
            .append(true)
            .open(&self.path)?;

        // 寫入鍵的長度與內容
        let len = key.len() as u32;
        file.write_all(&len.to_le_bytes())?;
        file.write_all(key)?;

        // 寫入值的長度與內容
        let len = value.len() as u32;
        file.write_all(&len.to_le_bytes())?;
        file.write_all(value)?;

        Ok(())
    }

    /// Recover all unflushed data from WAL
    ///
    /// Read all records from WAL and return as a list of key-value pairs.
    pub fn recover(&self) -> Result<Vec<(Vec<u8>, Vec<u8>)>> {
        let mut file = File::open(&self.path)?;
        let mut results = Vec::new();

        // 依序讀取每一組 [key_len][key][value_len][value]
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

    /// Clear WAL content (called after data has been flushed to SSTable)
    pub fn clear(&self) -> Result<()> {
        let file = OpenOptions::new()
            .write(true)
            .truncate(true)
            .open(&self.path)?;
        drop(file);
        Ok(())
    }
}