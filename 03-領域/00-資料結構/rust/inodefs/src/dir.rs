use std::io::{Cursor, Read, Write};

use crate::inode::FileType;

pub const DIR_ENTRY_SIZE: u32 = 8;

#[derive(Debug, Clone)]
pub struct DirEntry {
    pub inode: u32,
    pub name: String,
    pub file_type: FileType,
}

impl DirEntry {
    pub fn new(inode: u32, name: &str, file_type: FileType) -> Self {
        Self {
            inode,
            name: name.to_string(),
            file_type,
        }
    }

    pub fn size(&self) -> u32 {
        8 + self.name.len() as u32
    }

    pub fn to_bytes(&self) -> Vec<u8> {
        let mut buf = Vec::with_capacity(self.size() as usize);
        buf.write_all(&self.inode.to_le_bytes()).unwrap();
        buf.push(self.name.len() as u8);
        buf.push(self.file_type.to_u16() as u8);
        buf.write_all(self.name.as_bytes()).unwrap();
        buf
    }

    pub fn from_bytes(data: &[u8]) -> Option<Self> {
        if data.len() < 4 {
            return None;
        }
        let mut cursor = Cursor::new(data);
        let mut ino_buf = [0u8; 4];
        cursor.read_exact(&mut ino_buf).unwrap();
        let inode = u32::from_le_bytes(ino_buf);

        let mut name_len_buf = [0u8; 1];
        cursor.read_exact(&mut name_len_buf).unwrap();
        let name_len = name_len_buf[0] as usize;

        let mut type_buf = [0u8; 1];
        cursor.read_exact(&mut type_buf).unwrap();
        let file_type_val = type_buf[0];

        let mut name_buf = vec![0u8; name_len];
        cursor.read_exact(&mut name_buf).unwrap();
        let name = String::from_utf8(name_buf).ok()?;

        let file_type = FileType::from_u16(file_type_val as u16 * 0x10).unwrap_or(FileType::Reg);

        Some(Self {
            inode,
            name,
            file_type,
        })
    }
}

#[derive(Debug, Clone)]
pub struct Directory {
    entries: Vec<DirEntry>,
}

impl Directory {
    pub fn new() -> Self {
        Self {
            entries: Vec::new(),
        }
    }

    pub fn add_entry(&mut self, entry: DirEntry) {
        self.entries.push(entry);
    }

    pub fn remove_entry(&mut self, name: &str) -> Option<DirEntry> {
        if let Some(pos) = self.entries.iter().position(|e| e.name == name) {
            Some(self.entries.remove(pos))
        } else {
            None
        }
    }

    pub fn find(&self, name: &str) -> Option<&DirEntry> {
        self.entries.iter().find(|e| e.name == name)
    }

    pub fn find_inode(&self, name: &str) -> Option<u32> {
        self.find(name).map(|e| e.inode)
    }

    pub fn entries(&self) -> &[DirEntry] {
        &self.entries
    }

    pub fn is_empty(&self) -> bool {
        self.entries.is_empty()
    }

    pub fn len(&self) -> usize {
        self.entries.len()
    }

    pub fn to_bytes(&self) -> Vec<u8> {
        let mut result = Vec::new();
        for entry in &self.entries {
            result.extend(entry.to_bytes());
        }
        result
    }

    pub fn from_inode_content(data: &[u8]) -> Self {
        let mut dir = Directory::new();
        let mut offset: usize = 0;

        while offset + 6 <= data.len() {
            let entry_data = &data[offset..];
            if let Some(entry) = DirEntry::from_bytes(entry_data) {
                if entry.inode != 0 {
                    dir.entries.push(entry.clone());
                }
                offset += 6 + entry.name.len() as usize;
            } else {
                break;
            }
        }

        dir
    }
}

impl Default for Directory {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_dir_entry_serialization() {
        let entry = DirEntry::new(42, "test.txt", FileType::Reg);
        let bytes = entry.to_bytes();
        let entry2 = DirEntry::from_bytes(&bytes).unwrap();

        assert_eq!(entry.inode, entry2.inode);
        assert_eq!(entry.name, entry2.name);
    }

    #[test]
    fn test_directory_add_find_remove() {
        let mut dir = Directory::new();

        dir.add_entry(DirEntry::new(2, "a.txt", FileType::Reg));
        dir.add_entry(DirEntry::new(3, "b.txt", FileType::Reg));

        assert_eq!(dir.find_inode("a.txt"), Some(2));
        assert_eq!(dir.find_inode("missing"), None);

        let removed = dir.remove_entry("a.txt").unwrap();
        assert_eq!(removed.inode, 2);
        assert_eq!(dir.find_inode("a.txt"), None);
    }

    #[test]
    fn test_directory_to_from_bytes() {
        let mut dir = Directory::new();
        dir.add_entry(DirEntry::new(1, ".", FileType::Dir));
        dir.add_entry(DirEntry::new(1, "..", FileType::Dir));
        dir.add_entry(DirEntry::new(5, "file.txt", FileType::Reg));

        let bytes = dir.to_bytes();
        let dir2 = Directory::from_inode_content(&bytes);

        assert_eq!(dir2.len(), 3);
        assert_eq!(dir2.find_inode("file.txt"), Some(5));
    }
}