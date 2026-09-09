//! AST：SQL 語句的抽象語法樹節點定義

// ── 頂層語句 ──────────────────────────────────────────────────────────────

#[derive(Debug, Clone, PartialEq)]
pub enum Statement {
    Select(SelectStmt),
    Insert(InsertStmt),
    Update(UpdateStmt),
    Delete(DeleteStmt),
    CreateTable(CreateTableStmt),
    DropTable(DropTableStmt),
    CreateIndex(CreateIndexStmt),
    Begin,
    Commit,
    Rollback,
}

// ── SELECT ────────────────────────────────────────────────────────────────

#[derive(Debug, Clone, PartialEq)]
pub struct SelectStmt {
    pub with:      Vec<Cte>,            // WITH ... AS (...)
    pub distinct:  bool,
    pub columns:   Vec<SelectItem>,
    pub from:      Option<FromItem>,    // table name 或子查詢
    pub joins:     Vec<Join>,
    pub where_:    Option<Expr>,
    pub group_by:  Vec<Expr>,
    pub having:    Option<Expr>,
    pub order_by:  Vec<OrderItem>,
    pub limit:     Option<Expr>,
    pub offset:    Option<Expr>,
}

#[derive(Debug, Clone, PartialEq)]
pub enum SelectItem {
    Star,                          // *
    TableStar(String),             // table.*
    Expr { expr: Expr, alias: Option<String> },
}

#[derive(Debug, Clone, PartialEq)]
pub struct TableRef {
    pub name:  String,
    pub alias: Option<String>,
}

/// FROM 子句可以是資料表名稱或子查詢
#[derive(Debug, Clone, PartialEq)]
pub enum FromItem {
    Table(TableRef),
    Subquery { query: Box<SelectStmt>, alias: String },
}

/// CTE（Common Table Expression）定義：WITH name AS (query)
#[derive(Debug, Clone, PartialEq)]
pub struct Cte {
    pub name:  String,
    pub query: Box<SelectStmt>,
}

#[derive(Debug, Clone, PartialEq)]
pub struct Join {
    pub kind:      JoinKind,
    pub table:     TableRef,   // 暫保留 TableRef，子查詢 JOIN 後續擴充
    pub condition: JoinCondition,
}

#[derive(Debug, Clone, PartialEq)]
pub enum JoinKind {
    Inner, Left, Right, Full, Cross, Natural,
}

#[derive(Debug, Clone, PartialEq)]
pub enum JoinCondition {
    On(Expr),
    Using(Vec<String>),
    None,
}

#[derive(Debug, Clone, PartialEq)]
pub struct OrderItem {
    pub expr: Expr,
    pub asc:  bool,
}

// ── INSERT ────────────────────────────────────────────────────────────────

#[derive(Debug, Clone, PartialEq)]
pub struct InsertStmt {
    pub table:   String,
    pub columns: Vec<String>,   // 空表示不指定欄位
    pub values:  Vec<Vec<Expr>>,
}

// ── UPDATE ────────────────────────────────────────────────────────────────

#[derive(Debug, Clone, PartialEq)]
pub struct UpdateStmt {
    pub table:   String,
    pub sets:    Vec<(String, Expr)>,
    pub where_:  Option<Expr>,
}

// ── DELETE ────────────────────────────────────────────────────────────────

#[derive(Debug, Clone, PartialEq)]
pub struct DeleteStmt {
    pub table:  String,
    pub where_: Option<Expr>,
}

// ── CREATE TABLE ─────────────────────────────────────────────────────────

#[derive(Debug, Clone, PartialEq)]
pub struct CreateTableStmt {
    pub if_not_exists: bool,
    pub name:          String,
    pub columns:       Vec<ColumnDef>,
    pub constraints:   Vec<TableConstraint>,
}

#[derive(Debug, Clone, PartialEq)]
pub struct ColumnDef {
    pub name:        String,
    pub data_type:   SqlType,
    pub constraints: Vec<ColumnConstraint>,
}

#[derive(Debug, Clone, PartialEq)]
pub enum SqlType {
    Integer, Real, Text, Blob, Boolean, Null,
}

#[derive(Debug, Clone, PartialEq)]
pub enum ColumnConstraint {
    NotNull,
    PrimaryKey { autoincrement: bool },
    Unique,
    Default(Expr),
}

#[derive(Debug, Clone, PartialEq)]
pub enum TableConstraint {
    PrimaryKey(Vec<String>),
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

// ── 運算式 ────────────────────────────────────────────────────────────────

#[derive(Debug, Clone, PartialEq)]
pub enum Expr {
    // 字面值
    LitInt(i64),
    LitFloat(f64),
    LitStr(String),
    LitBool(bool),
    LitNull,

    // 欄位參照（可帶 table prefix）
    Column { table: Option<String>, name: String },

    // 函式呼叫
    Function { name: String, args: Vec<Expr>, distinct: bool },

    // 二元運算
    BinOp { left: Box<Expr>, op: BinOp, right: Box<Expr> },

    // 一元運算
    UnaryOp { op: UnaryOp, expr: Box<Expr> },

    // IS NULL / IS NOT NULL
    IsNull  { expr: Box<Expr>, negated: bool },

    // BETWEEN
    Between { expr: Box<Expr>, low: Box<Expr>, high: Box<Expr>, negated: bool },

    // IN (...)
    InList  { expr: Box<Expr>, list: Vec<Expr>, negated: bool },

    // IN (SELECT ...)
    InSubquery { expr: Box<Expr>, query: Box<SelectStmt>, negated: bool },

    // EXISTS (SELECT ...)
    Exists { query: Box<SelectStmt>, negated: bool },

    // 純量子查詢 (SELECT ...)
    ScalarSubquery(Box<SelectStmt>),

    // LIKE
    Like    { expr: Box<Expr>, pattern: Box<Expr>, negated: bool },

    // 子查詢（留待後續實作）
    Subquery(Box<SelectStmt>),

    // CAST(expr AS type)
    Cast { expr: Box<Expr>, to: SqlType },
}

#[derive(Debug, Clone, PartialEq)]
pub enum BinOp {
    Eq, NotEq, Lt, LtEq, Gt, GtEq,
    And, Or,
    Add, Sub, Mul, Div, Mod,
    Concat,
}

#[derive(Debug, Clone, PartialEq)]
pub enum UnaryOp {
    Neg,    // -
    Not,    // NOT
}
