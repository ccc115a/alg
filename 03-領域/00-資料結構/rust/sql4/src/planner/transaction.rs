//! 交易管理器（Transaction Manager）
//!
//! 整合 WAL 與 Executor，讓 BEGIN / COMMIT / ROLLBACK 真正有效果：
//!
//! - BEGIN：通知 Storage 層開始交易，記錄目前 table row counts（snapshot）
//! - COMMIT：刷新 WAL commit frame，更新 catalog
//! - ROLLBACK：通知 Storage 丟棄 dirty pages，還原 row count snapshot
//!
//! 目前實作為單執行緒、單一活躍交易（與 SQLite 預設行為相同）

use std::collections::HashMap;

/// 一筆交易的 snapshot（用於 rollback）
#[derive(Debug, Clone)]
pub struct TxnSnapshot {
    /// 各表在交易開始時的 row count
    pub row_counts: HashMap<String, usize>,
}

/// 交易狀態機
#[derive(Debug, Clone, PartialEq)]
pub enum TxnState {
    Idle,
    Active,
}

/// 交易管理器
pub struct TransactionManager {
    pub state:    TxnState,
    pub snapshot: Option<TxnSnapshot>,
    pub txn_id:   u64,
}

impl TransactionManager {
    pub fn new() -> Self {
        TransactionManager {
            state:    TxnState::Idle,
            snapshot: None,
            txn_id:   0,
        }
    }

    /// 開始交易，記錄 row count snapshot
    pub fn begin(&mut self, row_counts: HashMap<String, usize>) -> Result<(), String> {
        if self.state == TxnState::Active {
            return Err("transaction already active".to_string());
        }
        self.txn_id += 1;
        self.snapshot = Some(TxnSnapshot { row_counts });
        self.state = TxnState::Active;
        Ok(())
    }

    /// 提交：清除 snapshot，回到 Idle
    pub fn commit(&mut self) -> Result<(), String> {
        if self.state != TxnState::Active {
            return Err("no active transaction".to_string());
        }
        self.snapshot = None;
        self.state = TxnState::Idle;
        Ok(())
    }

    /// Rollback：回傳 snapshot 供 Executor 還原狀態，清除交易
    pub fn rollback(&mut self) -> Result<TxnSnapshot, String> {
        if self.state != TxnState::Active {
            return Err("no active transaction".to_string());
        }
        let snap = self.snapshot.take().ok_or("no snapshot")?;
        self.state = TxnState::Idle;
        Ok(snap)
    }

    pub fn is_active(&self) -> bool { self.state == TxnState::Active }
}

impl Default for TransactionManager {
    fn default() -> Self { Self::new() }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn counts(pairs: &[(&str, usize)]) -> HashMap<String, usize> {
        pairs.iter().map(|(k, v)| (k.to_string(), *v)).collect()
    }

    #[test]
    fn begin_commit_cycle() {
        let mut tm = TransactionManager::new();
        tm.begin(counts(&[("users", 3)])).unwrap();
        assert!(tm.is_active());
        tm.commit().unwrap();
        assert!(!tm.is_active());
    }

    #[test]
    fn rollback_returns_snapshot() {
        let mut tm = TransactionManager::new();
        tm.begin(counts(&[("users", 3), ("orders", 5)])).unwrap();
        let snap = tm.rollback().unwrap();
        assert_eq!(snap.row_counts["users"], 3);
        assert_eq!(snap.row_counts["orders"], 5);
        assert!(!tm.is_active());
    }

    #[test]
    fn double_begin_fails() {
        let mut tm = TransactionManager::new();
        tm.begin(counts(&[])).unwrap();
        assert!(tm.begin(counts(&[])).is_err());
    }

    #[test]
    fn commit_without_begin_fails() {
        let mut tm = TransactionManager::new();
        assert!(tm.commit().is_err());
    }

    #[test]
    fn rollback_without_begin_fails() {
        let mut tm = TransactionManager::new();
        assert!(tm.rollback().is_err());
    }
}
