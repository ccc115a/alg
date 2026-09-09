use std::fmt;

#[derive(Debug, Clone)]
pub enum Error {
    Io(String),
    NotFound(String),
    AlreadyExists(String),
    IsDirectory(String),
    NotDirectory(String),
    DirectoryNotEmpty,
    InvalidInode(u32),
    InvalidBlock(u32),
    OutOfSpace,
    NotSupported(String),
    Corrupted(String),
    PermissionDenied,
    InvalidPath(String),
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Error::Io(s) => write!(f, "IO error: {}", s),
            Error::NotFound(s) => write!(f, "Not found: {}", s),
            Error::AlreadyExists(s) => write!(f, "Already exists: {}", s),
            Error::IsDirectory(s) => write!(f, "Is a directory: {}", s),
            Error::NotDirectory(s) => write!(f, "Not a directory: {}", s),
            Error::DirectoryNotEmpty => write!(f, "Directory not empty"),
            Error::InvalidInode(ino) => write!(f, "Invalid inode: {}", ino),
            Error::InvalidBlock(blk) => write!(f, "Invalid block: {}", blk),
            Error::OutOfSpace => write!(f, "Out of space"),
            Error::NotSupported(s) => write!(f, "Not supported: {}", s),
            Error::Corrupted(s) => write!(f, "Corrupted: {}", s),
            Error::PermissionDenied => write!(f, "Permission denied"),
            Error::InvalidPath(s) => write!(f, "Invalid path: {}", s),
        }
    }
}

impl From<std::io::Error> for Error {
    fn from(e: std::io::Error) -> Self {
        Error::Io(e.to_string())
    }
}

pub type Result<T> = std::result::Result<T, Error>;