const fs = require('fs');

// ==========================================
// 1. 抽象語法樹 (AST) 定義
// ==========================================
class Var {
    constructor(name) { this.name = name; }
    toString() { return this.name; }
}

class Abs {
    constructor(param, body) { this.param = param; this.body = body; }
    toString() { return `(\\${this.param}.${this.body.toString()})`; }
}

class App {
    constructor(left, right) { this.left = left; this.right = right; }
    toString() { return `(${this.left.toString()} ${this.right.toString()})`; }
}

// ==========================================
// 2. 詞法分析 (Tokenizer) 與 語法解析 (Parser)
// ==========================================
function tokenize(input) {
    let str = input.trim();
    let i = 0;
    const result = [];
    while (i < str.length) {
        if (/\s/.test(str[i])) {
            i++;
            continue;
        }
        if (str[i] === '\\' || str[i] === 'λ' || str[i] === '.' || str[i] === '(' || str[i] === ')') {
            result.push(str[i]);
            i++;
        } else if (/[a-zA-Z_]/.test(str[i])) {
            let ident = '';
            while (i < str.length && /[a-zA-Z0-9_]/.test(str[i])) {
                ident += str[i];
                i++;
            }
            result.push(ident);
        } else {
            throw new Error(`未預期的字元: ${str[i]} 在位置 ${i}`);
        }
    }
    return result;
}

class Parser {
    constructor(tokens) {
        this.tokens = tokens;
        this.pos = 0;
    }

    peek() { return this.tokens[this.pos]; }
    consume(expected) {
        const t = this.peek();
        if (expected && t !== expected) throw new Error(`預期 '${expected}', 但得到 '${t}'`);
        this.pos++;
        return t;
    }

    parseTerm() { return this.parseApp(); }

    parseApp() {
        let left = this.parseAtom();
        while (this.pos < this.tokens.length) {
            const t = this.peek();
            if (t === ')' || t === '.' || t === undefined) break;
            if (t === '(' || t === '\\' || t === 'λ' || /^[a-zA-Z_]/.test(t)) {
                let right = this.parseAtom();
                left = new App(left, right);
            } else {
                break;
            }
        }
        return left;
    }

    parseAtom() {
        const t = this.peek();
        if (t === undefined) throw new Error("未預期的輸入結尾");
        if (t === '(') {
            this.consume('(');
            let term = this.parseTerm();
            this.consume(')');
            return term;
        }
        if (t === '\\' || t === 'λ') {
            this.consume();
            const param = this.consume();
            if (!/^[a-zA-Z_]/.test(param)) throw new Error(`預期參數名稱，得到 '${param}'`);
            this.consume('.');
            const body = this.parseTerm();
            return new Abs(param, body);
        }
        if (/^[a-zA-Z_]/.test(t)) {
            this.consume();
            return new Var(t);
        }
        throw new Error(`未預期的 Token: ${t}`);
    }
}

function parse(input) {
    const tokens = tokenize(input);
    const parser = new Parser(tokens);
    const ast = parser.parseTerm();
    if (parser.pos < tokens.length) throw new Error(`多餘的 Token 從 '${parser.peek()}' 開始`);
    return ast;
}

// ==========================================
// 3. 自由變數與變數替換 (Beta Reduction & Substitution)
// ==========================================
function freeVars(node) {
    if (node instanceof Var) return new Set([node.name]);
    if (node instanceof Abs) {
        const fv = freeVars(node.body);
        fv.delete(node.param);
        return fv;
    }
    if (node instanceof App) {
        return new Set([...freeVars(node.left), ...freeVars(node.right)]);
    }
}

let freshCounter = 0;
function freshVar(base, avoidSet) {
    let name = base;
    while (avoidSet.has(name)) {
        name = base + (++freshCounter);
    }
    return name;
}

function clone(node) {
    if (node instanceof Var) return new Var(node.name);
    if (node instanceof Abs) return new Abs(node.param, clone(node.body));
    if (node instanceof App) return new App(clone(node.left), clone(node.right));
}

function substitute(node, varName, repl) {
    if (node instanceof Var) {
        return node.name === varName ? clone(repl) : new Var(node.name);
    }
    if (node instanceof Abs) {
        if (node.param === varName) return new Abs(node.param, clone(node.body));
        const fvRepl = freeVars(repl);
        if (fvRepl.has(node.param)) {
            const newParam = freshVar(node.param, new Set([...freeVars(node.body), ...fvRepl, varName]));
            const newBody = substitute(node.body, node.param, new Var(newParam));
            return new Abs(newParam, substitute(newBody, varName, repl));
        } else {
            return new Abs(node.param, substitute(node.body, varName, repl));
        }
    }
    if (node instanceof App) {
        return new App(substitute(node.left, varName, repl), substitute(node.right, varName, repl));
    }
}

// ==========================================
// 4. 正規序化簡器 (Normal Order Evaluation)
// ==========================================
function reduceNormalOrder(node) {
    if (node instanceof App) {
        if (node.left instanceof Abs) {
            const reduced = substitute(node.left.body, node.left.param, node.right);
            return { reduced: true, expr: reduced };
        }
        const resLeft = reduceNormalOrder(node.left);
        if (resLeft.reduced) {
            return { reduced: true, expr: new App(resLeft.expr, clone(node.right)) };
        }
        const resRight = reduceNormalOrder(node.right);
        if (resRight.reduced) {
            return { reduced: true, expr: new App(clone(node.left), resRight.expr) };
        }
        return { reduced: false, expr: node };
    }
    if (node instanceof Abs) {
        const resBody = reduceNormalOrder(node.body);
        if (resBody.reduced) {
            return { reduced: true, expr: new Abs(node.param, resBody.expr) };
        }
        return { reduced: false, expr: node };
    }
    return { reduced: false, expr: node };
}

// ==========================================
// 5. 巨集展開與執行引擎（已修正：支援遞迴展開巢狀巨集）
// ==========================================
function expandMacros(node, macros, expandingStack = new Set()) {
    if (node instanceof Var) {
        if (macros.has(node.name)) {
            if (expandingStack.has(node.name)) {
                throw new Error(`偵測到巨集循環定義: ${node.name}`);
            }
            expandingStack.add(node.name);
            // 遞迴展開巨集內容內部的其他巨集
            const expanded = expandMacros(macros.get(node.name), macros, expandingStack);
            expandingStack.delete(node.name);
            return clone(expanded);
        }
        return new Var(node.name);
    }
    if (node instanceof Abs) {
        return new Abs(node.param, expandMacros(node.body, macros, expandingStack));
    }
    if (node instanceof App) {
        return new App(
            expandMacros(node.left, macros, expandingStack), 
            expandMacros(node.right, macros, expandingStack)
        );
    }
    return node;
}

function evaluate(ast, macros, maxSteps = 3000) { // 提高預設最大步數以支援遞迴
    let current = expandMacros(ast, macros);
    console.log(`  [原始] ${current.toString()}`);
    let steps = 0;

    while (steps < maxSteps) {
        const { reduced, expr } = reduceNormalOrder(current);
        if (!reduced) {
            console.log(`  [結果] 達到標準形: ${current.toString()}`);
            break;
        }
        steps++;
        current = expr;
        console.log(`  步驟 ${steps}: ${current.toString()}`);
    }
    if (steps >= maxSteps) {
        console.log(`  [警告] 超過最大化簡步數限制 (${maxSteps})`);
    }
}

// ==========================================
// 6. 主程式：從命令列讀取檔案並執行
// ==========================================
function runFromFile(filename) {
    if (!fs.existsSync(filename)) {
        console.error(`❌ 錯誤：找不到指定的檔案 "${filename}"`);
        process.exit(1);
    }

    const content = fs.readFileSync(filename, 'utf-8');
    const lines = content.split('\n');
    const macros = new Map();

    console.log("==========================================");
    console.log(` Lambda Calculus 解譯器 (執行檔案: ${filename})`);
    console.log("==========================================\n");

    let exprCount = 0;
    for (let line of lines) {
        line = line.replace(/#.*$/, '').trim();
        if (!line) continue;

        if (line.includes('=')) {
            const parts = line.split('=').map(p => p.trim());
            const name = parts[0];
            const exprStr = parts[1];
            try {
                const ast = parse(exprStr);
                macros.set(name, ast);
                console.log(`定義巨集: ${name} = ${ast.toString()}`);
            } catch (e) {
                console.error(`解析巨集失敗 [${line}]: ${e.message}`);
            }
            console.log("------------------------------------------");
        } else {
            exprCount++;
            console.log(`\n[運算式 ${exprCount}] 輸入: ${line}`);
            try {
                const ast = parse(line);
                evaluate(ast, macros);
            } catch (e) {
                console.error(`執行錯誤: ${e.message}`);
            }
            console.log("------------------------------------------");
        }
    }
}

// 取得命令列參數
const args = process.argv.slice(2);
if (args.length === 0) {
    console.log("使用方式:");
    console.log("  node interpreter.js <檔案路徑>");
    console.log("範例:");
    console.log("  node interpreter.js examples.txt");
    process.exit(1);
}

runFromFile(args[0]);