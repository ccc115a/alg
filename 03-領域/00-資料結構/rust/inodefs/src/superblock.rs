use super::disk::BLOCK_SIZE;
use std::io::{Cursor, Read};

pub const MAGIC: u16 = 0xDF5C;
pub const VERSION: u16 = 1;

pub const SUPERBLOCK_BLOCK: u32 = 0;
pub const INODE_BITMAP_BLOCK: u32 = 1;
pub const BLOCK_BITMAP_BLOCK: u32 = 2;
pub const INODE_TABLE_START: u32 = 3;
pub const INODE_TABLE_BLOCKS: u32 = 64;
pub const DATA_BLOCKS_START: u32 = INODE_TABLE_START + INODE_TABLE_BLOCKS;

pub const INODE_COUNT: u32 = 512;
pub const INODES_PER_BLOCK: u32 = BLOCK_SIZE / INODE_SIZE;
pub const INODE_SIZE: u32 = 128;

pub const ROOT_INODE: u32 = 1;

#[derive(Debug, Clone)]
pub struct Superblock {
    pub magic: u16,
    pub version: u16,
    pub block_size: u32,
    pub total_blocks: u32,
    pub free_blocks: u32,
    pub inode_count: u32,
    pub free_inodes: u32,
    pub root_inode: u32,
    pub first_bitmap: u32,
    pub block_bitmap: u32,
    pub padding: [u8; 96],
}

impl Default for Superblock {
    fn default() -> Self {
        Self {
            magic: MAGIC,
            version: VERSION,
            block_size: BLOCK_SIZE,
            total_blocks: 1024,
            free_blocks: 1024 - DATA_BLOCKS_START,
            inode_count: INODE_COUNT,
            free_inodes: INODE_COUNT - 1,
            root_inode: ROOT_INODE,
            first_bitmap: INODE_BITMAP_BLOCK,
            block_bitmap: BLOCK_BITMAP_BLOCK,
            padding: [0u8; 96],
        }
    }
}

impl Superblock {
    pub fn to_bytes(&self) -> [u8; BLOCK_SIZE as usize] {
        let mut buf = [0u8; BLOCK_SIZE as usize];
        let mut pos = 0usize;

        buf[pos..pos + 2].copy_from_slice(&self.magic.to_le_bytes());
        pos += 2;
        buf[pos..pos + 2].copy_from_slice(&self.version.to_le_bytes());
        pos += 2;
        buf[pos..pos + 4].copy_from_slice(&self.block_size.to_le_bytes());
        pos += 4;
        buf[pos..pos + 4].copy_from_slice(&self.total_blocks.to_le_bytes());
        pos += 4;
        buf[pos..pos + 4].copy_from_slice(&self.free_blocks.to_le_bytes());
        pos += 4;
        buf[pos..pos + 4].copy_from_slice(&self.inode_count.to_le_bytes());
        pos += 4;
        buf[pos..pos + 4].copy_from_slice(&self.free_inodes.to_le_bytes());
        pos += 4;
        buf[pos..pos + 4].copy_from_slice(&self.root_inode.to_le_bytes());
        pos += 4;
        buf[pos..pos + 4].copy_from_slice(&self.first_bitmap.to_le_bytes());
        pos += 4;
        buf[pos..pos + 4].copy_from_slice(&self.block_bitmap.to_le_bytes());

        buf
    }

    pub fn from_bytes(data: &[u8]) -> Self {
        let mut cursor = Cursor::new(data);

        let mut magic_buf = [0u8; 2];
        let mut version_buf = [0u8; 2];
        let mut block_size_buf = [0u8; 4];
        let mut total_blocks_buf = [0u8; 4];
        let mut free_blocks_buf = [0u8; 4];
        let mut inode_count_buf = [0u8; 4];
        let mut free_inodes_buf = [0u8; 4];
        let mut root_inode_buf = [0u8; 4];
        let mut first_bitmap_buf = [0u8; 4];
        let mut block_bitmap_buf = [0u8; 4];

        cursor.read_exact(&mut magic_buf).unwrap();
        cursor.read_exact(&mut version_buf).unwrap();
        cursor.read_exact(&mut block_size_buf).unwrap();
        cursor.read_exact(&mut total_blocks_buf).unwrap();
        cursor.read_exact(&mut free_blocks_buf).unwrap();
        cursor.read_exact(&mut inode_count_buf).unwrap();
        cursor.read_exact(&mut free_inodes_buf).unwrap();
        cursor.read_exact(&mut root_inode_buf).unwrap();
        cursor.read_exact(&mut first_bitmap_buf).unwrap();
        cursor.read_exact(&mut block_bitmap_buf).unwrap();

        Self {
            magic: u16::from_le_bytes(magic_buf),
            version: u16::from_le_bytes(version_buf),
            block_size: u32::from_le_bytes(block_size_buf),
            total_blocks: u32::from_le_bytes(total_blocks_buf),
            free_blocks: u32::from_le_bytes(free_blocks_buf),
            inode_count: u32::from_le_bytes(inode_count_buf),
            free_inodes: u32::from_le_bytes(free_inodes_buf),
            root_inode: u32::from_le_bytes(root_inode_buf),
            first_bitmap: u32::from_le_bytes(first_bitmap_buf),
            block_bitmap: u32::from_le_bytes(block_bitmap_buf),
            padding: [0u8; 96],
        }
    }
}

pub const FILE_TYPES: &[&str] = &["FIFO", "CHR", "DIR", "BLK", "REG", "LNK", "SOCK"];

pub fn file_type_str(mode: u16) -> &'static str {
    let ft = (mode >> 12) & 0xF;
    match ft {
        0x1 => "FIFO",
        0x2 => "CHR",
        0x4 => "DIR",
        0x6 => "BLK",
        0x8 => "REG",
        0xA => "LNK",
        0xC => "SOCK",
        _ => "UNKNOWN",
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_superblock_serialization() {
        let sb = Superblock::default();
        let bytes = sb.to_bytes();
        let sb2 = Superblock::from_bytes(&bytes);

        assert_eq!(sb.magic, sb2.magic);
        assert_eq!(sb.version, sb2.version);
        assert_eq!(sb.block_size, sb2.block_size);
        assert_eq!(sb.total_blocks, sb2.total_blocks);
        assert_eq!(sb.root_inode, sb2.root_inode);
    }

    #[test]
    fn test_file_type_str() {
        assert_eq!(file_type_str(0o100644), "REG");
        assert_eq!(file_type_str(0o40755), "DIR");
        assert_eq!(file_type_str(0o120644), "LNK");
    }
}