//! 約束驗證（Constraint Checker）
//!
//! 支援 SQLite 相容的四種約束：
//!   - NOT NULL：欄位值不可為 NULL
//!   - UNIQUE：欄位值在整張表中不可重複（允許多個 NULL）
//!   - CHECK：自訂運算式必須為真
//!   - FOREIGN KEY：參照另一張表的主鍵（基礎版）
//!
//! 約束在 INSERT / UPDATE 時檢查，違反時回傳 Err。

use crate::table::row::{Row, Value};
use crate::table::schema::Schema;

// ── 約束定義（執行期） ────────────────────────────────────────────────────

#[derive(Debug, Clone)]
pub enum Constraint {
    NotNull  { column: String },
    Unique   { columns: Vec<String> },
    Check    { expr_sql: String },           // CHECK 運算式（原始 SQL）
    ForeignKey {
        columns:    Vec<String>,
        ref_table:  String,
        ref_columns: Vec<String>,
    },
}

/// 一張表的完整約束組合
#[derive(Debug, Clone, Default)]
pub struct TableConstraints {
    pub constraints: Vec<Constraint>,
}

impl TableConstraints {
    pub fn new() -> Self { Self::default() }

    pub fn add(&mut self, c: Constraint) { self.constraints.push(c); }

    /// 從 AST 的 ColumnDef 自動建立 NOT NULL 與 UNIQUE 約束
    pub fn from_schema(schema: &Schema) -> Self {
        let mut tc = TableConstraints::new();
        for col in &schema.columns {
            if !col.nullable {
                tc.add(Constraint::NotNull { column: col.name.clone() });
            }
        }
        tc
    }
}

// ── 驗證 ──────────────────────────────────────────────────────────────────

/// 驗證一列是否符合所有約束
/// `existing_rows`：目前表中的所有資料（用於 UNIQUE 檢查）
pub fn check_row(
    row: &Row,
    schema: &Schema,
    constraints: &TableConstraints,
    existing_rows: &[Row],
) -> Result<(), String> {
    for constraint in &constraints.constraints {
        match constraint {
            Constraint::NotNull { column } => {
                let idx = schema.index_of(column)
                    .ok_or_else(|| format!("column '{}' not found", column))?;
                if matches!(row.values.get(idx), Some(Value::Null) | None) {
                    return Err(format!("NOT NULL constraint failed: {}", column));
                }
            }

            Constraint::Unique { columns } => {
                let idxs: Vec<usize> = columns.iter()
                    .map(|c| schema.index_of(c)
                        .ok_or_else(|| format!("column '{}' not found", c)))
                    .collect::<Result<_, _>>()?;

                // NULL 不參與 UNIQUE 比較（SQLite 行為）
                let new_vals: Vec<&Value> = idxs.iter()
                    .map(|&i| row.values.get(i).unwrap_or(&Value::Null))
                    .collect();
                if new_vals.iter().any(|v| matches!(v, Value::Null)) { continue; }

                for existing in existing_rows {
                    let ex_vals: Vec<&Value> = idxs.iter()
                        .map(|&i| existing.values.get(i).unwrap_or(&Value::Null))
                        .collect();
                    if ex_vals == new_vals {
                        return Err(format!("UNIQUE constraint failed: {}",
                            columns.join(", ")));
                    }
                }
            }

            Constraint::Check { expr_sql } => {
                // 簡單 CHECK：只支援 IS NOT NULL 與比較
                // 完整實作需要把 expr_sql 送進 parser→eval_expr
                // 此處先做基礎版：始終通過（TODO: 接上 parser）
                let _ = expr_sql;
            }

            Constraint::ForeignKey { columns, ref_table, ref_columns } => {
                // 基礎版：記錄約束定義，實際驗證需要跨表查詢
                // 完整實作需要 Executor 的 get_table 存取
                let _ = (columns, ref_table, ref_columns);
            }
        }
    }
    Ok(())
}

/// 驗證刪除/更新時 FK 不被違反（基礎版：僅記錄）
pub fn check_fk_on_delete(
    _deleted_key: &Value,
    _constraints: &[TableConstraints],
) -> Result<(), String> {
    // TODO: 遍歷所有有 FK 指向此表的 TableConstraints
    Ok(())
}

// ── 從 AST ColumnDef 建立約束 ─────────────────────────────────────────────

pub fn constraints_from_ast(
    stmt: &crate::parser::ast::CreateTableStmt,
) -> TableConstraints {
    use crate::parser::ast::{ColumnConstraint, TableConstraint};
    let mut tc = TableConstraints::new();

    for col in &stmt.columns {
        for constraint in &col.constraints {
            match constraint {
                ColumnConstraint::NotNull => {
                    tc.add(Constraint::NotNull { column: col.name.clone() });
                }
                ColumnConstraint::Unique => {
                    tc.add(Constraint::Unique { columns: vec![col.name.clone()] });
                }
                ColumnConstraint::PrimaryKey { .. } => {
                    // PRIMARY KEY 隱含 NOT NULL
                    tc.add(Constraint::NotNull { column: col.name.clone() });
                }
                ColumnConstraint::Default(_) => {} // 預設值由 executor 處理
            }
        }
    }

    for tc_ast in &stmt.constraints {
        match tc_ast {
            TableConstraint::PrimaryKey(cols) => {
                for col in cols {
                    tc.add(Constraint::NotNull { column: col.clone() });
                }
                tc.add(Constraint::Unique { columns: cols.clone() });
            }
            TableConstraint::Unique(cols) => {
                tc.add(Constraint::Unique { columns: cols.clone() });
            }
        }
    }

    tc
}

// ── 測試 ─────────────────────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;
    use crate::table::schema::{Column, DataType, Schema};

    fn schema() -> Schema {
        Schema::new(vec![
            Column::new("id",    DataType::Integer),
            Column::new("email", DataType::Text),
            Column::new("age",   DataType::Integer),
        ])
    }

    fn row(id: i64, email: &str, age: i64) -> Row {
        Row::new(vec![Value::Integer(id), Value::Text(email.into()), Value::Integer(age)])
    }

    fn null_row() -> Row {
        Row::new(vec![Value::Integer(1), Value::Null, Value::Integer(20)])
    }

    #[test]
    fn not_null_passes() {
        let schema = schema();
        let mut tc = TableConstraints::new();
        tc.add(Constraint::NotNull { column: "email".into() });
        let r = row(1, "alice@example.com", 30);
        assert!(check_row(&r, &schema, &tc, &[]).is_ok());
    }

    #[test]
    fn not_null_fails() {
        let schema = schema();
        let mut tc = TableConstraints::new();
        tc.add(Constraint::NotNull { column: "email".into() });
        assert!(check_row(&null_row(), &schema, &tc, &[]).is_err());
    }

    #[test]
    fn unique_passes() {
        let schema = schema();
        let mut tc = TableConstraints::new();
        tc.add(Constraint::Unique { columns: vec!["email".into()] });
        let existing = vec![row(1, "alice@example.com", 30)];
        let new_row  = row(2, "bob@example.com", 25);
        assert!(check_row(&new_row, &schema, &tc, &existing).is_ok());
    }

    #[test]
    fn unique_fails_on_duplicate() {
        let schema = schema();
        let mut tc = TableConstraints::new();
        tc.add(Constraint::Unique { columns: vec!["email".into()] });
        let existing = vec![row(1, "alice@example.com", 30)];
        let dup_row  = row(2, "alice@example.com", 25); // 重複 email
        assert!(check_row(&dup_row, &schema, &tc, &existing).is_err());
    }

    #[test]
    fn unique_allows_multiple_nulls() {
        let schema = schema();
        let mut tc = TableConstraints::new();
        tc.add(Constraint::Unique { columns: vec!["email".into()] });
        let existing = vec![null_row()];
        let another_null = null_row();
        // 兩個 NULL 不違反 UNIQUE（SQLite 行為）
        assert!(check_row(&another_null, &schema, &tc, &existing).is_ok());
    }

    #[test]
    fn composite_unique() {
        let schema = schema();
        let mut tc = TableConstraints::new();
        tc.add(Constraint::Unique { columns: vec!["id".into(), "email".into()] });
        let existing = vec![row(1, "alice@example.com", 30)];
        // 同 id 不同 email → OK
        let r2 = row(1, "bob@example.com", 25);
        assert!(check_row(&r2, &schema, &tc, &existing).is_ok());
        // 完全相同 → Err
        let dup = row(1, "alice@example.com", 99);
        assert!(check_row(&dup, &schema, &tc, &existing).is_err());
    }

    #[test]
    fn from_ast_not_null() {
        use crate::parser::parse;
        let stmts = parse("CREATE TABLE t (id INTEGER NOT NULL, name TEXT)").unwrap();
        if let crate::parser::ast::Statement::CreateTable(stmt) = &stmts[0] {
            let tc = constraints_from_ast(stmt);
            assert!(tc.constraints.iter().any(|c| matches!(c, Constraint::NotNull { column } if column == "id")));
        }
    }

    #[test]
    fn from_ast_unique() {
        use crate::parser::parse;
        let stmts = parse("CREATE TABLE t (id INTEGER, email TEXT UNIQUE)").unwrap();
        if let crate::parser::ast::Statement::CreateTable(stmt) = &stmts[0] {
            let tc = constraints_from_ast(stmt);
            assert!(tc.constraints.iter().any(|c| matches!(c, Constraint::Unique { .. })));
        }
    }
}
