//! Query planner (ported from sql6/src/planner/planner.rs)
//!
//! Engine limitations:
//! - LSM: does not support JOIN, complex ORDER BY, or FTS (high I/O cost)

use crate::engine::StorageEngine;
use crate::error::{Error, Result};
use crate::sql::parser::ast::*;
use crate::sql::planner::plan::*;

pub struct Planner;

impl Planner {
    pub fn new() -> Self {
        Planner
    }

    pub fn plan(&self, stmt: &Statement, engine_type: &str) -> Result<Plan> {
        match stmt {
            Statement::Select(s) => self.plan_select(s, engine_type),
            Statement::Insert(i) => Ok(Plan::Insert(InsertPlan {
                table: i.table.clone(),
                values: i.values.clone(),
            })),
            Statement::Update(u) => Ok(Plan::Update(UpdatePlan {
                table: u.table.clone(),
                set: u.sets.clone(),
                filter: u.where_.clone(),
            })),
            Statement::Delete(d) => Ok(Plan::Delete(DeletePlan {
                table: d.table.clone(),
                filter: d.where_.clone(),
            })),
            Statement::CreateTable(c) => Ok(Plan::CreateTable(CreateTablePlan {
                name: c.name.clone(),
                columns: c.columns.clone(),
                if_not_exists: c.if_not_exists,
            })),
            Statement::DropTable(d) => Ok(Plan::DropTable(DropTablePlan {
                name: d.name.clone(),
                if_exists: d.if_exists,
            })),
            _ => Ok(Plan::Empty),
        }
    }

    fn plan_select(&self, s: &SelectStmt, engine_type: &str) -> Result<Plan> {
        // Check for JOIN
        if let Some(ref join) = s.joins.first() {
            // LSM engine limitation: JOIN not supported
            if engine_type == "lsm" {
                return Err(Error::NotSupported(
                    "JOIN not supported with LSM engine".into(),
                ));
            }
            // Create JOIN plan
            let left_table = match &s.from {
                Some(FromItem::Table(t)) => t.name.clone(),
                _ => String::new(),
            };
            let right_table = join.table.name.clone();
            let kind = format!("{:?}", join.kind);
            let condition = match &join.condition {
                JoinCondition::On(expr) => Some(expr.clone()),
                _ => None,
            };
            return Ok(Plan::Join(JoinPlan {
                left: Box::new(Plan::Scan(ScanPlan {
                    table: left_table,
                    filter: None,
                    order_by: vec![],
                    limit: None,
                    is_fts: false,
                    fts_query: None,
                })),
                right: Box::new(Plan::Scan(ScanPlan {
                    table: right_table,
                    filter: None,
                    order_by: vec![],
                    limit: None,
                    is_fts: false,
                    fts_query: None,
                })),
                kind,
                condition,
            }));
        }

        let table = match &s.from {
            Some(FromItem::Table(t)) => t.name.clone(),
            _ => String::new(),
        };

        // LSM engine limitation: ORDER BY not supported (high I/O cost)
        if engine_type == "lsm" && !s.order_by.is_empty() {
            return Err(Error::NotSupported(
                "ORDER BY not supported with LSM engine (high I/O cost)".into(),
            ));
        }

        // LSM engine limitation: FTS not supported
        if engine_type == "lsm" {
            if let Some(ref where_) = s.where_ {
                if self.contains_fts_match(where_) {
                    return Err(Error::NotSupported(
                        "FTS not supported with LSM engine".into(),
                    ));
                }
            }
        }

        Ok(Plan::Scan(ScanPlan {
            table,
            filter: s.where_.clone(),
            order_by: s.order_by.clone(),
            limit: None,
            is_fts: false,
            fts_query: None,
        }))
    }

    fn contains_fts_match(&self, expr: &Expr) -> bool {
        match expr {
            Expr::Like { .. } => true,
            _ => false,
        }
    }
}