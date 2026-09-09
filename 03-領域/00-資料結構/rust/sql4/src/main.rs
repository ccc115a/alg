mod btree;
mod catalog;
mod fts;
mod interface;
mod pager;
mod parser;
mod planner;
mod table;

use interface::Repl;

fn main() {
    Repl::new().run();
}
