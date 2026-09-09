//! Query executor — runs SQL queries against KV stores

use crate::engine::StorageEngine;
use crate::error::{Error, Result};
use crate::sql::parser::parse;
use super::json_path::eval_expr;
use std::sync::atomic::{AtomicUsize, Ordering};

fn apply_group_by(
    rows: Vec<(Vec<u8>, Vec<u8>)>,
    group_by: &[crate::sql::parser::ast::Expr],
    having: &Option<crate::sql::parser::ast::Expr>,
    columns: &[crate::sql::parser::ast::SelectItem],
) -> Result<Vec<(Vec<u8>, Vec<u8>)>> {
    use std::collections::HashMap;
    use crate::sql::parser::ast::Expr;
    use crate::sql::parser::ast::{BinOp, SelectItem};

    if group_by.is_empty() {
        return Ok(rows);
    }

    let mut groups: HashMap<String, Vec<(Vec<u8>, Vec<u8>)>> = HashMap::new();

    for (k, v) in rows {
        let group_key = match &group_by[0] {
            Expr::Column { table: _, name } if name == "key" => {
                String::from_utf8_lossy(&k).to_string()
            }
            Expr::Column { table: _, name } if name == "value" => {
                String::from_utf8_lossy(&v).to_string()
            }
            Expr::Column { table: _, name } => {
                let val = String::from_utf8_lossy(&v);
                json_path_get(&val, &[name.clone()])
            }
            Expr::JsonPath { path, .. } => {
                let val = String::from_utf8_lossy(&v);
                json_path_get(&val, path)
            }
            _ => String::from_utf8_lossy(&v).to_string(),
        };
        groups.entry(group_key).or_insert_with(Vec::new).push((k, v));
    }

    let mut result: Vec<(Vec<u8>, Vec<u8>)> = Vec::new();

    for (group_key, group_rows) in groups {
        let grouped_row = group_key.clone().into_bytes();

        let value = if columns.iter().any(|c| matches!(c, SelectItem::Expr { expr: Expr::Function { name, .. }, .. } if name.eq_ignore_ascii_case("count"))) {
            group_rows.len().to_string()
        } else if columns.iter().any(|c| matches!(c, SelectItem::Expr { expr: Expr::Function { name, .. }, .. } if name.eq_ignore_ascii_case("sum"))) {
            let sum: f64 = group_rows.iter()
                .filter_map(|(_, v)| String::from_utf8_lossy(v).parse::<f64>().ok())
                .sum();
            sum.to_string()
        } else if columns.iter().any(|c| matches!(c, SelectItem::Expr { expr: Expr::Function { name, .. }, .. } if name.eq_ignore_ascii_case("avg"))) {
            let sum: f64 = group_rows.iter()
                .filter_map(|(_, v)| String::from_utf8_lossy(v).parse::<f64>().ok())
                .sum();
            let count = group_rows.len() as f64;
            if count > 0.0 {
                (sum / count).to_string()
            } else {
                "0".to_string()
            }
        } else if columns.iter().any(|c| matches!(c, SelectItem::Expr { expr: Expr::Function { name, .. }, .. } if name.eq_ignore_ascii_case("min"))) {
            group_rows.iter()
                .filter_map(|(_, v)| String::from_utf8_lossy(v).parse::<f64>().ok())
                .fold(f64::INFINITY, f64::min)
                .to_string()
        } else if columns.iter().any(|c| matches!(c, SelectItem::Expr { expr: Expr::Function { name, .. }, .. } if name.eq_ignore_ascii_case("max"))) {
            group_rows.iter()
                .filter_map(|(_, v)| String::from_utf8_lossy(v).parse::<f64>().ok())
                .fold(f64::NEG_INFINITY, f64::max)
                .to_string()
        } else {
            String::from_utf8_lossy(&group_rows[0].1).to_string()
        };

        if let Some(ref having_expr) = having {
            let mut passed = true;
            if let Expr::BinOp { left, op, right } = having_expr {
                if let Expr::Function { name: func_name, .. } = left.as_ref() {
                    let rhs = match right.as_ref() {
                        Expr::LitInt(n) => *n as f64,
                        Expr::LitFloat(f) => *f,
                        _ => 0.0,
                    };
                    let agg_value = value.parse::<f64>().unwrap_or(0.0);
                    passed = match op {
                        BinOp::Gt => agg_value > rhs,
                        BinOp::GtEq => agg_value >= rhs,
                        BinOp::Lt => agg_value < rhs,
                        BinOp::LtEq => agg_value <= rhs,
                        BinOp::Eq => (agg_value - rhs).abs() < 1e-9,
                        BinOp::NotEq => (agg_value - rhs).abs() >= 1e-9,
                        _ => true,
                    };
                }
            }
            if !passed {
                continue;
            }
        }

        result.push((grouped_row, value.into_bytes()));
    }

    Ok(result)
}

fn json_path_get(json_str: &str, path: &[String]) -> String {
    if let Ok(v) = serde_json::from_str::<serde_json::Value>(json_str) {
        let mut current = &v;
        for key in path {
            if let Some(next) = current.get(key) {
                current = next;
            } else {
                return String::new();
            }
        }
        return match current {
            serde_json::Value::String(s) => s.clone(),
            serde_json::Value::Number(n) => n.to_string(),
            serde_json::Value::Bool(b) => b.to_string(),
            serde_json::Value::Null => String::new(),
            _ => current.to_string(),
        };
    }
    String::new()
}

fn collect_subquery_values(
    query: &crate::sql::parser::ast::SelectStmt,
    engine: &dyn StorageEngine,
) -> Vec<String> {
    use crate::sql::parser::ast::SelectItem;

    let main_table = match &query.from {
        Some(from_item) => get_table_name_from_from_item(from_item),
        None => return vec![],
    };

    let prefix = get_table_prefix(&main_table);
    let end = format!("{};", main_table);
    let rows = match engine.scan(1, &prefix, end.as_bytes()) {
        Ok(r) => r,
        Err(_) => return vec![],
    };

    if query.columns.is_empty() {
        return rows.iter().map(|(_, v)| String::from_utf8_lossy(v).to_string()).collect();
    }

    let mut values = Vec::new();
    for row in &rows {
        let val = String::from_utf8_lossy(&row.1).to_string();
        if let crate::sql::parser::ast::SelectItem::Expr { expr, .. } = &query.columns[0] {
            match expr {
                crate::sql::parser::ast::Expr::Column { name, .. } if name == "key" => {
                    values.push(String::from_utf8_lossy(&row.0).to_string());
                }
                crate::sql::parser::ast::Expr::Column { name, .. } => {
                    values.push(json_path_get(&val, &[name.clone()]));
                }
                crate::sql::parser::ast::Expr::JsonPath { path, .. } => {
                    values.push(json_path_get(&val, path));
                }
                crate::sql::parser::ast::Expr::LitStr(s) => {
                    values.push(s.clone());
                }
                crate::sql::parser::ast::Expr::LitInt(i) => {
                    values.push(i.to_string());
                }
                _ => {
                    values.push(val);
                }
            }
        } else {
            values.push(val);
        }
    }
    values
}

fn eval_expr_with_subqueries(
    expr: &crate::sql::parser::ast::Expr,
    value: &[u8],
    engine: &dyn StorageEngine,
) -> bool {
    use crate::sql::parser::ast::Expr;

    match expr {
        Expr::Exists { query, negated } => {
            let values = collect_subquery_values(query, engine);
            let exists = !values.is_empty();
            if *negated { !exists } else { exists }
        }
        Expr::InSubquery { expr: left_expr, query, negated } => {
            let values = collect_subquery_values(query, engine);
            let left_val = match left_expr.as_ref() {
                Expr::Column { name, .. } if name == "key" => String::from_utf8_lossy(value).to_string(),
                Expr::Column { name, .. } => {
                    let json_str = String::from_utf8_lossy(value);
                    json_path_get(&json_str, &[name.clone()])
                }
                Expr::JsonPath { path, .. } => {
                    let json_str = String::from_utf8_lossy(value);
                    json_path_get(&json_str, path)
                }
                _ => String::from_utf8_lossy(value).to_string(),
            };
            let found = values.contains(&left_val);
            if *negated { !found } else { found }
        }
        Expr::BinOp { left, op, right } => {
            let left_result = eval_expr_with_subqueries(left, value, engine);
            let right_result = eval_expr_with_subqueries(right, value, engine);
            match op {
                crate::sql::parser::ast::BinOp::And => left_result && right_result,
                crate::sql::parser::ast::BinOp::Or => left_result || right_result,
                _ => eval_expr(expr, value), // Fall back for regular comparisons
            }
        }
        Expr::UnaryOp { op: crate::sql::parser::ast::UnaryOp::Not, expr } => {
            !eval_expr_with_subqueries(expr, value, engine)
        }
        _ => eval_expr(expr, value), // Fall back to regular eval
    }
}

fn get_table_name_from_from_item(from: &crate::sql::parser::ast::FromItem) -> String {
    match from {
        crate::sql::parser::ast::FromItem::Table(table_ref) => table_ref.name.clone(),
        crate::sql::parser::ast::FromItem::Subquery { alias, .. } => alias.clone(),
    }
}

fn get_table_prefix(table_name: &str) -> Vec<u8> {
    format!("{}:", table_name).into_bytes()
}

fn eval_join_condition(
    expr: &crate::sql::parser::ast::Expr,
    left_key: &[u8],
    left_val: &[u8],
    right_key: &[u8],
    right_val: &[u8],
) -> bool {
    use crate::sql::parser::ast::{BinOp, Expr};

    match expr {
        Expr::BinOp { left, op, right } => {
            match op {
                BinOp::And => {
                    eval_join_condition(left, left_key, left_val, right_key, right_val)
                        && eval_join_condition(right, left_key, left_val, right_key, right_val)
                }
                BinOp::Or => {
                    eval_join_condition(left, left_key, left_val, right_key, right_val)
                        || eval_join_condition(right, left_key, left_val, right_key, right_val)
                }
                _ => {
                    let left_val_str = String::from_utf8_lossy(left_val);
                    let right_val_str = String::from_utf8_lossy(right_val);

                    let left_str = match left.as_ref() {
                        Expr::Column { table: _, name } => {
                            if name == "key" {
                                String::from_utf8_lossy(left_key).to_string()
                            } else {
                                json_path_get(&left_val_str, &[name.clone()])
                            }
                        }
                        Expr::JsonPath { path, .. } => json_path_get(&left_val_str, path),
                        _ => return false,
                    };

                    let right_str = match right.as_ref() {
                        Expr::Column { table: _, name } => {
                            if name == "key" {
                                String::from_utf8_lossy(right_key).to_string()
                            } else {
                                json_path_get(&right_val_str, &[name.clone()])
                            }
                        }
                        Expr::JsonPath { path, .. } => json_path_get(&right_val_str, path),
                        _ => return false,
                    };

                    match op {
                        BinOp::Eq => left_str == right_str,
                        BinOp::NotEq => left_str != right_str,
                        BinOp::Lt => left_str < right_str,
                        BinOp::LtEq => left_str <= right_str,
                        BinOp::Gt => left_str > right_str,
                        BinOp::GtEq => left_str >= right_str,
                        _ => false,
                    }
                }
            }
        }
        _ => false,
    }
}

fn merge_rows(left_key: &[u8], left_val: &[u8], right_key: &[u8], right_val: &[u8], columns: &[crate::sql::parser::ast::SelectItem]) -> Vec<String> {
    vec![
        String::from_utf8_lossy(left_key).to_string(),
        String::from_utf8_lossy(left_val).to_string(),
        String::from_utf8_lossy(right_key).to_string(),
        String::from_utf8_lossy(right_val).to_string(),
    ]
}

static NEXT_ID: AtomicUsize = AtomicUsize::new(1);

#[derive(Debug, Clone, Default)]
pub struct ResultSet {
    pub columns: Vec<String>,
    pub rows: Vec<Vec<String>>,
    pub affected: usize,
}

#[derive(Debug, Clone, Default)]
pub struct TableStats {
    pub row_count: u64,
    pub total_size: u64,
    pub avg_row_size: f64,
}

#[derive(Debug, Clone, Default)]
pub struct ExecutorStats {
    pub table_stats: std::collections::HashMap<String, TableStats>,
}

pub struct Executor {
    engine: Box<dyn StorageEngine>,
    views: std::collections::HashMap<String, crate::sql::parser::ast::SelectStmt>,
    stats: ExecutorStats,
}

impl Executor {
    pub fn new(engine: Box<dyn StorageEngine>) -> Self {
        Self { engine, views: std::collections::HashMap::new(), stats: ExecutorStats::default() }
    }

    pub fn execute(&mut self, sql: &str) -> Result<ResultSet> {
        let stmts = parse(sql).map_err(|e| Error::Sql(e.to_string()))?;

        if stmts.is_empty() {
            return Ok(ResultSet::default());
        }

        let stmt = &stmts[0];

        match stmt {
            crate::sql::parser::ast::Statement::Select(select) => {
                self.execute_select(select)
            }
            crate::sql::parser::ast::Statement::CreateView(view_stmt) => {
                self.execute_create_view(view_stmt)
            }
            crate::sql::parser::ast::Statement::DropView(drop_stmt) => {
                self.execute_drop_view(drop_stmt)
            }
            crate::sql::parser::ast::Statement::Insert(insert) => {
                self.execute_insert(insert)
            }
            crate::sql::parser::ast::Statement::Update(update) => {
                self.execute_update(update)
            }
            crate::sql::parser::ast::Statement::Delete(delete) => {
                self.execute_delete(delete)
            }
            crate::sql::parser::ast::Statement::CreateTable(_) => {
                Ok(ResultSet { columns: vec![], rows: vec![], affected: 0 })
            }
            crate::sql::parser::ast::Statement::DropTable(_) => {
                Ok(ResultSet { columns: vec![], rows: vec![], affected: 0 })
            }
            crate::sql::parser::ast::Statement::CreateVirtualTable(_) => {
                Ok(ResultSet { columns: vec![], rows: vec![], affected: 0 })
            }
            crate::sql::parser::ast::Statement::Vacuum => {
                self.execute_vacuum()
            }
            crate::sql::parser::ast::Statement::Analyze(analyze) => {
                self.execute_analyze(analyze)
            }
            crate::sql::parser::ast::Statement::Backup(backup) => {
                self.execute_backup(backup)
            }
            _ => Err(Error::Sql("Unsupported statement".into())),
        }
    }

    fn execute_select(&mut self, select: &crate::sql::parser::ast::SelectStmt) -> Result<ResultSet> {
        let from_item = select.from.as_ref().ok_or_else(|| Error::Sql("No table specified".into()))?;
        let main_table = get_table_name_from_from_item(from_item);

        if let Some(view_query) = self.views.get(&main_table).cloned() {
            return self.execute_select(&view_query);
        }

        let start = get_table_prefix(&main_table);
        let end = format!("{};", main_table).into_bytes();
        let mut rows = self.engine.scan(1, &start, &end)?;

        if let Some(ref where_expr) = select.where_ {
            rows.retain(|(k, v)| eval_expr_with_subqueries(where_expr, v, &*self.engine));
        }

        for join in &select.joins {
            let right_table = &join.table.name;
            let right_prefix = get_table_prefix(right_table);
            let right_rows: Vec<(Vec<u8>, Vec<u8>)> = self.engine.scan(1, &right_prefix, &format!("{}:", right_table).into_bytes())?;

            let condition_expr = match &join.condition {
                crate::sql::parser::ast::JoinCondition::On(expr) => Some(expr.clone()),
                _ => None,
            };

            let kind = &join.kind;
            let mut new_rows = Vec::new();

            match kind {
                crate::sql::parser::ast::JoinKind::Inner => {
                    for (lk, lv) in &rows {
                        for (rk, rv) in &right_rows {
                            if let Some(ref expr) = condition_expr {
                                if eval_join_condition(expr, lk, lv, rk, rv) {
                                    new_rows.push((
                                        lk.clone(),
                                        lv.clone(),
                                        rk.clone(),
                                        rv.clone(),
                                    ));
                                }
                            }
                        }
                    }
                    rows = new_rows.into_iter().map(|(lk, lv, _, _)| (lk, lv)).collect();
                }
                crate::sql::parser::ast::JoinKind::Left => {
                    let mut left_matched: Vec<bool> = vec![false; rows.len()];
                    for (li, (lk, lv)) in rows.iter().enumerate() {
                        let mut found = false;
                        for (rk, rv) in &right_rows {
                            if let Some(ref expr) = condition_expr {
                                if eval_join_condition(expr, lk, lv, rk, rv) {
                                    new_rows.push((lk.clone(), lv.clone(), rk.clone(), rv.clone()));
                                    found = true;
                                    left_matched[li] = true;
                                }
                            }
                        }
                        if !found {
                            new_rows.push((lk.clone(), lv.clone(), vec![], vec![]));
                        }
                    }
                    rows = new_rows.into_iter().map(|(lk, lv, rk, rv)| {
                        if rk.is_empty() {
                            (lk, format!("{{}}").into_bytes())
                        } else {
                            (lk, rv)
                        }
                    }).collect();
                }
                _ => {
                    return Err(Error::Sql(format!("JOIN kind {:?} not supported", kind)));
                }
            }
        }

        if !select.group_by.is_empty() {
            rows = apply_group_by(rows, &select.group_by, &select.having, &select.columns)?;
        }

        let columns = if select.columns.is_empty() {
            vec!["key".to_string(), "value".to_string()]
        } else {
            select.columns.iter().filter_map(|c| {
                match c {
                    crate::sql::parser::ast::SelectItem::Star => Some("*".to_string()),
                    crate::sql::parser::ast::SelectItem::TableStar(t) => Some(format!("{}.*", t)),
                    crate::sql::parser::ast::SelectItem::Expr { alias, .. } => alias.clone(),
                }
            }).collect()
        };

        if !select.order_by.is_empty() {
            let order = &select.order_by[0];
            rows.sort_by(|a, b| {
                let cmp = a.0.cmp(&b.0);
                if order.asc { cmp } else { cmp.reverse() }
            });
        }

        let mut result_rows: Vec<Vec<String>> = Vec::new();
        for (k, v) in &rows {
            let k_str = String::from_utf8_lossy(k).to_string();
            let v_str = String::from_utf8_lossy(v).to_string();
            
            if select.columns.is_empty() || select.columns.iter().any(|c| matches!(c, crate::sql::parser::ast::SelectItem::Star)) {
                result_rows.push(vec![k_str, v_str]);
            } else {
                let mut output_row = Vec::new();
                for col in &select.columns {
                    if let crate::sql::parser::ast::SelectItem::Expr { expr, .. } = col {
                        match expr {
                            crate::sql::parser::ast::Expr::Column { name, .. } if name == "key" => {
                                output_row.push(k_str.clone());
                            }
                            crate::sql::parser::ast::Expr::Column { name, .. } if name == "value" => {
                                output_row.push(v_str.clone());
                            }
                            crate::sql::parser::ast::Expr::Column { name, .. } => {
                                output_row.push(json_path_get(&v_str, &[name.clone()]));
                            }
                            crate::sql::parser::ast::Expr::JsonPath { path, .. } => {
                                output_row.push(json_path_get(&v_str, path));
                            }
                            _ => output_row.push(v_str.clone()),
                        }
                    } else {
                        output_row.push(v_str.clone());
                    }
                }
                result_rows.push(output_row);
            }
        }

        if let Some(limit_expr) = &select.limit {
            if let crate::sql::parser::ast::Expr::LitInt(n) = limit_expr {
                let n = *n as usize;
                if n < result_rows.len() {
                    result_rows.truncate(n);
                }
            }
        }

        Ok(ResultSet {
            columns,
            rows: result_rows,
            affected: 0,
        })
    }

    fn execute_insert(&mut self, insert: &crate::sql::parser::ast::InsertStmt) -> Result<ResultSet> {
        let table = &insert.table;

        let eval_lit = |expr: &crate::sql::parser::ast::Expr| -> String {
            match expr {
                crate::sql::parser::ast::Expr::LitStr(s) => s.clone(),
                crate::sql::parser::ast::Expr::LitInt(i) => i.to_string(),
                crate::sql::parser::ast::Expr::LitFloat(f) => f.to_string(),
                crate::sql::parser::ast::Expr::LitNull => String::new(),
                _ => "".to_string(),
            }
        };

        let mut affected = 0;
        for row in &insert.values {
            if !row.is_empty() {
                let (key, value) = if row.len() >= 2 {
                    let k = eval_lit(&row[0]);
                    let prefixed = if k.starts_with(&format!("{}:", table)) {
                        k
                    } else {
                        format!("{}:{}", table, k)
                    };
                    (prefixed, eval_lit(&row[1]))
                } else {
                    let id = NEXT_ID.fetch_add(1, Ordering::SeqCst);
                    (format!("{}:{}", table, id), eval_lit(&row[0]))
                };
                self.engine.put(1, key.as_bytes(), value.as_bytes())?;
                affected += 1;
            }
        }

        Ok(ResultSet { columns: vec![], rows: vec![], affected })
    }

    fn execute_create_view(&mut self, stmt: &crate::sql::parser::ast::CreateViewStmt) -> Result<ResultSet> {
        let query = stmt.query.as_ref().clone();
        self.views.insert(stmt.name.clone(), query);
        Ok(ResultSet { columns: vec![], rows: vec![], affected: 0 })
    }

    fn execute_drop_view(&mut self, stmt: &crate::sql::parser::ast::DropViewStmt) -> Result<ResultSet> {
        if stmt.if_exists {
            self.views.remove(&stmt.name);
        } else if let Some(_) = self.views.remove(&stmt.name) {
            // removed
        } else {
            return Err(Error::Sql(format!("View '{}' not found", stmt.name)));
        }
        Ok(ResultSet { columns: vec![], rows: vec![], affected: 0 })
    }

    fn execute_update(&mut self, update: &crate::sql::parser::ast::UpdateStmt) -> Result<ResultSet> {
        let table_prefix = get_table_prefix(&update.table);
        let table_end = format!("{};", update.table);
        let rows = self.engine.scan(1, &table_prefix, table_end.as_bytes())?;
        let mut affected = 0;

        let new_value = if !update.sets.is_empty() {
            let (_, expr) = &update.sets[0];
            match expr {
                crate::sql::parser::ast::Expr::LitStr(s) => Some(s.clone()),
                crate::sql::parser::ast::Expr::LitInt(i) => Some(i.to_string()),
                crate::sql::parser::ast::Expr::LitFloat(f) => Some(f.to_string()),
                crate::sql::parser::ast::Expr::LitNull => Some(String::new()),
                _ => None,
            }
        } else {
            None
        };

        if let Some(value) = new_value {
            for (key, val) in rows {
                if let Some(ref where_expr) = update.where_ {
                    if !eval_expr(where_expr, &val) {
                        continue;
                    }
                }
                self.engine.put(1, &key, value.as_bytes())?;
                affected += 1;
            }
        }

        Ok(ResultSet { columns: vec![], rows: vec![], affected })
    }

    fn execute_delete(&mut self, delete: &crate::sql::parser::ast::DeleteStmt) -> Result<ResultSet> {
        let table_prefix = get_table_prefix(&delete.table);
        let table_end = format!("{};", delete.table);
        let rows = self.engine.scan(1, &table_prefix, table_end.as_bytes())?;
        let mut affected = 0;

        for (key, val) in rows {
            if let Some(ref where_expr) = delete.where_ {
                if !eval_expr(where_expr, &val) {
                    continue;
                }
            }
            self.engine.delete(1, &key)?;
            affected += 1;
        }

        Ok(ResultSet { columns: vec![], rows: vec![], affected })
    }

    fn execute_vacuum(&mut self) -> Result<ResultSet> {
        match self.engine.engine_type() {
            "memory" => {
                // Memory engine: no-op, BTreeMap has no fragmentation
            }
            "btree" => {
                self.engine.flush()?;
            }
            "lsm" => {
                self.engine.flush()?;
            }
            _ => return Err(Error::Sql("Unsupported engine".into())),
        }
        Ok(ResultSet { columns: vec![], rows: vec![], affected: 0 })
    }

    fn execute_analyze(&mut self, analyze: &crate::sql::parser::ast::AnalyzeStmt) -> Result<ResultSet> {
        match &analyze.name {
            Some(table_name) => {
                self.analyze_table(table_name)?;
            }
            None => {
                let tables = ["users", "products", "orders"];
                for table in tables {
                    let _ = self.analyze_table(table);
                }
            }
        }
        Ok(ResultSet { columns: vec![], rows: vec![], affected: 0 })
    }

    fn analyze_table(&mut self, table_name: &str) -> Result<()> {
        let table_prefix = get_table_prefix(table_name);
        let table_end = format!("{};", table_name);
        let rows = self.engine.scan(1, &table_prefix, table_end.as_bytes())?;

        let row_count = rows.len() as u64;
        let total_size: u64 = rows.iter().map(|(_, v)| v.len() as u64).sum();
        let avg_row_size = if row_count > 0 {
            total_size as f64 / row_count as f64
        } else {
            0.0
        };

        let stats = TableStats {
            row_count,
            total_size,
            avg_row_size,
        };

        self.stats.table_stats.insert(table_name.to_string(), stats);
        Ok(())
    }

    fn execute_backup(&mut self, backup: &crate::sql::parser::ast::BackupStmt) -> Result<ResultSet> {
        use std::io::Write;

        let path = std::path::Path::new(&backup.path);
        let mut file = std::fs::File::create(path)
            .map_err(|e| Error::Sql(format!("Failed to create backup file: {}", e)))?;

        let mut all_data = std::collections::HashMap::new();
        let start = vec![];
        let end = vec![];
        if let Ok(rows) = self.engine.scan(1, &start, &end) {
            for (k, v) in rows {
                let key_str = String::from_utf8_lossy(&k).to_string();
                let val_str = String::from_utf8_lossy(&v).to_string();
                all_data.insert(key_str, val_str);
            }
        }

        let json = serde_json::to_vec(&all_data)
            .map_err(|e| Error::Sql(format!("Failed to serialize backup: {}", e)))?;
        file.write_all(&json)
            .map_err(|e| Error::Sql(format!("Failed to write backup: {}", e)))?;

        Ok(ResultSet { columns: vec![], rows: vec![], affected: 0 })
    }
}

impl Default for Executor {
    fn default() -> Self {
        Self::new(Box::new(crate::engine::BTreeMemoryEngine::new()))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_executor_insert_and_select() {
        let engine = crate::engine::BTreeMemoryEngine::new();
        let mut exec = Executor::new(Box::new(engine));

        exec.execute("INSERT INTO test VALUES ('{\"name\":\"Alice\",\"age\":30}')").unwrap();
        let result = exec.execute("SELECT * FROM test").unwrap();

        assert_eq!(result.rows.len(), 1, "Should have 1 row");
        assert_eq!(result.rows[0][1], "{\"name\":\"Alice\",\"age\":30}");
    }

    #[test]
    fn test_executor_multiple_insert() {
        let engine = crate::engine::BTreeMemoryEngine::new();
        let mut exec = Executor::new(Box::new(engine));

        exec.execute("INSERT INTO test VALUES ('v1')").unwrap();
        exec.execute("INSERT INTO test VALUES ('v2')").unwrap();
        exec.execute("INSERT INTO test VALUES ('v3')").unwrap();

        let result = exec.execute("SELECT * FROM test").unwrap();
        assert_eq!(result.rows.len(), 3, "Should have 3 rows");
    }

    #[test]
    fn test_json_path_filter() {
        let engine = crate::engine::BTreeMemoryEngine::new();
        let mut exec = Executor::new(Box::new(engine));

        exec.execute("INSERT INTO users VALUES ('{\"name\":\"Alice\",\"age\":30}')").unwrap();
        exec.execute("INSERT INTO users VALUES ('{\"name\":\"Bob\",\"age\":25}')").unwrap();
        exec.execute("INSERT INTO users VALUES ('{\"name\":\"Charlie\",\"age\":35}')").unwrap();

        let result = exec.execute("SELECT * FROM users WHERE @.age > 27").unwrap();
        assert_eq!(result.rows.len(), 2, "Should have 2 users with age > 27");
    }

    #[test]
    fn test_json_path_is_null() {
        let engine = crate::engine::BTreeMemoryEngine::new();
        let mut exec = Executor::new(Box::new(engine));

        exec.execute("INSERT INTO users VALUES ('{\"name\":\"Alice\"}')").unwrap();
        exec.execute("INSERT INTO users VALUES ('{\"name\":\"Bob\",\"phone\":\"123\"}')").unwrap();

        let result = exec.execute("SELECT * FROM users WHERE @.phone IS NULL").unwrap();
        assert_eq!(result.rows.len(), 1, "Should have 1 user without phone");
    }

    #[test]
    fn test_executor_insert_two_values() {
        let engine = crate::engine::BTreeMemoryEngine::new();
        let mut exec = Executor::new(Box::new(engine));

        exec.execute("INSERT INTO test VALUES ('key1', '{\"name\":\"Alice\",\"age\":30}')").unwrap();
        exec.execute("INSERT INTO test VALUES ('key2', '{\"name\":\"Bob\",\"age\":25}')").unwrap();

        let result = exec.execute("SELECT * FROM test").unwrap();
        assert_eq!(result.rows.len(), 2, "Should have 2 rows");
        assert!(result.rows[0][1].contains("Alice"), "First row should contain Alice JSON");
        assert!(result.rows[1][1].contains("Bob"), "Second row should contain Bob JSON");
    }

    #[test]
    fn test_executor_insert() {
        let engine = crate::engine::BTreeMemoryEngine::new();
        let mut exec = Executor::new(Box::new(engine));

        let result = exec.execute("INSERT INTO test VALUES ('hello')").unwrap();
        assert_eq!(result.affected, 1);
    }

    #[test]
    fn test_subquery_in_list() {
        let engine = crate::engine::BTreeMemoryEngine::new();
        let mut exec = Executor::new(Box::new(engine));

        exec.execute("INSERT INTO users VALUES ('{\"name\":\"Alice\"}')").unwrap();
        exec.execute("INSERT INTO users VALUES ('{\"name\":\"Bob\"}')").unwrap();
        exec.execute("INSERT INTO users VALUES ('{\"name\":\"Charlie\"}')").unwrap();
        exec.execute("INSERT INTO approved VALUES ('{\"name\":\"Alice\"}')").unwrap();
        exec.execute("INSERT INTO approved VALUES ('{\"name\":\"Carol\"}')").unwrap();

        let result = exec.execute(
            "SELECT * FROM users WHERE @.name IN (SELECT @.name FROM approved)"
        ).unwrap();
        assert_eq!(result.rows.len(), 1, "Should have 1 user (only Alice is in approved)");
        assert!(result.rows[0][1].contains("Alice"), "Should be Alice");
    }

    #[test]
    fn test_subquery_select_column() {
        let engine = crate::engine::BTreeMemoryEngine::new();
        let mut exec = Executor::new(Box::new(engine));

        exec.execute("INSERT INTO t1 VALUES ('key1', 'v1')").unwrap();
        exec.execute("INSERT INTO t1 VALUES ('key2', 'v2')").unwrap();
        exec.execute("INSERT INTO t1 VALUES ('key3', 'v3')").unwrap();

        let result = exec.execute("SELECT value FROM t1").unwrap();
        assert_eq!(result.rows.len(), 3, "Should have 3 rows");
        assert_eq!(result.rows[0][0], "v1", "First row value should be v1");
        assert_eq!(result.rows[1][0], "v2", "Second row value should be v2");
        assert_eq!(result.rows[2][0], "v3", "Third row value should be v3");
    }
}

// =============================================================================
// Typed Executor with compile-time capability checking
// =============================================================================

pub struct SqlExecutor<E: crate::engine::StorageEngine> {
    engine: E,
    views: std::collections::HashMap<String, crate::sql::parser::ast::SelectStmt>,
}

impl<E: crate::engine::StorageEngine> SqlExecutor<E> {
    pub fn new(engine: E) -> Self {
        Self { engine, views: std::collections::HashMap::new() }
    }

    pub fn execute_order_by(&mut self, sql: &str) -> Result<ResultSet>
    where
        E: crate::engine::CanOrderBy,
    {
        self.execute(sql)
    }

    pub fn execute_fts(&mut self, sql: &str) -> Result<ResultSet>
    where
        E: crate::engine::CanFts,
    {
        self.execute(sql)
    }

    pub fn execute_with_tx(&mut self, sql: &str) -> Result<ResultSet>
    where
        E: crate::engine::CanTransaction,
    {
        self.execute(sql)
    }

    pub fn execute(&mut self, sql: &str) -> Result<ResultSet> {
        let stmts = parse(sql).map_err(|e| Error::Sql(e.to_string()))?;

        if stmts.is_empty() {
            return Ok(ResultSet::default());
        }

        let stmt = &stmts[0];

        match stmt {
            crate::sql::parser::ast::Statement::Select(select) => {
                self.execute_select(select)
            }
            crate::sql::parser::ast::Statement::CreateView(view_stmt) => {
                self.execute_create_view(view_stmt)
            }
            crate::sql::parser::ast::Statement::DropView(drop_stmt) => {
                self.execute_drop_view(drop_stmt)
            }
            crate::sql::parser::ast::Statement::Insert(insert) => {
                self.execute_insert(insert)
            }
            crate::sql::parser::ast::Statement::Update(update) => {
                self.execute_update(update)
            }
            crate::sql::parser::ast::Statement::Delete(delete) => {
                self.execute_delete(delete)
            }
            crate::sql::parser::ast::Statement::Vacuum => {
                self.execute_vacuum()
            }
            crate::sql::parser::ast::Statement::Analyze(analyze) => {
                self.execute_analyze(analyze)
            }
            crate::sql::parser::ast::Statement::Backup(backup) => {
                self.execute_backup(backup)
            }
            _ => Err(Error::Sql("Unsupported statement".into())),
        }
    }

    fn execute_vacuum(&mut self) -> Result<ResultSet> {
        self.engine.flush()?;
        Ok(ResultSet { columns: vec![], rows: vec![], affected: 0 })
    }

    fn execute_analyze(&mut self, _analyze: &crate::sql::parser::ast::AnalyzeStmt) -> Result<ResultSet> {
        Ok(ResultSet { columns: vec![], rows: vec![], affected: 0 })
    }

    fn execute_backup(&mut self, backup: &crate::sql::parser::ast::BackupStmt) -> Result<ResultSet> {
        use std::io::Write;
        let path = std::path::Path::new(&backup.path);
        let mut file = std::fs::File::create(path)
            .map_err(|e| Error::Sql(format!("Failed to create backup file: {}", e)))?;
        let mut all_data = std::collections::HashMap::new();
        if let Ok(rows) = self.engine.scan(1, &[], &[]) {
            for (k, v) in rows {
                let key_str = String::from_utf8_lossy(&k).to_string();
                let val_str = String::from_utf8_lossy(&v).to_string();
                all_data.insert(key_str, val_str);
            }
        }
        let json = serde_json::to_vec(&all_data)
            .map_err(|e| Error::Sql(format!("Failed to serialize backup: {}", e)))?;
        file.write_all(&json)
            .map_err(|e| Error::Sql(format!("Failed to write backup: {}", e)))?;
        Ok(ResultSet { columns: vec![], rows: vec![], affected: 0 })
    }

    fn execute_select(&mut self, select: &crate::sql::parser::ast::SelectStmt) -> Result<ResultSet> {
        let from_item = select.from.as_ref().ok_or_else(|| Error::Sql("No table specified".into()))?;
        let main_table = get_table_name_from_from_item(from_item);

        if let Some(view_query) = self.views.get(&main_table).cloned() {
            return self.execute_select(&view_query);
        }

        let start = get_table_prefix(&main_table);
        let end = format!("{};", main_table).into_bytes();
        let mut rows = self.engine.scan(1, &start, &end)?;

        if let Some(ref where_expr) = select.where_ {
            rows.retain(|(k, v)| eval_expr_with_subqueries(where_expr, v, &self.engine));
        }

        if !select.group_by.is_empty() {
            rows = apply_group_by(rows, &select.group_by, &select.having, &select.columns)?;
        }

        let columns = if select.columns.is_empty() {
            vec!["key".to_string(), "value".to_string()]
        } else {
            select.columns.iter().filter_map(|c| {
                match c {
                    crate::sql::parser::ast::SelectItem::Star => Some("*".to_string()),
                    crate::sql::parser::ast::SelectItem::TableStar(t) => Some(format!("{}.*", t)),
                    crate::sql::parser::ast::SelectItem::Expr { alias, .. } => alias.clone(),
                }
            }).collect()
        };

        if !select.order_by.is_empty() {
            let order = &select.order_by[0];
            rows.sort_by(|a, b| {
                let cmp = a.0.cmp(&b.0);
                if order.asc { cmp } else { cmp.reverse() }
            });
        }

        let mut result_rows: Vec<Vec<String>> = Vec::new();
        for (k, v) in &rows {
            let k_str = String::from_utf8_lossy(k).to_string();
            let v_str = String::from_utf8_lossy(v).to_string();
            
            if select.columns.is_empty() || select.columns.iter().any(|c| matches!(c, crate::sql::parser::ast::SelectItem::Star)) {
                result_rows.push(vec![k_str, v_str]);
            } else {
                let mut output_row = Vec::new();
                for col in &select.columns {
                    if let crate::sql::parser::ast::SelectItem::Expr { expr, .. } = col {
                        match expr {
                            crate::sql::parser::ast::Expr::Column { name, .. } if name == "key" => {
                                output_row.push(k_str.clone());
                            }
                            crate::sql::parser::ast::Expr::Column { name, .. } if name == "value" => {
                                output_row.push(v_str.clone());
                            }
                            crate::sql::parser::ast::Expr::Column { name, .. } => {
                                output_row.push(json_path_get(&v_str, &[name.clone()]));
                            }
                            crate::sql::parser::ast::Expr::JsonPath { path, .. } => {
                                output_row.push(json_path_get(&v_str, path));
                            }
                            _ => output_row.push(v_str.clone()),
                        }
                    } else {
                        output_row.push(v_str.clone());
                    }
                }
                result_rows.push(output_row);
            }
        }

        if let Some(limit_expr) = &select.limit {
            if let crate::sql::parser::ast::Expr::LitInt(n) = limit_expr {
                let n = *n as usize;
                if n < result_rows.len() {
                    result_rows.truncate(n);
                }
            }
        }

        Ok(ResultSet {
            columns,
            rows: result_rows,
            affected: 0,
        })
    }

    fn execute_insert(&mut self, insert: &crate::sql::parser::ast::InsertStmt) -> Result<ResultSet> {
        let table = &insert.table;

        let eval_lit = |expr: &crate::sql::parser::ast::Expr| -> String {
            match expr {
                crate::sql::parser::ast::Expr::LitStr(s) => s.clone(),
                crate::sql::parser::ast::Expr::LitInt(i) => i.to_string(),
                crate::sql::parser::ast::Expr::LitFloat(f) => f.to_string(),
                crate::sql::parser::ast::Expr::LitNull => String::new(),
                _ => "".to_string(),
            }
        };

        let mut affected = 0;
        for row in &insert.values {
            if !row.is_empty() {
                let (key, value) = if row.len() >= 2 {
                    let k = eval_lit(&row[0]);
                    let prefixed = if k.starts_with(&format!("{}:", table)) {
                        k
                    } else {
                        format!("{}:{}", table, k)
                    };
                    (prefixed, eval_lit(&row[1]))
                } else {
                    let id = NEXT_ID.fetch_add(1, Ordering::SeqCst);
                    (format!("{}:{}", table, id), eval_lit(&row[0]))
                };
                self.engine.put(1, key.as_bytes(), value.as_bytes())?;
                affected += 1;
            }
        }

        Ok(ResultSet { columns: vec![], rows: vec![], affected })
    }

    fn execute_create_view(&mut self, stmt: &crate::sql::parser::ast::CreateViewStmt) -> Result<ResultSet> {
        let query = stmt.query.as_ref().clone();
        self.views.insert(stmt.name.clone(), query);
        Ok(ResultSet { columns: vec![], rows: vec![], affected: 0 })
    }

    fn execute_drop_view(&mut self, stmt: &crate::sql::parser::ast::DropViewStmt) -> Result<ResultSet> {
        if stmt.if_exists {
            self.views.remove(&stmt.name);
        } else if let Some(_) = self.views.remove(&stmt.name) {
            // removed
        } else {
            return Err(Error::Sql(format!("View '{}' not found", stmt.name)));
        }
        Ok(ResultSet { columns: vec![], rows: vec![], affected: 0 })
    }

    fn execute_update(&mut self, update: &crate::sql::parser::ast::UpdateStmt) -> Result<ResultSet> {
        let rows = self.engine.scan(1, b"", b"")?;
        let mut affected = 0;

        let new_value = if !update.sets.is_empty() {
            let (_, expr) = &update.sets[0];
            match expr {
                crate::sql::parser::ast::Expr::LitStr(s) => Some(s.clone()),
                crate::sql::parser::ast::Expr::LitInt(i) => Some(i.to_string()),
                crate::sql::parser::ast::Expr::LitFloat(f) => Some(f.to_string()),
                crate::sql::parser::ast::Expr::LitNull => Some(String::new()),
                _ => None,
            }
        } else {
            None
        };

        if let Some(value) = new_value {
            for (key, _) in rows {
                self.engine.put(1, &key, value.as_bytes())?;
                affected += 1;
            }
        }

        Ok(ResultSet { columns: vec![], rows: vec![], affected })
    }

    fn execute_delete(&mut self, delete: &crate::sql::parser::ast::DeleteStmt) -> Result<ResultSet> {
        let rows = self.engine.scan(1, b"", b"")?;
        let mut affected = 0;

        for (key, _) in rows {
            self.engine.delete(1, &key)?;
            affected += 1;
        }

        Ok(ResultSet { columns: vec![], rows: vec![], affected })
    }
}