//! 邏輯計畫節點（Logical Plan）
//!
//! AST → Plan 之後，executor 依照計畫執行。
//! 每個節點代表一個關聯代數運算子。

use crate::parser::ast::{Expr, OrderItem, SelectItem};

/// 邏輯計畫樹（遞迴結構）
#[derive(Debug, Clone)]
pub enum Plan {
    /// 全表掃描
    SeqScan {
        table: String,
        alias: Option<String>,
        filter: Option<Expr>,          // 下推的 WHERE 條件
    },

    /// 主鍵 / 索引查詢（等值）
    IndexScan {
        table:  String,
        alias:  Option<String>,
        column: String,
        value:  Expr,
    },

    /// 投影：選取欄位 / 運算式
    Projection {
        input:   Box<Plan>,
        columns: Vec<SelectItem>,
    },

    /// 篩選（WHERE）
    Filter {
        input:  Box<Plan>,
        expr:   Expr,
    },

    /// 排序（ORDER BY）
    Sort {
        input:  Box<Plan>,
        keys:   Vec<OrderItem>,
    },

    /// 分頁（LIMIT / OFFSET）
    Limit {
        input:  Box<Plan>,
        limit:  Option<u64>,
        offset: u64,
    },

    /// Nested-loop join
    Join {
        left:      Box<Plan>,
        right:     Box<Plan>,
        condition: Option<Expr>,
        kind:      JoinKind,
    },

    /// 聚合（GROUP BY + 聚合函式）
    Aggregate {
        input:    Box<Plan>,
        group_by: Vec<Expr>,
        having:   Option<Expr>,
        outputs:  Vec<SelectItem>,
    },

    /// 去重（DISTINCT）
    Distinct {
        input: Box<Plan>,
    },

    /// INSERT
    Insert {
        table:   String,
        columns: Vec<String>,
        source:  InsertSource,
    },

    /// UPDATE
    Update {
        table:  String,
        input:  Box<Plan>,          // 通常是 SeqScan + Filter
        sets:   Vec<(String, Expr)>,
    },

    /// DELETE
    Delete {
        table: String,
        input: Box<Plan>,
    },

    /// CREATE TABLE
    CreateTable {
        stmt: crate::parser::ast::CreateTableStmt,
    },

    /// DROP TABLE
    DropTable {
        name:      String,
        if_exists: bool,
    },

    /// CREATE INDEX
    CreateIndex {
        stmt: crate::parser::ast::CreateIndexStmt,
    },

    /// 子查詢作為掃描來源（FROM (SELECT ...)）
    SubqueryScan {
        query:  Box<Plan>,
        alias:  String,
    },

    /// CTE 展開（WITH name AS (query) SELECT ...）
    Cte {
        definitions: Vec<(String, Box<Plan>)>,
        query:       Box<Plan>,
    },

    /// 空計畫（BEGIN / COMMIT / ROLLBACK）
    Transaction(TransactionOp),
}

#[derive(Debug, Clone)]
pub enum InsertSource {
    Values(Vec<Vec<Expr>>),
}

#[derive(Debug, Clone, PartialEq)]
pub enum JoinKind {
    Inner, Left, Cross,
}

#[derive(Debug, Clone)]
pub enum TransactionOp {
    Begin, Commit, Rollback,
}
