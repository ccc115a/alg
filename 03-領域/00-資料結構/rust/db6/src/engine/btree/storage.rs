//! BTree storage layer — page management and persistence
//!
//! Provides a page-based storage abstraction, supporting both in-memory and file-based implementations.
//! Each page has a fixed size of 4096 bytes (matching the common OS page size).
//!
//! File storage format:
//! ```text
//! [Page 0: Header] -> [Page 1: Data] -> [Page 2: Data] -> ...
//! ```
//! Page 0 is the file header (BTreeHeader), recording the root page ID and total page count.

use std::collections::BTreeMap;
use std::fs::{File, OpenOptions};
use std::io::{Read, Seek, SeekFrom, Write};
use std::path::Path;
use std::sync::{Arc, Mutex};

use crate::error::Result;
use serde::{Deserialize, Serialize};

/// Page size: 4096 bytes (4KB)
pub const PAGE_SIZE: usize = 4096;

/// BTree file header, stored in Page 0
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BTreeHeader {
    /// Root page ID
    pub root_page: u64,
    /// Total number of allocated pages
    pub page_count: u64,
}

impl Default for BTreeHeader {
    fn default() -> Self {
        Self {
            root_page: 0,
            page_count: 1,
        }
    }
}

/// Page structure: fixed-size data block
#[derive(Debug, Clone)]
pub struct Page {
    /// Page unique identifier
    pub id: u64,
    /// Page content (fixed length of PAGE_SIZE)
    pub data: Vec<u8>,
}

impl Page {
    /// Create a new page filled with zeros
    pub fn new(id: u64) -> Self {
        Self {
            id,
            data: vec![0; PAGE_SIZE],
        }
    }

    /// Create a page from existing data
    pub fn from_data(id: u64, data: Vec<u8>) -> Self {
        Self { id, data }
    }
}

/// Storage abstraction trait, defines page-level operations
pub trait Storage: Send + Sync {
    /// Read data from the specified page
    fn read_page(&mut self, page_id: u64) -> Option<Page>;
    /// Write a page
    fn write_page(&mut self, page: &Page);
    /// Allocate a new page (returns the new page ID)
    fn alloc_page(&mut self) -> u64;
    /// Write all changes to disk
    fn flush(&mut self) -> Result<()>;
    /// Close storage
    fn close(&mut self);
    /// Read file header
    fn header(&self) -> Option<BTreeHeader>;
    /// Set file header
    fn set_header(&mut self, header: BTreeHeader);
}

/// File storage implementation
///
/// Stores BTree pages in a physical file, each page occupies fixed PAGE_SIZE bytes.
/// Uses `Arc<Mutex<Option<File>>>` for optional shared file access.
pub struct FileStorage {
    /// Underlying file (Option to support close operation)
    file: Arc<Mutex<Option<File>>>,
    /// File path
    path: std::path::PathBuf,
    /// File header (thread-safe)
    header: Mutex<BTreeHeader>,
}

impl FileStorage {
    /// Open or create a BTree file
    ///
    /// If file already exists and size is at least one page, tries to read the header.
    pub fn open(path: &Path) -> Result<Self> {
        let file = OpenOptions::new()
            .read(true)
            .write(true)
            .create(true)
            .open(path)?;

        let metadata = file.metadata()?;
        let header = if metadata.len() >= PAGE_SIZE as u64 {
            let mut buffer = vec![0u8; PAGE_SIZE];
            let mut f = file.try_clone()?;
            f.seek(SeekFrom::Start(0))?;
            f.read_exact(&mut buffer)?;
            bincode::deserialize(&buffer).unwrap_or_default()
        } else {
            BTreeHeader::default()
        };

        Ok(Self {
            file: Arc::new(Mutex::new(Some(file))),
            path: path.to_path_buf(),
            header: Mutex::new(header),
        })
    }

    fn file_mut(&self) -> std::sync::MutexGuard<'_, Option<File>> {
        self.file.lock().unwrap()
    }

    fn file_size(&self) -> u64 {
        self.file.lock().unwrap().as_ref()
            .map(|f| f.metadata().map(|m| m.len()).unwrap_or(0))
            .unwrap_or(0)
    }
}

impl Storage for FileStorage {
    fn read_page(&mut self, page_id: u64) -> Option<Page> {
        let offset = page_id * PAGE_SIZE as u64;
        if offset >= self.file_size() {
            return None;
        }

        let mut buffer = vec![0u8; PAGE_SIZE];
        if let Some(ref mut f) = *self.file_mut() {
            if f.seek(SeekFrom::Start(offset)).is_err() {
                return None;
            }
            if f.read(&mut buffer).is_err() {
                return None;
            }
            Some(Page::from_data(page_id, buffer))
        } else {
            None
        }
    }

    fn write_page(&mut self, page: &Page) {
        let data = &page.data;
        let offset = page.id * PAGE_SIZE as u64;

        if offset + data.len() as u64 > self.file_size() {
            if let Some(ref mut f) = *self.file_mut() {
                let _ = f.set_len(offset + data.len() as u64);
            }
        }

        if let Some(ref mut f) = *self.file_mut() {
            let _ = f.seek(SeekFrom::Start(offset));
            let _ = f.write_all(data);
        }
    }

    fn alloc_page(&mut self) -> u64 {
        let mut header = self.header.lock().unwrap();
        let id = header.page_count;
        header.page_count += 1;
        id
    }

    fn flush(&mut self) -> Result<()> {
        if let Some(ref mut f) = *self.file_mut() {
            f.flush()?;
        }
        let header = self.header.lock().unwrap();
        let data = bincode::serialize(&*header).unwrap_or_default();
        if let Some(ref mut f) = *self.file_mut() {
            f.seek(SeekFrom::Start(0))?;
            f.write_all(&data)?;
            f.flush()?;
        }
        Ok(())
    }

    fn close(&mut self) {
        *self.file_mut() = None;
    }

    fn header(&self) -> Option<BTreeHeader> {
        Some(self.header.lock().unwrap().clone())
    }

    fn set_header(&mut self, header: BTreeHeader) {
        *self.header.lock().unwrap() = header;
    }
}

/// Memory storage implementation (for testing)
///
/// Pages are stored in BTreeMap, flush does nothing.
pub struct MemoryStorage {
    pages: BTreeMap<u64, Page>,
    next_page_id: u64,
    header: BTreeHeader,
}

impl MemoryStorage {
    pub fn new() -> Self {
        Self {
            pages: BTreeMap::new(),
            next_page_id: 1,
            header: BTreeHeader::default(),
        }
    }
}

impl Default for MemoryStorage {
    fn default() -> Self {
        Self::new()
    }
}

impl Storage for MemoryStorage {
    fn read_page(&mut self, page_id: u64) -> Option<Page> {
        self.pages.get(&page_id).cloned()
    }

    fn write_page(&mut self, page: &Page) {
        self.pages.insert(page.id, page.clone());
    }

    fn alloc_page(&mut self) -> u64 {
        let id = self.next_page_id;
        self.next_page_id += 1;
        id
    }

    fn flush(&mut self) -> Result<()> {
        Ok(())
    }

    fn close(&mut self) {
        self.pages.clear();
        self.next_page_id = 1;
    }

    fn header(&self) -> Option<BTreeHeader> {
        Some(self.header.clone())
    }

    fn set_header(&mut self, header: BTreeHeader) {
        self.header = header;
    }
}