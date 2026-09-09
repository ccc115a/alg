//! Transaction support (ported from sql6/src/planner/transaction.rs)

use crate::error::Result;

pub struct Transaction;

impl Transaction {
    pub fn new() -> Self {
        Transaction
    }

    pub fn commit(&mut self) -> Result<()> {
        todo!()
    }

    pub fn rollback(&mut self) -> Result<()> {
        todo!()
    }

    pub fn is_committed(&self) -> bool {
        false
    }
}

impl Default for Transaction {
    fn default() -> Self {
        Self::new()
    }
}