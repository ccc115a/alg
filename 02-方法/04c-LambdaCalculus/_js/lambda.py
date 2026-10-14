import sys
import os

# ==========================================
# 1. 抽象語法樹 (AST) 定義
# ==========================================
class Var:
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return self.name

class Abs:
    def __init__(self, param, body):
        self.param = param
        self.body = body
    def __str__(self):
        return f"(\\{self.param}.{str(self.body)})"

class App:
    def __init__(self, left, right):
        self.left = left
        self.right = right
    def __str__(self):
        return f"({str(self.left)} {str(self.right)})"

# ==========================================
# 2. 詞法分析 (Tokenizer) 與 語法解析 (Parser)
# ==========================================
def tokenize(input_str):
    s = input_str.strip()
    i = 0
    result = []
    while i < len(s):
        if s[i].isspace():
            i += 1
            continue
        if s[i] in ('\\', 'λ', '.', '(', ')'):
            result.append(s[i])
            i += 1
        elif s[i].isalpha() or s[i] == '_':
            ident = ''
            while i < len(s) and (s[i].isalnum() or s[i] == '_'):
                ident += s[i]
                i += 1
            result.append(ident)
        else:
            raise ValueError(f"未預期的字元: {s[i]} 在位置 {i}")
    return result

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume(self, expected=None):
        t = self.peek()
        if expected and t != expected:
            raise ValueError(f"預期 '{expected}', 但得到 '{t}'")
        self.pos += 1
        return t

    def parse_term(self):
        return self.parse_app()

    def parse_app(self):
        left = self.parse_atom()
        while self.pos < len(self.tokens):
            t = self.peek()
            if t in (')', '.', None):
                break
            if t == '(' or t == '\\' or t == 'λ' or (t and (t[0].isalpha() or t[0] == '_')):
                right = self.parse_atom()
                left = App(left, right)
            else:
                break
        return left

    def parse_atom(self):
        t = self.peek()
        if t is None:
            raise ValueError("未預期的輸入結尾")
        if t == '(':
            self.consume('(')
            term = self.parse_term()
            self.consume(')')
            return term
        if t == '\\' or t == 'λ':
            self.consume()
            param = self.consume()
            if not param or not (param[0].isalpha() or param[0] == '_'):
                raise ValueError(f"預期參數名稱，得到 '{param}'")
            self.consume('.')
            body = self.parse_term()
            return Abs(param, body)
        if t and (t[0].isalpha() or t[0] == '_'):
            self.consume()
            return Var(t)
        raise ValueError(f"未預期的 Token: {t}")

def parse(input_str):
    tokens = tokenize(input_str)
    parser = Parser(tokens)
    ast = parser.parse_term()
    if parser.pos < len(tokens):
        raise ValueError(f"多餘的 Token 從 '{parser.peek()}' 開始")
    return ast

# ==========================================
# 3. 自由變數與變數替換 (Beta Reduction & Substitution)
# ==========================================
def free_vars(node):
    if isinstance(node, Var):
        return {node.name}
    if isinstance(node, Abs):
        fv = free_vars(node.body)
        fv.discard(node.param)
        return fv
    if isinstance(node, App):
        return free_vars(node.left).union(free_vars(node.right))
    return set()

fresh_counter = 0
def fresh_var(base, avoid_set):
    global fresh_counter
    name = base
    while name in avoid_set:
        fresh_counter += 1
        name = f"{base}_{fresh_counter}"
    return name

def clone(node):
    if isinstance(node, Var):
        return Var(node.name)
    if isinstance(node, Abs):
        return Abs(node.param, clone(node.body))
    if isinstance(node, App):
        return App(clone(node.left), clone(node.right))
    return node

def substitute(node, var_name, repl):
    if isinstance(node, Var):
        return clone(repl) if node.name == var_name else Var(node.name)
    if isinstance(node, Abs):
        if node.param == var_name:
            return Abs(node.param, clone(node.body))
        fv_repl = free_vars(repl)
        if node.param in fv_repl:
            avoid = free_vars(node.body).union(fv_repl).union({var_name})
            new_param = fresh_var(node.param, avoid)
            new_body = substitute(node.body, node.param, Var(new_param))
            return Abs(new_param, substitute(new_body, var_name, repl))
        else:
            return Abs(node.param, substitute(node.body, var_name, repl))
    if isinstance(node, App):
        return App(substitute(node.left, var_name, repl), substitute(node.right, var_name, repl))
    return node

# ==========================================
# 4. 正規序化簡器 (Normal Order Evaluation)
# ==========================================
def reduce_normal_order(node):
    if isinstance(node, App):
        if isinstance(node.left, Abs):
            reduced = substitute(node.left.body, node.left.param, node.right)
            return True, reduced
        res_left, expr_left = reduce_normal_order(node.left)
        if res_left:
            return True, App(expr_left, clone(node.right))
        res_right, expr_right = reduce_normal_order(node.right)
        if res_right:
            return True, App(clone(node.left), expr_right)
        return False, node
    if isinstance(node, Abs):
        res_body, expr_body = reduce_normal_order(node.body)
        if res_body:
            return True, Abs(node.param, expr_body)
        return False, node
    return False, node

# ==========================================
# 5. 巨集展開與執行引擎
# ==========================================
def expand_macros(node, macros, expanding_stack=None):
    if expanding_stack is None:
        expanding_stack = set()
        
    if isinstance(node, Var):
        if node.name in macros:
            if node.name in expanding_stack:
                raise ValueError(f"偵測到巨集循環定義: {node.name}")
            expanding_stack.add(node.name)
            expanded = expand_macros(macros[node.name], macros, expanding_stack)
            expanding_stack.remove(node.name)
            return clone(expanded)
        return Var(node.name)
    if isinstance(node, Abs):
        return Abs(node.param, expand_macros(node.body, macros, expanding_stack))
    if isinstance(node, App):
        return App(
            expand_macros(node.left, macros, expanding_stack),
            expand_macros(node.right, macros, expanding_stack)
        )
    return node

def evaluate(ast, macros, max_steps=3000):
    current = expand_macros(ast, macros)
    print(f"  [原始] {str(current)}")
    steps = 0

    while steps < max_steps:
        reduced, expr = reduce_normal_order(current)
        if not reduced:
            print(f"  [結果] 達到標準形: {str(current)}")
            break
        steps += 1
        current = expr
        print(f"  步驟 {steps}: {str(current)}")
    if steps >= max_steps:
        print(f"  [警告] 超過最大化簡步數限制 ({max_steps})")

# ==========================================
# 6. 主程式：從命令列讀取檔案並執行
# ==========================================
def run_from_file(filename):
    if not os.path.exists(filename):
        print(f"❌ 錯誤：找不到指定的檔案 '{filename}'")
        sys.exit(1)

    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    macros = {}

    print("==========================================")
    print(f" Lambda Calculus 解譯器 (Python 版)")
    print(f" 執行檔案: {filename}")
    print("==========================================\n")

    expr_count = 0
    for line in lines:
        # 移除註解與前後空白
        line = line.split('#')[0].strip()
        if not line:
            continue

        if '=' in line:
            parts = [p.strip() for p in line.split('=', 1)]
            name = parts[0]
            expr_str = parts[1]
            try:
                ast = parse(expr_str)
                macros[name] = ast
                print(f"定義巨集: {name} = {str(ast)}")
            except Exception as e:
                print(f"解析巨集失敗 [{line}]: {e}")
            print("------------------------------------------")
        else:
            expr_count += 1
            print(f"\n[運算式 {expr_count}] 輸入: {line}")
            try:
                ast = parse(line)
                evaluate(ast, macros)
            except Exception as e:
                print(f"執行錯誤: {e}")
            print("------------------------------------------")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("使用方式:")
        print("  python interpreter.py <檔案路徑>")
        print("範例:")
        print("  python interpreter.py examples.txt")
        sys.exit(1)
        
    run_from_file(sys.argv[1])