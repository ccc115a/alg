//! 儲存後端抽象（含 WAL 交易支援）

use crate::codec::{decode_node, encode_node, PAGE_SIZE};
use crate::node::Node;
use crate::wal::Wal;
use std::collections::HashMap;
use std::fs::{File, OpenOptions};
use std::io::{Read, Seek, SeekFrom, Write};
use std::path::Path;

pub trait Storage {
    fn read_node(&mut self, page_id: usize) -> Node;
    fn write_node(&mut self, page_id: usize, node: &Node);
    fn alloc_page(&mut self) -> usize;
    fn page_count(&self) -> usize;
    fn flush(&mut self);

    fn begin_txn(&mut self) {}
    fn commit_txn(&mut self) {}
    fn rollback_txn(&mut self) {}
}

pub struct MemoryStorage {
    pages: HashMap<usize, Node>,
    next_page: usize,
}

impl MemoryStorage {
    pub fn new() -> Self {
        MemoryStorage {
            pages: HashMap::new(),
            next_page: 0,
        }
    }
}

impl Default for MemoryStorage {
    fn default() -> Self {
        Self::new()
    }
}

impl Storage for MemoryStorage {
    fn read_node(&mut self, page_id: usize) -> Node {
        self.pages
            .get(&page_id)
            .cloned()
            .expect("MemoryStorage: page not found")
    }

    fn write_node(&mut self, page_id: usize, node: &Node) {
        self.pages.insert(page_id, node.clone());
    }

    fn alloc_page(&mut self) -> usize {
        let id = self.next_page;
        self.next_page += 1;
        id
    }

    fn page_count(&self) -> usize {
        self.next_page
    }

    fn flush(&mut self) {}
}

pub struct DiskStorage {
    file: File,
    page_count: usize,
    pub catalog_root: Option<usize>,
    wal: Wal,
}

const MAGIC: &[u8; 8] = b"SQL4DB\0\0";
const VERSION: u32 = 2;
const HEADER_OFFSET: u64 = PAGE_SIZE as u64;

impl DiskStorage {
    pub fn open<P: AsRef<Path>>(path: P) -> std::io::Result<Self> {
        let path = path.as_ref();
        let exists = path.exists();

        let file = OpenOptions::new()
            .read(true)
            .write(true)
            .create(true)
            .open(path)?;

        let wal = Wal::open(path)?;

        let mut storage = DiskStorage {
            file,
            page_count: 0,
            catalog_root: None,
            wal,
        };

        if exists {
            storage.read_header()?;
        } else {
            storage.write_header()?;
        }

        Ok(storage)
    }

    pub fn set_catalog_root(&mut self, root: usize) {
        self.catalog_root = Some(root);
        let _ = self.write_header();
    }

    fn write_header(&mut self) -> std::io::Result<()> {
        let mut hdr = vec![0u8; PAGE_SIZE];
        hdr[0..8].copy_from_slice(MAGIC);
        hdr[8..12].copy_from_slice(&VERSION.to_le_bytes());
        hdr[12..16].copy_from_slice(&(self.page_count as u32).to_le_bytes());
        let cat_root = self.catalog_root.unwrap_or(0) as u32;
        hdr[16..20].copy_from_slice(&cat_root.to_le_bytes());
        self.file.seek(SeekFrom::Start(0))?;
        self.file.write_all(&hdr)?;
        self.file.flush()
    }

    fn read_header(&mut self) -> std::io::Result<()> {
        let mut hdr = vec![0u8; PAGE_SIZE];
        self.file.seek(SeekFrom::Start(0))?;
        self.file.read_exact(&mut hdr)?;

        if &hdr[0..8] != MAGIC {
            return Err(std::io::Error::new(
                std::io::ErrorKind::InvalidData,
                "invalid sql4db magic",
            ));
        }
        self.page_count = u32::from_le_bytes(hdr[12..16].try_into().unwrap()) as usize;
        let cat_root = u32::from_le_bytes(hdr[16..20].try_into().unwrap()) as usize;
        self.catalog_root = if cat_root == 0 { None } else { Some(cat_root) };
        Ok(())
    }

    fn page_offset(page_id: usize) -> u64 {
        HEADER_OFFSET + (page_id as u64) * PAGE_SIZE as u64
    }

    fn read_page_from_file(&mut self, page_id: usize) -> Vec<u8> {
        let offset = Self::page_offset(page_id);
        let mut buf = vec![0u8; PAGE_SIZE];
        self.file.seek(SeekFrom::Start(offset)).unwrap();
        let _ = self.file.read_exact(&mut buf);
        buf
    }

    fn write_page_to_file(
        &mut self,
        page_id: u32,
        data: &[u8],
    ) -> std::io::Result<()> {
        let offset = Self::page_offset(page_id as usize);
        self.file.seek(SeekFrom::Start(offset))?;
        self.file.write_all(data)?;
        Ok(())
    }
}

impl Storage for DiskStorage {
    fn read_node(&mut self, page_id: usize) -> Node {
        if let Some(data) = self.wal.read_page(page_id as u32) {
            return decode_node(data);
        }
        let buf = self.read_page_from_file(page_id);
        decode_node(&buf)
    }

    fn write_node(&mut self, page_id: usize, node: &Node) {
        let buf = encode_node(node);
        self.wal.write_page(page_id as u32, buf);
    }

    fn alloc_page(&mut self) -> usize {
        let id = self.page_count;
        self.page_count += 1;
        let blank = vec![0u8; PAGE_SIZE];
        let offset = Self::page_offset(id);
        self.file.seek(SeekFrom::Start(offset)).unwrap();
        self.file.write_all(&blank).unwrap();
        id
    }

    fn page_count(&self) -> usize {
        self.page_count
    }

    fn flush(&mut self) {
        if self.wal.needs_checkpoint() {
            let file = &mut self.file;
            let header_offset = HEADER_OFFSET;
            self.wal
                .checkpoint(|page_id, data| {
                    let offset = header_offset + (page_id as u64) * PAGE_SIZE as u64;
                    file.seek(SeekFrom::Start(offset))?;
                    file.write_all(data)
                })
                .unwrap();
        }
        self.write_header().unwrap();
        self.file.flush().unwrap();
    }

    fn begin_txn(&mut self) {
        self.wal.begin();
    }
    fn commit_txn(&mut self) {
        self.wal.commit().unwrap();
    }
    fn rollback_txn(&mut self) {
        self.wal.rollback();
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::node::{Key, Node, Record};

    fn leaf_with(key: i64, val: &str) -> Node {
        let mut node = Node::new_leaf();
        node.keys.push(Key::Integer(key));
        node.records.push(Record {
            key: Key::Integer(key),
            value: val.as_bytes().to_vec(),
        });
        node
    }

    fn cleanup(name: &str) {
        let _ = std::fs::remove_file(format!("/tmp/btree_{}.db", name));
        let _ = std::fs::remove_file(format!("/tmp/btree_{}.sql4wal", name));
    }

    #[test]
    fn memory_alloc_write_read() {
        let mut store = MemoryStorage::new();
        let id = store.alloc_page();
        let node = leaf_with(42, "hello");
        store.write_node(id, &node);
        let back = store.read_node(id);
        assert_eq!(back.keys, node.keys);
        assert_eq!(back.records[0].value, b"hello");
    }

    #[test]
    fn disk_write_and_read() {
        cleanup("disk_rw");
        {
            let mut store = DiskStorage::open("/tmp/btree_disk_rw.db").unwrap();
            store.begin_txn();
            let id = store.alloc_page();
            store.write_node(id, &leaf_with(99, "world"));
            store.commit_txn();
            store.flush();
        }
        {
            let mut store = DiskStorage::open("/tmp/btree_disk_rw.db").unwrap();
            let node = store.read_node(0);
            assert_eq!(node.keys[0], Key::Integer(99));
            assert_eq!(node.records[0].value, b"world");
        }
        cleanup("disk_rw");
    }

    #[test]
    fn disk_rollback() {
        cleanup("rollback");
        {
            let mut store = DiskStorage::open("/tmp/btree_rollback.db").unwrap();
            store.begin_txn();
            let id = store.alloc_page();
            store.write_node(id, &leaf_with(1, "committed"));
            store.commit_txn();
            store.flush();

            store.begin_txn();
            store.write_node(id, &leaf_with(1, "should_be_gone"));
            store.rollback_txn();

            let node = store.read_node(id);
            assert_eq!(node.records[0].value, b"committed");
        }
        cleanup("rollback");
    }

    #[test]
    fn disk_crash_recovery() {
        cleanup("crash");
        {
            let mut store = DiskStorage::open("/tmp/btree_crash.db").unwrap();
            store.begin_txn();
            let id = store.alloc_page();
            store.write_node(id, &leaf_with(777, "survived"));
            store.commit_txn();
        }
        {
            let mut store = DiskStorage::open("/tmp/btree_crash.db").unwrap();
            let node = store.read_node(0);
            assert_eq!(node.keys[0], Key::Integer(777));
            assert_eq!(node.records[0].value, b"survived");
        }
        cleanup("crash");
    }

    #[test]
    fn catalog_root_persists() {
        cleanup("catroot");
        {
            let mut store = DiskStorage::open("/tmp/btree_catroot.db").unwrap();
            store.set_catalog_root(42);
        }
        {
            let store = DiskStorage::open("/tmp/btree_catroot.db").unwrap();
            assert_eq!(store.catalog_root, Some(42));
        }
        cleanup("catroot");
    }
}