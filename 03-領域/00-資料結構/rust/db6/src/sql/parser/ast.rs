//! AST (Abstract Syntax Tree): SQL statement AST node definitions
//!
//! ## Design Philosophy
//!
//! The AST is a tree representation of SQL statements, where each node represents a syntactic structure:
//! - **Statement**: The unit of execution, e.g. SELECT, INSERT
//! - **Expr**: An expression that produces a value, e.g. `1 + 2`, `name LIKE 'A%'`
//! - **SelectItem**: Columns after SELECT
//!
//! ## Traversal
//!
//! The AST is a recursive structure, typically traversed using the visitor pattern:
//! ```text
//! SELECT name FROM users WHERE age > 18
//!         ↓
//! Statement::Select(SelectStmt {
//!     columns: [SelectItem::Expr(...)],
//!     from: Some(FromItem::Table(...)),
//!     where_: Some(Expr::BinOp(...)),
//! })
//! ```

// ── Top-level Statements ──────────────────────────────────────────────────────────────

/// Root enum for SQL statements
///
/// All executable SQL statements are parsed into one variant of this enum.
///
/// # Variant Descriptions
///
/// | Variant | SQL | Description |
/// |---------|-----|-------------|
/// | `Select` | SELECT ... | Query statement |
/// | `Insert` | INSERT INTO ... | Insert data |
/// | `Update` | UPDATE ... SET ... | Update data |
/// | `Delete` | DELETE FROM ... | Delete data |
/// | `CreateTable` | CREATE TABLE ... | Create table |
/// | `DropTable` | DROP TABLE ... | Drop table |
/// | `CreateIndex` | CREATE INDEX ... | Create index |
/// | `Begin` | BEGIN | Start transaction |
/// | `Commit` | COMMIT | Commit transaction |
/// | `Rollback` | ROLLBACK | Rollback transaction |
#[derive(Debug, Clone, PartialEq)]
pub enum Statement {
    /// SELECT query statement
    Select(SelectStmt),
    /// INSERT statement
    Insert(InsertStmt),
    /// UPDATE statement
    Update(UpdateStmt),
    /// DELETE statement
    Delete(DeleteStmt),
    /// CREATE TABLE statement
    CreateTable(CreateTableStmt),
    /// DROP TABLE statement
    DropTable(DropTableStmt),
    /// CREATE INDEX statement
    CreateIndex(CreateIndexStmt),
    /// DROP INDEX statement
    DropIndex(DropIndexStmt),
    /// ALTER TABLE statement
    AlterTable(AlterTableStmt),
    /// PRAGMA statement
    Pragma(PragmaStmt),
    /// EXPLAIN query plan
    Explain(ExplainStmt),
    /// CREATE VIEW statement
    CreateView(CreateViewStmt),
    /// DROP VIEW statement
    DropView(DropViewStmt),
    /// CREATE TRIGGER statement
    CreateTrigger(CreateTriggerStmt),
    /// DROP TRIGGER statement
    DropTrigger(DropTriggerStmt),
    /// REINDEX statement
    Reindex(ReindexStmt),
    /// ANALYZE statement
    Analyze(AnalyzeStmt),
    /// ATTACH DATABASE
    Attach { path: String, alias: String },
    /// DETACH DATABASE
    Detach { alias: String },
    /// VACUUM
    Vacuum,
    /// BACKUP
    Backup(BackupStmt),
    /// BEGIN transaction
    Begin,
    /// COMMIT transaction
    Commit,
    /// ROLLBACK transaction
    Rollback,
    /// CREATE VIRTUAL TABLE for FTS
    CreateVirtualTable(CreateVirtualTableStmt),
}

// ── SELECT ────────────────────────────────────────────────────────────────

/// SELECT query statement structure
///
/// Contains all query clauses:
/// - WITH: CTE (Common Table Expression)
/// - SELECT: DISTINCT, column list
/// - FROM: data source, JOIN
/// - WHERE: filter condition
/// - GROUP BY / HAVING: grouping
/// - ORDER BY: sorting
/// - LIMIT / OFFSET: pagination
/// - UNION: set operation
#[derive(Debug, Clone, PartialEq)]
pub struct SelectStmt {
    /// WITH ... AS (...)  Common Table Expression
    pub with:      Vec<Cte>,
    /// DISTINCT deduplication
    pub distinct:  bool,
    /// Selected column list
    pub columns:   Vec<SelectItem>,
    /// FROM clause (table name or subquery)
    pub from:      Option<FromItem>,
    /// JOIN clause list
    pub joins:     Vec<Join>,
    /// WHERE condition
    pub where_:    Option<Expr>,
    /// GROUP BY columns
    pub group_by:  Vec<Expr>,
    /// HAVING condition (post-grouping filter)
    pub having:    Option<Expr>,
    /// ORDER BY
    pub order_by:  Vec<OrderItem>,
    /// LIMIT
    pub limit:     Option<Expr>,
    /// OFFSET
    pub offset:    Option<Expr>,
    /// UNION set operation (right, is_all)
    pub union_with: Option<Box<(SelectStmt, bool)>>,
}

/// SELECT column selection item
///
/// Has three forms:
/// - `Star`: * (all columns)
/// - `TableStar`: table.* (all columns for a specific table)
/// - `Expr`: expression, optionally with an alias
#[derive(Debug, Clone, PartialEq)]
pub enum SelectItem {
    /// * all columns
    Star,
    /// table.* all columns for a specific table
    TableStar(String),
    /// Expression, optional alias
    Expr { expr: Expr, alias: Option<String> },
}

/// Table reference (with optional alias)
///
/// Used in FROM and JOIN clauses to reference tables
#[derive(Debug, Clone, PartialEq)]
pub struct TableRef {
    /// Table name
    pub name:  String,
    /// Alias (name after AS)
    pub alias: Option<String>,
}

/// FROM clause data source
///
/// Can be:
/// - A table name (with optional alias)
/// - A subquery (must have an alias)
#[derive(Debug, Clone, PartialEq)]
pub enum FromItem {
    /// Table reference
    Table(TableRef),
    /// Subquery (must have alias)
    Subquery { query: Box<SelectStmt>, alias: String },
}

/// CTE (Common Table Expression)
///
/// Syntax: `WITH name AS (query)`
///
/// # Example
/// ```sql
/// WITH active_users AS (
///     SELECT * FROM users WHERE active = true
/// )
/// SELECT * FROM active_users WHERE id > 100
/// ```
#[derive(Debug, Clone, PartialEq)]
pub struct Cte {
    /// CTE name
    pub name:  String,
    /// Query definition
    pub query: Box<SelectStmt>,
}

/// JOIN operation
///
/// Contains the join type, target table, and join condition
#[derive(Debug, Clone, PartialEq)]
pub struct Join {
    /// Join type
    pub kind:      JoinKind,
    /// Target table reference
    pub table:     TableRef,
    /// Join condition
    pub condition: JoinCondition,
}

/// JOIN type
///
/// | Type  | Description |
/// |-------|-------------|
/// | Inner | Inner join, only matching rows |
/// | Left | Left outer join, preserves all left rows |
/// | Right | Right outer join, preserves all right rows |
/// | Full | Full outer join |
/// | Cross | Cross join (Cartesian product) |
/// | Natural | Natural join (auto-match on same column names) |
#[derive(Debug, Clone, PartialEq)]
pub enum JoinKind {
    Inner, Left, Right, Full, Cross, Natural,
}

/// JOIN condition
///
/// | Type | Syntax |
/// |------|------|
/// | On | ON expr |
/// | Using | USING (col1, col2, ...) |
/// | None | No condition (only used for CROSS JOIN) |
#[derive(Debug, Clone, PartialEq)]
pub enum JoinCondition {
    On(Expr),
    Using(Vec<String>),
    None,
}

/// ORDER BY item
///
/// # Example
/// ```sql
/// ORDER BY name ASC, created_at DESC
/// ```
#[derive(Debug, Clone, PartialEq)]
pub struct OrderItem {
    /// Sort expression
    pub expr: Expr,
    /// Whether ascending (true=ASC, false=DESC)
    pub asc:  bool,
}

// ── INSERT ────────────────────────────────────────────────────────────────

/// INSERT statement
///
/// # Syntax
/// ```sql
/// INSERT INTO table (col1, col2, ...) VALUES (v1, v2, ...), ...
/// INSERT INTO table DEFAULT VALUES
/// INSERT INTO table ... ON CONFLICT DO NOTHING
/// ```
#[derive(Debug, Clone, PartialEq)]
pub struct InsertStmt {
    /// Target table name
    pub table:   String,
    /// Column name list (empty means all columns)
    pub columns: Vec<String>,
    /// Values to insert (multiple groups for batch insert)
    pub values:  Vec<Vec<Expr>>,
    /// Whether DEFAULT VALUES
    pub default_values: bool,
    /// ON CONFLICT handling
    pub on_conflict: Option<OnConflict>,
}

/// ON CONFLICT handling strategy
#[derive(Debug, Clone, PartialEq)]
pub enum OnConflict {
    /// DO NOTHING (ignore conflict)
    DoNothing,
    /// DO UPDATE SET column = value (update existing row)
    DoUpdate { column: String, value: Expr },
}

// ── UPDATE ────────────────────────────────────────────────────────────────

/// UPDATE statement
///
/// # Syntax
/// ```sql
/// UPDATE table SET col1 = val1, col2 = val2 WHERE condition
/// ```
#[derive(Debug, Clone, PartialEq)]
pub struct UpdateStmt {
    /// Target table
    pub table:   String,
    /// Columns and values to update
    pub sets:    Vec<(String, Expr)>,
    /// WHERE condition (optional)
    pub where_:  Option<Expr>,
}

// ── DELETE ────────────────────────────────────────────────────────────────

/// DELETE statement
///
/// # Syntax
/// ```sql
/// DELETE FROM table WHERE condition
/// ```
#[derive(Debug, Clone, PartialEq)]
pub struct DeleteStmt {
    /// Target table
    pub table:  String,
    /// WHERE condition (optional, None when deleting all)
    pub where_: Option<Expr>,
}

// ── CREATE TABLE ─────────────────────────────────────────────────────────

/// CREATE TABLE statement
///
/// # Syntax
/// ```sql
/// CREATE TABLE [IF NOT EXISTS] name (
///     column1 type [constraints],
///     column2 type [constraints],
///     [table_constraints]
/// )
/// ```
#[derive(Debug, Clone, PartialEq)]
pub struct CreateTableStmt {
    /// IF NOT EXISTS
    pub if_not_exists: bool,
    /// Table name
    pub name:          String,
    /// Column definitions
    pub columns:       Vec<ColumnDef>,
    /// Table-level constraints
    pub constraints:   Vec<TableConstraint>,
}

/// CREATE VIRTUAL TABLE for FTS
///
/// ```sql
/// CREATE VIRTUAL TABLE articles USING fts(title, content);
/// ```
#[derive(Debug, Clone, PartialEq)]
pub struct CreateVirtualTableStmt {
    /// IF NOT EXISTS
    pub if_not_exists: bool,
    /// Table name
    pub name:          String,
    /// FTS column list
    pub columns:       Vec<String>,
}

/// Column definition
///
/// Contains column name, type, and constraints
#[derive(Debug, Clone, PartialEq)]
pub struct ColumnDef {
    pub name:        String,
    pub data_type:   SqlType,
    pub constraints: Vec<ColumnConstraint>,
}

/// SQL data type
///
/// | Type    | Description |
/// |---------|-------------|
/// | Integer | 64-bit signed integer |
/// | Real    | 64-bit floating point |
/// | Text    | UTF-8 string |
/// | Blob    | Binary data |
/// | Boolean | true/false |
/// | Null    | NULL value |
#[derive(Debug, Clone, PartialEq)]
pub enum SqlType {
    Integer, Real, Text, Blob, Boolean, Null,
}

/// Column-level constraint
///
/// | Constraint | Description |
/// |------------|-------------|
/// | NotNull | Non-null |
/// | PrimaryKey | Primary key |
/// | Unique | Unique |
/// | Default(expr) | Default value |
/// | Check(expr) | CHECK constraint |
/// | References | Foreign key reference |
#[derive(Debug, Clone, PartialEq)]
pub enum ColumnConstraint {
    /// Not null constraint
    NotNull,
    /// Primary key constraint
    PrimaryKey { autoincrement: bool },
    /// Unique constraint
    Unique,
    /// Default value
    Default(Expr),
    /// CHECK constraint
    Check(Expr),
    /// Foreign key reference
    References { table: String, column: Option<String> },
}

/// Table-level constraint
#[derive(Debug, Clone, PartialEq)]
pub enum TableConstraint {
    /// Primary key constraint (multi-column)
    PrimaryKey(Vec<String>),
    /// Unique constraint (multi-column)
    Unique(Vec<String>),
}

// ── DROP TABLE ────────────────────────────────────────────────────────────

#[derive(Debug, Clone, PartialEq)]
pub struct DropTableStmt {
    pub if_exists: bool,
    pub name:      String,
}

// ── CREATE INDEX ──────────────────────────────────────────────────────────

#[derive(Debug, Clone, PartialEq)]
pub struct CreateIndexStmt {
    pub unique:    bool,
    pub name:      String,
    pub table:     String,
    pub columns:   Vec<String>,
}

// ── DROP INDEX ────────────────────────────────────────────────────────────

#[derive(Debug, Clone, PartialEq)]
pub struct DropIndexStmt {
    pub if_exists: bool,
    pub name:      String,
}

// ── ALTER TABLE ──────────────────────────────────────────────────────────

#[derive(Debug, Clone, PartialEq)]
pub enum AlterTableOp {
    RenameTo(String),
    AddColumn { name: String, data_type: SqlType },
}

#[derive(Debug, Clone, PartialEq)]
pub struct AlterTableStmt {
    pub table: String,
    pub op:    AlterTableOp,
}

// ── PRAGMA ───────────────────────────────────────────────────────────────

#[derive(Debug, Clone, PartialEq)]
pub struct PragmaStmt {
    pub name:  String,
    pub value: Option<Expr>,
}

// ── EXPLAIN ─────────────────────────────────────────────────────────────

#[derive(Debug, Clone, PartialEq)]
pub struct ExplainStmt {
    pub inner: Box<Statement>,
}

// ── CREATE VIEW ──────────────────────────────────────────────────────────

#[derive(Debug, Clone, PartialEq)]
pub struct CreateViewStmt {
    pub if_not_exists: bool,
    pub temp:         bool,
    pub name:         String,
    pub query:        Box<SelectStmt>,
}

// ── DROP VIEW ────────────────────────────────────────────────────────────

#[derive(Debug, Clone, PartialEq)]
pub struct DropViewStmt {
    pub if_exists: bool,
    pub name:      String,
}

// ── TRIGGER ────────────────────────────────────────────────────────────────

#[derive(Debug, Clone, PartialEq)]
pub struct CreateTriggerStmt {
    pub if_not_exists: bool,
    pub name:          String,
    pub table:         String,
    pub timing:        TriggerTiming,
    pub event:         TriggerEvent,
    pub for_each_row:  bool,
    pub when:          Option<Box<Expr>>,
    pub body:          String,
}

#[derive(Debug, Clone, PartialEq)]
pub enum TriggerTiming {
    Before,
    After,
    InsteadOf,
}

#[derive(Debug, Clone, PartialEq)]
pub enum TriggerEvent {
    Delete,
    Insert,
    Update(Option<Vec<String>>),
}

#[derive(Debug, Clone, PartialEq)]
pub struct DropTriggerStmt {
    pub if_exists: bool,
    pub name:      String,
}

// ── REINDEX ─────────────────────────────────────────────────────────────

#[derive(Debug, Clone, PartialEq)]
pub struct ReindexStmt {
    pub name: Option<String>,
}

// ── ANALYZE ─────────────────────────────────────────────────────────────

#[derive(Debug, Clone, PartialEq)]
pub struct AnalyzeStmt {
    pub name: Option<String>,
}

// ── BACKUP ─────────────────────────────────────────────────────────────

#[derive(Debug, Clone, PartialEq)]
pub struct BackupStmt {
    pub path: String,
}

// ── Expressions ────────────────────────────────────────────────────────────────

/// Expression
///
/// An expression is a syntactic structure that produces a value, used in:
/// - SELECT columns
/// - WHERE conditions
/// - SET clauses
/// - VALUES clauses
///
/// # Expression Types
///
/// | Type     | Example | Description |
/// |----------|---------|-------------|
/// | LitInt | `42` | Integer literal |
/// | LitFloat | `3.14` | Float literal |
/// | LitStr | `'hello'` | String literal |
/// | LitBool | `TRUE` | Boolean literal |
/// | LitNull | `NULL` | Null value |
/// | Column | `name`, `t.name` | Column reference |
/// | Function | `COUNT(*)` | Function call |
/// | BinOp | `a + b`, `x > 5` | Binary operation |
/// | UnaryOp | `-x`, `NOT y` | Unary operation |
/// | IsNull | `x IS NULL` | Null check |
/// | Between | `n BETWEEN 1 AND 10` | Range check |
/// | InList | `x IN (1, 2, 3)` | List membership |
/// | Like | `name LIKE 'A%'` | Pattern match |
/// | Cast | `CAST(x AS INTEGER)` | Type conversion |
#[derive(Debug, Clone, PartialEq)]
pub enum Expr {
    // ── Literals ────────────────────────────────────────────────────────────

    /// Integer literal
    LitInt(i64),
    /// Float literal
    LitFloat(f64),
    /// String literal (enclosed in single quotes)
    LitStr(String),
    /// Boolean literal (TRUE / FALSE)
    LitBool(bool),
    /// Null value
    LitNull,

    // ── Column Reference ─────────────────────────────────────────────────────────

    /// Column reference
    ///
    /// # Examples
    /// - `name` → Column { table: None, name: "name" }
    /// - `t.name` → Column { table: Some("t"), name: "name" }
    Column { table: Option<String>, name: String },

    // ── Function ─────────────────────────────────────────────────────────────

    /// Function call
    ///
    /// # Examples
    /// - `COUNT(*)` → Function { name: "COUNT", args: [*], distinct: false }
    /// - `SUM(DISTINCT x)` → Function { name: "SUM", args: [x], distinct: true }
    Function { name: String, args: Vec<Expr>, distinct: bool },

    // ── Binary Operation ─────────────────────────────────────────────────────────

    /// Binary operation (left op right)
    ///
    /// # Supported operators
    /// - Comparison: =, !=, <, <=, >, >=
    /// - Logical: AND, OR
    /// - Arithmetic: +, -, *, /, %
    /// - String: ||
    BinOp { left: Box<Expr>, op: BinOp, right: Box<Expr> },

    // ── Unary Operation ─────────────────────────────────────────────────────────

    /// Unary operation (op expr)
    ///
    /// # Supported operators
    /// - Neg: Negation (-x)
    /// - Not: Logical NOT (NOT x)
    UnaryOp { op: UnaryOp, expr: Box<Expr> },

    // ── Null Check ─────────────────────────────────────────────────────────

    /// IS [NOT] NULL
    ///
    /// # Examples
    /// - `x IS NULL` → IsNull { expr: x, negated: false }
    /// - `x IS NOT NULL` → IsNull { expr: x, negated: true }
    IsNull  { expr: Box<Expr>, negated: bool },

    // ── Range Check ─────────────────────────────────────────────────────────

    /// BETWEEN ... AND ...
    ///
    /// # Examples
    /// - `age BETWEEN 18 AND 65` → Between { expr: age, low: 18, high: 65, negated: false }
    /// - `age NOT BETWEEN 18 AND 65` → negated: true
    Between { expr: Box<Expr>, low: Box<Expr>, high: Box<Expr>, negated: bool },

    // ── List Membership ─────────────────────────────────────────────────────

    /// IN (...) list membership
    ///
    /// # Examples
    /// - `id IN (1, 2, 3)` → InList { expr: id, list: [1, 2, 3], negated: false }
    InList  { expr: Box<Expr>, list: Vec<Expr>, negated: bool },

    /// IN (SELECT ...) subquery
    InSubquery { expr: Box<Expr>, query: Box<SelectStmt>, negated: bool },

    /// EXISTS (SELECT ...)
    Exists { query: Box<SelectStmt>, negated: bool },

    /// Scalar subquery (used as a single value)
    ScalarSubquery(Box<SelectStmt>),

    // ── Pattern Match ─────────────────────────────────────────────────────────

    /// LIKE pattern match
    ///
    /// # Examples
    /// - `name LIKE 'A%'` → Like { expr: name, pattern: 'A%', negated: false }
    Like    { expr: Box<Expr>, pattern: Box<Expr>, negated: bool },

    /// GLOB pattern match (case-sensitive, uses * and ?)
    Glob    { expr: Box<Expr>, pattern: Box<Expr>, negated: bool },

    /// FTS MATCH full-text search
    ///
    /// # Examples
    /// - `articles MATCH 'search term'` → Match { table: "articles", query: "search term" }
    Match { table: String, query: String },

    // ── JSON Path ─────────────────────────────────────────────────────────

    /// JSON Path expression (@.field op value)
    ///
    /// # Examples
    /// - `@.age > 25` → JsonPath { path: ["age"], op: Gt, value: LitInt(25), negated: false }
    /// - `@.name = 'Alice'` → JsonPath { path: ["name"], op: Eq, value: LitStr("Alice"), negated: false }
    /// - `@.address.city = 'Taipei'` → JsonPath { path: ["address", "city"], ... }
    JsonPath {
        path: Vec<String>,
        op: JsonPathOpKind,
        negated: bool,
        value: Box<Expr>,
    },

    // ── Type Cast ─────────────────────────────────────────────────────────

    /// CAST(expr AS type)
    Cast { expr: Box<Expr>, to: SqlType },

    /// Subquery (reserved)
    Subquery(Box<SelectStmt>),
}

/// Binary operator
///
/// # Categories
/// - Comparison: Eq, NotEq, Lt, LtEq, Gt, GtEq
/// - Logical: And, Or
/// - Arithmetic: Add, Sub, Mul, Div, Mod
/// - String: Concat (||)
#[derive(Debug, Clone, PartialEq)]
pub enum BinOp {
    Eq, NotEq, Lt, LtEq, Gt, GtEq,  // Comparison
    And, Or,                         // Logical
    Add, Sub, Mul, Div, Mod,         // Arithmetic
    Concat,                           // String concatenation (||)
}

/// Unary operator
///
/// | Operator | Description | Example |
/// |----------|-------------|---------|
/// | Neg | Negation | -5 |
/// | Not | Logical NOT | NOT x |
#[derive(Debug, Clone, PartialEq)]
pub enum UnaryOp {
    Neg,    // Negation
    Not,    // Logical NOT
}

/// JSON Path operator kind
#[derive(Debug, Clone, PartialEq)]
pub enum JsonPathOpKind {
    Eq,      // =
    Ne,      // !=
    Lt,      // <
    LtEq,    // <=
    Gt,      // >
    GtEq,    // >=
    Like,    // LIKE
    In,      // IN (...)
    IsNull,  // IS NULL
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_expr_lit_int() {
        let e = Expr::LitInt(42);
        assert!(matches!(e, Expr::LitInt(42)));
    }

    #[test]
    fn test_expr_lit_float() {
        let e = Expr::LitFloat(3.14);
        assert!(matches!(e, Expr::LitFloat(3.14)));
    }

    #[test]
    fn test_expr_lit_str() {
        let e = Expr::LitStr("hello".to_string());
        assert!(matches!(e, Expr::LitStr(s) if s == "hello"));
    }

    #[test]
    fn test_expr_lit_bool() {
        let t = Expr::LitBool(true);
        let f = Expr::LitBool(false);
        assert!(matches!(t, Expr::LitBool(true)));
        assert!(matches!(f, Expr::LitBool(false)));
    }

    #[test]
    fn test_expr_lit_null() {
        let e = Expr::LitNull;
        assert!(matches!(e, Expr::LitNull));
    }

    #[test]
    fn test_expr_column() {
        let e = Expr::Column { table: None, name: "id".to_string() };
        assert!(matches!(e, Expr::Column { table: None, name } if name == "id"));
    }

    #[test]
    fn test_expr_column_with_table() {
        let e = Expr::Column { table: Some("users".to_string()), name: "id".to_string() };
        assert!(matches!(e, Expr::Column { table: Some(t), name } if t == "users" && name == "id"));
    }

    #[test]
    fn test_expr_function() {
        let e = Expr::Function { name: "COUNT".to_string(), args: vec![Expr::Column { table: None, name: "*".to_string() }], distinct: false };
        assert!(matches!(e, Expr::Function { name, .. } if name == "COUNT"));
    }

    #[test]
    fn test_expr_binop() {
        use BinOp::*;
        let e = Expr::BinOp {
            left: Box::new(Expr::LitInt(1)),
            op: Add,
            right: Box::new(Expr::LitInt(2)),
        };
        assert!(matches!(e, Expr::BinOp { op: Add, .. }));
    }

    #[test]
    fn test_expr_unary_op() {
        let e = Expr::UnaryOp { op: UnaryOp::Neg, expr: Box::new(Expr::LitInt(5)) };
        assert!(matches!(e, Expr::UnaryOp { op: UnaryOp::Neg, .. }));
    }

    #[test]
    fn test_expr_is_null() {
        let e = Expr::IsNull { expr: Box::new(Expr::Column { table: None, name: "x".to_string() }), negated: false };
        assert!(matches!(e, Expr::IsNull { negated: false, .. }));
    }

    #[test]
    fn test_expr_is_not_null() {
        let e = Expr::IsNull { expr: Box::new(Expr::Column { table: None, name: "x".to_string() }), negated: true };
        assert!(matches!(e, Expr::IsNull { negated: true, .. }));
    }

    #[test]
    fn test_binop_equality() {
        let eq = BinOp::Eq;
        let ne = BinOp::NotEq;
        assert!(matches!(eq, BinOp::Eq));
        assert!(matches!(ne, BinOp::NotEq));
    }

    #[test]
    fn test_binop_comparison() {
        assert!(matches!(BinOp::Lt, BinOp::Lt));
        assert!(matches!(BinOp::LtEq, BinOp::LtEq));
        assert!(matches!(BinOp::Gt, BinOp::Gt));
        assert!(matches!(BinOp::GtEq, BinOp::GtEq));
    }

    #[test]
    fn test_binop_logical() {
        assert!(matches!(BinOp::And, BinOp::And));
        assert!(matches!(BinOp::Or, BinOp::Or));
    }

    #[test]
    fn test_binop_arithmetic() {
        assert!(matches!(BinOp::Add, BinOp::Add));
        assert!(matches!(BinOp::Sub, BinOp::Sub));
        assert!(matches!(BinOp::Mul, BinOp::Mul));
        assert!(matches!(BinOp::Div, BinOp::Div));
        assert!(matches!(BinOp::Mod, BinOp::Mod));
    }

    #[test]
    fn test_unary_op() {
        assert!(matches!(UnaryOp::Neg, UnaryOp::Neg));
        assert!(matches!(UnaryOp::Not, UnaryOp::Not));
    }

    #[test]
    fn test_select_item_star() {
        assert!(matches!(SelectItem::Star, SelectItem::Star));
    }

    #[test]
    fn test_select_item_table_star() {
        let si = SelectItem::TableStar("users".to_string());
        match si {
            SelectItem::TableStar(s) => assert_eq!(s, "users"),
            _ => panic!("not TableStar"),
        }
    }

    #[test]
    fn test_select_item_expr() {
        let si = SelectItem::Expr { expr: Expr::LitInt(1), alias: Some("one".to_string()) };
        assert!(matches!(si, SelectItem::Expr { alias: Some(a), .. } if a == "one"));
    }

    #[test]
    fn test_table_ref() {
        let t = TableRef { name: "users".to_string(), alias: Some("u".to_string()) };
        assert_eq!(t.name, "users");
        assert_eq!(t.alias, Some("u".to_string()));
    }

    #[test]
    fn test_from_item_table() {
        let fi = FromItem::Table(TableRef { name: "users".to_string(), alias: None });
        assert!(matches!(fi, FromItem::Table(t) if t.name == "users"));
    }

    #[test]
    fn test_order_item() {
        let oi = OrderItem { expr: Expr::LitInt(1), asc: true };
        assert!(oi.asc);
        assert!(matches!(oi.expr, Expr::LitInt(1)));
    }

    #[test]
    fn test_join_kind() {
        assert!(matches!(JoinKind::Inner, JoinKind::Inner));
        assert!(matches!(JoinKind::Left, JoinKind::Left));
        assert!(matches!(JoinKind::Right, JoinKind::Right));
        assert!(matches!(JoinKind::Full, JoinKind::Full));
        assert!(matches!(JoinKind::Cross, JoinKind::Cross));
        assert!(matches!(JoinKind::Natural, JoinKind::Natural));
    }

    #[test]
    fn test_join_condition() {
        let on = JoinCondition::On(Expr::LitInt(1));
        let using = JoinCondition::Using(vec!["id".to_string()]);
        let none = JoinCondition::None;
        assert!(matches!(on, JoinCondition::On(_)));
        assert!(matches!(using, JoinCondition::Using(_)));
        assert!(matches!(none, JoinCondition::None));
    }

    #[test]
    fn test_insert_stmt() {
        let stmt = InsertStmt {
            table: "users".to_string(),
            columns: vec!["name".to_string()],
            values: vec![vec![Expr::LitStr("Alice".to_string())]],
            default_values: false,
            on_conflict: None,
        };
        assert_eq!(stmt.table, "users");
        assert_eq!(stmt.columns.len(), 1);
    }

    #[test]
    fn test_update_stmt() {
        let stmt = UpdateStmt {
            table: "users".to_string(),
            sets: vec![("age".to_string(), Expr::LitInt(30))],
            where_: None,
        };
        assert_eq!(stmt.table, "users");
        assert_eq!(stmt.sets.len(), 1);
    }

    #[test]
    fn test_delete_stmt() {
        let stmt = DeleteStmt { table: "users".to_string(), where_: None };
        assert_eq!(stmt.table, "users");
    }

    #[test]
    fn test_create_table_stmt() {
        let stmt = CreateTableStmt {
            if_not_exists: true,
            name: "users".to_string(),
            columns: vec![],
            constraints: vec![],
        };
        assert!(stmt.if_not_exists);
        assert_eq!(stmt.name, "users");
    }

    #[test]
    fn test_drop_table_stmt() {
        let stmt = DropTableStmt { if_exists: true, name: "users".to_string() };
        assert!(stmt.if_exists);
        assert_eq!(stmt.name, "users");
    }

    #[test]
    fn test_sql_type() {
        assert!(matches!(SqlType::Integer, SqlType::Integer));
        assert!(matches!(SqlType::Real, SqlType::Real));
        assert!(matches!(SqlType::Text, SqlType::Text));
        assert!(matches!(SqlType::Blob, SqlType::Blob));
        assert!(matches!(SqlType::Boolean, SqlType::Boolean));
        assert!(matches!(SqlType::Null, SqlType::Null));
    }

    #[test]
    fn test_column_constraint() {
        let not_null = ColumnConstraint::NotNull;
        let pk = ColumnConstraint::PrimaryKey { autoincrement: false };
        let unique = ColumnConstraint::Unique;
        assert!(matches!(not_null, ColumnConstraint::NotNull));
        assert!(matches!(pk, ColumnConstraint::PrimaryKey { autoincrement: false }));
        assert!(matches!(unique, ColumnConstraint::Unique));
    }

    #[test]
    fn test_trigger_timing() {
        assert!(matches!(TriggerTiming::Before, TriggerTiming::Before));
        assert!(matches!(TriggerTiming::After, TriggerTiming::After));
        assert!(matches!(TriggerTiming::InsteadOf, TriggerTiming::InsteadOf));
    }

    #[test]
    fn test_trigger_event() {
        assert!(matches!(TriggerEvent::Delete, TriggerEvent::Delete));
        assert!(matches!(TriggerEvent::Insert, TriggerEvent::Insert));
        assert!(matches!(TriggerEvent::Update(None), TriggerEvent::Update(None)));
        if let TriggerEvent::Update(Some(cols)) = TriggerEvent::Update(Some(vec!["id".to_string()])) {
            assert_eq!(cols.len(), 1);
        } else {
            panic!("expected Update with Some");
        }
    }

    #[test]
    fn test_statement() {
        let s = Statement::Begin;
        assert!(matches!(s, Statement::Begin));

        let s = Statement::Commit;
        assert!(matches!(s, Statement::Commit));

        let s = Statement::Rollback;
        assert!(matches!(s, Statement::Rollback));

        let s = Statement::Vacuum;
        assert!(matches!(s, Statement::Vacuum));
    }

    #[test]
    fn test_expr_clone() {
        let e = Expr::LitInt(42);
        let cloned = e.clone();
        assert_eq!(e, cloned);
    }

    #[test]
    fn test_statement_clone() {
        let stmt = Statement::Begin;
        let cloned = stmt.clone();
        assert_eq!(stmt, cloned);
    }
}
