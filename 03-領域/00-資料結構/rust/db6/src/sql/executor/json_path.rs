//! JSON Path evaluation utilities
//!
//! Provides evaluation of JSON Path expressions in SQL WHERE clauses
//!
//! # Supported Syntax
//!
//! - `@.field > value` - comparison
//! - `@.field = 'value'` - string comparison
//! - `@.field LIKE 'pattern%'` - pattern match
//! - `@.field IN ('a', 'b')` - list membership
//! - `@.field IS NULL` - null check
//! - `AND / OR` - compound conditions

use crate::sql::parser::ast::{Expr, JsonPathOpKind};

/// Evaluate WHERE expression (supports JSON Path)
pub fn eval_expr(expr: &Expr, value: &[u8]) -> bool {
    match expr {
        Expr::JsonPath { path, op, negated, value: cmp_value } => {
            let json_str = String::from_utf8_lossy(value);
            let json: serde_json::Value = match serde_json::from_str(&json_str) {
                Ok(v) => v,
                Err(_) => return false,
            };
            let field_value = json_get(&json, path);
            let result = json_path_compare(&field_value, op, cmp_value);
            if *negated { !result } else { result }
        }
        Expr::BinOp { left, op, right } => {
            let left_result = eval_expr(left, value);
            let right_result = eval_expr(right, value);
            match op {
                crate::sql::parser::ast::BinOp::And => left_result && right_result,
                crate::sql::parser::ast::BinOp::Or => left_result || right_result,
                _ => false,
            }
        }
        Expr::UnaryOp { op: crate::sql::parser::ast::UnaryOp::Not, expr } => {
            !eval_expr(expr, value)
        }
        _ => true,
    }
}

/// Get value from JSON based on JSON Path
pub fn json_get(json: &serde_json::Value, path: &[String]) -> serde_json::Value {
    let mut current = json.clone();
    for key in path {
        if let serde_json::Value::Object(map) = &current {
            if let Some(v) = map.get(key) { current = v.clone(); }
            else { return serde_json::Value::Null; }
        } else { return serde_json::Value::Null; }
    }
    current
}

/// Compare JSON value with expression value
pub fn json_path_compare(json_val: &serde_json::Value, op: &JsonPathOpKind, cmp: &Expr) -> bool {
    use JsonPathOpKind::*;
    let cmp_prim = match cmp {
        Expr::LitStr(s) => serde_json::Value::String(s.clone()),
        Expr::LitInt(i) => serde_json::Value::Number(serde_json::Number::from(*i)),
        Expr::LitFloat(f) => serde_json::json!(f),
        Expr::LitBool(b) => serde_json::Value::Bool(*b),
        Expr::LitNull => serde_json::Value::Null,
        _ => return false,
    };
    match op {
        Eq => json_val == &cmp_prim,
        Ne => json_val != &cmp_prim,
        Lt => json_cmp(json_val, &cmp_prim) == std::cmp::Ordering::Less,
        LtEq => matches!(json_cmp(json_val, &cmp_prim), std::cmp::Ordering::Less | std::cmp::Ordering::Equal),
        Gt => json_cmp(json_val, &cmp_prim) == std::cmp::Ordering::Greater,
        GtEq => matches!(json_cmp(json_val, &cmp_prim), std::cmp::Ordering::Greater | std::cmp::Ordering::Equal),
        Like => {
            if let (serde_json::Value::String(s), serde_json::Value::String(p)) = (json_val, &cmp_prim) {
                if p.ends_with('%') { s.starts_with(&p[..p.len()-1]) } else { s.contains(p.as_str()) }
            } else { false }
        }
        In => json_val == &cmp_prim,
        IsNull => matches!(json_val, serde_json::Value::Null),
    }
}

/// Compare two JSON values
fn json_cmp(a: &serde_json::Value, b: &serde_json::Value) -> std::cmp::Ordering {
    use serde_json::Value;
    match (a, b) {
        (Value::Number(an), Value::Number(bn)) => {
            an.as_f64()
                .and_then(|af| bn.as_f64().map(|bf| af.partial_cmp(&bf).unwrap_or(std::cmp::Ordering::Equal)))
                .unwrap_or(std::cmp::Ordering::Equal)
        }
        (Value::String(as_str), Value::String(bs_str)) => as_str.cmp(bs_str),
        (Value::Bool(ab), Value::Bool(bb)) => ab.cmp(bb),
        _ => std::cmp::Ordering::Equal,
    }
}