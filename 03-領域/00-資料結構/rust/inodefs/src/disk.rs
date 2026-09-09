use std::fs::{File, OpenOptions};
use std::io::{Read, Seek, SeekFrom, Write};
use std::path::Path;

use crate::error::{Error, Result};

pub const BLOCK_SIZE: u32 = 1024;
pub const DISK_SIZE: u32 = 1024 * 1024; // 1MB
pub const TOTAL_BLOCKS: u32 = DISK_SIZE / BLOCK_SIZE;

pub struct Disk {
    file: File,
    path: std::path::PathBuf,
}

impl Disk {
    pub fn create(path: &Path) -> Result<Self> {
        let file = OpenOptions::new()
            .create(true)
            .write(true)
            .read(true)
            .truncate(true)
            .open(path)?;

        let mut disk = Self {
            file,
            path: path.to_path_buf(),
        };
        disk.zero_fill()?;
        Ok(disk)
    }

    pub fn open(path: &Path) -> Result<Self> {
        let file = OpenOptions::new()
            .create(true)
            .write(true)
            .read(true)
            .open(path)?;

        Ok(Self {
            file,
            path: path.to_path_buf(),
        })
    }

    fn zero_fill(&mut self) -> Result<()> {
        let zeros = vec![0u8; BLOCK_SIZE as usize];
        for _ in 0..TOTAL_BLOCKS {
            self.file.write_all(&zeros)?;
        }
        self.file.flush()?;
        Ok(())
    }

    pub fn read_block(&mut self, block_num: u32) -> Result<Vec<u8>> {
        let offset = (block_num as u64) * (BLOCK_SIZE as u64);
        self.file.seek(SeekFrom::Start(offset))?;
        let mut buf = vec![0u8; BLOCK_SIZE as usize];
        self.file.read_exact(&mut buf)?;
        Ok(buf)
    }

    pub fn write_block(&mut self, block_num: u32, data: &[u8]) -> Result<()> {
        if data.len() != BLOCK_SIZE as usize {
            return Err(Error::Io(format!(
                "Block size must be {}, got {}",
                BLOCK_SIZE,
                data.len()
            )));
        }
        let offset = (block_num as u64) * (BLOCK_SIZE as u64);
        self.file.seek(SeekFrom::Start(offset))?;
        self.file.write_all(data)?;
        Ok(())
    }

    pub fn sync(&mut self) -> Result<()> {
        self.file.flush()?;
        Ok(())
    }

    pub fn path(&self) -> &Path {
        &self.path
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_disk_create_and_read() {
        let path = std::env::temp_dir().join("test_disk.img");
        std::fs::remove_file(&path).ok();

        {
            let disk = Disk::create(&path).unwrap();
            assert_eq!(disk.path, path);
        }

        {
            let mut disk = Disk::open(&path).unwrap();
            let block = disk.read_block(0).unwrap();
            assert_eq!(block.len(), BLOCK_SIZE as usize);
            assert!(block.iter().all(|&b| b == 0));
        }

        std::fs::remove_file(&path).ok();
    }

    #[test]
    fn test_disk_write_and_read_block() {
        let path = std::env::temp_dir().join("test_disk2.img");
        std::fs::remove_file(&path).ok();

        {
            let mut disk = Disk::create(&path).unwrap();
            let mut data = vec![0u8; BLOCK_SIZE as usize];
            data[0] = 0xDE;
            data[1] = 0xAD;
            data[2] = 0xBE;
            data[3] = 0xEF;

            disk.write_block(5, &data).unwrap();
        }

        {
            let mut disk = Disk::open(&path).unwrap();
            let block = disk.read_block(5).unwrap();
            assert_eq!(block[0], 0xDE);
            assert_eq!(block[1], 0xAD);
            assert_eq!(block[2], 0xBE);
            assert_eq!(block[3], 0xEF);
        }

        std::fs::remove_file(&path).ok();
    }
}