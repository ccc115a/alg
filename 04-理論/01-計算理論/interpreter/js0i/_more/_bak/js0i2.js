const fs = require('fs');
const acorn = require('acorn');

function makeEnv(parent) {
    return { record: {}, parent: parent };
}

function getVar(env, name) {
    let curr = env;
    while (curr) {
        if (name in curr.record) {
            return curr.record[name];
        }
        curr = curr.parent;
    }
    return undefined;
}

function setVar(env, name, val) {
    let curr = env;
    while (curr) {
        if (name in curr.record) {
            curr.record[name] = val;
            return val;
        }
        curr = curr.parent;
    }
    env.record[name] = val; 
    return val;
}

function defVar(env, name, val) {
    env.record[name] = val;
}

function evaluate(node, env) {
    if (!node) { return undefined; }
    let type = node.type;
    
    if (type === 'Program' || type === 'BlockStatement') {
        let res = undefined;
        let i = 0;
        while (i < node.body.length) {
            res = evaluate(node.body[i], env);
            if (res && res.__isReturn) { return res; }
            i = i + 1;
        }
        return res;
    }
    
    if (type === 'ExpressionStatement') {
        return evaluate(node.expression, env);
    }
    
    if (type === 'VariableDeclaration') {
        let i = 0;
        while (i < node.declarations.length) {
            let decl = node.declarations[i];
            let init = decl.init ? evaluate(decl.init, env) : undefined;
            defVar(env, decl.id.name, init);
            i = i + 1;
        }
        return undefined;
    }
    
    if (type === 'Identifier') {
        return getVar(env, node.name);
    }
    
    if (type === 'Literal') {
        return node.value;
    }
    
    if (type === 'MemberExpression') {
        let obj = evaluate(node.object, env);
        let prop = node.computed ? evaluate(node.property, env) : node.property.name;
        let val = obj[prop];
        if (typeof val === 'function') {
            return val.bind(obj);
        }
        return val;
    }
    
    if (type === 'CallExpression') {
        let callee = evaluate(node.callee, env);
        let args = [];
        let i = 0;
        while (i < node.arguments.length) {
            args.push(evaluate(node.arguments[i], env));
            i = i + 1;
        }
        return callee.apply(null, args);
    }
    
    // --- 【修正區塊：補齊基礎運算子】 ---
    if (type === 'BinaryExpression') {
        let l = evaluate(node.left, env);
        let r = evaluate(node.right, env);
        let op = node.operator;
        if (op === '+') return l + r;
        if (op === '-') return l - r;
        if (op === '*') return l * r;   // 補上乘法
        if (op === '/') return l / r;   // 補上除法
        if (op === '%') return l % r;   // 補上取餘數
        if (op === '===') return l === r;
        if (op === '==') return l == r; // 補上寬鬆相等
        if (op === '!==') return l !== r;
        if (op === '!=') return l != r; // 補上寬鬆不相等
        if (op === '<') return l < r;
        if (op === '<=') return l <= r; // 補上小於等於
        if (op === '>') return l > r;
        if (op === '>=') return l >= r; // 補上大於等於
        if (op === 'in') return l in r;
    }

    if (type === 'LogicalExpression') {
        let l = evaluate(node.left, env);
        if (node.operator === '&&') return l && evaluate(node.right, env);
        if (node.operator === '||') return l || evaluate(node.right, env);
    }

    if (type === 'UnaryExpression') {
        let arg = evaluate(node.argument, env);
        if (node.operator === '!') return !arg;
        if (node.operator === 'typeof') return typeof arg;
    }
    
    if (type === 'IfStatement') {
        if (evaluate(node.test, env)) {
            return evaluate(node.consequent, env);
        } else if (node.alternate) {
            return evaluate(node.alternate, env);
        }
        return undefined;
    }

    if (type === 'ConditionalExpression') {
        if (evaluate(node.test, env)) {
            return evaluate(node.consequent, env);
        } else {
            return evaluate(node.alternate, env);
        }
    }
    
    if (type === 'WhileStatement') {
        while (evaluate(node.test, env)) {
            let res = evaluate(node.body, env);
            if (res && res.__isReturn) { return res; }
        }
        return undefined;
    }
    
    if (type === 'FunctionDeclaration' || type === 'FunctionExpression') {
        let fn = function() {
            let fnEnv = makeEnv(env);
            defVar(fnEnv, 'arguments', arguments);
            let i = 0;
            while (i < node.params.length) {
                defVar(fnEnv, node.params[i].name, arguments[i]);
                i = i + 1;
            }
            let res = evaluate(node.body, fnEnv);
            if (res && res.__isReturn) { return res.val; }
            return res;
        };
        if (type === 'FunctionDeclaration') {
            defVar(env, node.id.name, fn);
            return undefined;
        }
        return fn;
    }
    
    if (type === 'ReturnStatement') {
        let val = node.argument ? evaluate(node.argument, env) : undefined;
        return { __isReturn: true, val: val };
    }
    
    if (type === 'ArrayExpression') {
        let arr = [];
        let i = 0;
        while (i < node.elements.length) {
            arr.push(evaluate(node.elements[i], env));
            i = i + 1;
        }
        return arr;
    }

    if (type === 'ObjectExpression') {
        let obj = {};
        let i = 0;
        while (i < node.properties.length) {
            let prop = node.properties[i];
            let key = prop.key.name || prop.key.value;
            obj[key] = evaluate(prop.value, env);
            i = i + 1;
        }
        return obj;
    }
    
    if (type === 'AssignmentExpression') {
        let right = evaluate(node.right, env);
        if (node.left.type === 'Identifier') {
            setVar(env, node.left.name, right);
        } else if (node.left.type === 'MemberExpression') {
            let obj = evaluate(node.left.object, env);
            let prop = node.left.computed ? evaluate(node.left.property, env) : node.left.property.name;
            obj[prop] = right;
        }
        return right;
    }
    
    return undefined;
}

// --- 啟動區 ---
let myArgv = process.argv;
if (myArgv.length > 2) {
    let guestArgv = [myArgv[0]];
    let i = 2;
    while (i < myArgv.length) {
        guestArgv.push(myArgv[i]);
        i = i + 1;
    }
    
    let targetPath = guestArgv[1];
    let code = fs.readFileSync(targetPath, 'utf8');
    let ast = acorn.parse(code, { ecmaVersion: 2020 });
    
    let globalEnv = makeEnv(null);
    defVar(globalEnv, 'console', console);
    defVar(globalEnv, 'require', require);
    defVar(globalEnv, 'undefined', undefined);
    defVar(globalEnv, 'Object', Object);
    
    let guestProcess = Object.assign({}, process);
    guestProcess.argv = guestArgv;
    defVar(globalEnv, 'process', guestProcess);
    
    evaluate(ast, globalEnv);
}