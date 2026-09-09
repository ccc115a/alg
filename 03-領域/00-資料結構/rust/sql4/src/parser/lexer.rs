//! Lexer：SQL 字串 → Token 串
//!
//! 支援的 token 類型：
//!   - 關鍵字（SELECT、FROM、WHERE…）
//!   - 識別符（表名、欄位名）
//!   - 字面值（整數、浮點數、字串、NULL、TRUE、FALSE）
//!   - 運算子與標點（=、<、>、(、)、,、;…）

#[derive(Debug, Clone, PartialEq)]
pub enum Token {
    // ── 關鍵字 ──────────────────────────────────────────────────────────
    Select, From, Where, Insert, Into, Values,
    Update, Set, Delete, Create, Drop, Table,
    Index, On, Primary, Key, Not, Null, Unique,
    And, Or, Is, In, Like, Between, Order, By,
    Asc, Desc, Limit, Offset, Join, Inner, Left,
    Right, Outer, Cross, Natural, Using, Group,
    Having, Distinct, All, As, If, Exists,
    Begin, Commit, Rollback, Transaction,
    Virtual, Match,  // FTS5
    With, Recursive,  // CTE
    KwInteger, KwText,       // 型別關鍵字
    Real, Blob, Boolean,
    True, False,

    // ── 識別符 ──────────────────────────────────────────────────────────
    Ident(String),

    // ── 字面值 ──────────────────────────────────────────────────────────
    LitInt(i64),
    LitFloat(f64),
    LitStr(String),
    LitNull,

    // ── 運算子 ──────────────────────────────────────────────────────────
    Eq,         // =
    NotEq,      // != or <>
    Lt,         // <
    LtEq,       // <=
    Gt,         // >
    GtEq,       // >=
    Plus,       // +
    Minus,      // -
    Star,       // *
    Slash,      // /
    Percent,    // %
    Concat,     // ||

    // ── 標點 ────────────────────────────────────────────────────────────
    LParen,     // (
    RParen,     // )
    Comma,      // ,
    Semicolon,  // ;
    Dot,        // .

    // ── 特殊 ────────────────────────────────────────────────────────────
    Eof,
}

// ── 關鍵字對照表 ─────────────────────────────────────────────────────────

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
        _             => None,
    }
}

// ── Lexer ────────────────────────────────────────────────────────────────

pub struct Lexer {
    input: Vec<char>,
    pos:   usize,
}

impl Lexer {
    pub fn new(input: &str) -> Self {
        Lexer { input: input.chars().collect(), pos: 0 }
    }

    /// 掃描全部 token，遇到錯誤回傳 Err
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

    fn peek(&self) -> Option<char> { self.input.get(self.pos).copied() }
    fn peek2(&self) -> Option<char> { self.input.get(self.pos + 1).copied() }
    fn advance(&mut self) -> Option<char> {
        let c = self.input.get(self.pos).copied();
        if c.is_some() { self.pos += 1; }
        c
    }

    fn next_token(&mut self) -> Result<Token, String> {
        // 跳過空白與單行注解
        loop {
            match self.peek() {
                Some(c) if c.is_whitespace() => { self.advance(); }
                Some('-') if self.peek2() == Some('-') => {
                    while self.peek().map(|c| c != '\n').unwrap_or(false) { self.advance(); }
                }
                _ => break,
            }
        }

        match self.peek() {
            None => Ok(Token::Eof),
            Some(c) => match c {
                '(' => { self.advance(); Ok(Token::LParen) }
                ')' => { self.advance(); Ok(Token::RParen) }
                ',' => { self.advance(); Ok(Token::Comma) }
                ';' => { self.advance(); Ok(Token::Semicolon) }
                '.' => { self.advance(); Ok(Token::Dot) }
                '+' => { self.advance(); Ok(Token::Plus) }
                '-' => { self.advance(); Ok(Token::Minus) }
                '*' => { self.advance(); Ok(Token::Star) }
                '/' => { self.advance(); Ok(Token::Slash) }
                '%' => { self.advance(); Ok(Token::Percent) }
                '=' => { self.advance(); Ok(Token::Eq) }
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
                // 字串字面值（單引號）
                '\'' => self.lex_string(),
                // 反引號或雙引號識別符
                '`' | '"' => self.lex_quoted_ident(),
                // 數字
                c if c.is_ascii_digit() => self.lex_number(),
                // 識別符 / 關鍵字
                c if c.is_alphabetic() || c == '_' => self.lex_ident(),
                c => Err(format!("unexpected character '{}'", c)),
            }
        }
    }

    fn lex_string(&mut self) -> Result<Token, String> {
        self.advance(); // 吃掉開頭 '
        let mut s = String::new();
        loop {
            match self.advance() {
                None => return Err("unterminated string".to_string()),
                Some('\'') => {
                    // '' 是跳脫的單引號
                    if self.peek() == Some('\'') { self.advance(); s.push('\''); }
                    else { break; }
                }
                Some(c) => s.push(c),
            }
        }
        Ok(Token::LitStr(s))
    }

    fn lex_quoted_ident(&mut self) -> Result<Token, String> {
        let close = if self.peek() == Some('`') { '`' } else { '"' };
        self.advance();
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

    fn lex_number(&mut self) -> Result<Token, String> {
        let mut s = String::new();
        while self.peek().map(|c| c.is_ascii_digit()).unwrap_or(false) {
            s.push(self.advance().unwrap());
        }
        // 浮點數
        if self.peek() == Some('.') && self.peek2().map(|c| c.is_ascii_digit()).unwrap_or(false) {
            s.push(self.advance().unwrap()); // '.'
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

    fn lex_ident(&mut self) -> Result<Token, String> {
        let mut s = String::new();
        while self.peek().map(|c| c.is_alphanumeric() || c == '_').unwrap_or(false) {
            s.push(self.advance().unwrap());
        }
        Ok(keyword(&s).unwrap_or(Token::Ident(s)))
    }
}

// ── 測試 ─────────────────────────────────────────────────────────────────

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
