//! Query plan nodes (ported from sql6/src/planner/plan.rs)

use crate::sql::parser::ast::{Expr, SelectStmt};

#[derive(Debug, Clone)]
pub enum Plan {
    Scan(ScanPlan),
    Join(JoinPlan),
    Insert(InsertPlan),
    Update(UpdatePlan),
    Delete(DeletePlan),
    CreateTable(CreateTablePlan),
    CreateFtsTable(FtsPlan),
    DropTable(DropTablePlan),
    Empty,
}

#[derive(Debug, Clone)]
pub struct ScanPlan {
    pub table: String,
    pub filter: Option<Expr>,
    pub order_by: Vec<crate::sql::parser::ast::OrderItem>,
    pub limit: Option<i64>,
    pub is_fts: bool,
    pub fts_query: Option<String>,
}

#[derive(Debug, Clone)]
pub struct JoinPlan {
    pub left: Box<Plan>,
    pub right: Box<Plan>,
    pub kind: String,
    pub condition: Option<Expr>,
}

#[derive(Debug, Clone)]
pub struct InsertPlan {
    pub table: String,
    pub values: Vec<Vec<Expr>>,
}

#[derive(Debug, Clone)]
pub struct UpdatePlan {
    pub table: String,
    pub set: Vec<(String, Expr)>,
    pub filter: Option<Expr>,
}

#[derive(Debug, Clone)]
pub struct DeletePlan {
    pub table: String,
    pub filter: Option<Expr>,
}

#[derive(Debug, Clone)]
pub struct CreateTablePlan {
    pub name: String,
    pub columns: Vec<crate::sql::parser::ast::ColumnDef>,
    pub if_not_exists: bool,
}

#[derive(Debug, Clone)]
pub struct FtsPlan {
    pub name: String,
    pub columns: Vec<crate::sql::parser::ast::ColumnDef>,
    pub tokenize: String,
}

#[derive(Debug, Clone)]
pub struct DropTablePlan {
    pub name: String,
    pub if_exists: bool,
}