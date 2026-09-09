//! Planner：AST → 邏輯計畫
//!
//! 同時做簡單最佳化：
//!   - 等值條件下推 → IndexScan（若主鍵欄位）
//!   - WHERE 條件盡量下推到 SeqScan.filter

use crate::catalog::Catalog;
use crate::parser::ast::*;
use crate::pager::storage::Storage;
use super::plan::{InsertSource, JoinKind as PlanJoinKind, Plan, TransactionOp};

pub struct Planner<'a, S: Storage> {
    catalog: &'a Catalog<S>,
}

impl<'a, S: Storage> Planner<'a, S> {
    pub fn new(catalog: &'a Catalog<S>) -> Self {
        Planner { catalog }
    }

    pub fn plan(&self, stmt: Statement) -> Result<Plan, String> {
        match stmt {
            Statement::Select(s)      => self.plan_select(s),
            Statement::Insert(s)      => self.plan_insert(s),
            Statement::Update(s)      => self.plan_update(s),
            Statement::Delete(s)      => self.plan_delete(s),
            Statement::CreateTable(s) => Ok(Plan::CreateTable { stmt: s }),
            Statement::DropTable(s)   => Ok(Plan::DropTable { name: s.name, if_exists: s.if_exists }),
            Statement::CreateIndex(s) => Ok(Plan::CreateIndex { stmt: s }),
            Statement::Begin          => Ok(Plan::Transaction(TransactionOp::Begin)),
            Statement::Commit         => Ok(Plan::Transaction(TransactionOp::Commit)),
            Statement::Rollback       => Ok(Plan::Transaction(TransactionOp::Rollback)),
        }
    }

    // ── SELECT ────────────────────────────────────────────────────────────

    fn plan_select(&self, s: SelectStmt) -> Result<Plan, String> {
        use crate::parser::ast::FromItem;

        // 0. CTEs → 展開為 Cte 計畫節點
        let cte_plans: Vec<(String, Box<Plan>)> = s.with.iter()
            .map(|cte| {
                let p = self.plan_select(*cte.query.clone())?;
                Ok((cte.name.clone(), Box::new(p)))
            })
            .collect::<Result<_, String>>()?;

        // 1. 掃描來源表或子查詢
        let mut plan = if let Some(from_item) = s.from {
            match from_item {
                FromItem::Table(tref) =>
                    self.plan_table_scan(&tref.name, tref.alias.as_deref(), s.where_.clone())?,
                FromItem::Subquery { query, alias } => {
                    let inner = self.plan_select(*query)?;
                    Plan::SubqueryScan { query: Box::new(inner), alias }
                }
            }
        } else {
            // 無 FROM（如 SELECT 1+1）
            Plan::SeqScan { table: "__dual__".to_string(), alias: None, filter: None }
        };

        // 2. JOIN
        for join in s.joins {
            let right = self.plan_table_scan(&join.table.name, join.table.alias.as_deref(), None)?;
            let condition = match join.condition {
                JoinCondition::On(expr) => Some(expr),
                _ => None,
            };
            let kind = match join.kind {
                crate::parser::ast::JoinKind::Left  => PlanJoinKind::Left,
                crate::parser::ast::JoinKind::Cross => PlanJoinKind::Cross,
                _ => PlanJoinKind::Inner,
            };
            plan = Plan::Join { left: Box::new(plan), right: Box::new(right), condition, kind: kind };
        }

        // 3. WHERE（未下推的部分）
        if let Some(expr) = &s.where_ {
            if !self.is_pushed_down(&plan, expr) {
                plan = Plan::Filter { input: Box::new(plan), expr: expr.clone() };
            }
        }

        // 4. GROUP BY / Aggregate
        let has_agg = s.columns.iter().any(|c| contains_aggregate(c));
        if !s.group_by.is_empty() || has_agg {
            plan = Plan::Aggregate {
                input:    Box::new(plan),
                group_by: s.group_by,
                having:   s.having,
                outputs:  s.columns.clone(),
            };
        }

        // 5. DISTINCT
        if s.distinct {
            plan = Plan::Distinct { input: Box::new(plan) };
        }

        // 6. ORDER BY
        if !s.order_by.is_empty() {
            plan = Plan::Sort { input: Box::new(plan), keys: s.order_by };
        }

        // 7. LIMIT / OFFSET
        let limit  = expr_to_u64(s.limit.as_ref());
        let offset = expr_to_u64(s.offset.as_ref()).unwrap_or(0);
        if limit.is_some() || offset > 0 {
            plan = Plan::Limit { input: Box::new(plan), limit, offset };
        }

        // 8. Projection（有 aggregate 時已在 Aggregate 節點處理）
        if !has_agg {
            plan = Plan::Projection { input: Box::new(plan), columns: s.columns };
        }

        // 若有 CTE，包裝在 Cte 計畫節點
        if !cte_plans.is_empty() {
            plan = Plan::Cte { definitions: cte_plans, query: Box::new(plan) };
        }

        Ok(plan)
    }

    /// 嘗試把 WHERE 下推為 IndexScan 或 SeqScan.filter
    fn plan_table_scan(
        &self,
        table: &str,
        alias: Option<&str>,
        where_: Option<Expr>,
    ) -> Result<Plan, String> {
        // 嘗試等值主鍵 → IndexScan
        if let Some(expr) = &where_ {
            if let Some((col, val)) = extract_eq_condition(expr) {
                if self.is_primary_key(table, &col) {
                    return Ok(Plan::IndexScan {
                        table:  table.to_string(),
                        alias:  alias.map(|s| s.to_string()),
                        column: col,
                        value:  val,
                    });
                }
            }
        }

        Ok(Plan::SeqScan {
            table:  table.to_string(),
            alias:  alias.map(|s| s.to_string()),
            filter: where_,
        })
    }

    fn is_primary_key(&self, table: &str, column: &str) -> bool {
        self.catalog
            .get_table(table)
            .map(|meta| {
                meta.schema.columns.first()
                    .map(|c| c.name == column)
                    .unwrap_or(false)
            })
            .unwrap_or(false)
    }

    /// 判斷 WHERE 是否已被下推到掃描節點（避免重複套 Filter）
    fn is_pushed_down(&self, plan: &Plan, expr: &Expr) -> bool {
        match plan {
            Plan::SeqScan { filter, .. } => filter.as_ref() == Some(expr),
            Plan::IndexScan { .. } => true,
            _ => false,
        }
    }

    // ── INSERT ────────────────────────────────────────────────────────────

    fn plan_insert(&self, s: InsertStmt) -> Result<Plan, String> {
        if !self.catalog.table_exists(&s.table) {
            return Err(format!("table '{}' does not exist", s.table));
        }
        Ok(Plan::Insert {
            table:   s.table,
            columns: s.columns,
            source:  InsertSource::Values(s.values),
        })
    }

    // ── UPDATE ────────────────────────────────────────────────────────────

    fn plan_update(&self, s: UpdateStmt) -> Result<Plan, String> {
        if !self.catalog.table_exists(&s.table) {
            return Err(format!("table '{}' does not exist", s.table));
        }
        let scan = self.plan_table_scan(&s.table, None, s.where_)?;
        Ok(Plan::Update { table: s.table, input: Box::new(scan), sets: s.sets })
    }

    // ── DELETE ────────────────────────────────────────────────────────────

    fn plan_delete(&self, s: DeleteStmt) -> Result<Plan, String> {
        if !self.catalog.table_exists(&s.table) {
            return Err(format!("table '{}' does not exist", s.table));
        }
        let scan = self.plan_table_scan(&s.table, None, s.where_)?;
        Ok(Plan::Delete { table: s.table, input: Box::new(scan) })
    }
}

// ── 輔助函式 ──────────────────────────────────────────────────────────────

/// 從等值條件 `col = val` 提取 (column_name, value_expr)
fn extract_eq_condition(expr: &Expr) -> Option<(String, Expr)> {
    if let Expr::BinOp { left, op: BinOp::Eq, right } = expr {
        match (left.as_ref(), right.as_ref()) {
            (Expr::Column { table: None, name }, val) =>
                Some((name.clone(), val.clone())),
            (val, Expr::Column { table: None, name }) =>
                Some((name.clone(), val.clone())),
            _ => None,
        }
    } else { None }
}

fn contains_aggregate(item: &SelectItem) -> bool {
    match item {
        SelectItem::Expr { expr, .. } => expr_has_agg(expr),
        _ => false,
    }
}

fn expr_has_agg(expr: &Expr) -> bool {
    match expr {
        Expr::Function { name, .. } =>
            matches!(name.as_str(), "COUNT"|"SUM"|"AVG"|"MAX"|"MIN"),
        Expr::BinOp { left, right, .. } => expr_has_agg(left) || expr_has_agg(right),
        _ => false,
    }
}

fn expr_to_u64(expr: Option<&Expr>) -> Option<u64> {
    match expr? {
        Expr::LitInt(v) => Some(*v as u64),
        _ => None,
    }
}

// ── 測試 ─────────────────────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;
    use crate::catalog::Catalog;
    use crate::pager::storage::MemoryStorage;
    use crate::table::schema::{Column, DataType, Schema};
    use crate::parser::parse;

    fn make_catalog() -> Catalog<MemoryStorage> {
        let mut cat = Catalog::new(MemoryStorage::new());
        cat.create_table("users", Schema::new(vec![
            Column::new("id",   DataType::Integer),
            Column::new("name", DataType::Text),
            Column::new("age",  DataType::Integer),
        ])).unwrap();
        cat.create_table("orders", Schema::new(vec![
            Column::new("order_id", DataType::Integer),
            Column::new("user_id",  DataType::Integer),
            Column::new("amount",   DataType::Float),
        ])).unwrap();
        cat
    }

    fn plan_sql(cat: &Catalog<MemoryStorage>, sql: &str) -> Plan {
        let stmts = parse(sql).unwrap();
        Planner::new(cat).plan(stmts.into_iter().next().unwrap()).unwrap()
    }

    #[test]
    fn seq_scan() {
        let cat = make_catalog();
        let plan = plan_sql(&cat, "SELECT * FROM users");
        assert!(matches!(plan, Plan::Projection { input, .. } if matches!(input.as_ref(), Plan::SeqScan { table, .. } if table == "users")));
    }

    #[test]
    fn index_scan_on_pk() {
        let cat = make_catalog();
        let plan = plan_sql(&cat, "SELECT * FROM users WHERE id = 42");
        // Projection → IndexScan
        if let Plan::Projection { input, .. } = plan {
            assert!(matches!(input.as_ref(), Plan::IndexScan { table, .. } if table == "users"));
        } else { panic!("expected Projection over IndexScan") }
    }

    #[test]
    fn seq_scan_with_filter() {
        let cat = make_catalog();
        let plan = plan_sql(&cat, "SELECT * FROM users WHERE name = 'Alice'");
        if let Plan::Projection { input, .. } = plan {
            assert!(matches!(input.as_ref(), Plan::SeqScan { filter: Some(_), .. }));
        } else { panic!() }
    }

    #[test]
    fn order_limit() {
        let cat = make_catalog();
        let plan = plan_sql(&cat, "SELECT * FROM users ORDER BY age DESC LIMIT 10");
        assert!(matches!(plan, Plan::Projection { input, .. } if matches!(input.as_ref(), Plan::Limit { .. })));
    }

    #[test]
    fn insert_plan() {
        let cat = make_catalog();
        let plan = plan_sql(&cat, "INSERT INTO users VALUES (1, 'Alice', 30)");
        assert!(matches!(plan, Plan::Insert { table, .. } if table == "users"));
    }

    #[test]
    fn insert_unknown_table() {
        let cat = make_catalog();
        let stmts = parse("INSERT INTO ghost VALUES (1)").unwrap();
        let result = Planner::new(&cat).plan(stmts.into_iter().next().unwrap());
        assert!(result.is_err());
    }

    #[test]
    fn update_plan() {
        let cat = make_catalog();
        let plan = plan_sql(&cat, "UPDATE users SET name='Bob' WHERE id=1");
        assert!(matches!(plan, Plan::Update { table, .. } if table == "users"));
    }

    #[test]
    fn delete_plan() {
        let cat = make_catalog();
        let plan = plan_sql(&cat, "DELETE FROM users WHERE id=5");
        assert!(matches!(plan, Plan::Delete { table, .. } if table == "users"));
    }

    #[test]
    fn join_plan() {
        let cat = make_catalog();
        let plan = plan_sql(&cat, "SELECT * FROM users JOIN orders ON users.id = orders.user_id");
        // Projection → Join
        if let Plan::Projection { input, .. } = plan {
            assert!(matches!(input.as_ref(), Plan::Join { .. }));
        } else { panic!() }
    }

    #[test]
    fn transaction_plan() {
        let cat = make_catalog();
        let plan = plan_sql(&cat, "BEGIN");
        assert!(matches!(plan, Plan::Transaction(TransactionOp::Begin)));
    }
}
