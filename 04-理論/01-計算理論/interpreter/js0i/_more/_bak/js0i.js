// js0i.js — A JavaScript interpreter written in JavaScript
// Usage: deno run -A js0i.js <script.js> [args...]

// ─────────────────────────────────────────────
// LEXER
// ─────────────────────────────────────────────
const TT = {
  NUM: "NUM", STR: "STR", BOOL: "BOOL", NULL: "NULL", UNDEF: "UNDEF",
  IDENT: "IDENT", KEYWORD: "KEYWORD",
  PLUS: "+", MINUS: "-", STAR: "*", SLASH: "/", PERCENT: "%",
  STARSTAR: "**",
  EQ: "==", NEQ: "!=", SEQ: "===", SNEQ: "!==",
  LT: "<", LTE: "<=", GT: ">", GTE: ">=",
  AND: "&&", OR: "||", NOT: "!",
  AMP: "&", PIPE: "|", CARET: "^", TILDE: "~", SHL: "<<", SHR: ">>", USHR: ">>>",
  ASSIGN: "=",
  PLUS_ASSIGN: "+=", MINUS_ASSIGN: "-=", STAR_ASSIGN: "*=", SLASH_ASSIGN: "/=",
  PERCENT_ASSIGN: "%=", STARSTAR_ASSIGN: "**=",
  AND_ASSIGN: "&&=", OR_ASSIGN: "||=", NULLC_ASSIGN: "??=",
  AMP_ASSIGN: "&=", PIPE_ASSIGN: "|=", CARET_ASSIGN: "^=",
  SHL_ASSIGN: "<<=", SHR_ASSIGN: ">>=", USHR_ASSIGN: ">>>=",
  INC: "++", DEC: "--",
  QMARK: "?", COLON: ":", NULLC: "??",
  DOT: ".", OPTCHAIN: "?.", SPREAD: "...",
  LPAREN: "(", RPAREN: ")",
  LBRACE: "{", RBRACE: "}",
  LBRACKET: "[", RBRACKET: "]",
  SEMI: ";", COMMA: ",",
  ARROW: "=>",
  BACKTICK: "BACKTICK",
  EOF: "EOF",
};

const KEYWORDS = new Set([
  "var","let","const","function","return","if","else","while","for","do",
  "break","continue","new","delete","typeof","instanceof","void","in","of",
  "throw","try","catch","finally","class","extends","super","import","export",
  "switch","case","default","yield","async","await","debugger","static","get","set",
  "true","false","null","undefined","this","arguments",
]);

class Token {
  constructor(type, value, line) { this.type = type; this.value = value; this.line = line; }
}

class Lexer {
  constructor(src) {
    this.src = src; this.pos = 0; this.line = 1; this.tokens = [];
  }
  error(msg) { throw new SyntaxError(`[Lexer] Line ${this.line}: ${msg}`); }
  peek(off=0) { return this.src[this.pos+off]; }
  advance() { const c = this.src[this.pos++]; if(c==="\n") this.line++; return c; }
  match(ch) { if(this.src[this.pos]===ch){ this.pos++; return true; } return false; }

  tokenize() {
    while(this.pos < this.src.length) {
      this.skipWhitespaceAndComments();
      if(this.pos >= this.src.length) break;
      const c = this.peek();
      const line = this.line;
      if(c==="`") { this.readTemplate(line); continue; }
      if(c==='"'||c==="'") { this.tokens.push(new Token(TT.STR, this.readString(c), line)); continue; }
      if(c>="0"&&c<="9"||(c==="."&&this.peek(1)>="0"&&this.peek(1)<="9")) {
        this.tokens.push(new Token(TT.NUM, this.readNumber(), line)); continue;
      }
      if(c==="_"||c==="$"||(c>="a"&&c<="z")||(c>="A"&&c<="Z")) {
        const id = this.readIdent();
        if(id==="true"||id==="false") this.tokens.push(new Token(TT.BOOL, id==="true", line));
        else if(id==="null") this.tokens.push(new Token(TT.NULL, null, line));
        else if(id==="undefined") this.tokens.push(new Token(TT.UNDEF, undefined, line));
        else if(KEYWORDS.has(id)) this.tokens.push(new Token(TT.KEYWORD, id, line));
        else this.tokens.push(new Token(TT.IDENT, id, line));
        continue;
      }
      this.readPunct(line);
    }
    this.tokens.push(new Token(TT.EOF, null, this.line));
    return this.tokens;
  }

  skipWhitespaceAndComments() {
    while(this.pos < this.src.length) {
      const c = this.peek();
      if(c===" "||c==="\t"||c==="\r"||c==="\n") { this.advance(); continue; }
      if(c==="/"&&this.peek(1)==="/") { while(this.pos<this.src.length&&this.peek()!=="\n") this.advance(); continue; }
      if(c==="/"&&this.peek(1)==="*") {
        this.advance(); this.advance();
        while(this.pos<this.src.length&&!(this.peek()==="*"&&this.peek(1)==="/")) this.advance();
        this.advance(); this.advance(); continue;
      }
      break;
    }
  }

  readString(quote) {
    this.advance(); let s="";
    while(this.pos<this.src.length&&this.peek()!==quote) {
      if(this.peek()==="\\") { this.advance(); s+=this.escapeChar(); }
      else s+=this.advance();
    }
    if(this.pos>=this.src.length) this.error("Unterminated string");
    this.advance(); return s;
  }

  escapeChar() {
    const c = this.advance();
    const map = {n:"\n",t:"\t",r:"\r",b:"\b",f:"\f",v:"\v","0":"\0","\\":"\\","'":"'",'"':'"','`':'`'};
    if(map[c]!==undefined) return map[c];
    if(c==="u") {
      if(this.peek()==="{") {
        this.advance(); let hex="";
        while(this.peek()!=="}") hex+=this.advance();
        this.advance(); return String.fromCodePoint(parseInt(hex,16));
      }
      let hex=""; for(let i=0;i<4;i++) hex+=this.advance();
      return String.fromCharCode(parseInt(hex,16));
    }
    if(c==="x") { let hex=""; for(let i=0;i<2;i++) hex+=this.advance(); return String.fromCharCode(parseInt(hex,16)); }
    return c;
  }

  readTemplate(line) {
    this.advance(); // consume `
    const parts = []; let str = "";
    while(this.pos < this.src.length) {
      const c = this.peek();
      if(c==="`") { this.advance(); break; }
      if(c==="$"&&this.peek(1)==="{") {
        this.advance(); this.advance();
        parts.push({type:"str", value:str}); str="";
        // tokenize inner expression until matching }
        let depth=1, innerSrc="";
        while(this.pos<this.src.length&&depth>0) {
          const ch=this.peek();
          if(ch==="{") depth++;
          else if(ch==="}") { depth--; if(depth===0){this.advance();break;} }
          innerSrc+=this.advance();
        }
        parts.push({type:"expr", src:innerSrc});
        continue;
      }
      if(c==="\\") { this.advance(); str+=this.escapeChar(); }
      else { if(c==="\n") this.line++; str+=this.advance(); }
    }
    parts.push({type:"str", value:str});
    this.tokens.push(new Token(TT.BACKTICK, parts, line));
  }

  readNumber() {
    let s="";
    if(this.peek()==="0"&&(this.peek(1)==="x"||this.peek(1)==="X")) {
      s+=this.advance(); s+=this.advance();
      while(/[0-9a-fA-F_]/.test(this.peek())) { const c=this.advance(); if(c!=="_") s+=c; }
      return parseInt(s,16);
    }
    if(this.peek()==="0"&&(this.peek(1)==="b"||this.peek(1)==="B")) {
      s+=this.advance(); s+=this.advance();
      while(/[01_]/.test(this.peek())) { const c=this.advance(); if(c!=="_") s+=c; }
      return parseInt(s,2);
    }
    if(this.peek()==="0"&&(this.peek(1)==="o"||this.peek(1)==="O")) {
      s+=this.advance(); s+=this.advance();
      while(/[0-7_]/.test(this.peek())) { const c=this.advance(); if(c!=="_") s+=c; }
      return parseInt(s,8);
    }
    while(this.pos<this.src.length&&(/[0-9_]/.test(this.peek())||this.peek()===".")) {
      const c=this.advance(); if(c!=="_") s+=c;
      if(c==="."&&(this.peek()<"0"||this.peek()>"9")) break;
    }
    if(this.peek()==="e"||this.peek()==="E") {
      s+=this.advance();
      if(this.peek()==="+"||this.peek()==="-") s+=this.advance();
      while(this.pos<this.src.length&&this.peek()>="0"&&this.peek()<="9") s+=this.advance();
    }
    if(this.peek()==="n") { this.advance(); return BigInt(s); }
    return Number(s);
  }

  readIdent() {
    let s="";
    while(this.pos<this.src.length&&/[\w$]/.test(this.peek())) s+=this.advance();
    return s;
  }

  readPunct(line) {
    const c = this.advance();
    const add = (type, val) => this.tokens.push(new Token(type, val??c, line));
    switch(c) {
      case "(": add(TT.LPAREN); break; case ")": add(TT.RPAREN); break;
      case "{": add(TT.LBRACE); break; case "}": add(TT.RBRACE); break;
      case "[": add(TT.LBRACKET); break; case "]": add(TT.RBRACKET); break;
      case ";": add(TT.SEMI); break; case ",": add(TT.COMMA); break;
      case "~": add(TT.TILDE); break;
      case ".":
        if(this.peek()==="."&&this.peek(1)===".") { this.advance(); this.advance(); add(TT.SPREAD,"..."); }
        else add(TT.DOT); break;
      case "+":
        if(this.match("+")) add(TT.INC,"++");
        else if(this.match("=")) add(TT.PLUS_ASSIGN,"+=");
        else add(TT.PLUS,"+"); break;
      case "-":
        if(this.match("-")) add(TT.DEC,"--");
        else if(this.match("=")) add(TT.MINUS_ASSIGN,"-=");
        else add(TT.MINUS,"-"); break;
      case "*":
        if(this.match("*")) { if(this.match("=")) add(TT.STARSTAR_ASSIGN,"**="); else add(TT.STARSTAR,"**"); }
        else if(this.match("=")) add(TT.STAR_ASSIGN,"*=");
        else add(TT.STAR,"*"); break;
      case "/":
        if(this.match("=")) add(TT.SLASH_ASSIGN,"/=");
        else add(TT.SLASH,"/"); break;
      case "%":
        if(this.match("=")) add(TT.PERCENT_ASSIGN,"%="); else add(TT.PERCENT,"%"); break;
      case "=":
        if(this.match("=")) { if(this.match("=")) add(TT.SEQ,"==="); else add(TT.EQ,"=="); }
        else if(this.match(">")) add(TT.ARROW,"=>");
        else add(TT.ASSIGN,"="); break;
      case "!":
        if(this.match("=")) { if(this.match("=")) add(TT.SNEQ,"!=="); else add(TT.NEQ,"!="); }
        else add(TT.NOT,"!"); break;
      case "<":
        if(this.match("<")) { if(this.match("=")) add(TT.SHL_ASSIGN,"<<="); else add(TT.SHL,"<<"); }
        else if(this.match("=")) add(TT.LTE,"<=");
        else add(TT.LT,"<"); break;
      case ">":
        if(this.match(">")) {
          if(this.match(">")) { if(this.match("=")) add(TT.USHR_ASSIGN,">>>="); else add(TT.USHR,">>>"); }
          else if(this.match("=")) add(TT.SHR_ASSIGN,">>="); else add(TT.SHR,">>"); }
        else if(this.match("=")) add(TT.GTE,">=");
        else add(TT.GT,">"); break;
      case "&":
        if(this.match("&")) { if(this.match("=")) add(TT.AND_ASSIGN,"&&="); else add(TT.AND,"&&"); }
        else if(this.match("=")) add(TT.AMP_ASSIGN,"&=");
        else add(TT.AMP,"&"); break;
      case "|":
        if(this.match("|")) { if(this.match("=")) add(TT.OR_ASSIGN,"||="); else add(TT.OR,"||"); }
        else if(this.match("=")) add(TT.PIPE_ASSIGN,"|=");
        else add(TT.PIPE,"|"); break;
      case "^":
        if(this.match("=")) add(TT.CARET_ASSIGN,"^="); else add(TT.CARET,"^"); break;
      case "?":
        if(this.match("?")) { if(this.match("=")) add(TT.NULLC_ASSIGN,"??="); else add(TT.NULLC,"??"); }
        else if(this.match(".")) add(TT.OPTCHAIN,"?.");
        else add(TT.QMARK,"?"); break;
      case ":": add(TT.COLON); break;
      default: // skip unknown chars
    }
  }
}

// ─────────────────────────────────────────────
// PARSER → AST
// ─────────────────────────────────────────────
class Parser {
  constructor(tokens) { this.tokens = tokens; this.pos = 0; }
  peek(off=0) { return this.tokens[Math.min(this.pos+off, this.tokens.length-1)]; }
  advance() { const t=this.tokens[this.pos]; if(this.pos<this.tokens.length-1) this.pos++; return t; }
  check(type, val) { const t=this.peek(); return t.type===type && (val===undefined||t.value===val); }
  match(type, val) { if(this.check(type,val)){ this.advance(); return true; } return false; }
  expect(type, val) {
    if(!this.check(type,val)) {
      const t=this.peek();
      throw new SyntaxError(`[Parser] Line ${t.line}: Expected ${type}${val!==undefined?" '"+val+"'":""}, got ${t.type} '${t.value}'`);
    }
    return this.advance();
  }
  eof() { return this.peek().type===TT.EOF; }

  parse() { return this.parseProgram(); }

  parseProgram() {
    const body=[];
    while(!this.eof()) body.push(this.parseStatement());
    return {type:"Program", body};
  }

  parseStatement() {
    const t = this.peek();
    if(t.type===TT.KEYWORD) {
      switch(t.value) {
        case "var": case "let": case "const": return this.parseVarDecl();
        case "function": return this.parseFunctionDecl();
        case "class": return this.parseClassDecl();
        case "return": return this.parseReturn();
        case "if": return this.parseIf();
        case "while": return this.parseWhile();
        case "do": return this.parseDoWhile();
        case "for": return this.parseFor();
        case "break": this.advance(); this.match(TT.SEMI); return {type:"BreakStatement"};
        case "continue": this.advance(); this.match(TT.SEMI); return {type:"ContinueStatement"};
        case "throw": return this.parseThrow();
        case "try": return this.parseTry();
        case "switch": return this.parseSwitch();
        case "import": return this.parseImport();
        case "export": return this.parseExport();
        case "async": {
          // async function
          if(this.peek(1).type===TT.KEYWORD&&this.peek(1).value==="function") {
            this.advance(); return this.parseFunctionDecl(true);
          }
          break;
        }
        case "debugger": this.advance(); this.match(TT.SEMI); return {type:"DebuggerStatement"};
      }
    }
    if(t.type===TT.LBRACE) return this.parseBlock();
    if(t.type===TT.SEMI) { this.advance(); return {type:"EmptyStatement"}; }
    return this.parseExpressionStatement();
  }

  parseBlock() {
    this.expect(TT.LBRACE);
    const body=[];
    while(!this.check(TT.RBRACE)&&!this.eof()) body.push(this.parseStatement());
    this.expect(TT.RBRACE);
    return {type:"BlockStatement", body};
  }

  parseVarDecl() {
    const kind = this.advance().value; // var/let/const
    const decls=[];
    do {
      const id = this.parsePattern();
      let init=null;
      if(this.match(TT.ASSIGN)) init=this.parseAssignment();
      decls.push({id, init});
    } while(this.match(TT.COMMA));
    this.match(TT.SEMI);
    return {type:"VariableDeclaration", kind, declarations:decls};
  }

  parsePattern() {
    if(this.check(TT.LBRACE)) return this.parseObjectPattern();
    if(this.check(TT.LBRACKET)) return this.parseArrayPattern();
    return {type:"Identifier", name: this.expect(TT.IDENT).value};
  }

  parseObjectPattern() {
    this.expect(TT.LBRACE);
    const props=[];
    while(!this.check(TT.RBRACE)&&!this.eof()) {
      if(this.check(TT.SPREAD)) {
        this.advance();
        props.push({type:"RestElement", argument: this.parsePattern()});
        break;
      }
      let key, value, shorthand=false, defaultValue=null;
      if(this.check(TT.LBRACKET)) {
        this.advance();
        key = this.parseAssignment();
        this.expect(TT.RBRACKET);
        this.expect(TT.COLON);
        value = this.parsePattern();
      } else {
        key = {type:"Identifier", name: (this.check(TT.IDENT)||this.check(TT.KEYWORD)) ? this.advance().value : this.advance().value};
        if(this.match(TT.COLON)) { value = this.parsePattern(); }
        else { value = {type:"Identifier", name:key.name}; shorthand=true; }
      }
      if(this.match(TT.ASSIGN)) defaultValue=this.parseAssignment();
      props.push({type:"Property", key, value, shorthand, computed:false, defaultValue});
      this.match(TT.COMMA);
    }
    this.expect(TT.RBRACE);
    return {type:"ObjectPattern", properties:props};
  }

  parseArrayPattern() {
    this.expect(TT.LBRACKET);
    const elements=[];
    while(!this.check(TT.RBRACKET)&&!this.eof()) {
      if(this.check(TT.COMMA)) { this.advance(); elements.push(null); continue; }
      if(this.check(TT.SPREAD)) { this.advance(); elements.push({type:"RestElement",argument:this.parsePattern()}); break; }
      const el = this.parsePattern();
      let def=null; if(this.match(TT.ASSIGN)) def=this.parseAssignment();
      elements.push(def?{type:"AssignmentPattern",left:el,right:def}:el);
      this.match(TT.COMMA);
    }
    this.expect(TT.RBRACKET);
    return {type:"ArrayPattern", elements};
  }

  parseFunctionDecl(isAsync=false) {
    this.expect(TT.KEYWORD,"function");
    const generator = this.match(TT.STAR);
    let name=null;
    if(this.check(TT.IDENT)) name=this.advance().value;
    else if(this.check(TT.KEYWORD)) name=this.advance().value;
    const params=this.parseParams();
    const body=this.parseBlock();
    return {type:"FunctionDeclaration", name, params, body, async:isAsync, generator};
  }

  parseParams() {
    this.expect(TT.LPAREN);
    const params=[];
    while(!this.check(TT.RPAREN)&&!this.eof()) {
      if(this.check(TT.SPREAD)) { this.advance(); params.push({type:"RestElement",argument:this.parsePattern()}); break; }
      const p=this.parsePattern();
      if(this.match(TT.ASSIGN)) params.push({type:"AssignmentPattern",left:p,right:this.parseAssignment()});
      else params.push(p);
      this.match(TT.COMMA);
    }
    this.expect(TT.RPAREN);
    return params;
  }

  parseClassDecl() {
    this.expect(TT.KEYWORD,"class");
    let name=null;
    if(this.check(TT.IDENT)) name=this.advance().value;
    let superClass=null;
    if(this.match(TT.KEYWORD,"extends")) superClass=this.parseLeftHandSide();
    this.expect(TT.LBRACE);
    const methods=[];
    while(!this.check(TT.RBRACE)&&!this.eof()) {
      if(this.match(TT.SEMI)) continue;
      let isStatic=false, isAsync=false, isGenerator=false;
      let kind="method";
      if(this.check(TT.KEYWORD,"static")) { this.advance(); isStatic=true; }
      if(this.check(TT.KEYWORD,"async")) { this.advance(); isAsync=true; }
      if(this.match(TT.STAR)) isGenerator=true;
      if(this.check(TT.KEYWORD,"get")&&!this.check(TT.LPAREN,undefined,1)) { this.advance(); kind="get"; }
      else if(this.check(TT.KEYWORD,"set")&&!this.check(TT.LPAREN,undefined,1)) { this.advance(); kind="set"; }
      let computed=false, key;
      if(this.check(TT.LBRACKET)) {
        this.advance(); key=this.parseAssignment(); this.expect(TT.RBRACKET); computed=true;
      } else if(this.check(TT.IDENT)||this.check(TT.KEYWORD)||this.check(TT.NUM)||this.check(TT.STR)) {
        const t=this.advance(); key={type:"Identifier",name:String(t.value)};
      } else { key={type:"Identifier",name:this.advance().value}; }
      // field declaration (no parens)
      if(!this.check(TT.LPAREN)) {
        let fieldInit=null;
        if(this.match(TT.ASSIGN)) fieldInit=this.parseAssignment();
        this.match(TT.SEMI);
        methods.push({type:"ClassField", key, value:fieldInit, static:isStatic, computed});
        continue;
      }
      const params=this.parseParams();
      const body=this.parseBlock();
      methods.push({type:"MethodDefinition", key, value:{type:"FunctionExpression",params,body,async:isAsync,generator:isGenerator}, kind, static:isStatic, computed});
    }
    this.expect(TT.RBRACE);
    return {type:"ClassDeclaration", name, superClass, methods};
  }

  parseReturn() {
    this.advance();
    let arg=null;
    if(!this.check(TT.SEMI)&&!this.check(TT.RBRACE)&&!this.eof()&&!this.checkNewlineBefore()) {
      arg=this.parseAssignment();
    }
    this.match(TT.SEMI);
    return {type:"ReturnStatement", argument:arg};
  }
  checkNewlineBefore() { return false; } // simplified; newline ASI not fully tracked

  parseIf() {
    this.advance();
    this.expect(TT.LPAREN);
    const test=this.parseExpression();
    this.expect(TT.RPAREN);
    const consequent=this.parseStatement();
    let alternate=null;
    if(this.match(TT.KEYWORD,"else")) alternate=this.parseStatement();
    return {type:"IfStatement", test, consequent, alternate};
  }

  parseWhile() {
    this.advance();
    this.expect(TT.LPAREN);
    const test=this.parseExpression();
    this.expect(TT.RPAREN);
    const body=this.parseStatement();
    return {type:"WhileStatement", test, body};
  }

  parseDoWhile() {
    this.advance();
    const body=this.parseStatement();
    this.expect(TT.KEYWORD,"while");
    this.expect(TT.LPAREN);
    const test=this.parseExpression();
    this.expect(TT.RPAREN);
    this.match(TT.SEMI);
    return {type:"DoWhileStatement", test, body};
  }

  parseFor() {
    this.advance(); this.expect(TT.LPAREN);
    // for-of / for-in / for
    let init=null;
    if(!this.check(TT.SEMI)) {
      const savedPos=this.pos;
      if(this.check(TT.KEYWORD,"var")||this.check(TT.KEYWORD,"let")||this.check(TT.KEYWORD,"const")) {
        const kind=this.advance().value;
        const id=this.parsePattern();
        if(this.check(TT.KEYWORD,"of")||this.check(TT.KEYWORD,"in")) {
          const iterType=this.advance().value; // of/in
          const right=this.parseAssignment();
          this.expect(TT.RPAREN);
          const body=this.parseStatement();
          return {type:iterType==="of"?"ForOfStatement":"ForInStatement",
            left:{type:"VariableDeclaration",kind,declarations:[{id,init:null}]},
            right, body};
        }
        let declarations=[{id,init:null}];
        if(this.match(TT.ASSIGN)) declarations[0].init=this.parseAssignment();
        while(this.match(TT.COMMA)) {
          const id2=this.parsePattern(); let i2=null;
          if(this.match(TT.ASSIGN)) i2=this.parseAssignment();
          declarations.push({id:id2,init:i2});
        }
        init={type:"VariableDeclaration",kind,declarations};
      } else {
        init=this.parseExpression();
        if(this.check(TT.KEYWORD,"of")||this.check(TT.KEYWORD,"in")) {
          const iterType=this.advance().value;
          const right=this.parseAssignment();
          this.expect(TT.RPAREN);
          const body=this.parseStatement();
          return {type:iterType==="of"?"ForOfStatement":"ForInStatement", left:init, right, body};
        }
      }
    }
    this.expect(TT.SEMI);
    let test=null; if(!this.check(TT.SEMI)) test=this.parseExpression();
    this.expect(TT.SEMI);
    let update=null; if(!this.check(TT.RPAREN)) update=this.parseExpression();
    this.expect(TT.RPAREN);
    const body=this.parseStatement();
    return {type:"ForStatement", init, test, update, body};
  }

  parseThrow() {
    this.advance();
    const arg=this.parseAssignment();
    this.match(TT.SEMI);
    return {type:"ThrowStatement", argument:arg};
  }

  parseTry() {
    this.advance();
    const block=this.parseBlock();
    let handler=null, finalizer=null;
    if(this.match(TT.KEYWORD,"catch")) {
      let param=null;
      if(this.match(TT.LPAREN)) { param=this.parsePattern(); this.expect(TT.RPAREN); }
      const body=this.parseBlock();
      handler={param, body};
    }
    if(this.match(TT.KEYWORD,"finally")) finalizer=this.parseBlock();
    return {type:"TryStatement", block, handler, finalizer};
  }

  parseSwitch() {
    this.advance(); this.expect(TT.LPAREN);
    const disc=this.parseExpression(); this.expect(TT.RPAREN);
    this.expect(TT.LBRACE);
    const cases=[];
    while(!this.check(TT.RBRACE)&&!this.eof()) {
      let test=null;
      if(this.match(TT.KEYWORD,"case")) test=this.parseExpression();
      else this.expect(TT.KEYWORD,"default");
      this.expect(TT.COLON);
      const cons=[];
      while(!this.check(TT.KEYWORD,"case")&&!this.check(TT.KEYWORD,"default")&&!this.check(TT.RBRACE)&&!this.eof())
        cons.push(this.parseStatement());
      cases.push({test,consequent:cons});
    }
    this.expect(TT.RBRACE);
    return {type:"SwitchStatement", discriminant:disc, cases};
  }

  parseImport() {
    // Simplified: just skip import statements
    this.advance();
    while(!this.check(TT.SEMI)&&!this.eof()&&!this.check(TT.KEYWORD,"from")) this.advance();
    if(this.check(TT.KEYWORD,"from")) { this.advance(); this.advance(); }
    this.match(TT.SEMI);
    return {type:"EmptyStatement"};
  }

  parseExport() {
    this.advance(); // export
    if(this.check(TT.KEYWORD,"default")) { this.advance(); const decl=this.parseStatement(); return {type:"ExportDefaultDeclaration",declaration:decl}; }
    const decl=this.parseStatement();
    return {type:"ExportNamedDeclaration", declaration:decl};
  }

  parseExpressionStatement() {
    const expr=this.parseExpression();
    this.match(TT.SEMI);
    return {type:"ExpressionStatement", expression:expr};
  }

  parseExpression() {
    const exprs=[this.parseAssignment()];
    while(this.match(TT.COMMA)) exprs.push(this.parseAssignment());
    return exprs.length===1 ? exprs[0] : {type:"SequenceExpression", expressions:exprs};
  }

  parseAssignment() {
    // Check for arrow function
    const arrow = this.tryParseArrow();
    if(arrow) return arrow;

    const left = this.parseConditional();
    const t = this.peek();
    const assignOps = new Set([TT.ASSIGN,TT.PLUS_ASSIGN,TT.MINUS_ASSIGN,TT.STAR_ASSIGN,TT.SLASH_ASSIGN,
      TT.PERCENT_ASSIGN,TT.STARSTAR_ASSIGN,TT.AND_ASSIGN,TT.OR_ASSIGN,TT.NULLC_ASSIGN,
      TT.AMP_ASSIGN,TT.PIPE_ASSIGN,TT.CARET_ASSIGN,TT.SHL_ASSIGN,TT.SHR_ASSIGN,TT.USHR_ASSIGN]);
    if(assignOps.has(t.type)) {
      const op=this.advance().value;
      const right=this.parseAssignment();
      return {type:"AssignmentExpression", operator:op, left, right};
    }
    return left;
  }

  tryParseArrow() {
    const savedPos=this.pos;
    try {
      // async arrow?
      let isAsync=false;
      if(this.check(TT.KEYWORD,"async")) {
        // peek ahead: async (... => or async ident =>
        const next=this.peek(1);
        if(next.type===TT.IDENT||next.type===TT.LPAREN) { this.advance(); isAsync=true; }
        else return null;
      }
      let params=[];
      if(this.check(TT.LPAREN)) {
        params=this.parseParams();
      } else if(this.check(TT.IDENT)) {
        params=[{type:"Identifier",name:this.advance().value}];
      } else { this.pos=savedPos; return null; }
      if(!this.check(TT.ARROW)) { this.pos=savedPos; return null; }
      this.advance(); // =>
      const body=this.check(TT.LBRACE) ? this.parseBlock() : this.parseAssignment();
      return {type:"ArrowFunctionExpression", params, body, async:isAsync, expression:body.type!=="BlockStatement"};
    } catch(e) { this.pos=savedPos; return null; }
  }

  parseConditional() {
    let left=this.parseNullCoalesce();
    if(this.match(TT.QMARK)) {
      const consequent=this.parseAssignment();
      this.expect(TT.COLON);
      const alternate=this.parseAssignment();
      return {type:"ConditionalExpression", test:left, consequent, alternate};
    }
    return left;
  }

  parseNullCoalesce() {
    let left=this.parseOr();
    while(this.check(TT.NULLC)) { this.advance(); left={type:"LogicalExpression",operator:"??",left,right:this.parseOr()}; }
    return left;
  }

  parseOr() {
    let left=this.parseAnd();
    while(this.check(TT.OR)) { this.advance(); left={type:"LogicalExpression",operator:"||",left,right:this.parseAnd()}; }
    return left;
  }

  parseAnd() {
    let left=this.parseBitOr();
    while(this.check(TT.AND)) { this.advance(); left={type:"LogicalExpression",operator:"&&",left,right:this.parseBitOr()}; }
    return left;
  }

  parseBitOr() {
    let left=this.parseBitXor();
    while(this.check(TT.PIPE)) { this.advance(); left={type:"BinaryExpression",operator:"|",left,right:this.parseBitXor()}; }
    return left;
  }
  parseBitXor() {
    let left=this.parseBitAnd();
    while(this.check(TT.CARET)) { this.advance(); left={type:"BinaryExpression",operator:"^",left,right:this.parseBitAnd()}; }
    return left;
  }
  parseBitAnd() {
    let left=this.parseEquality();
    while(this.check(TT.AMP)) { this.advance(); left={type:"BinaryExpression",operator:"&",left,right:this.parseEquality()}; }
    return left;
  }

  parseEquality() {
    let left=this.parseRelational();
    while(this.check(TT.EQ)||this.check(TT.NEQ)||this.check(TT.SEQ)||this.check(TT.SNEQ)) {
      const op=this.advance().value; left={type:"BinaryExpression",operator:op,left,right:this.parseRelational()};
    }
    return left;
  }

  parseRelational() {
    let left=this.parseShift();
    while(this.check(TT.LT)||this.check(TT.LTE)||this.check(TT.GT)||this.check(TT.GTE)||
          (this.check(TT.KEYWORD,"instanceof"))||(this.check(TT.KEYWORD,"in"))) {
      const op=this.advance().value; left={type:"BinaryExpression",operator:op,left,right:this.parseShift()};
    }
    return left;
  }

  parseShift() {
    let left=this.parseAdditive();
    while(this.check(TT.SHL)||this.check(TT.SHR)||this.check(TT.USHR)) {
      const op=this.advance().value; left={type:"BinaryExpression",operator:op,left,right:this.parseAdditive()};
    }
    return left;
  }

  parseAdditive() {
    let left=this.parseMultiplicative();
    while(this.check(TT.PLUS)||this.check(TT.MINUS)) {
      const op=this.advance().value; left={type:"BinaryExpression",operator:op,left,right:this.parseMultiplicative()};
    }
    return left;
  }

  parseMultiplicative() {
    let left=this.parseExponent();
    while(this.check(TT.STAR)||this.check(TT.SLASH)||this.check(TT.PERCENT)) {
      const op=this.advance().value; left={type:"BinaryExpression",operator:op,left,right:this.parseExponent()};
    }
    return left;
  }

  parseExponent() {
    let base=this.parseUnary();
    if(this.check(TT.STARSTAR)) { this.advance(); return {type:"BinaryExpression",operator:"**",left:base,right:this.parseExponent()}; }
    return base;
  }

  parseUnary() {
    if(this.check(TT.NOT)) { this.advance(); return {type:"UnaryExpression",operator:"!",argument:this.parseUnary()}; }
    if(this.check(TT.TILDE)) { this.advance(); return {type:"UnaryExpression",operator:"~",argument:this.parseUnary()}; }
    if(this.check(TT.MINUS)) { this.advance(); return {type:"UnaryExpression",operator:"-",argument:this.parseUnary()}; }
    if(this.check(TT.PLUS)) { this.advance(); return {type:"UnaryExpression",operator:"+",argument:this.parseUnary()}; }
    if(this.check(TT.KEYWORD,"typeof")) { this.advance(); return {type:"UnaryExpression",operator:"typeof",argument:this.parseUnary()}; }
    if(this.check(TT.KEYWORD,"void")) { this.advance(); return {type:"UnaryExpression",operator:"void",argument:this.parseUnary()}; }
    if(this.check(TT.KEYWORD,"delete")) { this.advance(); return {type:"UnaryExpression",operator:"delete",argument:this.parseUnary()}; }
    if(this.check(TT.KEYWORD,"await")) { this.advance(); return {type:"AwaitExpression",argument:this.parseUnary()}; }
    if(this.check(TT.INC)) { this.advance(); return {type:"UpdateExpression",operator:"++",prefix:true,argument:this.parseUnary()}; }
    if(this.check(TT.DEC)) { this.advance(); return {type:"UpdateExpression",operator:"--",prefix:true,argument:this.parseUnary()}; }
    return this.parsePostfix();
  }

  parsePostfix() {
    let expr=this.parseCallMember();
    if(this.check(TT.INC)) { this.advance(); return {type:"UpdateExpression",operator:"++",prefix:false,argument:expr}; }
    if(this.check(TT.DEC)) { this.advance(); return {type:"UpdateExpression",operator:"--",prefix:false,argument:expr}; }
    return expr;
  }

  parseCallMember() { return this.parseCallMemberExpr(this.parsePrimary()); }

  parseCallMemberExpr(obj) {
    while(true) {
      if(this.check(TT.DOT)||this.check(TT.OPTCHAIN)) {
        const optional=this.check(TT.OPTCHAIN); this.advance();
        let prop;
        if(this.check(TT.IDENT)||this.check(TT.KEYWORD)||this.check(TT.NUM)) {
          prop={type:"Identifier",name:String(this.advance().value)};
        } else prop={type:"Identifier",name:this.advance().value};
        obj={type:"MemberExpression",object:obj,property:prop,computed:false,optional};
      } else if(this.check(TT.LBRACKET)) {
        this.advance();
        const prop=this.parseExpression();
        this.expect(TT.RBRACKET);
        obj={type:"MemberExpression",object:obj,property:prop,computed:true,optional:false};
      } else if(this.check(TT.LPAREN)) {
        const args=this.parseArgList();
        obj={type:"CallExpression",callee:obj,arguments:args};
      } else if(this.check(TT.BACKTICK)) {
        // tagged template
        const quasi=this.parsePrimary();
        obj={type:"TaggedTemplateExpression",tag:obj,quasi};
      } else break;
    }
    return obj;
  }

  parseLeftHandSide() { return this.parseCallMemberExpr(this.parsePrimary()); }

  parseArgList() {
    this.expect(TT.LPAREN);
    const args=[];
    while(!this.check(TT.RPAREN)&&!this.eof()) {
      if(this.check(TT.SPREAD)) { this.advance(); args.push({type:"SpreadElement",argument:this.parseAssignment()}); }
      else args.push(this.parseAssignment());
      this.match(TT.COMMA);
    }
    this.expect(TT.RPAREN);
    return args;
  }

  parsePrimary() {
    const t=this.peek();
    if(t.type===TT.NUM) { this.advance(); return {type:"Literal",value:t.value}; }
    if(t.type===TT.STR) { this.advance(); return {type:"Literal",value:t.value}; }
    if(t.type===TT.BOOL) { this.advance(); return {type:"Literal",value:t.value}; }
    if(t.type===TT.NULL) { this.advance(); return {type:"Literal",value:null}; }
    if(t.type===TT.UNDEF) { this.advance(); return {type:"Identifier",name:"undefined"}; }
    if(t.type===TT.BACKTICK) { this.advance(); return {type:"TemplateLiteral",parts:t.value}; }
    if(t.type===TT.IDENT) { this.advance(); return {type:"Identifier",name:t.value}; }
    if(t.type===TT.KEYWORD&&t.value==="this") { this.advance(); return {type:"ThisExpression"}; }
    if(t.type===TT.KEYWORD&&t.value==="super") { this.advance(); return {type:"Super"}; }
    if(t.type===TT.KEYWORD&&t.value==="new") { return this.parseNew(); }
    if(t.type===TT.KEYWORD&&t.value==="function") { return this.parseFunctionExpr(); }
    if(t.type===TT.KEYWORD&&t.value==="class") { return this.parseClassExpr(); }
    if(t.type===TT.KEYWORD&&t.value==="yield") { this.advance(); const arg=this.parseAssignment(); return {type:"YieldExpression",argument:arg}; }
    if(t.type===TT.LBRACKET) { return this.parseArrayLiteral(); }
    if(t.type===TT.LBRACE) { return this.parseObjectLiteral(); }
    if(t.type===TT.LPAREN) {
      this.advance();
      if(this.check(TT.RPAREN)) { this.advance(); /* empty parens - will be caught by arrow */ return {type:"Literal",value:undefined}; }
      const expr=this.parseExpression();
      this.expect(TT.RPAREN);
      return expr;
    }
    // Slash could be regex
    if(t.type===TT.SLASH) { return this.parseRegex(); }
    this.advance(); // skip unknown
    return {type:"Literal",value:undefined};
  }

  parseRegex() {
    // Basic regex literal parsing
    this.advance(); // /
    let src="/", flags="";
    while(this.pos<this.tokens.length) {
      const t=this.tokens[this.pos];
      if(t.type===TT.SLASH) { this.advance(); break; }
      src+=t.value!==undefined?String(t.value):t.type; this.advance();
    }
    // flags
    if(this.check(TT.IDENT)) flags=this.advance().value;
    return {type:"RegexLiteral",pattern:src.slice(1),flags};
  }

  parseNew() {
    this.advance(); // new
    if(this.check(TT.KEYWORD,"new")) return {type:"NewExpression",callee:this.parseNew(),arguments:[]};
    let callee=this.parseLeftHandSide();
    let args=[];
    if(this.check(TT.LPAREN)) args=this.parseArgList();
    return {type:"NewExpression",callee,arguments:args};
  }

  parseFunctionExpr(isAsync=false) {
    this.expect(TT.KEYWORD,"function");
    const generator=this.match(TT.STAR);
    let name=null;
    if(this.check(TT.IDENT)) name=this.advance().value;
    const params=this.parseParams();
    const body=this.parseBlock();
    return {type:"FunctionExpression",name,params,body,async:isAsync,generator};
  }

  parseClassExpr() {
    this.expect(TT.KEYWORD,"class");
    let name=null; if(this.check(TT.IDENT)) name=this.advance().value;
    let superClass=null;
    if(this.match(TT.KEYWORD,"extends")) superClass=this.parseLeftHandSide();
    this.expect(TT.LBRACE);
    const methods=[];
    while(!this.check(TT.RBRACE)&&!this.eof()) {
      if(this.match(TT.SEMI)) continue;
      let isStatic=false, isAsync=false, isGenerator=false, kind="method";
      if(this.check(TT.KEYWORD,"static")) { this.advance(); isStatic=true; }
      if(this.check(TT.KEYWORD,"async")) { this.advance(); isAsync=true; }
      if(this.match(TT.STAR)) isGenerator=true;
      if(this.check(TT.KEYWORD,"get")) { this.advance(); kind="get"; }
      else if(this.check(TT.KEYWORD,"set")) { this.advance(); kind="set"; }
      let computed=false, key;
      if(this.check(TT.LBRACKET)) { this.advance(); key=this.parseAssignment(); this.expect(TT.RBRACKET); computed=true; }
      else { const kt=this.advance(); key={type:"Identifier",name:String(kt.value)}; }
      if(!this.check(TT.LPAREN)) {
        let fieldInit=null; if(this.match(TT.ASSIGN)) fieldInit=this.parseAssignment();
        this.match(TT.SEMI);
        methods.push({type:"ClassField",key,value:fieldInit,static:isStatic,computed}); continue;
      }
      const params=this.parseParams();
      const body=this.parseBlock();
      methods.push({type:"MethodDefinition",key,value:{type:"FunctionExpression",params,body,async:isAsync,generator:isGenerator},kind,static:isStatic,computed});
    }
    this.expect(TT.RBRACE);
    return {type:"ClassExpression",name,superClass,methods};
  }

  parseArrayLiteral() {
    this.expect(TT.LBRACKET);
    const elements=[];
    while(!this.check(TT.RBRACKET)&&!this.eof()) {
      if(this.check(TT.COMMA)) { this.advance(); elements.push(null); continue; }
      if(this.check(TT.SPREAD)) { this.advance(); elements.push({type:"SpreadElement",argument:this.parseAssignment()}); this.match(TT.COMMA); continue; }
      elements.push(this.parseAssignment());
      this.match(TT.COMMA);
    }
    this.expect(TT.RBRACKET);
    return {type:"ArrayExpression",elements};
  }

  parseObjectLiteral() {
    this.expect(TT.LBRACE);
    const props=[];
    while(!this.check(TT.RBRACE)&&!this.eof()) {
      if(this.check(TT.SPREAD)) { this.advance(); props.push({type:"SpreadElement",argument:this.parseAssignment()}); this.match(TT.COMMA); continue; }
      let isAsync=false, isGenerator=false, kind="init";
      if(this.check(TT.KEYWORD,"async")&&this.peek(1).type!==TT.COLON&&this.peek(1).type!==TT.COMMA&&this.peek(1).type!==TT.RBRACE) {
        this.advance(); isAsync=true;
      }
      if(this.match(TT.STAR)) isGenerator=true;
      let kind2="init";
      if((this.check(TT.KEYWORD,"get")||this.check(TT.KEYWORD,"set"))&&this.peek(1).type!==TT.COLON&&this.peek(1).type!==TT.COMMA&&this.peek(1).type!==TT.LPAREN&&this.peek(1).type!==TT.RBRACE) {
        kind2=this.advance().value;
      }
      let computed=false, key;
      if(this.check(TT.LBRACKET)) { this.advance(); key=this.parseAssignment(); this.expect(TT.RBRACKET); computed=true; }
      else if(this.check(TT.IDENT)||this.check(TT.KEYWORD)||this.check(TT.NUM)||this.check(TT.STR)) {
        const kt=this.advance(); key={type:"Identifier",name:String(kt.value),raw:kt.value};
      } else { const kt=this.advance(); key={type:"Identifier",name:String(kt.value)}; }

      if(this.check(TT.LPAREN)) {
        const params=this.parseParams(); const body=this.parseBlock();
        props.push({type:"Property",kind:kind2==="init"?"init":kind2,key,value:{type:"FunctionExpression",params,body,async:isAsync,generator:isGenerator},computed,shorthand:false});
      } else if(this.match(TT.COLON)) {
        const val=this.parseAssignment();
        props.push({type:"Property",kind:"init",key,value:val,computed,shorthand:false});
      } else {
        // shorthand
        props.push({type:"Property",kind:"init",key,value:{type:"Identifier",name:key.name},computed,shorthand:true});
      }
      this.match(TT.COMMA);
    }
    this.expect(TT.RBRACE);
    return {type:"ObjectExpression",properties:props};
  }
}

// ─────────────────────────────────────────────
// SIGNAL classes for control flow
// ─────────────────────────────────────────────
class ReturnSignal { constructor(v){this.value=v;} }
class BreakSignal { constructor(label){this.label=label;} }
class ContinueSignal { constructor(label){this.label=label;} }
class ThrowSignal { constructor(v){this.value=v;} }

// ─────────────────────────────────────────────
// ENVIRONMENT
// ─────────────────────────────────────────────
class Env {
  constructor(parent=null, isBlock=false) {
    this.vars=new Map(); this.parent=parent; this.isBlock=isBlock;
  }
  define(name, val, kind="var") { this.vars.set(name,{val,kind}); }
  lookup(name) {
    if(this.vars.has(name)) return this;
    if(this.parent) return this.parent.lookup(name);
    return null;
  }
  get(name) {
    const env=this.lookup(name);
    if(env) return env.vars.get(name).val;
    return undefined;
  }
  set(name, val) {
    const env=this.lookup(name);
    if(env) { env.vars.get(name).val=val; return val; }
    // global assignment
    let top=this; while(top.parent) top=top.parent;
    top.vars.set(name,{val,kind:"var"});
    return val;
  }
  has(name) { return !!this.lookup(name); }
  funcEnv() { // walk up to function scope
    let e=this; while(e.isBlock&&e.parent) e=e.parent; return e;
  }
}

// ─────────────────────────────────────────────
// INTERPRETER
// ─────────────────────────────────────────────
class Interpreter {
  constructor() {
    this.globalEnv = new Env();
    this.setupGlobals();
  }

  setupGlobals() {
    const G = this.globalEnv;
    // console
    const con = {
      log:   (...a)=>{ console.log(...a.map(v=>this.hostStr(v))); },
      error: (...a)=>{ console.error(...a.map(v=>this.hostStr(v))); },
      warn:  (...a)=>{ console.warn(...a.map(v=>this.hostStr(v))); },
      info:  (...a)=>{ console.info(...a.map(v=>this.hostStr(v))); },
      dir:   (...a)=>{ console.log(...a.map(v=>this.hostStr(v))); },
    };
    G.define("console", con);
    G.define("undefined", undefined);
    G.define("Infinity", Infinity);
    G.define("NaN", NaN);
    G.define("globalThis", null); // placeholder

    // process / Deno shim
    const argv = (typeof Deno !== "undefined") ? [...Deno.args.slice(1)] : [];
    const proc = {
      argv: ["deno","script.js",...argv],
      env: { get:(k)=>typeof Deno!=="undefined"?Deno.env.get(k):undefined },
      exit: (code)=>{ if(typeof Deno!=="undefined") Deno.exit(code); else process.exit(code); },
      stdout: { write:(s)=>{ const enc=new TextEncoder(); if(typeof Deno!=="undefined") Deno.stdout.writeSync(enc.encode(s)); else process.stdout.write(s); } },
      stderr: { write:(s)=>{ const enc=new TextEncoder(); if(typeof Deno!=="undefined") Deno.stderr.writeSync(enc.encode(s)); else process.stderr.write(s); } },
    };
    G.define("process", proc);

    // Math
    G.define("Math", Math);
    G.define("JSON", JSON);
    G.define("Date", Date);
    G.define("RegExp", RegExp);
    G.define("Error", Error);
    G.define("TypeError", TypeError);
    G.define("RangeError", RangeError);
    G.define("SyntaxError", SyntaxError);
    G.define("ReferenceError", ReferenceError);
    G.define("EvalError", EvalError);
    G.define("URIError", URIError);

    // Primitives constructors
    G.define("Object", Object);
    G.define("Array", Array);
    G.define("String", String);
    G.define("Number", Number);
    G.define("Boolean", Boolean);
    G.define("BigInt", BigInt);
    G.define("Symbol", Symbol);
    G.define("Map", Map);
    G.define("Set", Set);
    G.define("WeakMap", WeakMap);
    G.define("WeakSet", WeakSet);
    G.define("Promise", Promise);
    G.define("Proxy", Proxy);
    G.define("Reflect", Reflect);
    G.define("ArrayBuffer", ArrayBuffer);
    G.define("DataView", DataView);
    G.define("Int8Array", Int8Array);
    G.define("Uint8Array", Uint8Array);
    G.define("Uint8ClampedArray", Uint8ClampedArray);
    G.define("Int16Array", Int16Array);
    G.define("Uint16Array", Uint16Array);
    G.define("Int32Array", Int32Array);
    G.define("Uint32Array", Uint32Array);
    G.define("Float32Array", Float32Array);
    G.define("Float64Array", Float64Array);
    G.define("BigInt64Array", BigInt64Array);
    G.define("BigUint64Array", BigUint64Array);
    G.define("Function", Function);

    // Globals
    G.define("parseInt", parseInt);
    G.define("parseFloat", parseFloat);
    G.define("isNaN", isNaN);
    G.define("isFinite", isFinite);
    G.define("encodeURIComponent", encodeURIComponent);
    G.define("decodeURIComponent", decodeURIComponent);
    G.define("encodeURI", encodeURI);
    G.define("decodeURI", decodeURI);
    G.define("escape", typeof escape!=="undefined"?escape:s=>s);
    G.define("unescape", typeof unescape!=="undefined"?unescape:s=>s);
    G.define("atob", typeof atob!=="undefined"?atob:s=>Buffer.from(s,"base64").toString());
    G.define("btoa", typeof btoa!=="undefined"?btoa:s=>Buffer.from(s).toString("base64"));
    G.define("queueMicrotask", typeof queueMicrotask!=="undefined"?queueMicrotask:f=>Promise.resolve().then(f));
    G.define("structuredClone", typeof structuredClone!=="undefined"?structuredClone:JSON.parse.bind(null,JSON.stringify));
    G.define("setTimeout", typeof setTimeout!=="undefined"?setTimeout:(_,__)=>{});
    G.define("clearTimeout", typeof clearTimeout!=="undefined"?clearTimeout:()=>{});
    G.define("setInterval", typeof setInterval!=="undefined"?setInterval:(_,__)=>{});
    G.define("clearInterval", typeof clearInterval!=="undefined"?clearInterval:()=>{});
    G.define("URL", typeof URL!=="undefined"?URL:class URL{});
    G.define("TextEncoder", typeof TextEncoder!=="undefined"?TextEncoder:class{});
    G.define("TextDecoder", typeof TextDecoder!=="undefined"?TextDecoder:class{});
    G.define("fetch", typeof fetch!=="undefined"?fetch:async()=>{throw new Error("fetch not available");});
    G.define("crypto", typeof crypto!=="undefined"?crypto:{});

    // Make globalThis reference itself
    const gt = {};
    G.vars.forEach((v,k) => { try{gt[k]=v.val;}catch(e){} });
    gt.globalThis = gt;
    G.define("globalThis", gt);

    // Deno
    if(typeof Deno!=="undefined") G.define("Deno", Deno);
  }

  hostStr(v) {
    if(v===null) return "null";
    if(v===undefined) return "undefined";
    if(typeof v==="string") return v;
    if(typeof v==="function") return v.toString ? v.toString() : "[Function]";
    if(Array.isArray(v)) return "[ "+v.map(x=>this.inspectVal(x)).join(", ")+" ]";
    if(typeof v==="object") {
      try { return JSON.stringify(v, null, 2); } catch(e) { return "[Object]"; }
    }
    return String(v);
  }
  inspectVal(v) {
    if(v===null) return "null";
    if(v===undefined) return "undefined";
    if(typeof v==="string") return `'${v}'`;
    if(Array.isArray(v)) return "["+v.map(x=>this.inspectVal(x)).join(",")+"]";
    if(typeof v==="object") { try{return JSON.stringify(v);}catch(e){return "[Object]";} }
    return String(v);
  }

  // ── Hoisting ──
  hoist(body, env) {
    for(const node of body) {
      if(!node) continue;
      if(node.type==="FunctionDeclaration"&&node.name) {
        env.funcEnv().define(node.name, this.makeFunction(node, env), "var");
      } else if(node.type==="VariableDeclaration"&&node.kind==="var") {
        for(const d of node.declarations) this.hoistPattern(d.id, env.funcEnv());
      } else if(node.type==="ExportNamedDeclaration"&&node.declaration) {
        this.hoist([node.declaration], env);
      }
    }
  }
  hoistPattern(pat, env) {
    if(pat.type==="Identifier") { if(!env.vars.has(pat.name)) env.define(pat.name, undefined, "var"); }
    else if(pat.type==="ObjectPattern") pat.properties.forEach(p=>p.type==="RestElement"?this.hoistPattern(p.argument,env):this.hoistPattern(p.value,env));
    else if(pat.type==="ArrayPattern") pat.elements.forEach(e=>e&&this.hoistPattern(e.type==="AssignmentPattern"?e.left:e,env));
  }

  // ── Execute statements ──
  execBlock(body, env) {
    this.hoist(body, env);
    for(const node of body) {
      const r = this.exec(node, env);
      if(r instanceof ReturnSignal||r instanceof BreakSignal||r instanceof ContinueSignal||r instanceof ThrowSignal) return r;
    }
    return undefined;
  }

  exec(node, env) {
    if(!node) return undefined;
    switch(node.type) {
      case "Program": return this.execBlock(node.body, env);
      case "EmptyStatement": case "DebuggerStatement": return undefined;
      case "BlockStatement": { const benv=new Env(env,true); return this.execBlock(node.body,benv); }
      case "ExpressionStatement": return this.eval(node.expression, env);
      case "VariableDeclaration": {
        for(const d of node.declarations) {
          const val = d.init ? this.eval(d.init, env) : undefined;
          this.bindPattern(d.id, val, env, node.kind);
        }
        return undefined;
      }
      case "FunctionDeclaration": return undefined; // already hoisted
      case "ClassDeclaration": {
        const cls=this.makeClass(node, env);
        if(node.name) env.define(node.name, cls, "let");
        return undefined;
      }
      case "ReturnStatement": return new ReturnSignal(node.argument ? this.eval(node.argument,env) : undefined);
      case "BreakStatement": return new BreakSignal(node.label);
      case "ContinueStatement": return new ContinueSignal(node.label);
      case "ThrowStatement": return new ThrowSignal(this.eval(node.argument, env));
      case "IfStatement": {
        const test=this.eval(node.test, env);
        return test ? this.exec(node.consequent, env) : (node.alternate ? this.exec(node.alternate, env) : undefined);
      }
      case "WhileStatement": {
        while(this.eval(node.test, env)) {
          const r=this.exec(node.body, env);
          if(r instanceof BreakSignal) break;
          if(r instanceof ContinueSignal) continue;
          if(r instanceof ReturnSignal||r instanceof ThrowSignal) return r;
        }
        return undefined;
      }
      case "DoWhileStatement": {
        do {
          const r=this.exec(node.body, env);
          if(r instanceof BreakSignal) break;
          if(r instanceof ContinueSignal) continue;
          if(r instanceof ReturnSignal||r instanceof ThrowSignal) return r;
        } while(this.eval(node.test, env));
        return undefined;
      }
      case "ForStatement": {
        const fenv=new Env(env,true);
        if(node.init) {
          if(node.init.type==="VariableDeclaration") this.exec(node.init, fenv);
          else this.eval(node.init, fenv);
        }
        while(!node.test||this.eval(node.test,fenv)) {
          const benv=new Env(fenv,true);
          const r=this.exec(node.body, benv);
          if(r instanceof BreakSignal) break;
          if(r instanceof ContinueSignal) { if(node.update) this.eval(node.update,fenv); continue; }
          if(r instanceof ReturnSignal||r instanceof ThrowSignal) return r;
          if(node.update) this.eval(node.update, fenv);
        }
        return undefined;
      }
      case "ForInStatement": {
        const obj=this.eval(node.right, env);
        for(const key in obj) {
          const benv=new Env(env,true);
          this.assignTarget(node.left, key, benv);
          const r=this.exec(node.body, benv);
          if(r instanceof BreakSignal) break;
          if(r instanceof ContinueSignal) continue;
          if(r instanceof ReturnSignal||r instanceof ThrowSignal) return r;
        }
        return undefined;
      }
      case "ForOfStatement": {
        const iter=this.eval(node.right, env);
        for(const val of iter) {
          const benv=new Env(env,true);
          this.assignTarget(node.left, val, benv);
          const r=this.exec(node.body, benv);
          if(r instanceof BreakSignal) break;
          if(r instanceof ContinueSignal) continue;
          if(r instanceof ReturnSignal||r instanceof ThrowSignal) return r;
        }
        return undefined;
      }
      case "TryStatement": {
        let result;
        try {
          result = this.exec(node.block, env);
          if(result instanceof ThrowSignal) throw result;
        } catch(e) {
          const thrown = e instanceof ThrowSignal ? e.value : e;
          if(node.handler) {
            const henv=new Env(env,true);
            if(node.handler.param) this.bindPattern(node.handler.param, thrown, henv, "let");
            result = this.exec(node.handler.body, henv);
          }
        } finally {
          if(node.finalizer) { const fr=this.exec(node.finalizer,env); if(fr instanceof ReturnSignal||fr instanceof ThrowSignal) return fr; }
        }
        return result;
      }
      case "SwitchStatement": {
        const disc=this.eval(node.discriminant, env);
        let matched=false;
        for(const c of node.cases) {
          if(!matched&&c.test!==null) {
            if(this.eval(c.test, env)===disc) matched=true;
          } else if(c.test===null) matched=true;
          if(matched) {
            for(const stmt of c.consequent) {
              const r=this.exec(stmt, env);
              if(r instanceof BreakSignal) return undefined;
              if(r instanceof ReturnSignal||r instanceof ContinueSignal||r instanceof ThrowSignal) return r;
            }
          }
        }
        return undefined;
      }
      case "ExportDefaultDeclaration": return this.exec(node.declaration, env);
      case "ExportNamedDeclaration": return node.declaration ? this.exec(node.declaration, env) : undefined;
      default: return undefined;
    }
  }

  assignTarget(target, val, env) {
    if(target.type==="VariableDeclaration") {
      this.bindPattern(target.declarations[0].id, val, env, target.kind);
    } else if(target.type==="Identifier") {
      if(!env.has(target.name)) env.define(target.name, val, "let");
      else env.set(target.name, val);
    } else if(target.type==="MemberExpression") {
      const obj=this.eval(target.object, env);
      const key=target.computed ? this.eval(target.property,env) : target.property.name;
      obj[key]=val;
    }
  }

  bindPattern(pat, val, env, kind) {
    if(pat.type==="Identifier") {
      if(kind==="var") env.funcEnv().define(pat.name, val, kind);
      else env.define(pat.name, val, kind);
    } else if(pat.type==="ObjectPattern") {
      const obj=val??{};
      const used=new Set();
      for(const prop of pat.properties) {
        if(prop.type==="RestElement") {
          const rest={};
          for(const k of Object.keys(obj)) if(!used.has(k)) rest[k]=obj[k];
          this.bindPattern(prop.argument, rest, env, kind);
        } else {
          const key=prop.computed ? this.eval(prop.key,env) : (prop.key.name??prop.key.raw??prop.key.value);
          used.add(key);
          let v=obj[key];
          if(v===undefined&&prop.defaultValue) v=this.eval(prop.defaultValue,env);
          this.bindPattern(prop.value, v, env, kind);
        }
      }
    } else if(pat.type==="ArrayPattern") {
      const arr=val??[];
      let i=0;
      for(const el of pat.elements) {
        if(!el) { i++; continue; }
        if(el.type==="RestElement") { this.bindPattern(el.argument, arr.slice(i), env, kind); break; }
        if(el.type==="AssignmentPattern") {
          let v=arr[i]; if(v===undefined) v=this.eval(el.right,env);
          this.bindPattern(el.left, v, env, kind);
        } else {
          this.bindPattern(el, arr[i], env, kind);
        }
        i++;
      }
    } else if(pat.type==="AssignmentPattern") {
      let v=val; if(v===undefined) v=this.eval(pat.right,env);
      this.bindPattern(pat.left, v, env, kind);
    }
  }

  // ── Evaluate expressions ──
  eval(node, env) {
    if(!node) return undefined;
    switch(node.type) {
      case "Literal": return node.value;
      case "Identifier": return env.get(node.name);
      case "ThisExpression": return env.get("this");
      case "Super": return env.get("__super__");
      case "TemplateLiteral": {
        let result="";
        for(const part of node.parts) {
          if(part.type==="str") result+=part.value;
          else {
            const inner=new Lexer(part.src).tokenize();
            const ast=new Parser(inner).parseExpression();
            result+=String(this.eval(ast,env));
          }
        }
        return result;
      }
      case "RegexLiteral": return new RegExp(node.pattern, node.flags);
      case "ArrayExpression": {
        const arr=[];
        for(const el of node.elements) {
          if(!el) { arr.push(undefined); continue; }
          if(el.type==="SpreadElement") { const s=this.eval(el.argument,env); arr.push(...(Array.isArray(s)?s:[...s])); }
          else arr.push(this.eval(el, env));
        }
        return arr;
      }
      case "ObjectExpression": {
        const obj={};
        for(const prop of node.properties) {
          if(prop.type==="SpreadElement") { Object.assign(obj, this.eval(prop.argument,env)); continue; }
          const key=prop.computed ? this.eval(prop.key,env) : (prop.key.name??String(prop.key.raw??prop.key.value));
          if(prop.kind==="get") {
            Object.defineProperty(obj, key, {get:this.eval(prop.value,env), enumerable:true, configurable:true});
          } else if(prop.kind==="set") {
            Object.defineProperty(obj, key, {set:this.eval(prop.value,env), enumerable:true, configurable:true});
          } else {
            obj[key]=this.eval(prop.value, env);
          }
        }
        return obj;
      }
      case "FunctionExpression": case "ArrowFunctionExpression": return this.makeFunction(node, env);
      case "ClassExpression": return this.makeClass(node, env);
      case "MemberExpression": {
        if(node.optional) {
          const obj=this.eval(node.object,env);
          if(obj==null) return undefined;
          const key=node.computed?this.eval(node.property,env):node.property.name;
          return obj[key];
        }
        const obj=this.eval(node.object,env);
        const key=node.computed?this.eval(node.property,env):node.property.name;
        if(obj==null) throw new TypeError(`Cannot read properties of ${obj} (reading '${key}')`);
        const val=obj[key];
        if(val&&val.__jsInterp__) {
          // wrap so 'this' is bound to obj for non-arrow functions
          if(!val.__jsInterp__.isArrow) {
            const bound=(...args)=>this.callFunction(val,obj,args);
            bound.__jsInterp__=val.__jsInterp__;
            bound.__boundThis__=obj;
            return bound;
          }
          return val;
        }
        return typeof val==="function"?val.bind(obj):val;
      }
      case "CallExpression": return this.evalCall(node, env);
      case "NewExpression": return this.evalNew(node, env);
      case "TaggedTemplateExpression": {
        const tag=this.eval(node.tag,env);
        const quasi=node.quasi; // TemplateLiteral
        const strings=[], values=[];
        for(const part of quasi.parts) {
          if(part.type==="str") strings.push(part.value);
          else {
            const inner=new Lexer(part.src).tokenize();
            const ast=new Parser(inner).parseExpression();
            values.push(this.eval(ast,env));
          }
        }
        return this.callFunction(tag, null, [strings,...values]);
      }
      case "AssignmentExpression": return this.evalAssign(node, env);
      case "BinaryExpression": return this.evalBinary(node, env);
      case "LogicalExpression": {
        const left=this.eval(node.left,env);
        if(node.operator==="&&") return left ? this.eval(node.right,env) : left;
        if(node.operator==="||") return left ? left : this.eval(node.right,env);
        if(node.operator==="??") return left!=null ? left : this.eval(node.right,env);
        return left;
      }
      case "UnaryExpression": {
        if(node.operator==="typeof"&&node.argument.type==="Identifier") {
          const v=env.get(node.argument.name); return typeof v;
        }
        const arg=this.eval(node.argument,env);
        switch(node.operator) {
          case "!": return !arg;
          case "-": return -arg;
          case "+": return +arg;
          case "~": return ~arg;
          case "typeof": return typeof arg;
          case "void": return undefined;
          case "delete": {
            const a=node.argument;
            if(a.type==="MemberExpression") {
              const obj=this.eval(a.object,env);
              const key=a.computed?this.eval(a.property,env):a.property.name;
              return delete obj[key];
            }
            return true;
          }
        }
        return undefined;
      }
      case "UpdateExpression": {
        const arg=node.argument;
        const old=this.evalLVal(arg,env);
        const nv=node.operator==="++"?old+1:old-1;
        this.setLVal(arg, nv, env);
        return node.prefix?nv:old;
      }
      case "ConditionalExpression": {
        return this.eval(node.test,env) ? this.eval(node.consequent,env) : this.eval(node.alternate,env);
      }
      case "SequenceExpression": {
        let v; for(const e of node.expressions) v=this.eval(e,env); return v;
      }
      case "SpreadElement": return this.eval(node.argument,env);
      case "AwaitExpression": return this.eval(node.argument,env); // simplified: sync await
      case "YieldExpression": return this.eval(node.argument,env);
      default: return undefined;
    }
  }

  evalLVal(node, env) {
    if(node.type==="Identifier") return env.get(node.name);
    if(node.type==="MemberExpression") {
      const obj=this.eval(node.object,env);
      const key=node.computed?this.eval(node.property,env):node.property.name;
      return obj[key];
    }
    return undefined;
  }

  setLVal(node, val, env) {
    if(node.type==="Identifier") env.set(node.name, val);
    else if(node.type==="MemberExpression") {
      const obj=this.eval(node.object,env);
      const key=node.computed?this.eval(node.property,env):node.property.name;
      obj[key]=val;
    }
  }

  evalAssign(node, env) {
    const op=node.operator;
    if(op==="=") {
      const val=this.eval(node.right,env);
      if(node.left.type==="Identifier") return env.set(node.left.name,val);
      if(node.left.type==="MemberExpression") {
        const obj=this.eval(node.left.object,env);
        const key=node.left.computed?this.eval(node.left.property,env):node.left.property.name;
        obj[key]=val; return val;
      }
      if(node.left.type==="ArrayPattern"||node.left.type==="ObjectPattern") {
        this.bindPattern(node.left, val, env, "let"); return val;
      }
      return val;
    }
    const cur=this.evalLVal(node.left,env);
    let nv;
    switch(op) {
      case "+=": nv=cur+this.eval(node.right,env); break;
      case "-=": nv=cur-this.eval(node.right,env); break;
      case "*=": nv=cur*this.eval(node.right,env); break;
      case "/=": nv=cur/this.eval(node.right,env); break;
      case "%=": nv=cur%this.eval(node.right,env); break;
      case "**=": nv=cur**this.eval(node.right,env); break;
      case "&&=": nv=cur&&this.eval(node.right,env); break;
      case "||=": nv=cur||this.eval(node.right,env); break;
      case "??=": nv=cur??this.eval(node.right,env); break;
      case "&=": nv=cur&this.eval(node.right,env); break;
      case "|=": nv=cur|this.eval(node.right,env); break;
      case "^=": nv=cur^this.eval(node.right,env); break;
      case "<<=": nv=cur<<this.eval(node.right,env); break;
      case ">>=": nv=cur>>this.eval(node.right,env); break;
      case ">>>=": nv=cur>>>this.eval(node.right,env); break;
      default: nv=this.eval(node.right,env);
    }
    this.setLVal(node.left, nv, env);
    return nv;
  }

  evalBinary(node, env) {
    const l=this.eval(node.left,env), r=this.eval(node.right,env);
    switch(node.operator) {
      case "+": return l+r; case "-": return l-r; case "*": return l*r;
      case "/": return l/r; case "%": return l%r; case "**": return l**r;
      case "===": return l===r; case "!==": return l!==r;
      case "==": return l==r; case "!=": return l!=r;
      case "<": return l<r; case "<=": return l<=r;
      case ">": return l>r; case ">=": return l>=r;
      case "&": return l&r; case "|": return l|r; case "^": return l^r;
      case "<<": return l<<r; case ">>": return l>>r; case ">>>": return l>>>r;
      case "instanceof": return l instanceof r;
      case "in": return l in r;
    }
    return undefined;
  }

  evalCall(node, env) {
    // Special: super()
    if(node.callee.type==="Super") {
      const superClass=env.get("__superClass__");
      const args=this.evalArgs(node.arguments, env);
      const thisVal=env.get("this");
      if(superClass) superClass.call(thisVal, ...args);
      return thisVal;
    }
    // Method call
    if(node.callee.type==="MemberExpression") {
      const m=node.callee;
      const obj=this.eval(m.object,env);
      if(node.callee.optional&&obj==null) return undefined;
      const key=m.computed?this.eval(m.property,env):m.property.name;
      if(obj==null) throw new TypeError(`Cannot read properties of ${obj} (reading '${key}')`);
      const fn=obj[key];
      const args=this.evalArgs(node.arguments, env);
      if(fn&&fn.__jsInterp__) return this.callFunction(fn, obj, args);
      if(typeof fn==="function") return fn.apply(obj, args);
      throw new TypeError(`${key} is not a function`);
    }
    const fn=this.eval(node.callee, env);
    const args=this.evalArgs(node.arguments, env);
    let thisVal=null;
    if(node.callee.type==="Identifier") thisVal=null;
    return this.callFunction(fn, thisVal, args, env);
  }

  evalArgs(argNodes, env) {
    const args=[];
    for(const a of argNodes) {
      if(a.type==="SpreadElement") { const v=this.eval(a.argument,env); args.push(...(Array.isArray(v)?v:[...v])); }
      else args.push(this.eval(a,env));
    }
    return args;
  }

  callFunction(fn, thisVal, args, callerEnv) {
    if(!fn) throw new TypeError(`${fn} is not a function`);
    if(fn.__jsInterp__) {
      const {params, body, closure, isArrow, isAsync, isGenerator, name} = fn.__jsInterp__;
      const fenv = new Env(closure);
      const resolvedThis = thisVal ?? fn.__boundThis__ ?? fn.__jsInterp__.defaultThis ?? null;
      if(!isArrow) fenv.define("this", resolvedThis);
      fenv.define("arguments", args);
      this.bindParams(params, args, fenv);
      if(name) fenv.define(name, fn); // named function expr recursion
      if(isAsync) {
        return (async()=>{
          let r;
          if(fn.__jsInterp__.expression) r=new ReturnSignal(this.eval(body,fenv));
          else r=this.execBlock(body.body??[body], fenv);
          if(r instanceof ReturnSignal) return r.value;
          if(r instanceof ThrowSignal) throw r.value;
          return undefined;
        })();
      }
      if(isGenerator) {
        const interp=this;
        function* gen() {
          let r;
          if(fn.__jsInterp__.expression) r=new ReturnSignal(interp.eval(body,fenv));
          else r=interp.execBlock(body.body??[body], fenv);
          if(r instanceof ReturnSignal) return r.value;
          if(r instanceof ThrowSignal) throw r.value;
          return undefined;
        }
        return gen();
      }
      let r;
      if(fn.__jsInterp__.expression) r=new ReturnSignal(this.eval(body,fenv));
      else r=this.execBlock(body.body??[body], fenv);
      if(r instanceof ReturnSignal) return r.value;
      if(r instanceof ThrowSignal) throw r.value;
      return undefined;
    }
    if(typeof fn==="function") return fn.apply(thisVal, args);
    throw new TypeError(`${typeof fn} is not a function`);
  }

  bindParams(params, args, env) {
    for(let i=0;i<params.length;i++) {
      const p=params[i];
      if(p.type==="RestElement") {
        this.bindPattern(p.argument, args.slice(i), env, "let");
        break;
      } else if(p.type==="AssignmentPattern") {
        let v=args[i]; if(v===undefined) v=this.eval(p.right, env);
        this.bindPattern(p.left, v, env, "let");
      } else {
        this.bindPattern(p, args[i], env, "let");
      }
    }
  }

  makeFunction(node, env) {
    const fn = (...args) => this.callFunction(fn, null, args);
    fn.__jsInterp__ = {
      params: node.params,
      body: node.body,
      closure: env,
      isArrow: node.type==="ArrowFunctionExpression",
      isAsync: !!node.async,
      isGenerator: !!node.generator,
      name: node.name,
      expression: !!node.expression,
    };
    if(node.name) fn.__name__ = node.name;
    Object.defineProperty(fn, "name", {value: node.name??""});
    Object.defineProperty(fn, "length", {value: node.params.filter(p=>p.type!=="RestElement"&&p.type!=="AssignmentPattern").length});
    fn.prototype = {constructor:fn};
    fn.toString = ()=>`function ${node.name??''}(${node.params.map(p=>p.name??'...').join(',')}) { [interpreted code] }`;
    return fn;
  }

  evalNew(node, env) {
    let ctor = this.eval(node.callee, env);
    const args = this.evalArgs(node.arguments, env);
    if(ctor&&ctor.__jsInterp__&&!ctor.__jsInterp__.isClass) {
      const obj=Object.create(ctor.prototype??{});
      const {params,body,closure,name}=ctor.__jsInterp__;
      const fenv=new Env(closure);
      fenv.define("this", obj);
      if(params) this.bindParams(params, args, fenv);
      if(name) fenv.define(name, ctor);
      const r=this.execBlock(body.body??[body], fenv);
      if(r instanceof ThrowSignal) throw r.value;
      if(r instanceof ReturnSignal&&r.value&&typeof r.value==="object") return r.value;
      return obj;
    }
    if(typeof ctor==="function") return new ctor(...args);
    throw new TypeError(`${ctor} is not a constructor`);
  }

  makeClass(node, env) {
    let superCtor=null;
    if(node.superClass) superCtor=this.eval(node.superClass,env);

    const methods={}, staticMethods={}, getters={}, setters={}, staticGetters={}, staticSetters={};
    let ctorNode=null;

    for(const m of node.methods) {
      if(m.type==="ClassField") continue; // handled in constructor
      const key=m.computed?this.eval(m.key,env):m.key.name;
      if(key==="constructor") { ctorNode=m; continue; }
      const fn=this.makeFunction(m.value, env);
      if(m.static) {
        if(m.kind==="get") staticGetters[key]=fn;
        else if(m.kind==="set") staticSetters[key]=fn;
        else staticMethods[key]=fn;
      } else {
        if(m.kind==="get") getters[key]=fn;
        else if(m.kind==="set") setters[key]=fn;
        else methods[key]=fn;
      }
    }

    const fields = node.methods.filter(m=>m.type==="ClassField");
    const interp=this;

    const cls = function(...args) {
      if(superCtor&&superCtor.__jsInterp__) {
        // will call super() inside constructor
      } else if(superCtor) {
        superCtor.apply(this, []);
      }
      // bind instance methods
      // apply fields
      for(const f of fields) {
        if(!f.static) {
          const k=f.computed?interp.eval(f.key,env):f.key.name;
          this[k]=f.value?interp.eval(f.value,env):undefined;
        }
      }
      if(ctorNode) {
        const fenv=new Env(env);
        fenv.define("this", this);
        fenv.define("__superClass__", superCtor);
        if(superCtor) fenv.define("__super__", superCtor);
        interp.bindParams(ctorNode.value.params, args, fenv);
        const r=interp.execBlock(ctorNode.value.body.body, fenv);
        if(r instanceof ThrowSignal) throw r.value;
      } else if(superCtor) {
        if(superCtor.__jsInterp__) interp.callFunction(superCtor, this, args);
        else superCtor.apply(this, args);
      }
    };

    // prototype chain
    if(superCtor) {
      cls.prototype=Object.create(superCtor.prototype??{});
      cls.prototype.constructor=cls;
      // copy super static methods
      Object.setPrototypeOf(cls, superCtor);
    } else {
      cls.prototype={constructor:cls};
    }

    // assign methods to prototype
    for(const [k,fn] of Object.entries(methods)) {
      const f=fn;
      cls.prototype[k]=function(...args){return interp.callFunction(f, this, args);};
      cls.prototype[k].__jsInterp__=f.__jsInterp__;
    }
    for(const [k,fn] of Object.entries(getters)) {
      Object.defineProperty(cls.prototype, k, {get:function(){return interp.callFunction(fn,this,[]);}, configurable:true, enumerable:false});
    }
    for(const [k,fn] of Object.entries(setters)) {
      const desc=Object.getOwnPropertyDescriptor(cls.prototype,k)||{};
      Object.defineProperty(cls.prototype, k, {set:function(v){interp.callFunction(fn,this,[v]);}, get:desc.get, configurable:true, enumerable:false});
    }
    for(const [k,fn] of Object.entries(staticMethods)) cls[k]=(...args)=>interp.callFunction(fn, cls, args);
    for(const [k,fn] of Object.entries(staticGetters)) Object.defineProperty(cls,k,{get:()=>interp.callFunction(fn,cls,[]),configurable:true});
    for(const [k,fn] of Object.entries(staticSetters)) {
      const desc=Object.getOwnPropertyDescriptor(cls,k)||{};
      Object.defineProperty(cls,k,{set:(v)=>interp.callFunction(fn,cls,[v]),get:desc.get,configurable:true});
    }
    // static fields
    for(const f of fields) {
      if(f.static) { const k=f.computed?interp.eval(f.key,env):f.key.name; cls[k]=f.value?interp.eval(f.value,env):undefined; }
    }

    cls.__jsInterp__={isClass:true,name:node.name};
    if(node.name) { cls.name&&Object.defineProperty(cls,"name",{value:node.name,configurable:true}); }
    cls.toString=()=>`[class ${node.name??'(anonymous)'}]`;

    // super method call support: cls.prototype methods need access to super
    for(const k of Object.keys(methods)) {
      const origFn=cls.prototype[k];
      const superProto=superCtor?.prototype;
      if(origFn&&origFn.__jsInterp__) {
        const fi=origFn.__jsInterp__;
        fi.superProto=superProto;
      }
    }

    return cls;
  }

  run(src) {
    const tokens = new Lexer(src).tokenize();
    const ast = new Parser(tokens).parse();
    const r = this.exec(ast, this.globalEnv);
    if(r instanceof ThrowSignal) throw r.value;
    return r;
  }
}

// ─────────────────────────────────────────────
// MAIN ENTRY POINT (Node.js)
// ─────────────────────────────────────────────
const fs = require("fs");
const path = require("path");

const args = process.argv.slice(2);
if (args.length === 0) {
  console.error("Usage: js0i.js <script.js> [args...]");
  process.exit(1);
}

const scriptPath = args[0];
let src;
try {
  src = fs.readFileSync(path.resolve(scriptPath), "utf8");
} catch (e) {
  console.error(`Cannot read file: ${scriptPath}: ${e.message}`);
  process.exit(1);
}

const interp = new Interpreter();
const proc = interp.globalEnv.get("process");
proc.argv = ["node", scriptPath, ...args.slice(1)];

try {
  const result = interp.run(src);
  if (result instanceof Promise) {
    result.catch(e => {
      console.error(e instanceof Error ? (e.stack ?? e.message) : String(e));
      process.exit(1);
    });
  }
} catch (e) {
  console.error(e instanceof Error ? (e.stack ?? e.message) : String(e));
  process.exit(1);
}