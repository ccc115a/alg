//! WAL（Write-Ahead Log）預寫日誌

use std::collections::HashMap;
use std::fs::{File, OpenOptions};
use std::io::{Read, Seek, SeekFrom, Write};
use std::path::{Path, PathBuf};

use crate::codec::PAGE_SIZE;

const WAL_MAGIC: &[u8; 8] = b"SQL4WAL\0";
const WAL_VERSION: u32 = 1;
const WAL_HEADER_SIZE: usize = 32;
const FRAME_HEADER_SIZE: usize = 24;
const FRAME_SIZE: usize = FRAME_HEADER_SIZE + PAGE_SIZE;

const FRAME_TYPE_DATA: u32 = 1;
const FRAME_TYPE_COMMIT: u32 = 2;

const CHECKPOINT_THRESHOLD: usize = 100;

#[derive(Debug, Clone)]
struct Frame {
    page_id: u32,
    frame_type: u32,
    txn_id: u32,
    checksum: u32,
    data: Vec<u8>,
}

impl Frame {
    fn encode(&self) -> Vec<u8> {
        let mut buf = Vec::with_capacity(FRAME_SIZE);
        buf.extend_from_slice(&self.page_id.to_le_bytes());
        buf.extend_from_slice(&self.frame_type.to_le_bytes());
        buf.extend_from_slice(&self.txn_id.to_le_bytes());
        buf.extend_from_slice(&self.checksum.to_le_bytes());
        buf.extend_from_slice(&[0u8; 8]);
        buf.extend_from_slice(&self.data);
        buf
    }

    fn decode(buf: &[u8]) -> Option<Frame> {
        if buf.len() < FRAME_SIZE {
            return None;
        }
        let page_id = u32::from_le_bytes(buf[0..4].try_into().ok()?);
        let frame_type = u32::from_le_bytes(buf[4..8].try_into().ok()?);
        let txn_id = u32::from_le_bytes(buf[8..12].try_into().ok()?);
        let checksum = u32::from_le_bytes(buf[12..16].try_into().ok()?);
        let data = buf[FRAME_HEADER_SIZE..FRAME_SIZE].to_vec();

        let actual = compute_checksum(&data);
        if actual != checksum {
            return None;
        }

        Some(Frame {
            page_id,
            frame_type,
            txn_id,
            checksum,
            data,
        })
    }
}

fn compute_checksum(data: &[u8]) -> u32 {
    data.chunks(4).fold(0u32, |acc, chunk| {
        let mut word = [0u8; 4];
        word[..chunk.len()].copy_from_slice(chunk);
        acc ^ u32::from_le_bytes(word)
    })
}

fn write_wal_header(file: &mut File, frame_count: u32) -> std::io::Result<()> {
    let mut hdr = vec![0u8; WAL_HEADER_SIZE];
    hdr[0..8].copy_from_slice(WAL_MAGIC);
    hdr[8..12].copy_from_slice(&WAL_VERSION.to_le_bytes());
    hdr[12..16].copy_from_slice(&(PAGE_SIZE as u32).to_le_bytes());
    hdr[16..20].copy_from_slice(&frame_count.to_le_bytes());
    file.seek(SeekFrom::Start(0))?;
    file.write_all(&hdr)?;
    file.flush()
}

fn read_wal_frame_count(file: &mut File) -> std::io::Result<u32> {
    let mut hdr = vec![0u8; WAL_HEADER_SIZE];
    file.seek(SeekFrom::Start(0))?;
    file.read_exact(&mut hdr)?;
    if &hdr[0..8] != WAL_MAGIC {
        return Ok(0);
    }
    Ok(u32::from_le_bytes(hdr[16..20].try_into().unwrap()))
}

pub struct Wal {
    wal_path: PathBuf,
    wal_file: File,
    frame_count: usize,
    committed: HashMap<u32, Vec<u8>>,
    dirty: HashMap<u32, Vec<u8>>,
    next_txn_id: u32,
    in_txn: bool,
}

impl Wal {
    pub fn open<P: AsRef<Path>>(db_path: P) -> std::io::Result<Self> {
        let db_path = db_path.as_ref();
        let wal_path = db_path.with_extension("sql4wal");

        let wal_exists = wal_path.exists();
        let wal_file = OpenOptions::new()
            .read(true)
            .write(true)
            .create(true)
            .open(&wal_path)?;

        let mut wal = Wal {
            wal_path,
            wal_file,
            frame_count: 0,
            committed: HashMap::new(),
            dirty: HashMap::new(),
            next_txn_id: 1,
            in_txn: false,
        };

        if wal_exists {
            wal.replay()?;
        } else {
            write_wal_header(&mut wal.wal_file, 0)?;
        }

        Ok(wal)
    }

    pub fn begin(&mut self) {
        self.dirty.clear();
        self.in_txn = true;
    }

    pub fn commit(&mut self) -> std::io::Result<()> {
        if !self.in_txn {
            return Ok(());
        }
        let txn_id = self.next_txn_id;
        self.next_txn_id += 1;

        let dirty_pages: Vec<(u32, Vec<u8>)> =
            self.dirty.iter().map(|(k, v)| (*k, v.clone())).collect();
        for (page_id, data) in &dirty_pages {
            self.write_frame(*page_id, FRAME_TYPE_DATA, txn_id, data)?;
        }

        let commit_data = vec![0u8; PAGE_SIZE];
        self.write_frame(u32::MAX, FRAME_TYPE_COMMIT, txn_id, &commit_data)?;

        for (page_id, data) in self.dirty.drain() {
            self.committed.insert(page_id, data);
        }

        self.in_txn = false;
        Ok(())
    }

    pub fn rollback(&mut self) {
        self.dirty.clear();
        self.in_txn = false;
    }

    pub fn read_page(&self, page_id: u32) -> Option<&[u8]> {
        self.dirty
            .get(&page_id)
            .or_else(|| self.committed.get(&page_id))
            .map(|v| v.as_slice())
    }

    pub fn write_page(&mut self, page_id: u32, data: Vec<u8>) {
        if self.in_txn {
            self.dirty.insert(page_id, data);
        } else {
            self.committed.insert(page_id, data.clone());
            let txn_id = self.next_txn_id;
            self.next_txn_id += 1;
            let _ = self.write_frame(page_id, FRAME_TYPE_DATA, txn_id, &data);
            let commit_data = vec![0u8; PAGE_SIZE];
            let _ = self.write_frame(u32::MAX, FRAME_TYPE_COMMIT, txn_id, &commit_data);
        }
    }

    pub fn needs_checkpoint(&self) -> bool {
        self.frame_count >= CHECKPOINT_THRESHOLD
    }

    pub fn checkpoint<F>(&mut self, mut write_back: F) -> std::io::Result<()>
    where
        F: FnMut(u32, &[u8]) -> std::io::Result<()>,
    {
        for (page_id, data) in &self.committed {
            write_back(*page_id, data)?;
        }
        self.wal_file.set_len(WAL_HEADER_SIZE as u64)?;
        write_wal_header(&mut self.wal_file, 0)?;
        self.frame_count = 0;
        self.committed.clear();
        Ok(())
    }

    fn write_frame(
        &mut self,
        page_id: u32,
        frame_type: u32,
        txn_id: u32,
        data: &[u8],
    ) -> std::io::Result<()> {
        let checksum = compute_checksum(data);
        let frame = Frame {
            page_id,
            frame_type,
            txn_id,
            checksum,
            data: data.to_vec(),
        };
        let encoded = frame.encode();

        let offset =
            WAL_HEADER_SIZE as u64 + (self.frame_count as u64) * FRAME_SIZE as u64;
        self.wal_file.seek(SeekFrom::Start(offset))?;
        self.wal_file.write_all(&encoded)?;
        self.frame_count += 1;

        write_wal_header(&mut self.wal_file, self.frame_count as u32)?;
        Ok(())
    }

    fn replay(&mut self) -> std::io::Result<()> {
        let frame_count = read_wal_frame_count(&mut self.wal_file)? as usize;
        if frame_count == 0 {
            return Ok(());
        }

        let mut frames: Vec<Frame> = Vec::new();
        for i in 0..frame_count {
            let offset = WAL_HEADER_SIZE as u64 + (i as u64) * FRAME_SIZE as u64;
            self.wal_file.seek(SeekFrom::Start(offset))?;
            let mut buf = vec![0u8; FRAME_SIZE];
            if self.wal_file.read_exact(&mut buf).is_err() {
                break;
            }
            if let Some(frame) = Frame::decode(&buf) {
                frames.push(frame);
            }
        }

        let committed_txns: std::collections::HashSet<u32> = frames
            .iter()
            .filter(|f| f.frame_type == FRAME_TYPE_COMMIT)
            .map(|f| f.txn_id)
            .collect();

        for frame in &frames {
            if frame.frame_type == FRAME_TYPE_DATA && committed_txns.contains(&frame.txn_id) {
                self.committed.insert(frame.page_id, frame.data.clone());
            }
        }

        self.frame_count = frame_count;
        Ok(())
    }
}