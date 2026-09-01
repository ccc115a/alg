'use strict';
var fs = require('fs');

// ===== Helpers =====
function isDigit(c) { return c >= '0' && c <= '9'; }
function isAlpha(c) { return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || c === '_' || c === '$'; }
function isAlNum(c) { return isAlpha(c) || isDigit(c); }
function isHex(c) { return isDigit(c) || (c >= 'a' && c <= 'f') || (c >= 'A' && c <= 'F'); }

// ===== Tokenizer =====
function tokenize(src) {
  var toks = [];
  var i = 0;
  var len = src.length;
  while (i < len) {
    var c = src[i];
    if (c === ' ' || c === '\t' || c === '\r' || c === '\n') { i++; continue; }
    if (c === '/' && i + 1 < len && src[i + 1] === '/') { i += 2; while (i < len && src[i] !== '\n') i++; continue; }
    if (c === '/' && i + 1 < len && src[i + 1] === '*') { i += 2; while (i + 1 < len && !(src[i] === '*' && src[i + 1] === '/')) i++; i += 2; continue; }
    if (isDigit(c)) {
      var s = i;
      if (c === '0' && i + 1 < len) {
        var nx = src[i + 1];
        if (nx === 'x' || nx === 'X') { i += 2; while (i < len && isHex(src[i])) i++; toks.push({t:'N',v:Number(src.substring(s,i))}); continue; }
        if (nx === 'b' || nx === 'B') { i += 2; while (i < len && (src[i]==='0'||src[i]==='1')) i++; toks.push({t:'N',v:Number(src.substring(s,i))}); continue; }
        if (nx === 'o' || nx === 'O') { i += 2; while (i < len && src[i]>='0' && src[i]<='7') i++; toks.push({t:'N',v:Number(src.substring(s,i))}); continue; }
      }
      while (i < len && isDigit(src[i])) i++;
      if (i < len && src[i] === '.' && (i+1>=len || src[i+1]!=='.')) { i++; while (i < len && isDigit(src[i])) i++; }
      if (i < len && (src[i]==='e'||src[i]==='E')) { i++; if (i<len&&(src[i]==='+'||src[i]==='-')) i++; while (i<len&&isDigit(src[i])) i++; }
      toks.push({t:'N',v:Number(src.substring(s,i))}); continue;
    }
    if (c === '"' || c === "'") {
      var q = c; i++; var str = '';
      while (i < len && src[i] !== q) {
        if (src[i] === '\\') {
          i++; var e = src[i];
          if (e==='n') str+='\n'; else if (e==='t') str+='\t'; else if (e==='r') str+='\r';
          else if (e==='\\') str+='\\'; else if (e==='0') str+='\0'; else if (e==="'") str+="'";
          else if (e==='"') str+='"'; else if (e==='b') str+='\b'; else if (e==='f') str+='\f';
          else if (e==='u') { i++; str+=String.fromCharCode(parseInt(src.substring(i,i+4),16)); i+=3; }
          else if (e==='x') { i++; str+=String.fromCharCode(parseInt(src.substring(i,i+2),16)); i+=1; }
          else str+=e;
          i++;
        } else { str += src[i]; i++; }
      }
      i++; toks.push({t:'S',v:str}); continue;
    }
    if (isAlpha(c)) { var s=i; while(i<len&&isAlNum(src[i]))i++; toks.push({t:'I',v:src.substring(s,i)}); continue; }
    var c3 = (i+2<len)?src.substring(i,i+3):'';
    var c2 = (i+1<len)?src.substring(i,i+2):'';
    if (c3==='==='||c3==='!=='||c3==='>>>'||c3==='**='||c3==='<<='||c3==='>>=') { toks.push({t:'P',v:c3}); i+=3; continue; }
    if (c2==='=='||c2==='!='||c2==='<='||c2==='>='||c2==='&&'||c2==='||'||c2==='+='||c2==='-='||
        c2==='*='||c2==='/='||c2==='%='||c2==='**'||c2==='++'||c2==='--'||c2==='=>'||c2==='<<'||
        c2==='>>'||c2==='&='||c2==='|='||c2==='^=') { toks.push({t:'P',v:c2}); i+=2; continue; }
    if ('+-*/%=<>!&|^~?:.;,(){}[]'.indexOf(c)>=0) { toks.push({t:'P',v:c}); i++; continue; }
    throw new Error('Unexpected char: '+c+' at pos '+i);
  }
  toks.push({t:'E',v:''}); return toks;
}

// ===== Parser =====
var PREC = {'||':1,'&&':2,'|':3,'^':4,'&':5,'==':6,'!=':6,'===':6,'!==':6,
  '<':7,'>':7,'<=':7,'>=':7,'<<':8,'>>':8,'>>>':8,'+':9,'-':9,'*':10,'/':10,'%':10,'**':11};

function Parser(toks) { this.toks=toks; this.pos=0; }
Parser.prototype.pk = function() { return this.toks[this.pos]; };
Parser.prototype.nx = function() { return this.toks[this.pos++]; };
Parser.prototype.at = function(t,v) { var k=this.pk(); return k.t===t&&(v===undefined||k.v===v); };
Parser.prototype.eat = function(t,v) { if(this.at(t,v)) return this.nx(); return null; };
Parser.prototype.ex = function(t,v) { var k=this.eat(t,v); if(!k) throw new SyntaxError('Expected '+(v||t)+' got '+this.pk().t+':'+this.pk().v+' at token '+this.pos); return k; };

Parser.prototype.parseProgram = function() {
  var body=[]; while(!this.at('E')) body.push(this.parseStmt()); return {type:'Prog',body:body};
};

Parser.prototype.parseStmt = function() {
  if (this.at('P','{')) return this.parseBlock();
  if (this.at('P',';')) { this.nx(); return {type:'Empty'}; }
  if (this.at('I','var')||this.at('I','let')||this.at('I','const')) return this.parseVarDecl(true);
  if (this.at('I','function')) return this.parseFuncDecl();
  if (this.at('I','return')) return this.parseReturn();
  if (this.at('I','if')) return this.parseIf();
  if (this.at('I','while')) return this.parseWhile();
  if (this.at('I','do')) return this.parseDo();
  if (this.at('I','for')) return this.parseFor();
  if (this.at('I','break')) { this.nx(); var l=null; if(this.at('I'))l=this.nx().v; this.eat('P',';'); return {type:'Break',label:l}; }
  if (this.at('I','continue')) { this.nx(); var l=null; if(this.at('I'))l=this.nx().v; this.eat('P',';'); return {type:'Cont',label:l}; }
  if (this.at('I','switch')) return this.parseSwitch();
  if (this.at('I','throw')) { this.nx(); var a=this.parseExpr(); this.eat('P',';'); return {type:'Throw',arg:a}; }
  if (this.at('I','try')) return this.parseTry();
  if (this.at('I')&&this.pos+1<this.toks.length&&this.toks[this.pos+1].t==='P'&&this.toks[this.pos+1].v===':') {
    var lb=this.nx().v; this.nx(); return {type:'Label',label:lb,body:this.parseStmt()};
  }
  var expr=this.parseExpr(); this.eat('P',';'); return {type:'ExprStmt',expr:expr};
};

Parser.prototype.parseBlock = function() {
  this.ex('P','{'); var body=[]; while(!this.at('P','}')) body.push(this.parseStmt()); this.ex('P','}');
  return {type:'Block',body:body};
};

Parser.prototype.parseVarDecl = function(semi) {
  var kind=this.nx().v; var decls=[];
  do { var name=this.ex('I').v; var init=null; if(this.eat('P','='))init=this.parseAssign(); decls.push({name:name,init:init}); } while(this.eat('P',','));
  if(semi) this.eat('P',';');
  return {type:'Var',kind:kind,decls:decls};
};

Parser.prototype.parseFuncDecl = function() {
  this.ex('I','function'); var name=this.ex('I').v; var params=this.parseParams(); var body=this.parseBlock();
  return {type:'FuncDecl',name:name,params:params,body:body};
};

Parser.prototype.parseParams = function() {
  this.ex('P','('); var p=[];
  if(!this.at('P',')')) { do { p.push(this.ex('I').v); } while(this.eat('P',',')); }
  this.ex('P',')'); return p;
};

Parser.prototype.parseReturn = function() {
  this.ex('I','return'); var a=null;
  if(!this.at('P',';')&&!this.at('P','}')&&!this.at('E')) a=this.parseExpr();
  this.eat('P',';'); return {type:'Return',arg:a};
};

Parser.prototype.parseIf = function() {
  this.ex('I','if'); this.ex('P','('); var t=this.parseExpr(); this.ex('P',')');
  var c=this.parseStmt(); var a=null; if(this.eat('I','else')) a=this.parseStmt();
  return {type:'If',test:t,cons:c,alt:a};
};

Parser.prototype.parseWhile = function() {
  this.ex('I','while'); this.ex('P','('); var t=this.parseExpr(); this.ex('P',')');
  return {type:'While',test:t,body:this.parseStmt()};
};

Parser.prototype.parseDo = function() {
  this.ex('I','do'); var b=this.parseStmt(); this.ex('I','while'); this.ex('P','(');
  var t=this.parseExpr(); this.ex('P',')'); this.eat('P',';');
  return {type:'DoWhile',test:t,body:b};
};

Parser.prototype.parseFor = function() {
  this.ex('I','for'); this.ex('P','(');
  var saved=this.pos;
  if (this.at('I','var')||this.at('I','let')||this.at('I','const')) {
    var kind=this.nx().v;
    if (this.at('I')) {
      var vn=this.nx().v;
      if (this.eat('I','in')) { var o=this.parseExpr(); this.ex('P',')'); return {type:'ForIn',kind:kind,name:vn,obj:o,body:this.parseStmt()}; }
      if (this.eat('I','of')) { var o=this.parseExpr(); this.ex('P',')'); return {type:'ForOf',kind:kind,name:vn,iter:o,body:this.parseStmt()}; }
    }
    this.pos=saved;
  } else if (this.at('I')) {
    var saved2=this.pos; var vn2=this.nx().v;
    if (this.eat('I','in')) { var o=this.parseExpr(); this.ex('P',')'); return {type:'ForIn',kind:null,name:vn2,obj:o,body:this.parseStmt()}; }
    this.pos=saved2;
  }
  var init=null;
  if(!this.at('P',';')) { if(this.at('I','var')||this.at('I','let')||this.at('I','const')) init=this.parseVarDecl(false); else init=this.parseExpr(); }
  this.ex('P',';'); var test=null; if(!this.at('P',';')) test=this.parseExpr();
  this.ex('P',';'); var upd=null; if(!this.at('P',')')) upd=this.parseExpr();
  this.ex('P',')'); return {type:'For',init:init,test:test,update:upd,body:this.parseStmt()};
};

Parser.prototype.parseSwitch = function() {
  this.ex('I','switch'); this.ex('P','('); var d=this.parseExpr(); this.ex('P',')'); this.ex('P','{');
  var cases=[];
  while(!this.at('P','}')) {
    if (this.eat('I','case')) { var t=this.parseExpr(); this.ex('P',':'); var b=[]; while(!this.at('P','}')&&!this.at('I','case')&&!this.at('I','default')) b.push(this.parseStmt()); cases.push({test:t,body:b}); }
    else if (this.eat('I','default')) { this.ex('P',':'); var b=[]; while(!this.at('P','}')&&!this.at('I','case')&&!this.at('I','default')) b.push(this.parseStmt()); cases.push({test:null,body:b}); }
  }
  this.ex('P','}'); return {type:'Switch',disc:d,cases:cases};
};

Parser.prototype.parseTry = function() {
  this.ex('I','try'); var bl=this.parseBlock(); var h=null;
  if(this.eat('I','catch')) { var p=null; if(this.eat('P','(')) { p=this.ex('I').v; this.ex('P',')'); } h={param:p,body:this.parseBlock()}; }
  var f=null; if(this.eat('I','finally')) f=this.parseBlock();
  return {type:'Try',block:bl,handler:h,fin:f};
};

// ===== Expression parsing =====
Parser.prototype.getPrec = function() {
  var tk=this.pk();
  if(tk.t==='P'&&PREC[tk.v]!==undefined) return PREC[tk.v];
  if(tk.t==='I'&&tk.v==='instanceof') return 7;
  if(tk.t==='I'&&tk.v==='in') return 7;
  return -1;
};

Parser.prototype.parseExpr = function() {
  var e=this.parseAssign(); while(this.eat('P',',')) { e={type:'Seq',left:e,right:this.parseAssign()}; } return e;
};

Parser.prototype.parseAssign = function() {
  var left=this.parseTernary();
  var ops=['=','+=','-=','*=','/=','%=','<<=','>>=','>>>=','&=','|=','^=','**='];
  for(var j=0;j<ops.length;j++) { if(this.eat('P',ops[j])) return {type:'Assign',op:ops[j],left:left,right:this.parseAssign()}; }
  return left;
};

Parser.prototype.parseTernary = function() {
  var e=this.parseBin(1);
  if(this.eat('P','?')) { var c=this.parseAssign(); this.ex('P',':'); return {type:'Cond',test:e,cons:c,alt:this.parseAssign()}; }
  return e;
};

Parser.prototype.parseBin = function(minP) {
  var left=this.parseUnary();
  while(true) {
    var p=this.getPrec(); if(p<minP) break;
    var op=this.nx().v;
    var right=this.parseBin(p+(op==='**'?0:1));
    left={type:(op==='||'||op==='&&')?'Logical':'Binary',op:op,left:left,right:right};
  }
  return left;
};

Parser.prototype.parseUnary = function() {
  if(this.at('P','!')||this.at('P','-')||this.at('P','+')||this.at('P','~')) { var op=this.nx().v; return {type:'Unary',op:op,arg:this.parseUnary(),prefix:true}; }
  if(this.at('P','++')||this.at('P','--')) { var op=this.nx().v; return {type:'Update',op:op,arg:this.parseUnary(),prefix:true}; }
  if(this.eat('I','typeof')) return {type:'Unary',op:'typeof',arg:this.parseUnary(),prefix:true};
  if(this.eat('I','void')) return {type:'Unary',op:'void',arg:this.parseUnary(),prefix:true};
  if(this.eat('I','delete')) return {type:'Unary',op:'delete',arg:this.parseUnary(),prefix:true};
  if(this.at('I','new')) return this.parseNew();
  return this.parsePostfix();
};

Parser.prototype.parseNew = function() {
  this.ex('I','new');
  if(this.at('I','new')) { var e=this.parseNew(); return {type:'New',callee:e,args:[]}; }
  var callee=this.parseMemberOnly(this.parsePrimary());
  var args=[];
  if(this.eat('P','(')) { if(!this.at('P',')')) { do{args.push(this.parseAssign());}while(this.eat('P',',')); } this.ex('P',')'); }
  return {type:'New',callee:callee,args:args};
};

Parser.prototype.parseMemberOnly = function(expr) {
  while(true) {
    if(this.eat('P','.')) { expr={type:'Member',obj:expr,prop:this.ex('I').v,computed:false}; }
    else if(this.eat('P','[')) { var p=this.parseExpr(); this.ex('P',']'); expr={type:'Member',obj:expr,prop:p,computed:true}; }
    else break;
  }
  return expr;
};

Parser.prototype.parsePostfix = function() {
  var e=this.parseCallMember();
  if(this.at('P','++')||this.at('P','--')) return {type:'Update',op:this.nx().v,arg:e,prefix:false};
  return e;
};

Parser.prototype.parseCallMember = function() {
  var e=this.parsePrimary();
  while(true) {
    if(this.eat('P','(')) { var a=[]; if(!this.at('P',')')) { do{a.push(this.parseAssign());}while(this.eat('P',',')); } this.ex('P',')'); e={type:'Call',callee:e,args:a}; }
    else if(this.eat('P','.')) { e={type:'Member',obj:e,prop:this.ex('I').v,computed:false}; }
    else if(this.eat('P','[')) { var p=this.parseExpr(); this.ex('P',']'); e={type:'Member',obj:e,prop:p,computed:true}; }
    else break;
  }
  return e;
};

Parser.prototype.parsePrimary = function() {
  if(this.at('N')) return {type:'Num',value:this.nx().v};
  if(this.at('S')) return {type:'Str',value:this.nx().v};
  if(this.eat('I','true')) return {type:'Bool',value:true};
  if(this.eat('I','false')) return {type:'Bool',value:false};
  if(this.eat('I','null')) return {type:'Lit',value:null};
  if(this.eat('I','undefined')) return {type:'Lit',value:undefined};
  if(this.eat('I','this')) return {type:'This'};
  if(this.at('I','function')) return this.parseFuncExpr();
  if(this.at('P','[')) return this.parseArrayLit();
  if(this.at('P','{')) return this.parseObjLit();
  if(this.eat('P','(')) { var e=this.parseExpr(); this.ex('P',')'); return e; }
  if(this.at('I')) return {type:'Id',name:this.nx().v};
  throw new SyntaxError('Unexpected: '+this.pk().v+' at token '+this.pos);
};

Parser.prototype.parseFuncExpr = function() {
  this.ex('I','function'); var name=null;
  if(this.at('I')&&!this.at('P','(')) name=this.nx().v;
  return {type:'FuncExpr',name:name,params:this.parseParams(),body:this.parseBlock()};
};

Parser.prototype.parseArrayLit = function() {
  this.ex('P','['); var el=[];
  while(!this.at('P',']')) {
    if(this.at('P',',')) { el.push(null); this.nx(); continue; }
    el.push(this.parseAssign());
    if(!this.at('P',']')) this.ex('P',',');
  }
  this.ex('P',']'); return {type:'Array',elems:el};
};

Parser.prototype.parseObjLit = function() {
  this.ex('P','{'); var props=[];
  while(!this.at('P','}')) {
    var key, computed=false;
    if(this.at('S')) key=this.nx().v;
    else if(this.at('N')) key=String(this.nx().v);
    else if(this.at('P','[')) { this.nx(); key=this.parseAssign(); this.ex('P',']'); computed=true; }
    else key=this.ex('I').v;
    if(!computed&&this.at('P','(')) {
      var p=this.parseParams(); var b=this.parseBlock();
      props.push({key:key,value:{type:'FuncExpr',name:key,params:p,body:b},computed:false});
    } else { this.ex('P',':'); props.push({key:key,value:this.parseAssign(),computed:computed}); }
    if(!this.at('P','}')) this.eat('P',',');
  }
  this.ex('P','}'); return {type:'Object',props:props};
};

// ===== Environment =====
function Env(parent) { this.parent=parent; this.vars={}; }
Env.prototype.def = function(n,v) { this.vars[n]=v; };
Env.prototype.get = function(n) {
  if(this.vars.hasOwnProperty(n)) return this.vars[n];
  if(this.parent) return this.parent.get(n);
  throw new ReferenceError(n+' is not defined');
};
Env.prototype.set = function(n,v) {
  if(this.vars.hasOwnProperty(n)) { this.vars[n]=v; return; }
  if(this.parent) { this.parent.set(n,v); return; }
  throw new ReferenceError(n+' is not defined');
};
Env.prototype.has = function(n) {
  if(this.vars.hasOwnProperty(n)) return true;
  if(this.parent) return this.parent.has(n);
  return false;
};

// ===== Signals =====
var SIG = {};
function RetSig(v) { this.s=SIG; this.v=v; }
function BrkSig(l) { this.s=SIG; this.l=l; }
function ContSig(l) { this.s=SIG; this.l=l; }
function isSig(e) { return e!==null&&e!==undefined&&typeof e==='object'&&e.s===SIG; }

// ===== Make interpreted function =====
function makeFunc(name, params, bodyNode, closureEnv) {
  var fn = function() {
    var localEnv = new Env(closureEnv);
    localEnv.def('this', this);
    var argsArr = [];
    for (var i = 0; i < arguments.length; i++) argsArr.push(arguments[i]);
    localEnv.def('arguments', argsArr);
    for (var i = 0; i < params.length; i++) {
      localEnv.def(params[i], i < argsArr.length ? argsArr[i] : undefined);
    }
    try { evalBody(bodyNode.body, localEnv); }
    catch(e) { if (e instanceof RetSig) return e.v; throw e; }
    return undefined;
  };
  if (name) {
    try { Object.defineProperty(fn, 'name', {value:name,configurable:true}); } catch(e) {}
  }
  fn.prototype = {};
  return fn;
}

// ===== Evaluator =====
function evalBody(body, env) {
  for (var i = 0; i < body.length; i++) {
    if (body[i].type === 'FuncDecl') {
      env.def(body[i].name, makeFunc(body[i].name, body[i].params, body[i].body, env));
    }
  }
  for (var i = 0; i < body.length; i++) evalNode(body[i], env);
}

function evalNode(node, env) {
  var tp = node.type;
  if (tp==='Prog'||tp==='Block') { evalBody(node.body, tp==='Block'?new Env(env):env); return; }
  if (tp==='Empty') return;
  if (tp==='ExprStmt') { evalExpr(node.expr, env); return; }
  if (tp==='Var') {
    for(var i=0;i<node.decls.length;i++) { var d=node.decls[i]; env.def(d.name, d.init?evalExpr(d.init,env):undefined); }
    return;
  }
  if (tp==='FuncDecl') { env.def(node.name, makeFunc(node.name, node.params, node.body, env)); return; }
  if (tp==='Return') { throw new RetSig(node.arg ? evalExpr(node.arg,env) : undefined); }
  if (tp==='If') { if(evalExpr(node.test,env)) evalNode(node.cons,env); else if(node.alt) evalNode(node.alt,env); return; }
  if (tp==='While') {
    while(evalExpr(node.test,env)) { try{evalNode(node.body,env);}catch(e){if(e instanceof ContSig&&!e.l)continue;if(e instanceof BrkSig&&!e.l)break;throw e;} }
    return;
  }
  if (tp==='DoWhile') {
    do { try{evalNode(node.body,env);}catch(e){if(e instanceof ContSig&&!e.l)continue;if(e instanceof BrkSig&&!e.l)break;throw e;} } while(evalExpr(node.test,env));
    return;
  }
  if (tp==='For') {
    var fe=new Env(env);
    if(node.init) { if(node.init.type==='Var') evalNode(node.init,fe); else evalExpr(node.init,fe); }
    while(node.test?evalExpr(node.test,fe):true) {
      try{evalNode(node.body,fe);}catch(e){if(e instanceof ContSig&&!e.l){if(node.update)evalExpr(node.update,fe);continue;}if(e instanceof BrkSig&&!e.l)break;throw e;}
      if(node.update)evalExpr(node.update,fe);
    }
    return;
  }
  if (tp==='ForIn') {
    var obj=evalExpr(node.obj,env);
    for(var key in obj) {
      if(node.kind) { var fe2=new Env(env); fe2.def(node.name,key); try{evalNode(node.body,fe2);}catch(e){if(e instanceof ContSig&&!e.l)continue;if(e instanceof BrkSig&&!e.l)break;throw e;} }
      else { env.set(node.name,key); try{evalNode(node.body,env);}catch(e){if(e instanceof ContSig&&!e.l)continue;if(e instanceof BrkSig&&!e.l)break;throw e;} }
    }
    return;
  }
  if (tp==='ForOf') {
    var iter=evalExpr(node.iter,env);
    for(var idx=0;idx<iter.length;idx++) {
      if(node.kind) { var fe3=new Env(env); fe3.def(node.name,iter[idx]); try{evalNode(node.body,fe3);}catch(e){if(e instanceof ContSig&&!e.l)continue;if(e instanceof BrkSig&&!e.l)break;throw e;} }
      else { env.set(node.name,iter[idx]); try{evalNode(node.body,env);}catch(e){if(e instanceof ContSig&&!e.l)continue;if(e instanceof BrkSig&&!e.l)break;throw e;} }
    }
    return;
  }
  if (tp==='Break') throw new BrkSig(node.label);
  if (tp==='Cont') throw new ContSig(node.label);
  if (tp==='Switch') {
    var dv=evalExpr(node.disc,env); var matched=false;
    for(var i=0;i<node.cases.length;i++) {
      var cs=node.cases[i];
      if(!matched&&cs.test!==null&&evalExpr(cs.test,env)===dv) matched=true;
      if(!matched&&cs.test===null) matched=true;
      if(matched) { try{for(var k=0;k<cs.body.length;k++)evalNode(cs.body[k],env);}catch(e){if(e instanceof BrkSig&&!e.l)return;throw e;} }
    }
    return;
  }
  if (tp==='Throw') throw evalExpr(node.arg,env);
  if (tp==='Try') {
    var caught=false;
    try { evalNode(node.block,env); }
    catch(e) {
      if(isSig(e)) { if(node.fin) evalNode(node.fin,env); throw e; }
      caught=true;
      if(node.handler) { var ce=new Env(env); if(node.handler.param) ce.def(node.handler.param,e); try{evalNode(node.handler.body,ce);}catch(e2){if(node.fin)evalNode(node.fin,env);throw e2;} }
    }
    if(node.fin) evalNode(node.fin,env);
    return;
  }
  if (tp==='Label') {
    try{evalNode(node.body,env);}catch(e){if(e instanceof BrkSig&&e.l===node.label)return;if(e instanceof ContSig&&e.l===node.label)return;throw e;}
    return;
  }
  throw new Error('Unknown node: '+tp);
}

function evalExpr(node, env) {
  var tp=node.type;
  if(tp==='Num'||tp==='Str'||tp==='Bool') return node.value;
  if(tp==='Lit') return node.value;
  if(tp==='This') { try{return env.get('this');}catch(e){return undefined;} }
  if(tp==='Id') { return env.get(node.name); }
  if(tp==='Array') {
    var arr=[]; for(var i=0;i<node.elems.length;i++) arr.push(node.elems[i]?evalExpr(node.elems[i],env):undefined);
    return arr;
  }
  if(tp==='Object') {
    var obj={}; for(var i=0;i<node.props.length;i++) {
      var p=node.props[i]; var k=p.computed?evalExpr(p.key,env):p.key;
      obj[k]=evalExpr(p.value,env);
    }
    return obj;
  }
  if(tp==='FuncExpr') {
    var fn=makeFunc(node.name,node.params,node.body,env);
    if(node.name) { var fnEnv=new Env(env); fnEnv.def(node.name,fn); fn=makeFunc(node.name,node.params,node.body,fnEnv); }
    return fn;
  }
  if(tp==='Assign') {
    var val=evalExpr(node.right,env);
    if(node.op!=='=') {
      var cur=evalLVal(node.left,env);
      if(node.op==='+=') val=cur+val; else if(node.op==='-=') val=cur-val;
      else if(node.op==='*=') val=cur*val; else if(node.op==='/=') val=cur/val;
      else if(node.op==='%=') val=cur%val; else if(node.op==='<<=') val=cur<<val;
      else if(node.op==='>>=') val=cur>>val; else if(node.op==='>>>=') val=cur>>>val;
      else if(node.op==='&=') val=cur&val; else if(node.op==='|=') val=cur|val;
      else if(node.op==='^=') val=cur^val; else if(node.op==='**=') val=Math.pow(cur,val);
    }
    setLVal(node.left,env,val); return val;
  }
  if(tp==='Binary') {
    var l=evalExpr(node.left,env), r=evalExpr(node.right,env);
    if(node.op==='+') return l+r; if(node.op==='-') return l-r;
    if(node.op==='*') return l*r; if(node.op==='/') return l/r; if(node.op==='%') return l%r;
    if(node.op==='**') return Math.pow(l,r);
    if(node.op==='==') return l==r; if(node.op==='!=') return l!=r;
    if(node.op==='===') return l===r; if(node.op==='!==') return l!==r;
    if(node.op==='<') return l<r; if(node.op==='>') return l>r;
    if(node.op==='<=') return l<=r; if(node.op==='>=') return l>=r;
    if(node.op==='<<') return l<<r; if(node.op==='>>') return l>>r; if(node.op==='>>>') return l>>>r;
    if(node.op==='&') return l&r; if(node.op==='|') return l|r; if(node.op==='^') return l^r;
    if(node.op==='instanceof') return l instanceof r;
    if(node.op==='in') return l in r;
    throw new Error('Unknown binary op: '+node.op);
  }
  if(tp==='Logical') {
    if(node.op==='&&') return evalExpr(node.left,env)&&evalExpr(node.right,env);
    if(node.op==='||') return evalExpr(node.left,env)||evalExpr(node.right,env);
  }
  if(tp==='Unary') {
    if(node.op==='typeof') {
      if(node.arg.type==='Id') { try{return typeof env.get(node.arg.name);}catch(e){return 'undefined';} }
      return typeof evalExpr(node.arg,env);
    }
    var a=evalExpr(node.arg,env);
    if(node.op==='!') return !a; if(node.op==='-') return -a;
    if(node.op==='+') return +a; if(node.op==='~') return ~a;
    if(node.op==='void') return undefined;
    if(node.op==='delete') {
      if(node.arg.type==='Member') { var o=evalExpr(node.arg.obj,env); var k=node.arg.computed?evalExpr(node.arg.prop,env):node.arg.prop; delete o[k]; return true; }
      return true;
    }
  }
  if(tp==='Update') {
    var cur=evalLVal(node.arg,env);
    var nv=node.op==='++'?cur+1:cur-1;
    setLVal(node.arg,env,nv);
    return node.prefix?nv:cur;
  }
  if(tp==='Cond') { return evalExpr(node.test,env)?evalExpr(node.cons,env):evalExpr(node.alt,env); }
  if(tp==='Seq') { evalExpr(node.left,env); return evalExpr(node.right,env); }
  if(tp==='Call') {
    var args=[]; for(var i=0;i<node.args.length;i++) args.push(evalExpr(node.args[i],env));
    if(node.callee.type==='Member') {
      var obj=evalExpr(node.callee.obj,env);
      var prop=node.callee.computed?evalExpr(node.callee.prop,env):node.callee.prop;
      var fn=obj[prop];
      if(typeof fn!=='function') throw new TypeError(prop+' is not a function');
      return fn.apply(obj,args);
    }
    var fn=evalExpr(node.callee,env);
    if(typeof fn!=='function') throw new TypeError('Not a function');
    return fn.apply(undefined,args);
  }
  if(tp==='New') {
    var ctor=evalExpr(node.callee,env);
    var args=[]; for(var i=0;i<node.args.length;i++) args.push(evalExpr(node.args[i],env));
    if(typeof ctor!=='function') throw new TypeError('Not a constructor');
    var bound=Function.prototype.bind.apply(ctor,[null].concat(args));
    return new bound();
  }
  if(tp==='Member') {
    var obj=evalExpr(node.obj,env);
    var prop=node.computed?evalExpr(node.prop,env):node.prop;
    return obj[prop];
  }
  throw new Error('Unknown expr: '+tp);
}

function evalLVal(node,env) {
  if(node.type==='Id') return env.get(node.name);
  if(node.type==='Member') { var o=evalExpr(node.obj,env); var k=node.computed?evalExpr(node.prop,env):node.prop; return o[k]; }
  throw new Error('Invalid lvalue');
}

function setLVal(node,env,val) {
  if(node.type==='Id') { if(env.has(node.name)) env.set(node.name,val); else env.def(node.name,val); return; }
  if(node.type==='Member') { var o=evalExpr(node.obj,env); var k=node.computed?evalExpr(node.prop,env):node.prop; o[k]=val; return; }
  throw new Error('Invalid lvalue');
}

// ===== Global environment =====
function makeGlobal(argv) {
  var env = new Env(null);
  env.def('undefined', undefined);
  env.def('null', null);
  env.def('true', true);
  env.def('false', false);
  env.def('NaN', NaN);
  env.def('Infinity', Infinity);
  env.def('console', {
    log: function() { var a=[]; for(var i=0;i<arguments.length;i++) a.push(arguments[i]); console.log.apply(console,a); },
    error: function() { var a=[]; for(var i=0;i<arguments.length;i++) a.push(arguments[i]); console.error.apply(console,a); },
    warn: function() { var a=[]; for(var i=0;i<arguments.length;i++) a.push(arguments[i]); console.warn.apply(console,a); }
  });
  env.def('process', { argv: argv, exit: function(code) { process.exit(code); }, stdout: process.stdout, stderr: process.stderr });
  env.def('require', function(name) {
    if(name==='fs') return fs;
    if(name==='path') return require('path');
    throw new Error('Cannot find module: '+name);
  });
  env.def('parseInt', parseInt);
  env.def('parseFloat', parseFloat);
  env.def('isNaN', isNaN);
  env.def('isFinite', isFinite);
  env.def('Math', Math);
  env.def('JSON', JSON);
  env.def('Object', Object);
  env.def('Array', Array);
  env.def('String', String);
  env.def('Number', Number);
  env.def('Boolean', Boolean);
  env.def('Function', Function);
  env.def('RegExp', RegExp);
  env.def('Date', Date);
  env.def('Error', Error);
  env.def('TypeError', TypeError);
  env.def('RangeError', RangeError);
  env.def('ReferenceError', ReferenceError);
  env.def('SyntaxError', SyntaxError);
  env.def('URIError', URIError);
  env.def('EvalError', EvalError);
  env.def('encodeURIComponent', encodeURIComponent);
  env.def('decodeURIComponent', decodeURIComponent);
  env.def('encodeURI', encodeURI);
  env.def('decodeURI', decodeURI);
  env.def('setTimeout', setTimeout);
  env.def('clearTimeout', clearTimeout);
  env.def('setInterval', setInterval);
  env.def('clearInterval', clearInterval);
  return env;
}

// ===== Run =====
function run(src, argv) {
  var tokens = tokenize(src);
  var parser = new Parser(tokens);
  var ast = parser.parseProgram();
  var env = makeGlobal(argv);
  evalBody(ast.body, env);
}

// ===== Main =====
var args = process.argv.slice(2);
if (args.length === 0) {
  console.error('Usage: node js0i.js <script> [args...]');
  process.exit(1);
}
var scriptFile = args[0];
var restArgs = args.slice(1);
var source = fs.readFileSync(scriptFile, 'utf8');
run(source, ['node'].concat(args));
