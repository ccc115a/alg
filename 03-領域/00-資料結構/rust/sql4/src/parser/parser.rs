//! Parser：Token 串 → AST

use super::ast::*;
use super::lexer::Token;

pub struct Parser {
    tokens: Vec<Token>,
    pos:    usize,
}

impl Parser {
    pub fn new(tokens: Vec<Token>) -> Self {
        Parser { tokens, pos: 0 }
    }

    // ── 基本操作 ──────────────────────────────────────────────────────────

    fn peek(&self) -> &Token {
        self.tokens.get(self.pos).unwrap_or(&Token::Eof)
    }

    fn peek2(&self) -> &Token {
        self.tokens.get(self.pos + 1).unwrap_or(&Token::Eof)
    }

    fn advance(&mut self) -> Token {
        let t = self.tokens.get(self.pos).cloned().unwrap_or(Token::Eof);
        if self.pos < self.tokens.len() { self.pos += 1; }
        t
    }

    fn check(&self, tok: &Token) -> bool { self.peek() == tok }

    fn eat(&mut self, tok: &Token) -> Result<(), String> {
        if self.peek() == tok {
            self.advance();
            Ok(())
        } else {
            Err(format!("expected {:?}, got {:?}", tok, self.peek()))
        }
    }

    fn eat_ident(&mut self) -> Result<String, String> {
        match self.advance() {
            Token::Ident(s) => Ok(s),
            // 允許關鍵字當作識別符（常見情形：表名叫 "order"）
            t => {
                if let Some(s) = token_as_ident(&t) { Ok(s) }
                else { Err(format!("expected identifier, got {:?}", t)) }
            }
        }
    }

    fn maybe(&mut self, tok: &Token) -> bool {
        if self.peek() == tok { self.advance(); true } else { false }
    }

    // ── 頂層解析 ──────────────────────────────────────────────────────────

    pub fn parse(&mut self) -> Result<Vec<Statement>, String> {
        let mut stmts = Vec::new();
        while self.peek() != &Token::Eof {
            self.maybe(&Token::Semicolon);
            if self.peek() == &Token::Eof { break; }
            stmts.push(self.parse_statement()?);
            self.maybe(&Token::Semicolon);
        }
        Ok(stmts)
    }

    fn parse_statement(&mut self) -> Result<Statement, String> {
        match self.peek().clone() {
            Token::Select | Token::With => Ok(Statement::Select(self.parse_select()?)),
            Token::Insert   => Ok(Statement::Insert(self.parse_insert()?)),
            Token::Update   => Ok(Statement::Update(self.parse_update()?)),
            Token::Delete   => Ok(Statement::Delete(self.parse_delete()?)),
            Token::Create   => self.parse_create(),
            Token::Drop     => Ok(Statement::DropTable(self.parse_drop_table()?)),
            Token::Begin    => { self.advance(); Ok(Statement::Begin) }
            Token::Commit   => { self.advance(); Ok(Statement::Commit) }
            Token::Rollback => { self.advance(); Ok(Statement::Rollback) }
            t => Err(format!("unexpected token {:?}", t)),
        }
    }

    // ── SELECT ────────────────────────────────────────────────────────────

    fn parse_select(&mut self) -> Result<SelectStmt, String> {
        // WITH ctes
        let with = self.parse_with_clause()?;

        self.eat(&Token::Select)?;
        let distinct = self.maybe(&Token::Distinct);

        let columns = self.parse_select_items()?;

        let from = if self.maybe(&Token::From) {
            Some(self.parse_from_item()?)
        } else { None };

        let joins = self.parse_joins()?;

        let where_ = if self.maybe(&Token::Where) {
            Some(self.parse_expr()?)
        } else { None };

        let group_by = if self.check(&Token::Group) && self.peek2() == &Token::By {
            self.advance(); self.advance();
            self.parse_expr_list()?
        } else { vec![] };

        let having = if self.maybe(&Token::Having) {
            Some(self.parse_expr()?)
        } else { None };

        let order_by = if self.check(&Token::Order) && self.peek2() == &Token::By {
            self.advance(); self.advance();
            self.parse_order_items()?
        } else { vec![] };

        let limit = if self.maybe(&Token::Limit) {
            Some(self.parse_expr()?)
        } else { None };

        let offset = if self.maybe(&Token::Offset) {
            Some(self.parse_expr()?)
        } else { None };

        Ok(SelectStmt { with, distinct, columns, from, joins, where_, group_by, having, order_by, limit, offset })
    }

    fn parse_select_items(&mut self) -> Result<Vec<SelectItem>, String> {
        let mut items = Vec::new();
        loop {
            let item = if self.check(&Token::Star) {
                self.advance();
                SelectItem::Star
            } else {
                let expr = self.parse_expr()?;
                // table.*
                if let Expr::Column { table: None, name } = &expr {
                    if self.check(&Token::Dot) && self.peek2() == &Token::Star {
                        let t = name.clone();
                        self.advance(); self.advance();
                        items.push(SelectItem::TableStar(t));
                        if !self.maybe(&Token::Comma) { break; }
                        continue;
                    }
                }
                let alias = if self.maybe(&Token::As) {
                    Some(self.eat_ident()?)
                } else if let Token::Ident(_) = self.peek() {
                    Some(self.eat_ident()?)
                } else { None };
                SelectItem::Expr { expr, alias }
            };
            items.push(item);
            if !self.maybe(&Token::Comma) { break; }
        }
        Ok(items)
    }

    fn parse_table_ref(&mut self) -> Result<TableRef, String> {
        let name = self.eat_ident()?;
        let alias = if self.maybe(&Token::As) {
            Some(self.eat_ident()?)
        } else if let Token::Ident(_) = self.peek() {
            Some(self.eat_ident()?)
        } else { None };
        Ok(TableRef { name, alias })
    }

    fn parse_joins(&mut self) -> Result<Vec<Join>, String> {
        let mut joins = Vec::new();
        loop {
            let kind = match self.peek().clone() {
                Token::Join | Token::Inner => {
                    if self.peek().clone() == Token::Inner { self.advance(); }
                    self.eat(&Token::Join)?;
                    JoinKind::Inner
                }
                Token::Left => {
                    self.advance();
                    self.maybe(&Token::Outer);
                    self.eat(&Token::Join)?;
                    JoinKind::Left
                }
                Token::Right => {
                    self.advance();
                    self.maybe(&Token::Outer);
                    self.eat(&Token::Join)?;
                    JoinKind::Right
                }
                Token::Cross => {
                    self.advance();
                    self.eat(&Token::Join)?;
                    JoinKind::Cross
                }
                Token::Natural => {
                    self.advance();
                    self.eat(&Token::Join)?;
                    JoinKind::Natural
                }
                _ => break,
            };
            let table = self.parse_table_ref()?;
            let condition = if self.maybe(&Token::On) {
                JoinCondition::On(self.parse_expr()?)
            } else if self.maybe(&Token::Using) {
                self.eat(&Token::LParen)?;
                let cols = self.parse_ident_list()?;
                self.eat(&Token::RParen)?;
                JoinCondition::Using(cols)
            } else {
                JoinCondition::None
            };
            joins.push(Join { kind, table, condition });
        }
        Ok(joins)
    }

    fn parse_order_items(&mut self) -> Result<Vec<OrderItem>, String> {
        let mut items = Vec::new();
        loop {
            let expr = self.parse_expr()?;
            let asc = !self.maybe(&Token::Desc);
            if self.check(&Token::Asc) { self.advance(); }
            items.push(OrderItem { expr, asc });
            if !self.maybe(&Token::Comma) { break; }
        }
        Ok(items)
    }

    // ── INSERT ────────────────────────────────────────────────────────────

    fn parse_insert(&mut self) -> Result<InsertStmt, String> {
        self.eat(&Token::Insert)?;
        self.eat(&Token::Into)?;
        let table = self.eat_ident()?;

        let columns = if self.check(&Token::LParen) && self.is_values_next() {
            self.eat(&Token::LParen)?;
            let cols = self.parse_ident_list()?;
            self.eat(&Token::RParen)?;
            cols
        } else { vec![] };

        self.eat(&Token::Values)?;
        let mut values = Vec::new();
        loop {
            self.eat(&Token::LParen)?;
            values.push(self.parse_expr_list()?);
            self.eat(&Token::RParen)?;
            if !self.maybe(&Token::Comma) { break; }
        }
        Ok(InsertStmt { table, columns, values })
    }

    fn is_values_next(&self) -> bool {
        // 往前掃 ) 之後是否接 VALUES
        let mut i = self.pos + 1;
        let mut depth = 1;
        while i < self.tokens.len() {
            match &self.tokens[i] {
                Token::LParen => depth += 1,
                Token::RParen => { depth -= 1; if depth == 0 { break; } }
                _ => {}
            }
            i += 1;
        }
        self.tokens.get(i + 1) == Some(&Token::Values)
    }

    // ── UPDATE ────────────────────────────────────────────────────────────

    fn parse_update(&mut self) -> Result<UpdateStmt, String> {
        self.eat(&Token::Update)?;
        let table = self.eat_ident()?;
        self.eat(&Token::Set)?;
        let mut sets = Vec::new();
        loop {
            let col = self.eat_ident()?;
            self.eat(&Token::Eq)?;
            let val = self.parse_expr()?;
            sets.push((col, val));
            if !self.maybe(&Token::Comma) { break; }
        }
        let where_ = if self.maybe(&Token::Where) { Some(self.parse_expr()?) } else { None };
        Ok(UpdateStmt { table, sets, where_ })
    }

    // ── DELETE ────────────────────────────────────────────────────────────

    fn parse_delete(&mut self) -> Result<DeleteStmt, String> {
        self.eat(&Token::Delete)?;
        self.eat(&Token::From)?;
        let table = self.eat_ident()?;
        let where_ = if self.maybe(&Token::Where) { Some(self.parse_expr()?) } else { None };
        Ok(DeleteStmt { table, where_ })
    }

    // ── CREATE ────────────────────────────────────────────────────────────

    fn parse_create(&mut self) -> Result<Statement, String> {
        self.eat(&Token::Create)?;
        let unique = self.maybe(&Token::Unique);
        match self.peek().clone() {
            Token::Table => Ok(Statement::CreateTable(self.parse_create_table()?)),
            Token::Index => Ok(Statement::CreateIndex(self.parse_create_index(unique)?)),
            t => Err(format!("expected TABLE or INDEX after CREATE, got {:?}", t)),
        }
    }

    fn parse_create_table(&mut self) -> Result<CreateTableStmt, String> {
        self.eat(&Token::Table)?;
        let if_not_exists = if self.check(&Token::If) {
            self.advance();
            self.eat(&Token::Not)?;
            self.eat(&Token::Exists)?;
            true
        } else { false };

        let name = self.eat_ident()?;
        self.eat(&Token::LParen)?;

        let mut columns = Vec::new();
        let mut constraints = Vec::new();
        loop {
            if self.check(&Token::Primary) || self.check(&Token::Unique) {
                constraints.push(self.parse_table_constraint()?);
            } else {
                columns.push(self.parse_column_def()?);
            }
            if !self.maybe(&Token::Comma) { break; }
            // 允許尾隨逗號前的 ) 結束
            if self.check(&Token::RParen) { break; }
        }
        self.eat(&Token::RParen)?;
        Ok(CreateTableStmt { if_not_exists, name, columns, constraints })
    }

    fn parse_column_def(&mut self) -> Result<ColumnDef, String> {
        let name = self.eat_ident()?;
        let data_type = self.parse_sql_type()?;
        let mut cons = Vec::new();
        loop {
            match self.peek().clone() {
                Token::Not => {
                    self.advance();
                    self.eat(&Token::LitNull)?;
                    cons.push(ColumnConstraint::NotNull);
                }
                Token::Primary => {
                    self.advance();
                    self.eat(&Token::Key)?;
                    let autoincrement = matches!(self.peek(), Token::Ident(s) if s.eq_ignore_ascii_case("AUTOINCREMENT"));
                    if autoincrement { self.advance(); }
                    cons.push(ColumnConstraint::PrimaryKey { autoincrement });
                }
                Token::Unique => { self.advance(); cons.push(ColumnConstraint::Unique); }
                _ => break,
            }
        }
        Ok(ColumnDef { name, data_type, constraints: cons })
    }

    fn parse_sql_type(&mut self) -> Result<SqlType, String> {
        match self.advance() {
            Token::KwInteger => Ok(SqlType::Integer),
            Token::Real      => Ok(SqlType::Real),
            Token::KwText    => Ok(SqlType::Text),
            Token::Blob      => Ok(SqlType::Blob),
            Token::Boolean   => Ok(SqlType::Boolean),
            Token::LitNull   => Ok(SqlType::Null),
            t => Err(format!("expected type, got {:?}", t)),
        }
    }

    fn parse_table_constraint(&mut self) -> Result<TableConstraint, String> {
        match self.peek().clone() {
            Token::Primary => {
                self.advance(); self.eat(&Token::Key)?;
                self.eat(&Token::LParen)?;
                let cols = self.parse_ident_list()?;
                self.eat(&Token::RParen)?;
                Ok(TableConstraint::PrimaryKey(cols))
            }
            Token::Unique => {
                self.advance();
                self.eat(&Token::LParen)?;
                let cols = self.parse_ident_list()?;
                self.eat(&Token::RParen)?;
                Ok(TableConstraint::Unique(cols))
            }
            t => Err(format!("expected table constraint, got {:?}", t)),
        }
    }

    fn parse_create_index(&mut self, unique: bool) -> Result<CreateIndexStmt, String> {
        self.eat(&Token::Index)?;
        let name = self.eat_ident()?;
        self.eat(&Token::On)?;
        let table = self.eat_ident()?;
        self.eat(&Token::LParen)?;
        let columns = self.parse_ident_list()?;
        self.eat(&Token::RParen)?;
        Ok(CreateIndexStmt { unique, name, table, columns })
    }

    // ── DROP TABLE ────────────────────────────────────────────────────────

    fn parse_drop_table(&mut self) -> Result<DropTableStmt, String> {
        self.eat(&Token::Drop)?;
        self.eat(&Token::Table)?;
        let if_exists = if self.check(&Token::If) {
            self.advance();
            self.eat(&Token::Exists)?;
            true
        } else { false };
        let name = self.eat_ident()?;
        Ok(DropTableStmt { if_exists, name })
    }

    // ── 運算式 (Pratt parser) ─────────────────────────────────────────────

    fn parse_expr(&mut self) -> Result<Expr, String> {
        self.parse_or()
    }

    fn parse_or(&mut self) -> Result<Expr, String> {
        let mut left = self.parse_and()?;
        while self.check(&Token::Or) {
            self.advance();
            let right = self.parse_and()?;
            left = Expr::BinOp { left: Box::new(left), op: BinOp::Or, right: Box::new(right) };
        }
        Ok(left)
    }

    fn parse_and(&mut self) -> Result<Expr, String> {
        let mut left = self.parse_not()?;
        while self.check(&Token::And) {
            self.advance();
            let right = self.parse_not()?;
            left = Expr::BinOp { left: Box::new(left), op: BinOp::And, right: Box::new(right) };
        }
        Ok(left)
    }

    fn parse_not(&mut self) -> Result<Expr, String> {
        if self.check(&Token::Not) {
            self.advance();
            let expr = self.parse_comparison()?;
            return Ok(Expr::UnaryOp { op: UnaryOp::Not, expr: Box::new(expr) });
        }
        self.parse_comparison()
    }

    fn parse_comparison(&mut self) -> Result<Expr, String> {
        let left = self.parse_addition()?;

        // IS [NOT] NULL
        if self.check(&Token::Is) {
            self.advance();
            let negated = self.maybe(&Token::Not);
            self.eat(&Token::LitNull)?;
            return Ok(Expr::IsNull { expr: Box::new(left), negated });
        }

        // [NOT] BETWEEN
        let negated_between = if self.check(&Token::Not) && self.peek2() == &Token::Between {
            self.advance(); true
        } else { false };
        if self.maybe(&Token::Between) {
            let low  = self.parse_addition()?;
            self.eat(&Token::And)?;
            let high = self.parse_addition()?;
            return Ok(Expr::Between { expr: Box::new(left), low: Box::new(low), high: Box::new(high), negated: negated_between });
        }

        // [NOT] IN (...)
        let negated_in = if !negated_between && self.check(&Token::Not) && self.peek2() == &Token::In {
            self.advance(); true
        } else { false };
        if self.maybe(&Token::In) {
            self.eat(&Token::LParen)?;
            // IN (SELECT ...) 子查詢
            if self.check(&Token::Select) || self.check(&Token::With) {
                let query = self.parse_select()?;
                self.eat(&Token::RParen)?;
                return Ok(Expr::InSubquery { expr: Box::new(left), query: Box::new(query), negated: negated_in });
            }
            let list = self.parse_expr_list()?;
            self.eat(&Token::RParen)?;
            return Ok(Expr::InList { expr: Box::new(left), list, negated: negated_in });
        }

        // [NOT] LIKE
        let negated_like = if !negated_in && self.check(&Token::Not) && self.peek2() == &Token::Like {
            self.advance(); true
        } else { false };
        if self.maybe(&Token::Like) {
            let pattern = self.parse_addition()?;
            return Ok(Expr::Like { expr: Box::new(left), pattern: Box::new(pattern), negated: negated_like });
        }

        let op = match self.peek() {
            Token::Eq     => BinOp::Eq,
            Token::NotEq  => BinOp::NotEq,
            Token::Lt     => BinOp::Lt,
            Token::LtEq   => BinOp::LtEq,
            Token::Gt     => BinOp::Gt,
            Token::GtEq   => BinOp::GtEq,
            _ => return Ok(left),
        };
        self.advance();
        let right = self.parse_addition()?;
        Ok(Expr::BinOp { left: Box::new(left), op, right: Box::new(right) })
    }

    fn parse_addition(&mut self) -> Result<Expr, String> {
        let mut left = self.parse_multiplication()?;
        loop {
            let op = match self.peek() {
                Token::Plus   => BinOp::Add,
                Token::Minus  => BinOp::Sub,
                Token::Concat => BinOp::Concat,
                _ => break,
            };
            self.advance();
            let right = self.parse_multiplication()?;
            left = Expr::BinOp { left: Box::new(left), op, right: Box::new(right) };
        }
        Ok(left)
    }

    fn parse_multiplication(&mut self) -> Result<Expr, String> {
        let mut left = self.parse_unary()?;
        loop {
            let op = match self.peek() {
                Token::Star    => BinOp::Mul,
                Token::Slash   => BinOp::Div,
                Token::Percent => BinOp::Mod,
                _ => break,
            };
            self.advance();
            let right = self.parse_unary()?;
            left = Expr::BinOp { left: Box::new(left), op, right: Box::new(right) };
        }
        Ok(left)
    }

    fn parse_unary(&mut self) -> Result<Expr, String> {
        if self.check(&Token::Minus) {
            self.advance();
            let expr = self.parse_primary()?;
            return Ok(Expr::UnaryOp { op: UnaryOp::Neg, expr: Box::new(expr) });
        }
        self.parse_primary()
    }

    fn parse_primary(&mut self) -> Result<Expr, String> {
        match self.peek().clone() {
            Token::LitInt(v)  => { self.advance(); Ok(Expr::LitInt(v)) }
            Token::LitFloat(v)=> { self.advance(); Ok(Expr::LitFloat(v)) }
            Token::LitStr(s)  => { self.advance(); Ok(Expr::LitStr(s)) }
            Token::LitNull    => { self.advance(); Ok(Expr::LitNull) }
            Token::True       => { self.advance(); Ok(Expr::LitBool(true)) }
            Token::False      => { self.advance(); Ok(Expr::LitBool(false)) }
            Token::LParen => {
                self.advance();
                // 純量子查詢 (SELECT ...)
                if self.check(&Token::Select) || self.check(&Token::With) {
                    let query = self.parse_select()?;
                    self.eat(&Token::RParen)?;
                    return Ok(Expr::ScalarSubquery(Box::new(query)));
                }
                let expr = self.parse_expr()?;
                self.eat(&Token::RParen)?;
                Ok(expr)
            }
            Token::Exists => {
                self.advance();
                let negated = false;
                self.eat(&Token::LParen)?;
                let query = self.parse_select()?;
                self.eat(&Token::RParen)?;
                Ok(Expr::Exists { query: Box::new(query), negated })
            }
            Token::Ident(name) => {
                self.advance();
                // function call
                if self.check(&Token::LParen) {
                    return self.parse_function_call(name);
                }
                // table.column
                if self.check(&Token::Dot) {
                    self.advance();
                    let col = self.eat_ident()?;
                    return Ok(Expr::Column { table: Some(name), name: col });
                }
                Ok(Expr::Column { table: None, name })
            }
            t => Err(format!("unexpected token in expression: {:?}", t)),
        }
    }

    fn parse_function_call(&mut self, name: String) -> Result<Expr, String> {
        self.eat(&Token::LParen)?;
        let distinct = self.maybe(&Token::Distinct);
        let args = if self.check(&Token::Star) {
            self.advance();
            vec![Expr::Column { table: None, name: "*".to_string() }]
        } else if self.check(&Token::RParen) {
            vec![]
        } else {
            self.parse_expr_list()?
        };
        self.eat(&Token::RParen)?;
        Ok(Expr::Function { name: name.to_uppercase(), args, distinct })
    }

    // ── 輔助 ──────────────────────────────────────────────────────────────

    fn parse_expr_list(&mut self) -> Result<Vec<Expr>, String> {
        let mut list = vec![self.parse_expr()?];
        while self.maybe(&Token::Comma) {
            if self.check(&Token::RParen) { break; }
            list.push(self.parse_expr()?);
        }
        Ok(list)
    }

    fn parse_ident_list(&mut self) -> Result<Vec<String>, String> {
        let mut list = vec![self.eat_ident()?];
        while self.maybe(&Token::Comma) { list.push(self.eat_ident()?); }
        Ok(list)
    }
    // ── WITH / CTE ────────────────────────────────────────────────────────

    fn parse_with_clause(&mut self) -> Result<Vec<crate::parser::ast::Cte>, String> {
        use crate::parser::ast::Cte;
        if !self.check(&Token::With) { return Ok(vec![]); }
        self.advance();
        self.maybe(&Token::Recursive);
        let mut ctes = Vec::new();
        loop {
            let name = self.eat_ident()?;
            self.eat(&Token::As)?;
            self.eat(&Token::LParen)?;
            let query = self.parse_select()?;
            self.eat(&Token::RParen)?;
            ctes.push(Cte { name, query: Box::new(query) });
            if !self.maybe(&Token::Comma) { break; }
        }
        Ok(ctes)
    }

    // ── FROM item（表名或子查詢） ──────────────────────────────────────────

    fn parse_from_item(&mut self) -> Result<crate::parser::ast::FromItem, String> {
        use crate::parser::ast::{FromItem, TableRef};
        if self.check(&Token::LParen) {
            self.advance();
            if self.check(&Token::Select) || self.check(&Token::With) {
                let query = self.parse_select()?;
                self.eat(&Token::RParen)?;
                let alias = if self.maybe(&Token::As) {
                    self.eat_ident()?
                } else {
                    self.eat_ident()?
                };
                Ok(FromItem::Subquery { query: Box::new(query), alias })
            } else {
                let name = self.eat_ident()?;
                self.eat(&Token::RParen)?;
                let alias = if self.maybe(&Token::As) { Some(self.eat_ident()?) }
                    else if let Token::Ident(_) = self.peek() { Some(self.eat_ident()?) }
                    else { None };
                Ok(FromItem::Table(TableRef { name, alias }))
            }
        } else {
            let tref = self.parse_table_ref()?;
            Ok(FromItem::Table(tref))
        }
    }


}

// 允許某些關鍵字作為識別符
fn token_as_ident(t: &Token) -> Option<String> {
    match t {
        Token::KwText    => Some("text".to_string()),
        Token::KwInteger => Some("integer".to_string()),
        Token::Real      => Some("real".to_string()),
        Token::Blob      => Some("blob".to_string()),
        Token::Boolean   => Some("boolean".to_string()),
        Token::Ident(s)  => Some(s.clone()),
        _ => None,
    }
}

// ── 公開便利函式 ──────────────────────────────────────────────────────────

pub fn parse(sql: &str) -> Result<Vec<Statement>, String> {
    let tokens = super::lexer::Lexer::new(sql).tokenize()?;
    Parser::new(tokens).parse()
}

// ── 測試 ─────────────────────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;

    fn p(sql: &str) -> Vec<Statement> {
        parse(sql).unwrap_or_else(|e| panic!("parse error: {}", e))
    }

    #[test]
    fn select_star() {
        let stmts = p("SELECT * FROM users");
        if let Statement::Select(s) = &stmts[0] {
            match s.from.as_ref().unwrap() {
                crate::parser::ast::FromItem::Table(t) => assert_eq!(t.name, "users"),
                _ => panic!("expected table"),
            }
        }
    }

    #[test]
    fn select_where() {
        let stmts = p("SELECT id, name FROM users WHERE id = 1");
        if let Statement::Select(s) = &stmts[0] {
            assert_eq!(s.columns.len(), 2);
            assert!(s.where_.is_some());
        } else { panic!() }
    }

    #[test]
    fn select_order_limit() {
        let stmts = p("SELECT * FROM t ORDER BY id DESC LIMIT 10 OFFSET 5");
        if let Statement::Select(s) = &stmts[0] {
            assert_eq!(s.order_by.len(), 1);
            assert!(!s.order_by[0].asc);
            assert!(s.limit.is_some());
            assert!(s.offset.is_some());
        } else { panic!() }
    }

    #[test]
    fn insert_with_columns() {
        let stmts = p("INSERT INTO users (id, name) VALUES (1, 'Alice')");
        if let Statement::Insert(s) = &stmts[0] {
            assert_eq!(s.table, "users");
            assert_eq!(s.columns, vec!["id", "name"]);
            assert_eq!(s.values.len(), 1);
            assert_eq!(s.values[0][0], Expr::LitInt(1));
        } else { panic!() }
    }

    #[test]
    fn insert_multi_rows() {
        let stmts = p("INSERT INTO t VALUES (1,'a'),(2,'b')");
        if let Statement::Insert(s) = &stmts[0] {
            assert_eq!(s.values.len(), 2);
        } else { panic!() }
    }

    #[test]
    fn update_stmt() {
        let stmts = p("UPDATE users SET name='Bob', age=30 WHERE id=1");
        if let Statement::Update(s) = &stmts[0] {
            assert_eq!(s.table, "users");
            assert_eq!(s.sets.len(), 2);
            assert!(s.where_.is_some());
        } else { panic!() }
    }

    #[test]
    fn delete_stmt() {
        let stmts = p("DELETE FROM users WHERE id = 42");
        if let Statement::Delete(s) = &stmts[0] {
            assert_eq!(s.table, "users");
            assert!(s.where_.is_some());
        } else { panic!() }
    }

    #[test]
    fn create_table() {
        let stmts = p("CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            score REAL
        )");
        if let Statement::CreateTable(s) = &stmts[0] {
            assert_eq!(s.name, "users");
            assert_eq!(s.columns.len(), 3);
            assert!(matches!(s.columns[0].constraints[0], ColumnConstraint::PrimaryKey { .. }));
            assert!(matches!(s.columns[1].constraints[0], ColumnConstraint::NotNull));
        } else { panic!() }
    }

    #[test]
    fn create_table_if_not_exists() {
        let stmts = p("CREATE TABLE IF NOT EXISTS t (id INTEGER)");
        if let Statement::CreateTable(s) = &stmts[0] {
            assert!(s.if_not_exists);
        } else { panic!() }
    }

    #[test]
    fn drop_table() {
        let stmts = p("DROP TABLE IF EXISTS users");
        if let Statement::DropTable(s) = &stmts[0] {
            assert!(s.if_exists);
            assert_eq!(s.name, "users");
        } else { panic!() }
    }

    #[test]
    fn create_index() {
        let stmts = p("CREATE UNIQUE INDEX idx_name ON users (name)");
        if let Statement::CreateIndex(s) = &stmts[0] {
            assert!(s.unique);
            assert_eq!(s.name, "idx_name");
            assert_eq!(s.table, "users");
        } else { panic!() }
    }

    #[test]
    fn expr_between() {
        let stmts = p("SELECT * FROM t WHERE age BETWEEN 18 AND 65");
        if let Statement::Select(s) = &stmts[0] {
            assert!(matches!(s.where_.as_ref().unwrap(), Expr::Between { .. }));
        } else { panic!() }
    }

    #[test]
    fn expr_in_list() {
        let stmts = p("SELECT * FROM t WHERE id IN (1, 2, 3)");
        if let Statement::Select(s) = &stmts[0] {
            assert!(matches!(s.where_.as_ref().unwrap(), Expr::InList { .. }));
        } else { panic!() }
    }

    #[test]
    fn expr_like() {
        let stmts = p("SELECT * FROM t WHERE name LIKE 'A%'");
        if let Statement::Select(s) = &stmts[0] {
            assert!(matches!(s.where_.as_ref().unwrap(), Expr::Like { .. }));
        } else { panic!() }
    }

    #[test]
    fn expr_is_null() {
        let stmts = p("SELECT * FROM t WHERE name IS NULL");
        if let Statement::Select(s) = &stmts[0] {
            assert!(matches!(s.where_.as_ref().unwrap(), Expr::IsNull { negated: false, .. }));
        } else { panic!() }
    }

    #[test]
    fn function_call() {
        let stmts = p("SELECT COUNT(*), MAX(score) FROM t");
        if let Statement::Select(s) = &stmts[0] {
            assert_eq!(s.columns.len(), 2);
        } else { panic!() }
    }

    #[test]
    fn join_stmt() {
        let stmts = p("SELECT * FROM users u JOIN orders o ON u.id = o.user_id");
        if let Statement::Select(s) = &stmts[0] {
            assert_eq!(s.joins.len(), 1);
            assert_eq!(s.joins[0].kind, JoinKind::Inner);
        } else { panic!() }
    }

    #[test]
    fn transaction() {
        let stmts = p("BEGIN; INSERT INTO t VALUES (1); COMMIT");
        assert_eq!(stmts.len(), 3);
        assert_eq!(stmts[0], Statement::Begin);
        assert_eq!(stmts[2], Statement::Commit);
    }

    #[test]
    fn multi_statement() {
        let stmts = p("SELECT 1; SELECT 2; SELECT 3");
        assert_eq!(stmts.len(), 3);
    }
}