//! Executor：執行邏輯計畫，回傳 ResultSet

use std::collections::HashMap;

use crate::btree::node::Key;
use crate::catalog::Catalog;
use crate::parser::ast::{BinOp, Expr, SelectItem, UnaryOp};
use crate::pager::storage::MemoryStorage;
use crate::table::row::{Row, Value};
use crate::table::Table;
use super::plan::{InsertSource, JoinKind, Plan, TransactionOp};
use super::transaction::TransactionManager;

// ── ResultSet ─────────────────────────────────────────────────────────────

#[derive(Debug, Default, Clone)]
pub struct ResultSet {
    pub columns: Vec<String>,
    pub rows:    Vec<Vec<Value>>,
}

impl ResultSet {
    pub fn empty() -> Self { Self::default() }

    pub fn ok_msg(msg: &str) -> Self {
        ResultSet {
            columns: vec!["result".into()],
            rows:    vec![vec![Value::Text(msg.into())]],
        }
    }

    pub fn row_count(&self) -> usize { self.rows.len() }

    pub fn display(&self) {
        if self.columns.is_empty() { return; }
        let header = self.columns.join(" | ");
        println!("{}", header);
        println!("{}", "-".repeat(header.len()));
        for row in &self.rows {
            println!("{}", row.iter().map(|v| v.to_string()).collect::<Vec<_>>().join(" | "));
        }
        println!("({} row{})", self.rows.len(), if self.rows.len() == 1 { "" } else { "s" });
    }
}

// ── Executor ──────────────────────────────────────────────────────────────
// 為了簡單起見，Executor 使用 MemoryStorage 管理資料表。
// 未來可以用 trait object 支援 DiskStorage。

pub struct Executor {
    catalog:     Catalog<MemoryStorage>,
    tables:      HashMap<String, Table<MemoryStorage>>,
    txn_mgr:     TransactionManager,
    cte_cache:   HashMap<String, ResultSet>,
    constraints: HashMap<String, crate::planner::constraints::TableConstraints>,
}

impl Executor {
    pub fn new() -> Self {
        Executor {
            catalog:     Catalog::new(MemoryStorage::new()),
            tables:      HashMap::new(),
            txn_mgr:     TransactionManager::new(),
            cte_cache:   HashMap::new(),
            constraints: HashMap::new(),
        }
    }

    pub fn catalog(&self) -> &Catalog<MemoryStorage> { &self.catalog }

    pub fn execute(&mut self, plan: Plan) -> Result<ResultSet, String> {
        match plan {
            Plan::Projection { input, columns }              => self.exec_projection(*input, columns),
            Plan::SeqScan   { table, filter, .. }            => self.exec_seq_scan(&table, filter),
            Plan::IndexScan { table, column, value, .. }     => self.exec_index_scan(&table, &column, value),
            Plan::Filter    { input, expr }                  => self.exec_filter(*input, expr),
            Plan::Sort      { input, keys }                  => self.exec_sort(*input, keys),
            Plan::Limit     { input, limit, offset }         => self.exec_limit(*input, limit, offset),
            Plan::Distinct  { input }                        => self.exec_distinct(*input),
            Plan::Aggregate { input, group_by, having, outputs } =>
                self.exec_aggregate(*input, group_by, having, outputs),
            Plan::Join      { left, right, condition, kind } =>
                self.exec_join(*left, *right, condition, kind),
            Plan::Insert    { table, columns, source }       => self.exec_insert(table, columns, source),
            Plan::Update    { table, input, sets }           => self.exec_update(table, *input, sets),
            Plan::Delete    { table, input }                 => self.exec_delete(table, *input),
            Plan::CreateTable { stmt }                       => self.exec_create_table(stmt),
            Plan::DropTable { name, if_exists }              => self.exec_drop_table(name, if_exists),
            Plan::CreateIndex { .. }                         => Ok(ResultSet::ok_msg("index created")),
            Plan::Transaction(op)                            => self.exec_transaction(op),
            Plan::SubqueryScan { query, alias }                  => self.exec_subquery_scan(*query, alias),
            Plan::Cte { definitions, query }                     => self.exec_cte(definitions, *query),
        }
    }

    // ── 掃描 ──────────────────────────────────────────────────────────────

    fn exec_seq_scan(&mut self, table: &str, filter: Option<Expr>) -> Result<ResultSet, String> {
        // 無 FROM 的 SELECT（dual 虛擬表）：回傳一列空 row 讓 projection 求值
        if table == "__dual__" {
            return Ok(ResultSet { columns: vec![], rows: vec![vec![]] });
        }
        // CTE 虛擬表優先
        if let Some(rs) = self.cte_cache.get(table).cloned() {
            let col_names = rs.columns.clone();
            let rows = rs.rows.into_iter()
                .filter(|row| match &filter {
                    Some(e) => eval_expr(e, &Row::new(row.clone()), &col_names)
                        .map(|v| is_truthy(&v)).unwrap_or(false),
                    None => true,
                })
                .collect();
            return Ok(ResultSet { columns: col_names, rows });
        }
        let col_names = self.col_names(table)?;
        // 先 resolve 子查詢（需要在掃描前執行，且需要 &mut self）
        let resolved_filter = match filter {
            Some(e) => Some(self.resolve_expr(e)?),
            None    => None,
        };
        let tbl = self.get_table(table)?;
        let all = tbl.scan();

        let rows = all.into_iter()
            .filter(|row| match &resolved_filter {
                Some(e) => eval_expr(e, row, &col_names).map(|v| is_truthy(&v)).unwrap_or(false),
                None    => true,
            })
            .map(|r| r.values)
            .collect();

        Ok(ResultSet { columns: col_names, rows })
    }

    fn exec_index_scan(&mut self, table: &str, _col: &str, value: Expr) -> Result<ResultSet, String> {
        let col_names = self.col_names(table)?;
        let key = expr_to_key(&value)?;
        let tbl = self.get_table(table)?;
        let rows = tbl.get(&key).map(|r| vec![r.values]).unwrap_or_default();
        Ok(ResultSet { columns: col_names, rows })
    }

    // ── 關聯代數 ──────────────────────────────────────────────────────────

    fn exec_projection(&mut self, input: Plan, columns: Vec<SelectItem>) -> Result<ResultSet, String> {
        let src = self.execute(input)?;

        if columns.len() == 1 && matches!(&columns[0], SelectItem::Star) {
            return Ok(src);
        }

        let mut out_cols: Vec<String> = Vec::new();
        let mut out_rows: Vec<Vec<Value>> = Vec::new();

        for src_row in &src.rows {
            let ctx = Row::new(src_row.clone());
            let mut vals: Vec<Value> = Vec::new();
            let first = out_cols.is_empty();

            for item in &columns {
                match item {
                    SelectItem::Star | SelectItem::TableStar(_) => {
                        if first { out_cols.extend(src.columns.clone()); }
                        vals.extend(src_row.clone());
                    }
                    SelectItem::Expr { expr, alias } => {
                        if first {
                            out_cols.push(alias.clone().unwrap_or_else(|| expr_name(expr)));
                        }
                        vals.push(eval_expr(expr, &ctx, &src.columns)?);
                    }
                }
            }
            out_rows.push(vals);
        }
        Ok(ResultSet { columns: out_cols, rows: out_rows })
    }

    fn exec_filter(&mut self, input: Plan, expr: Expr) -> Result<ResultSet, String> {
        let src = self.execute(input)?;
        // 預先解析子查詢（IN subquery, EXISTS, scalar subquery）
        let resolved = self.resolve_expr(expr)?;
        let rows = src.rows.into_iter()
            .filter(|r| {
                let row = Row::new(r.clone());
                eval_expr(&resolved, &row, &src.columns).map(|v| is_truthy(&v)).unwrap_or(false)
            })
            .collect();
        Ok(ResultSet { columns: src.columns, rows })
    }

    fn exec_sort(&mut self, input: Plan, keys: Vec<crate::parser::ast::OrderItem>) -> Result<ResultSet, String> {
        let mut src = self.execute(input)?;
        let cols = src.columns.clone();
        src.rows.sort_by(|a, b| {
            for k in &keys {
                let va = eval_expr(&k.expr, &Row::new(a.clone()), &cols).unwrap_or(Value::Null);
                let vb = eval_expr(&k.expr, &Row::new(b.clone()), &cols).unwrap_or(Value::Null);
                let ord = cmp_val(&va, &vb);
                let ord = if k.asc { ord } else { ord.reverse() };
                if ord != std::cmp::Ordering::Equal { return ord; }
            }
            std::cmp::Ordering::Equal
        });
        Ok(src)
    }

    fn exec_limit(&mut self, input: Plan, limit: Option<u64>, offset: u64) -> Result<ResultSet, String> {
        let src = self.execute(input)?;
        let rows = src.rows.into_iter()
            .skip(offset as usize)
            .take(limit.unwrap_or(u64::MAX) as usize)
            .collect();
        Ok(ResultSet { columns: src.columns, rows })
    }

    fn exec_distinct(&mut self, input: Plan) -> Result<ResultSet, String> {
        let src = self.execute(input)?;
        let mut seen = std::collections::HashSet::new();
        let rows = src.rows.into_iter()
            .filter(|r| seen.insert(r.iter().map(|v| format!("{:?}", v)).collect::<Vec<_>>().join(",")))
            .collect();
        Ok(ResultSet { columns: src.columns, rows })
    }

    fn exec_aggregate(
        &mut self, input: Plan,
        group_by: Vec<Expr>, having: Option<Expr>, outputs: Vec<SelectItem>,
    ) -> Result<ResultSet, String> {
        let src = self.execute(input)?;
        let cols = src.columns.clone();

        // 分組
        type Group = (Vec<Value>, Vec<Row>);
        let mut groups: Vec<Group> = Vec::new();
        for rv in src.rows {
            let row = Row::new(rv);
            let key: Vec<Value> = group_by.iter()
                .map(|e| eval_expr(e, &row, &cols).unwrap_or(Value::Null))
                .collect();
            if let Some(g) = groups.iter_mut().find(|(k, _)| k == &key) {
                g.1.push(row);
            } else {
                groups.push((key, vec![row]));
            }
        }
        if groups.is_empty() { groups.push((vec![], vec![])); }

        let mut out_cols: Vec<String> = Vec::new();
        let mut out_rows: Vec<Vec<Value>> = Vec::new();

        for (_, rows) in &groups {
            let mut rv: Vec<Value> = Vec::new();
            for item in &outputs {
                if let SelectItem::Expr { expr, alias } = item {
                    if out_cols.len() < outputs.len() {
                        out_cols.push(alias.clone().unwrap_or_else(|| expr_name(expr)));
                    }
                    rv.push(eval_aggregate(expr, rows, &cols)?);
                }
            }
            if let Some(h) = &having {
                let hrow = Row::new(rv.clone());
                if !is_truthy(&eval_expr(h, &hrow, &out_cols).unwrap_or(Value::Null)) { continue; }
            }
            out_rows.push(rv);
        }
        Ok(ResultSet { columns: out_cols, rows: out_rows })
    }

    fn exec_join(
        &mut self, left: Plan, right: Plan, condition: Option<Expr>, kind: JoinKind,
    ) -> Result<ResultSet, String> {
        let l = self.execute(left)?;
        let r = self.execute(right)?;
        let mut cols = l.columns.clone();
        cols.extend(r.columns.clone());
        let mut rows: Vec<Vec<Value>> = Vec::new();

        for lr in &l.rows {
            let mut matched = false;
            for rr in &r.rows {
                let combined: Vec<Value> = lr.iter().chain(rr.iter()).cloned().collect();
                let pass = match &condition {
                    Some(cond) => eval_expr(cond, &Row::new(combined.clone()), &cols)
                        .map(|v| is_truthy(&v)).unwrap_or(false),
                    None => true,
                };
                if pass { rows.push(combined); matched = true; }
            }
            if !matched && kind == JoinKind::Left {
                let mut combined = lr.clone();
                combined.extend(vec![Value::Null; r.columns.len()]);
                rows.push(combined);
            }
        }
        Ok(ResultSet { columns: cols, rows })
    }

    // ── DML ───────────────────────────────────────────────────────────────

    fn exec_insert(&mut self, table: String, columns: Vec<String>, source: InsertSource) -> Result<ResultSet, String> {
        let meta = self.catalog.get_table(&table)
            .ok_or_else(|| format!("table '{}' not found", table))?.clone();

        let InsertSource::Values(all_values) = source;
        let count = all_values.len();

        for value_exprs in all_values {
            let vals: Vec<Value> = value_exprs.iter()
                .map(eval_literal)
                .collect::<Result<_, _>>()?;

            let row = if columns.is_empty() {
                Row::new(vals)
            } else {
                let mut rv = vec![Value::Null; meta.schema.columns.len()];
                for (col, val) in columns.iter().zip(vals) {
                    let idx = meta.schema.index_of(col)
                        .ok_or_else(|| format!("column '{}' not found", col))?;
                    rv[idx] = val;
                }
                Row::new(rv)
            };

            // 約束檢查
            if let Some(tc) = self.constraints.get(&table) {
                let existing = self.tables.get_mut(&table)
                    .map(|t| t.scan()).unwrap_or_default();
                let meta = self.catalog.get_table(&table).cloned();
                if let Some(meta) = meta {
                    crate::planner::constraints::check_row(&row, &meta.schema, tc, &existing)
                        .map_err(|e| e)?;
                }
            }
            self.get_table(&table)?.insert(row)?;
        }

        let new_count = self.tables[&table].len();
        let root = self.tables[&table].root_page();
        self.catalog.update_table_meta(&table, root, new_count)?;
        Ok(ResultSet::ok_msg(&format!("{} row(s) inserted", count)))
    }

    fn exec_update(&mut self, table: String, input: Plan, sets: Vec<(String, Expr)>) -> Result<ResultSet, String> {
        let src = self.execute(input)?;
        let meta = self.catalog.get_table(&table)
            .ok_or_else(|| format!("table '{}' not found", table))?.clone();
        let col_names = src.columns.clone();
        let count = src.rows.len();

        for rv in src.rows {
            let old = Row::new(rv.clone());
            let key = row_to_key(&old)?;
            let mut new_vals = rv;
            for (col, expr) in &sets {
                let idx = meta.schema.index_of(col)
                    .ok_or_else(|| format!("column '{}' not found", col))?;
                new_vals[idx] = eval_expr(expr, &old, &col_names)?;
            }
            let tbl = self.get_table(&table)?;
            tbl.delete(&key);
            tbl.insert(Row::new(new_vals))?;
        }
        Ok(ResultSet::ok_msg(&format!("{} row(s) updated", count)))
    }

    fn exec_delete(&mut self, table: String, input: Plan) -> Result<ResultSet, String> {
        let src = self.execute(input)?;
        let count = src.rows.len();
        for rv in src.rows {
            let key = row_to_key(&Row::new(rv))?;
            self.get_table(&table)?.delete(&key);
        }
        Ok(ResultSet::ok_msg(&format!("{} row(s) deleted", count)))
    }

    // ── DDL ───────────────────────────────────────────────────────────────

    fn exec_create_table(&mut self, stmt: crate::parser::ast::CreateTableStmt) -> Result<ResultSet, String> {
        use crate::table::schema::{Column, DataType, Schema};
        use crate::parser::ast::SqlType;

        if self.catalog.table_exists(&stmt.name) {
            if stmt.if_not_exists { return Ok(ResultSet::ok_msg("table already exists")); }
            return Err(format!("table '{}' already exists", stmt.name));
        }
        let columns: Vec<Column> = stmt.columns.iter().map(|cd| {
            let dt = match cd.data_type {
                SqlType::Integer => DataType::Integer,
                SqlType::Real    => DataType::Float,
                SqlType::Text    => DataType::Text,
                SqlType::Blob    => DataType::Text,
                SqlType::Boolean => DataType::Boolean,
                SqlType::Null    => DataType::Text,
            };
            Column::new(&cd.name, dt)
        }).collect();
        let tc = crate::planner::constraints::constraints_from_ast(&stmt);
        self.constraints.insert(stmt.name.clone(), tc);
        self.catalog.create_table(&stmt.name, Schema::new(columns))?;
        Ok(ResultSet::ok_msg("table created"))
    }

    fn exec_drop_table(&mut self, name: String, if_exists: bool) -> Result<ResultSet, String> {
        if !self.catalog.table_exists(&name) {
            if if_exists { return Ok(ResultSet::ok_msg("table does not exist")); }
            return Err(format!("table '{}' does not exist", name));
        }
        self.tables.remove(&name);
        self.catalog.drop_table(&name)?;
        Ok(ResultSet::ok_msg("table dropped"))
    }

    /// 把運算式中的子查詢預先求值為字面值（需要 &mut self）
    fn resolve_expr(&mut self, expr: Expr) -> Result<Expr, String> {
        use crate::parser::ast::*;
        match expr {
            Expr::ScalarSubquery(query) => {
                let plan = crate::planner::planner::Planner::new(&self.catalog).plan(
                    Statement::Select(*query))?;
                let rs = self.execute(plan)?;
                let val = rs.rows.into_iter().next()
                    .and_then(|r| r.into_iter().next())
                    .unwrap_or(Value::Null);
                Ok(expr_from_value(val))
            }
            Expr::InSubquery { expr: inner, query, negated } => {
                let plan = crate::planner::planner::Planner::new(&self.catalog).plan(
                    Statement::Select(*query))?;
                let rs = self.execute(plan)?;
                let list: Vec<Expr> = rs.rows.into_iter()
                    .filter_map(|r| r.into_iter().next())
                    .map(expr_from_value)
                    .collect();
                Ok(Expr::InList { expr: inner, list, negated })
            }
            Expr::Exists { query, negated } => {
                let plan = crate::planner::planner::Planner::new(&self.catalog).plan(
                    Statement::Select(*query))?;
                let rs = self.execute(plan)?;
                let exists = !rs.rows.is_empty();
                Ok(Expr::LitBool(if negated { !exists } else { exists }))
            }
            Expr::BinOp { left, op, right } => {
                let left  = self.resolve_expr(*left)?;
                let right = self.resolve_expr(*right)?;
                Ok(Expr::BinOp { left: Box::new(left), op, right: Box::new(right) })
            }
            other => Ok(other),
        }
    }

    fn exec_subquery_scan(&mut self, plan: Plan, alias: String) -> Result<ResultSet, String> {
        // 執行子查詢，把結果存為暫時「虛擬表」
        let mut result = self.execute(plan)?;
        // 給欄位加上 alias 前綴（alias.col）
        result.columns = result.columns.iter()
            .map(|c| format!("{}.{}", alias, c))
            .collect();
        Ok(result)
    }

    fn exec_cte(&mut self, defs: Vec<(String, Box<Plan>)>, query: Plan) -> Result<ResultSet, String> {
        // 依序執行每個 CTE，暫存為虛擬結果集
        for (name, plan) in defs {
            let rs = self.execute(*plan)?;
            // 把 CTE 結果塞進 cte_cache（以 table name 儲存）
            self.cte_cache.insert(name, rs);
        }
        let result = self.execute(query)?;
        // 清除 CTE 快取（避免污染後續查詢）
        self.cte_cache.clear();
        Ok(result)
    }

    fn exec_transaction(&mut self, op: TransactionOp) -> Result<ResultSet, String> {
        match op {
            TransactionOp::Begin => {
                // 記錄所有表的 row count snapshot
                let counts: std::collections::HashMap<String, usize> = self.tables.iter()
                    .map(|(name, tbl)| (name.clone(), tbl.len()))
                    .collect();
                self.txn_mgr.begin(counts)?;
                Ok(ResultSet::ok_msg("transaction begun"))
            }
            TransactionOp::Commit => {
                self.txn_mgr.commit()?;
                Ok(ResultSet::ok_msg("committed"))
            }
            TransactionOp::Rollback => {
                let snap = self.txn_mgr.rollback()?;
                // 還原各表的資料（重建 Table 並截斷到 snapshot 的 row count）
                // 簡化實作：清除所有在交易中新建或修改的表，從空狀態重建
                // 完整實作需要 MVCC 或 WAL page-level rollback
                for (name, count) in &snap.row_counts {
                    if let Some(tbl) = self.tables.get_mut(name) {
                        // 把超過 snapshot 的資料截掉（掃描刪除）
                        let current = tbl.scan();
                        let to_delete: Vec<_> = current.into_iter()
                            .skip(*count)
                            .filter_map(|r| match r.values.first() {
                                Some(crate::table::row::Value::Integer(v)) =>
                                    Some(crate::btree::node::Key::Integer(*v)),
                                Some(crate::table::row::Value::Text(s)) =>
                                    Some(crate::btree::node::Key::Text(s.clone())),
                                _ => None,
                            })
                            .collect();
                        for key in to_delete {
                            tbl.delete(&key);
                        }
                    }
                }
                Ok(ResultSet::ok_msg("rolled back"))
            }
        }
    }

    // ── 輔助 ──────────────────────────────────────────────────────────────

    fn col_names(&self, table: &str) -> Result<Vec<String>, String> {
        self.catalog.get_table(table)
            .ok_or_else(|| format!("table '{}' not found", table))
            .map(|m| m.schema.columns.iter().map(|c| c.name.clone()).collect())
    }

    fn get_table(&mut self, name: &str) -> Result<&mut Table<MemoryStorage>, String> {
        if !self.tables.contains_key(name) {
            let meta = self.catalog.get_table(name)
                .ok_or_else(|| format!("table '{}' not found", name))?.clone();
            let tbl = Table::new(name, meta.schema.clone(), MemoryStorage::new());
            let root = tbl.root_page();
            self.catalog.update_table_meta(name, root, 0)?;
            self.tables.insert(name.to_string(), tbl);
        }
        self.tables.get_mut(name).ok_or_else(|| "internal error".to_string())
    }
}

// ── 運算式求值 ────────────────────────────────────────────────────────────

fn random_i64() -> i64 {
    // 簡單的線性同餘偽隨機（不需要 rand crate）
    use std::time::{SystemTime, UNIX_EPOCH};
    let seed = SystemTime::now().duration_since(UNIX_EPOCH)
        .unwrap_or_default().subsec_nanos() as i64;
    seed.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407)
}

fn expr_from_value(v: Value) -> crate::parser::ast::Expr {
    use crate::parser::ast::Expr;
    match v {
        Value::Integer(i) => Expr::LitInt(i),
        Value::Float(f)   => Expr::LitFloat(f),
        Value::Text(s)    => Expr::LitStr(s),
        Value::Boolean(b) => Expr::LitBool(b),
        Value::Null       => Expr::LitNull,
    }
}

fn eval_expr(expr: &Expr, row: &Row, cols: &[String]) -> Result<Value, String> {
    match expr {
        Expr::LitInt(v)   => Ok(Value::Integer(*v)),
        Expr::LitFloat(v) => Ok(Value::Float(*v)),
        Expr::LitStr(s)   => Ok(Value::Text(s.clone())),
        Expr::LitBool(b)  => Ok(Value::Boolean(*b)),
        Expr::LitNull     => Ok(Value::Null),

        Expr::Column { name, .. } => {
            let idx = cols.iter().position(|c| c == name)
                .ok_or_else(|| format!("column '{}' not found", name))?;
            Ok(row.values.get(idx).cloned().unwrap_or(Value::Null))
        }

        Expr::BinOp { left, op, right } => {
            let l = eval_expr(left, row, cols)?;
            let r = eval_expr(right, row, cols)?;
            eval_binop(op, l, r)
        }

        Expr::UnaryOp { op, expr } => match (op, eval_expr(expr, row, cols)?) {
            (UnaryOp::Neg, Value::Integer(i)) => Ok(Value::Integer(-i)),
            (UnaryOp::Neg, Value::Float(f))   => Ok(Value::Float(-f)),
            (UnaryOp::Not, v)                 => Ok(Value::Boolean(!is_truthy(&v))),
            _ => Err("type error in unary op".into()),
        },

        Expr::IsNull { expr, negated } => {
            let is_null = matches!(eval_expr(expr, row, cols)?, Value::Null);
            Ok(Value::Boolean(if *negated { !is_null } else { is_null }))
        }

        Expr::Between { expr, low, high, negated } => {
            let v  = eval_expr(expr, row, cols)?;
            let lo = eval_expr(low,  row, cols)?;
            let hi = eval_expr(high, row, cols)?;
            let between = cmp_val(&v, &lo) != std::cmp::Ordering::Less
                       && cmp_val(&v, &hi) != std::cmp::Ordering::Greater;
            Ok(Value::Boolean(if *negated { !between } else { between }))
        }

        Expr::InList { expr, list, negated } => {
            let v = eval_expr(expr, row, cols)?;
            let found = list.iter().any(|e| {
                eval_expr(e, row, cols).map(|rv| cmp_val(&v, &rv) == std::cmp::Ordering::Equal).unwrap_or(false)
            });
            Ok(Value::Boolean(if *negated { !found } else { found }))
        }

        Expr::Like { expr, pattern, negated } => {
            if let (Value::Text(s), Value::Text(pat)) =
                (eval_expr(expr, row, cols)?, eval_expr(pattern, row, cols)?) {
                let m = sql_like(&s, &pat);
                Ok(Value::Boolean(if *negated { !m } else { m }))
            } else { Ok(Value::Boolean(false)) }
        }

        Expr::Function { name, args, .. } => {
            // 先把參數求值為字串（日期函式需要）
            let eval_str_args = || -> Vec<String> {
                args.iter().map(|a| eval_expr(a, row, cols)
                    .unwrap_or(Value::Null).to_string()).collect()
            };
            match name.as_str() {
                "UPPER"    => match eval_expr(&args[0], row, cols)? {
                    Value::Text(s) => Ok(Value::Text(s.to_uppercase())), v => Ok(v) },
                "LOWER"    => match eval_expr(&args[0], row, cols)? {
                    Value::Text(s) => Ok(Value::Text(s.to_lowercase())), v => Ok(v) },
                "LENGTH"   => match eval_expr(&args[0], row, cols)? {
                    Value::Text(s) => Ok(Value::Integer(s.len() as i64)), _ => Ok(Value::Null) },
                "ABS"      => match eval_expr(&args[0], row, cols)? {
                    Value::Integer(i) => Ok(Value::Integer(i.abs())),
                    Value::Float(f)   => Ok(Value::Float(f.abs())),
                    v => Ok(v) },
                "ROUND"    => {
                    let v = eval_expr(&args[0], row, cols)?;
                    let digits = if args.len() > 1 {
                        match eval_expr(&args[1], row, cols)? { Value::Integer(i) => i, _ => 0 }
                    } else { 0 };
                    let factor = 10f64.powi(digits as i32);
                    match v {
                        Value::Float(f)   => Ok(Value::Float((f * factor).round() / factor)),
                        Value::Integer(i) => Ok(Value::Integer(i)),
                        _ => Ok(Value::Null),
                    }
                },
                "CEIL" | "CEILING" => match eval_expr(&args[0], row, cols)? {
                    Value::Float(f)   => Ok(Value::Float(f.ceil())),
                    Value::Integer(i) => Ok(Value::Integer(i)),
                    _ => Ok(Value::Null) },
                "FLOOR"    => match eval_expr(&args[0], row, cols)? {
                    Value::Float(f)   => Ok(Value::Float(f.floor())),
                    Value::Integer(i) => Ok(Value::Integer(i)),
                    _ => Ok(Value::Null) },
                "RANDOM"   => Ok(Value::Integer(random_i64())),
                "TYPEOF"   => {
                    let v = eval_expr(&args[0], row, cols)?;
                    Ok(Value::Text(match v {
                        Value::Integer(_) => "integer", Value::Float(_) => "real",
                        Value::Text(_) => "text", Value::Null => "null",
                        Value::Boolean(_) => "integer",
                    }.to_string()))
                },
                "IFNULL" | "NVL" => {
                    let v = eval_expr(&args[0], row, cols)?;
                    if matches!(v, Value::Null) { eval_expr(&args[1], row, cols) } else { Ok(v) }
                },
                "NULLIF" => {
                    let a = eval_expr(&args[0], row, cols)?;
                    let b = eval_expr(&args[1], row, cols)?;
                    if cmp_val(&a, &b) == std::cmp::Ordering::Equal { Ok(Value::Null) } else { Ok(a) }
                },
                "COALESCE" => {
                    for a in args { let v = eval_expr(a, row, cols)?; if !matches!(v, Value::Null) { return Ok(v); } }
                    Ok(Value::Null)
                },
                "SUBSTR" | "SUBSTRING" => {
                    if let Value::Text(s) = eval_expr(&args[0], row, cols)? {
                        let start = match eval_expr(&args[1], row, cols)? { Value::Integer(i) => (i - 1).max(0) as usize, _ => 0 };
                        let chars: Vec<char> = s.chars().collect();
                        let result: String = if args.len() > 2 {
                            let len = match eval_expr(&args[2], row, cols)? { Value::Integer(i) => i as usize, _ => 0 };
                            chars[start.min(chars.len())..].iter().take(len).collect()
                        } else {
                            chars[start.min(chars.len())..].iter().collect()
                        };
                        Ok(Value::Text(result))
                    } else { Ok(Value::Null) }
                },
                "TRIM"   => match eval_expr(&args[0], row, cols)? {
                    Value::Text(s) => Ok(Value::Text(s.trim().to_string())), v => Ok(v) },
                "LTRIM"  => match eval_expr(&args[0], row, cols)? {
                    Value::Text(s) => Ok(Value::Text(s.trim_start().to_string())), v => Ok(v) },
                "RTRIM"  => match eval_expr(&args[0], row, cols)? {
                    Value::Text(s) => Ok(Value::Text(s.trim_end().to_string())), v => Ok(v) },
                "REPLACE" => {
                    if let (Value::Text(s), Value::Text(from), Value::Text(to)) = (
                        eval_expr(&args[0], row, cols)?,
                        eval_expr(&args[1], row, cols)?,
                        eval_expr(&args[2], row, cols)?) {
                        Ok(Value::Text(s.replace(&from, &to)))
                    } else { Ok(Value::Null) }
                },
                "INSTR" => {
                    if let (Value::Text(s), Value::Text(needle)) = (
                        eval_expr(&args[0], row, cols)?, eval_expr(&args[1], row, cols)?) {
                        Ok(Value::Integer(s.find(&needle).map(|i| i as i64 + 1).unwrap_or(0)))
                    } else { Ok(Value::Null) }
                },
                // ── 日期時間函式 ────────────────────────────────────────
                "DATE"      => {
                    let str_args = eval_str_args();
                    Ok(crate::planner::datetime::fn_date(&str_args)
                        .map(Value::Text).unwrap_or(Value::Null))
                },
                "TIME"      => {
                    let str_args = eval_str_args();
                    Ok(crate::planner::datetime::fn_time(&str_args)
                        .map(Value::Text).unwrap_or(Value::Null))
                },
                "DATETIME"  => {
                    let str_args = eval_str_args();
                    Ok(crate::planner::datetime::fn_datetime(&str_args)
                        .map(Value::Text).unwrap_or(Value::Null))
                },
                "JULIANDAY" => {
                    let str_args = eval_str_args();
                    Ok(crate::planner::datetime::fn_julianday(&str_args)
                        .map(Value::Float).unwrap_or(Value::Null))
                },
                "STRFTIME"  => {
                    let str_args = eval_str_args();
                    Ok(crate::planner::datetime::fn_strftime(&str_args)
                        .map(Value::Text).unwrap_or(Value::Null))
                },
                "NOW"       => Ok(Value::Text(
                    crate::planner::datetime::fn_datetime(&vec!["now".into()])
                        .unwrap_or_default())),
                _ => Ok(Value::Null),
            }
        },

        Expr::ScalarSubquery(_) | Expr::InSubquery { .. } | Expr::Exists { .. } => {
            // 子查詢 expr 需要 Executor，在 exec_subquery_expr 中處理
            // 這裡回傳 sentinel，呼叫端應先透過 resolve_subquery_exprs 預處理
            Err("subquery expressions must be resolved before eval_expr".to_string())
        }

        _ => Err(format!("unsupported expr: {:?}", expr)),
    }
}

fn eval_aggregate(expr: &Expr, rows: &[Row], cols: &[String]) -> Result<Value, String> {
    if let Expr::Function { name, args, .. } = expr {
        let vals: Vec<Value> = rows.iter().map(|r| {
            if args.is_empty() || matches!(args[0], Expr::Column { name: ref n, .. } if n == "*") {
                Ok(Value::Integer(1))
            } else { eval_expr(&args[0], r, cols) }
        }).collect::<Result<_, _>>()?;

        match name.as_str() {
            "COUNT" => Ok(Value::Integer(vals.iter().filter(|v| !matches!(v, Value::Null)).count() as i64)),
            "SUM" => {
                let s: f64 = vals.iter().filter_map(|v| match v {
                    Value::Integer(i) => Some(*i as f64), Value::Float(f) => Some(*f), _ => None }).sum();
                Ok(Value::Float(s))
            }
            "AVG" => {
                let ns: Vec<f64> = vals.iter().filter_map(|v| match v {
                    Value::Integer(i) => Some(*i as f64), Value::Float(f) => Some(*f), _ => None }).collect();
                if ns.is_empty() { Ok(Value::Null) } else { Ok(Value::Float(ns.iter().sum::<f64>() / ns.len() as f64)) }
            }
            "MAX" => Ok(vals.into_iter().filter(|v| !matches!(v, Value::Null)).max_by(cmp_val).unwrap_or(Value::Null)),
            "MIN" => Ok(vals.into_iter().filter(|v| !matches!(v, Value::Null)).min_by(cmp_val).unwrap_or(Value::Null)),
            _ => Ok(Value::Null),
        }
    } else if !rows.is_empty() {
        eval_expr(expr, &rows[0], cols)
    } else {
        Ok(Value::Null)
    }
}

fn eval_binop(op: &BinOp, l: Value, r: Value) -> Result<Value, String> {
    match op {
        BinOp::And => Ok(Value::Boolean(is_truthy(&l) && is_truthy(&r))),
        BinOp::Or  => Ok(Value::Boolean(is_truthy(&l) || is_truthy(&r))),
        BinOp::Eq    => Ok(Value::Boolean(cmp_val(&l, &r) == std::cmp::Ordering::Equal)),
        BinOp::NotEq => Ok(Value::Boolean(cmp_val(&l, &r) != std::cmp::Ordering::Equal)),
        BinOp::Lt    => Ok(Value::Boolean(cmp_val(&l, &r) == std::cmp::Ordering::Less)),
        BinOp::LtEq  => Ok(Value::Boolean(cmp_val(&l, &r) != std::cmp::Ordering::Greater)),
        BinOp::Gt    => Ok(Value::Boolean(cmp_val(&l, &r) == std::cmp::Ordering::Greater)),
        BinOp::GtEq  => Ok(Value::Boolean(cmp_val(&l, &r) != std::cmp::Ordering::Less)),
        BinOp::Add => num_op(l, r, |a,b| a+b, |a,b| a+b),
        BinOp::Sub => num_op(l, r, |a,b| a-b, |a,b| a-b),
        BinOp::Mul => num_op(l, r, |a,b| a*b, |a,b| a*b),
        BinOp::Div => num_op(l, r, |a,b| a/b, |a,b| a/b),
        BinOp::Mod => num_op(l, r, |a,b| a%b, |a,b| a%b),
        BinOp::Concat => match (l, r) {
            (Value::Text(a), Value::Text(b)) => Ok(Value::Text(a + &b)),
            _ => Err("|| requires TEXT".into()),
        },
    }
}

fn num_op(l: Value, r: Value, ii: impl Fn(i64,i64)->i64, ff: impl Fn(f64,f64)->f64) -> Result<Value, String> {
    match (l, r) {
        (Value::Integer(a), Value::Integer(b)) => Ok(Value::Integer(ii(a, b))),
        (Value::Float(a),   Value::Float(b))   => Ok(Value::Float(ff(a, b))),
        (Value::Integer(a), Value::Float(b))   => Ok(Value::Float(ff(a as f64, b))),
        (Value::Float(a),   Value::Integer(b)) => Ok(Value::Float(ff(a, b as f64))),
        _ => Err("type error in arithmetic".into()),
    }
}

fn eval_literal(expr: &Expr) -> Result<Value, String> {
    match expr {
        Expr::LitInt(v)   => Ok(Value::Integer(*v)),
        Expr::LitFloat(v) => Ok(Value::Float(*v)),
        Expr::LitStr(s)   => Ok(Value::Text(s.clone())),
        Expr::LitBool(b)  => Ok(Value::Boolean(*b)),
        Expr::LitNull     => Ok(Value::Null),
        // 負數字面值（parser 會產生 UnaryOp Neg）
        Expr::UnaryOp { op: UnaryOp::Neg, expr } => match eval_literal(expr)? {
            Value::Integer(i) => Ok(Value::Integer(-i)),
            Value::Float(f)   => Ok(Value::Float(-f)),
            v => Err(format!("cannot negate {:?}", v)),
        },
        _ => Err(format!("expected literal, got {:?}", expr)),
    }
}

fn expr_to_key(expr: &Expr) -> Result<Key, String> {
    match expr {
        Expr::LitInt(v) => Ok(Key::Integer(*v)),
        Expr::LitStr(s) => Ok(Key::Text(s.clone())),
        _ => Err("unsupported key expression".into()),
    }
}

fn row_to_key(row: &Row) -> Result<Key, String> {
    match row.values.first() {
        Some(Value::Integer(v)) => Ok(Key::Integer(*v)),
        Some(Value::Text(s))    => Ok(Key::Text(s.clone())),
        _ => Err("cannot extract key from row".into()),
    }
}

fn is_truthy(v: &Value) -> bool {
    match v {
        Value::Boolean(b)  => *b,
        Value::Integer(i)  => *i != 0,
        Value::Float(f)    => *f != 0.0,
        Value::Text(s)     => !s.is_empty(),
        Value::Null        => false,
    }
}

fn cmp_val(a: &Value, b: &Value) -> std::cmp::Ordering {
    use std::cmp::Ordering::*;
    match (a, b) {
        (Value::Null, Value::Null) => Equal,
        (Value::Null, _) => Less,
        (_, Value::Null) => Greater,
        (Value::Integer(x), Value::Integer(y)) => x.cmp(y),
        (Value::Float(x),   Value::Float(y))   => x.partial_cmp(y).unwrap_or(Equal),
        (Value::Integer(x), Value::Float(y))   => (*x as f64).partial_cmp(y).unwrap_or(Equal),
        (Value::Float(x),   Value::Integer(y)) => x.partial_cmp(&(*y as f64)).unwrap_or(Equal),
        (Value::Text(x),    Value::Text(y))    => x.cmp(y),
        (Value::Boolean(x), Value::Boolean(y)) => x.cmp(y),
        _ => Equal,
    }
}

fn sql_like(s: &str, pat: &str) -> bool {
    let s: Vec<char> = s.chars().collect();
    let p: Vec<char> = pat.chars().collect();
    like_match(&s, &p)
}

fn like_match(s: &[char], p: &[char]) -> bool {
    match (s, p) {
        (_, [])              => s.is_empty(),
        (_, ['%', rest @ ..]) => {
            if rest.is_empty() { return true; }
            (0..=s.len()).any(|i| like_match(&s[i..], rest))
        }
        ([], _) => false,
        ([sc, sr @ ..], [pc, pr @ ..]) => {
            (*pc == '_' || pc.to_uppercase().eq(sc.to_uppercase())) && like_match(sr, pr)
        }
    }
}

fn expr_name(expr: &Expr) -> String {
    match expr {
        Expr::Column { name, .. }   => name.clone(),
        Expr::Function { name, .. } => name.clone(),
        _ => "?".into(),
    }
}

// ── 測試 ─────────────────────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser::parse;
    use crate::planner::planner::Planner;

    fn run(exec: &mut Executor, sql: &str) -> ResultSet {
        let stmts = parse(sql).unwrap_or_else(|e| panic!("parse: {}", e));
        let mut last = ResultSet::empty();
        for stmt in stmts {
            let plan = Planner::new(exec.catalog()).plan(stmt)
                .unwrap_or_else(|e| panic!("plan: {}", e));
            last = exec.execute(plan).unwrap_or_else(|e| panic!("exec: {}", e));
        }
        last
    }

    fn setup() -> Executor {
        let mut e = Executor::new();
        run(&mut e, "CREATE TABLE users (id INTEGER, name TEXT, age INTEGER)");
        run(&mut e, "INSERT INTO users VALUES (1, 'Alice', 30)");
        run(&mut e, "INSERT INTO users VALUES (2, 'Bob',   25)");
        run(&mut e, "INSERT INTO users VALUES (3, 'Carol', 35)");
        e
    }

    #[test]
    fn create_and_select_all() {
        let mut e = setup();
        let r = run(&mut e, "SELECT * FROM users");
        assert_eq!(r.row_count(), 3);
        assert_eq!(r.columns, vec!["id", "name", "age"]);
    }

    #[test]
    fn select_where_eq() {
        let mut e = setup();
        let r = run(&mut e, "SELECT * FROM users WHERE id = 2");
        assert_eq!(r.row_count(), 1);
        assert_eq!(r.rows[0][1], Value::Text("Bob".into()));
    }

    #[test]
    fn select_projection() {
        let mut e = setup();
        let r = run(&mut e, "SELECT name, age FROM users");
        assert_eq!(r.columns, vec!["name", "age"]);
        assert_eq!(r.row_count(), 3);
    }

    #[test]
    fn select_order_by() {
        let mut e = setup();
        let r = run(&mut e, "SELECT * FROM users ORDER BY age ASC");
        assert_eq!(r.rows[0][1], Value::Text("Bob".into()));
        assert_eq!(r.rows[2][1], Value::Text("Carol".into()));
    }

    #[test]
    fn select_limit_offset() {
        let mut e = setup();
        let r = run(&mut e, "SELECT * FROM users ORDER BY id ASC LIMIT 2 OFFSET 1");
        assert_eq!(r.row_count(), 2);
        assert_eq!(r.rows[0][0], Value::Integer(2));
    }

    #[test]
    fn select_where_like() {
        let mut e = setup();
        let r = run(&mut e, "SELECT * FROM users WHERE name LIKE 'A%'");
        assert_eq!(r.row_count(), 1);
        assert_eq!(r.rows[0][1], Value::Text("Alice".into()));
    }

    #[test]
    fn select_where_between() {
        let mut e = setup();
        let r = run(&mut e, "SELECT * FROM users WHERE age BETWEEN 25 AND 32");
        assert_eq!(r.row_count(), 2);
    }

    #[test]
    fn select_where_in() {
        let mut e = setup();
        let r = run(&mut e, "SELECT * FROM users WHERE id IN (1, 3)");
        assert_eq!(r.row_count(), 2);
    }

    #[test]
    fn select_count() {
        let mut e = setup();
        let r = run(&mut e, "SELECT COUNT(*) FROM users");
        assert_eq!(r.rows[0][0], Value::Integer(3));
    }

    #[test]
    fn select_max_min() {
        let mut e = setup();
        let r = run(&mut e, "SELECT MAX(age), MIN(age) FROM users");
        assert_eq!(r.rows[0][0], Value::Integer(35));
        assert_eq!(r.rows[0][1], Value::Integer(25));
    }

    #[test]
    fn update_row() {
        let mut e = setup();
        run(&mut e, "UPDATE users SET age = 99 WHERE id = 1");
        let r = run(&mut e, "SELECT age FROM users WHERE id = 1");
        assert_eq!(r.rows[0][0], Value::Integer(99));
    }

    #[test]
    fn delete_row() {
        let mut e = setup();
        run(&mut e, "DELETE FROM users WHERE id = 2");
        let r = run(&mut e, "SELECT * FROM users");
        assert_eq!(r.row_count(), 2);
    }

    #[test]
    fn drop_table() {
        let mut e = setup();
        run(&mut e, "DROP TABLE users");
        assert!(!e.catalog().table_exists("users"));
    }

    #[test]
    fn transaction_stmts() {
        let mut e = Executor::new();
        run(&mut e, "BEGIN");
        run(&mut e, "CREATE TABLE t (id INTEGER)");
        run(&mut e, "COMMIT");
    }

    #[test]
    fn inner_join() {
        let mut e = Executor::new();
        run(&mut e, "CREATE TABLE orders (order_id INTEGER, user_id INTEGER, amount REAL)");
        run(&mut e, "INSERT INTO orders VALUES (1, 1, 99.9)");
        run(&mut e, "INSERT INTO orders VALUES (2, 2, 50.0)");
        let mut e2 = setup();
        // 重建 orders 在同一個 executor
        run(&mut e2, "CREATE TABLE orders (order_id INTEGER, user_id INTEGER, amount REAL)");
        run(&mut e2, "INSERT INTO orders VALUES (1, 1, 99.9)");
        run(&mut e2, "INSERT INTO orders VALUES (2, 2, 50.0)");
        let r = run(&mut e2, "SELECT * FROM users JOIN orders ON users.id = orders.user_id");
        assert_eq!(r.row_count(), 2);
    }

    #[test]
    fn string_functions() {
        let mut e = setup();
        let r = run(&mut e, "SELECT UPPER(name) FROM users WHERE id = 1");
        assert_eq!(r.rows[0][0], Value::Text("ALICE".into()));
    }

    #[test]
    fn math_functions() {
        let mut e = Executor::new();
        run(&mut e, "CREATE TABLE t (id INTEGER, val REAL)");
        run(&mut e, "INSERT INTO t VALUES (1, -3.7)");
        let r = run(&mut e, "SELECT ABS(val), ROUND(val, 1), CEIL(val), FLOOR(val) FROM t");
        assert_eq!(r.rows[0][0], Value::Float(3.7));
        assert_eq!(r.rows[0][1], Value::Float(-3.7));
        assert_eq!(r.rows[0][2], Value::Float(-3.0));
        assert_eq!(r.rows[0][3], Value::Float(-4.0));
    }

    #[test]
    fn string_functions_extended() {
        let mut e = setup();
        let r = run(&mut e, "SELECT SUBSTR(name, 1, 3) FROM users WHERE id = 1");
        assert_eq!(r.rows[0][0], Value::Text("Ali".into()));
        let r = run(&mut e, "SELECT TRIM('  hello  ')");
        assert_eq!(r.rows[0][0], Value::Text("hello".into()));
        let r = run(&mut e, "SELECT REPLACE(name, 'Alice', 'Alicia') FROM users WHERE id = 1");
        assert_eq!(r.rows[0][0], Value::Text("Alicia".into()));
        let r = run(&mut e, "SELECT LENGTH(name) FROM users WHERE id = 1");
        assert_eq!(r.rows[0][0], Value::Integer(5));
    }

    #[test]
    fn datetime_functions() {
        let mut e = Executor::new();
        run(&mut e, "CREATE TABLE events (id INTEGER, dt TEXT)");
        run(&mut e, "INSERT INTO events VALUES (1, '2024-03-15 10:30:00')");
        let r = run(&mut e, "SELECT DATE(dt), TIME(dt) FROM events WHERE id = 1");
        assert_eq!(r.rows[0][0], Value::Text("2024-03-15".into()));
        assert_eq!(r.rows[0][1], Value::Text("10:30:00".into()));
        let r = run(&mut e, "SELECT DATE('2024-03-15', '+5 days') FROM events WHERE id = 1");
        assert_eq!(r.rows[0][0], Value::Text("2024-03-20".into()));
        let r = run(&mut e, "SELECT STRFTIME('%Y/%m/%d', dt) FROM events WHERE id = 1");
        assert_eq!(r.rows[0][0], Value::Text("2024/03/15".into()));
    }

    #[test]
    fn not_null_constraint() {
        let mut e = Executor::new();
        run(&mut e, "CREATE TABLE t (id INTEGER, name TEXT NOT NULL)");
        let stmts = crate::parser::parse("INSERT INTO t VALUES (1, NULL)").unwrap();
        let plan = crate::planner::planner::Planner::new(e.catalog()).plan(stmts.into_iter().next().unwrap()).unwrap();
        assert!(e.execute(plan).is_err(), "NOT NULL should reject NULL");
        // non-null should succeed
        run(&mut e, "INSERT INTO t VALUES (2, 'Alice')");
        let r = run(&mut e, "SELECT * FROM t");
        assert_eq!(r.row_count(), 1);
    }

    #[test]
    fn unique_constraint() {
        let mut e = Executor::new();
        run(&mut e, "CREATE TABLE t (id INTEGER, email TEXT UNIQUE)");
        run(&mut e, "INSERT INTO t VALUES (1, 'alice@test.com')");
        let stmts = crate::parser::parse("INSERT INTO t VALUES (2, 'alice@test.com')").unwrap();
        let plan = crate::planner::planner::Planner::new(e.catalog()).plan(stmts.into_iter().next().unwrap()).unwrap();
        assert!(e.execute(plan).is_err(), "UNIQUE should reject duplicate");
    }

    #[test]
    fn subquery_in_where() {
        let mut e = setup();
        // IN subquery
        let r = run(&mut e, "SELECT * FROM users WHERE id IN (SELECT id FROM users WHERE age > 28)");
        // Alice(30) and Carol(35) qualify
        assert_eq!(r.row_count(), 2);
    }

    #[test]
    fn scalar_subquery() {
        let mut e = setup();
        let r = run(&mut e, "SELECT name FROM users WHERE age = (SELECT MAX(age) FROM users)");
        assert_eq!(r.row_count(), 1);
        assert_eq!(r.rows[0][0], Value::Text("Carol".into()));
    }

    #[test]
    fn cte_basic() {
        let mut e = setup();
        let r = run(&mut e, "WITH old_users AS (SELECT * FROM users WHERE age >= 30) SELECT name FROM old_users");
        // Alice(30) and Carol(35)
        assert_eq!(r.row_count(), 2);
    }

    #[test]
    fn cte_chained() {
        let mut e = setup();
        let r = run(&mut e,
            "WITH u AS (SELECT * FROM users WHERE age > 20),                   old AS (SELECT * FROM u WHERE age >= 30)              SELECT name FROM old ORDER BY name ASC");
        assert_eq!(r.row_count(), 2);
        assert_eq!(r.rows[0][0], Value::Text("Alice".into()));
    }

    #[test]
    fn ifnull_coalesce() {
        let mut e = Executor::new();
        run(&mut e, "CREATE TABLE t (id INTEGER, val TEXT)");
        run(&mut e, "INSERT INTO t VALUES (1, NULL)");
        let r = run(&mut e, "SELECT IFNULL(val, 'default') FROM t");
        assert_eq!(r.rows[0][0], Value::Text("default".into()));
        let r = run(&mut e, "SELECT COALESCE(val, 'fallback') FROM t");
        assert_eq!(r.rows[0][0], Value::Text("fallback".into()));
    }

    #[test]
    fn nullif_test() {
        let mut e = setup();
        let r = run(&mut e, "SELECT NULLIF(age, 30) FROM users WHERE id = 1");
        assert_eq!(r.rows[0][0], Value::Null);
        let r = run(&mut e, "SELECT NULLIF(age, 99) FROM users WHERE id = 1");
        assert_eq!(r.rows[0][0], Value::Integer(30));
    }
}
