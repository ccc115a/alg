//! Lexer: Tokenizes SQL strings into a token stream
//!
//! Lexical analysis is the first phase of SQL processing. The Lexer reads raw SQL strings
//! and splits them into meaningful minimal units — tokens — according to SQL lexical rules.
//!
//! For example, `SELECT * FROM users` is tokenized into:
//! ```text
//! [Select, Star, From, Ident("users"), Eof]
//! ```
//!
//! ## Approach
//!
//! Implements a single-character lookahead approach, reading the input character by character:
//! - Letter or underscore → read the entire identifier/keyword
//! - Digit → read the entire number (integer or float)
//! - Single quote → read a string literal
//! - Special character → determine operator or punctuation
//! - Skip whitespace and comments
//!
//! ## Supported Token Types
//!
//! - **Keywords**: SELECT, FROM, WHERE, INSERT, CREATE, and 80+ other SQL keywords
//! - **Identifiers**: table names, column names (Ident(String))
//! - **Literals**: integer (LitInt), float (LitFloat), string (LitStr), NULL
//! - **Operators**: =, !=, <, >, <=, >=, +, -, *, /, %, ||
//! - **Punctuation**: (, ), ,, ;, .

/// SQL lexical unit (Token)
///
/// Each Token represents the smallest semantic unit in a SQL string.
#[derive(Debug, Clone, PartialEq)]
pub enum Token {
    // ── Keywords ──────────────────────────────────────────────────────
    /// SELECT query keyword
    Select, From, Where, Insert, Into, Values,
    /// UPDATE/DELETE operation keywords
    Update, Set, Delete,
    /// CREATE/DROP/ALTER DDL keywords
    Create, Drop, Table,
    /// Index-related
    Index, On, Primary, Key,
    /// Constraint-related
    Not, Null, Unique,
    /// Logical operators
    And, Or, Is, In, Like, Between,
    /// ORDER BY sorting
    Order, By, Asc, Desc, Limit, Offset,
    /// JOIN-related
    Join, Inner, Left, Right, Outer, Cross, Natural, Using,
    /// GROUP BY aggregation
    Group, Having, Distinct, All, As,
    /// Conditional
    If, Exists,
    /// Transaction control
    Begin, Commit, Rollback, Transaction,
    /// FTS5 full-text search
    Virtual, Match,
    /// CTE (Common Table Expression)
    With, Recursive,
    /// FOREIGN KEY constraint
    References,
    /// Data types
    KwInteger, KwText, Real, Blob, Boolean,
    /// Boolean literals
    True, False,
    /// Other SQL keywords
    Pragma, Explain, Alter, Rename, To, Add, Column, Do, Of,
    View, Reindex, Analyze, Temp, Conflict, Nothing, Union, Check, Cast, Default, GLOB,
    Trigger, Before, After, Instead, Each, Row, For, When, End, AutoIncrement,
    Attach, Detach, Database, Vacuum, Backup,

    // ── Identifiers ──────────────────────────────────────────────────────────
    /// Table name, column name, etc. (with original string)
    Ident(String),

    // ── Literals ──────────────────────────────────────────────────────────
    /// Integer literal
    LitInt(i64),
    /// Float literal
    LitFloat(f64),
    /// String literal (enclosed in single quotes)
    LitStr(String),
    /// NULL literal
    LitNull,

    // ── Operators ──────────────────────────────────────────────────────────
    /// Equal `=`
    Eq,
    /// Not equal `!=` or `<>`
    NotEq,
    /// Less than `<`
    Lt,
    /// Less than or equal `<=`
    LtEq,
    /// Greater than `>`
    Gt,
    /// Greater than or equal `>=`
    GtEq,
    /// Plus `+`
    Plus,
    /// Minus `-`
    Minus,
    /// Star `*` (SELECT * or multiplication)
    Star,
    /// Slash `/`
    Slash,
    /// Percent `%` (modulo)
    Percent,
    /// String concatenation `||`
    Concat,

    // ── Punctuation ────────────────────────────────────────────────────────
    /// Left parenthesis `(`
    LParen,
    /// Right parenthesis `)`
    RParen,
    /// Comma `,`
    Comma,
    /// Semicolon `;`
    Semicolon,
    /// Dot `.`
    Dot,

    // ── Special Tokens ──────────────────────────────────────────────────────
    /// End of input
    Eof,
    /// JSON Path prefix `@` (e.g. `@.field`)
    At,
}

// ── Keyword lookup table ─────────────────────────────────────────────────────────

fn keyword(s: &str) -> Option<Token> {
    match s.to_uppercase().as_str() {
        "SELECT"      => Some(Token::Select),
        "FROM"        => Some(Token::From),
        "WHERE"       => Some(Token::Where),
        "INSERT"      => Some(Token::Insert),
        "INTO"        => Some(Token::Into),
        "VALUES"      => Some(Token::Values),
        "UPDATE"      => Some(Token::Update),
        "SET"         => Some(Token::Set),
        "DELETE"      => Some(Token::Delete),
        "CREATE"      => Some(Token::Create),
        "DROP"        => Some(Token::Drop),
        "TABLE"       => Some(Token::Table),
        "INDEX"       => Some(Token::Index),
        "ON"          => Some(Token::On),
        "PRIMARY"     => Some(Token::Primary),
        "KEY"         => Some(Token::Key),
        "REFERENCES"  => Some(Token::References),
        "NOT"         => Some(Token::Not),
        "NULL"        => Some(Token::LitNull),
        "UNIQUE"      => Some(Token::Unique),
        "AND"         => Some(Token::And),
        "OR"          => Some(Token::Or),
        "IS"          => Some(Token::Is),
        "IN"          => Some(Token::In),
        "LIKE"        => Some(Token::Like),
        "BETWEEN"     => Some(Token::Between),
        "ORDER"       => Some(Token::Order),
        "BY"          => Some(Token::By),
        "ASC"         => Some(Token::Asc),
        "DESC"        => Some(Token::Desc),
        "LIMIT"       => Some(Token::Limit),
        "OFFSET"      => Some(Token::Offset),
        "JOIN"        => Some(Token::Join),
        "INNER"       => Some(Token::Inner),
        "LEFT"        => Some(Token::Left),
        "RIGHT"       => Some(Token::Right),
        "OUTER"       => Some(Token::Outer),
        "CROSS"       => Some(Token::Cross),
        "NATURAL"     => Some(Token::Natural),
        "USING"       => Some(Token::Using),
        "GROUP"       => Some(Token::Group),
        "HAVING"      => Some(Token::Having),
        "DISTINCT"    => Some(Token::Distinct),
        "ALL"         => Some(Token::All),
        "AS"          => Some(Token::As),
        "IF"          => Some(Token::If),
        "EXISTS"      => Some(Token::Exists),
        "BEGIN"       => Some(Token::Begin),
        "COMMIT"      => Some(Token::Commit),
        "ROLLBACK"    => Some(Token::Rollback),
        "TRANSACTION" => Some(Token::Transaction),
        "VIRTUAL"     => Some(Token::Virtual),
        "MATCH"       => Some(Token::Match),
        "WITH"        => Some(Token::With),
        "RECURSIVE"   => Some(Token::Recursive),
        "INTEGER"     => Some(Token::KwInteger),
        "INT"         => Some(Token::KwInteger),
        "TEXT"        => Some(Token::KwText),
        "VARCHAR"     => Some(Token::KwText),
        "REAL"        => Some(Token::Real),
        "FLOAT"       => Some(Token::Real),
        "BLOB"        => Some(Token::Blob),
        "BOOLEAN"     => Some(Token::Boolean),
        "BOOL"        => Some(Token::Boolean),
        "TRUE"        => Some(Token::True),
        "FALSE"       => Some(Token::False),
        "PRAGMA"      => Some(Token::Pragma),
        "EXPLAIN"     => Some(Token::Explain),
        "ALTER"       => Some(Token::Alter),
        "RENAME"      => Some(Token::Rename),
        "TO"          => Some(Token::To),
        "ADD"         => Some(Token::Add),
        "COLUMN"      => Some(Token::Column),
        "DO"          => Some(Token::Do),
        "VIEW"        => Some(Token::View),
        "REINDEX"     => Some(Token::Reindex),
        "ANALYZE"     => Some(Token::Analyze),
        "TEMP"        => Some(Token::Temp),
        "TEMPORARY"   => Some(Token::Temp),
        "CONFLICT"    => Some(Token::Conflict),
        "NOTHING"     => Some(Token::Nothing),
        "UNION"       => Some(Token::Union),
        "CHECK"       => Some(Token::Check),
        "CAST"        => Some(Token::Cast),
        "DEFAULT"     => Some(Token::Default),
        "GLOB"        => Some(Token::GLOB),
        "TRIGGER"     => Some(Token::Trigger),
        "BEFORE"      => Some(Token::Before),
        "AFTER"       => Some(Token::After),
        "INSTEAD"      => Some(Token::Instead),
        "OF"          => Some(Token::Of),
        "FOR"         => Some(Token::For),
        "EACH"        => Some(Token::Each),
        "ROW"         => Some(Token::Row),
        "WHEN"        => Some(Token::When),
        "END"         => Some(Token::End),
        "AUTOINCREMENT" => Some(Token::AutoIncrement),
        "ATTACH"       => Some(Token::Attach),
        "DETACH"       => Some(Token::Detach),
        "DATABASE"     => Some(Token::Database),
        "VACUUM"       => Some(Token::Vacuum),
        "BACKUP"       => Some(Token::Backup),
        _             => None,
    }
}

// ── Lexer ────────────────────────────────────────────────────

/// Lexer: Converts SQL strings into a token stream
///
/// ## Usage
///
/// ```
/// use db6::sql::parser::lexer::Lexer;
/// let mut lexer = Lexer::new("SELECT * FROM users");
/// let tokens = lexer.tokenize().unwrap();
/// ```
pub struct Lexer {
    /// Input character array (supports multi-byte characters)
    input: Vec<char>,
    /// Current read position
    pos:   usize,
}

impl Lexer {
    /// Create a new Lexer
    pub fn new(input: &str) -> Self {
        Lexer { input: input.chars().collect(), pos: 0 }
    }

    /// Scan all tokens, return Err on error
    pub fn tokenize(&mut self) -> Result<Vec<Token>, String> {
        let mut tokens = Vec::new();
        loop {
            let tok = self.next_token()?;
            let done = tok == Token::Eof;
            tokens.push(tok);
            if done { break; }
        }
        Ok(tokens)
    }

    /// Peek at the current character (without consuming)
    fn peek(&self) -> Option<char> { self.input.get(self.pos).copied() }

    /// Peek at the next character (without consuming)
    fn peek2(&self) -> Option<char> { self.input.get(self.pos + 1).copied() }

    /// Read the current character and advance position
    fn advance(&mut self) -> Option<char> {
        let c = self.input.get(self.pos).copied();
        if c.is_some() { self.pos += 1; }
        c
    }

    /// Read the next Token (core method)
    ///
    /// First skips whitespace and single-line comments (-- through newline),
    /// then decides how to proceed based on the first character type.
    fn next_token(&mut self) -> Result<Token, String> {
        // Skip whitespace and single-line comments
        loop {
            match self.peek() {
                Some(c) if c.is_whitespace() => { self.advance(); }
                Some('-') if self.peek2() == Some('-') => {
                    while self.peek().map(|c| c != '\n').unwrap_or(false) { self.advance(); }
                }
                _ => break,
            }
        }

        // Dispatch based on character type
        match self.peek() {
            None => Ok(Token::Eof),
            Some(c) => match c {
                // Punctuation
                '(' => { self.advance(); Ok(Token::LParen) }
                ')' => { self.advance(); Ok(Token::RParen) }
                ',' => { self.advance(); Ok(Token::Comma) }
                ';' => { self.advance(); Ok(Token::Semicolon) }
                '.' => { self.advance(); Ok(Token::Dot) }
                // Operators
                '+' => { self.advance(); Ok(Token::Plus) }
                '-' => { self.advance(); Ok(Token::Minus) }
                '*' => { self.advance(); Ok(Token::Star) }
                '/' => { self.advance(); Ok(Token::Slash) }
                '%' => { self.advance(); Ok(Token::Percent) }
                '=' => { self.advance(); Ok(Token::Eq) }
                '@' => { self.advance(); Ok(Token::At) }
                // Two-character operators
                '<' => {
                    self.advance();
                    match self.peek() {
                        Some('=') => { self.advance(); Ok(Token::LtEq) }
                        Some('>') => { self.advance(); Ok(Token::NotEq) }
                        _ => Ok(Token::Lt),
                    }
                }
                '>' => {
                    self.advance();
                    if self.peek() == Some('=') { self.advance(); Ok(Token::GtEq) }
                    else { Ok(Token::Gt) }
                }
                '!' => {
                    self.advance();
                    if self.peek() == Some('=') { self.advance(); Ok(Token::NotEq) }
                    else { Err(format!("unexpected character '!'")) }
                }
                '|' => {
                    self.advance();
                    if self.peek() == Some('|') { self.advance(); Ok(Token::Concat) }
                    else { Err("expected '||'".to_string()) }
                }
                // String literal (single quotes)
                '\'' => self.lex_string(),
                // Backtick or double-quote delimited identifier
                '`' | '"' => self.lex_quoted_ident(),
                // Number
                c if c.is_ascii_digit() => self.lex_number(),
                // Identifier / keyword
                c if c.is_alphabetic() || c == '_' => self.lex_ident(),
                c => Err(format!("unexpected character '{}'", c)),
            }
        }
    }

    /// Read a string literal enclosed in single quotes
    ///
    /// In SQL, two consecutive single quotes `''` represent an escaped single quote.
    fn lex_string(&mut self) -> Result<Token, String> {
        self.advance(); // Skip opening quote
        let mut s = String::new();
        loop {
            match self.advance() {
                None => return Err("unterminated string".to_string()),
                Some('\'') => {
                    // Consecutive '' represents an escaped single quote
                    if self.peek() == Some('\'') { self.advance(); s.push('\''); }
                    else { break; }
                }
                Some(c) => s.push(c),
            }
        }
        Ok(Token::LitStr(s))
    }

    /// Read a backtick or double-quote delimited identifier
    ///
    /// For example `` `my table` `` or `"column name"`.
    fn lex_quoted_ident(&mut self) -> Result<Token, String> {
        let close = if self.peek() == Some('`') { '`' } else { '"' };
        self.advance(); // Skip opening quote
        let mut s = String::new();
        loop {
            match self.advance() {
                None => return Err("unterminated quoted identifier".to_string()),
                Some(c) if c == close => break,
                Some(c) => s.push(c),
            }
        }
        Ok(Token::Ident(s))
    }

    /// Read a numeric literal (integer or float)
    ///
    /// If the number is followed by `.` and more digits, it is a float.
    fn lex_number(&mut self) -> Result<Token, String> {
        let mut s = String::new();
        while self.peek().map(|c| c.is_ascii_digit()).unwrap_or(false) {
            s.push(self.advance().unwrap());
        }
        // Check if it's float format (decimal point followed by digits)
        if self.peek() == Some('.') && self.peek2().map(|c| c.is_ascii_digit()).unwrap_or(false) {
            s.push(self.advance().unwrap()); // Decimal point
            while self.peek().map(|c| c.is_ascii_digit()).unwrap_or(false) {
                s.push(self.advance().unwrap());
            }
            return s.parse::<f64>()
                .map(Token::LitFloat)
                .map_err(|_| format!("invalid float: {}", s));
        }
        s.parse::<i64>()
            .map(Token::LitInt)
            .map_err(|_| format!("invalid integer: {}", s))
    }

    /// Read an identifier or keyword
    ///
    /// Starts with a letter or underscore, followed by letters, digits, or underscores.
    /// After reading the full string, looks up the keyword table; returns a keyword Token if matched.
    fn lex_ident(&mut self) -> Result<Token, String> {
        let mut s = String::new();
        while self.peek().map(|c| c.is_alphanumeric() || c == '_').unwrap_or(false) {
            s.push(self.advance().unwrap());
        }
        Ok(keyword(&s).unwrap_or(Token::Ident(s)))
    }
}

impl Token {
    /// Returns true if the Token is an identifier
    pub fn is_ident(&self) -> bool {
        matches!(self, Token::Ident(_))
    }
}

// ── Tests ─────────────────────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;

    fn lex(sql: &str) -> Vec<Token> {
        Lexer::new(sql).tokenize().unwrap()
    }

    #[test]
    fn basic_select() {
        let toks = lex("SELECT * FROM users;");
        assert_eq!(toks[0], Token::Select);
        assert_eq!(toks[1], Token::Star);
        assert_eq!(toks[2], Token::From);
        assert_eq!(toks[3], Token::Ident("users".into()));
        assert_eq!(toks[4], Token::Semicolon);
    }

    #[test]
    fn string_literal() {
        let toks = lex("'hello world'");
        assert_eq!(toks[0], Token::LitStr("hello world".into()));
    }

    #[test]
    fn escaped_quote() {
        let toks = lex("'it''s'");
        assert_eq!(toks[0], Token::LitStr("it's".into()));
    }

    #[test]
    fn numbers() {
        let toks = lex("42 3.14");
        assert_eq!(toks[0], Token::LitInt(42));
        assert_eq!(toks[1], Token::LitFloat(3.14));
    }

    #[test]
    fn operators() {
        let toks = lex("<= >= != <>");
        assert_eq!(toks[0], Token::LtEq);
        assert_eq!(toks[1], Token::GtEq);
        assert_eq!(toks[2], Token::NotEq);
        assert_eq!(toks[3], Token::NotEq);
    }

    #[test]
    fn keywords_case_insensitive() {
        let toks = lex("select FROM Where");
        assert_eq!(toks[0], Token::Select);
        assert_eq!(toks[1], Token::From);
        assert_eq!(toks[2], Token::Where);
    }

    #[test]
    fn line_comment() {
        let toks = lex("SELECT -- this is a comment\n* FROM t");
        assert_eq!(toks[0], Token::Select);
        assert_eq!(toks[1], Token::Star);
    }

    #[test]
    fn quoted_ident() {
        let toks = lex("`my table`");
        assert_eq!(toks[0], Token::Ident("my table".into()));
    }
}
