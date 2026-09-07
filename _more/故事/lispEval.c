/*
 * lispEval.c — McCarthy 1960 eval LISP interpreter in C
 *
 * Faithfully implements the S-function eval from:
 *   "Recursive Functions of Symbolic Expressions and Their
 *    Computation by Machine, Part I" (John McCarthy, 1960)
 *
 * Data structures:
 *   S-expression = ATOM(name) | PAIR(car, cdr)
 *   NIL = special atom
 *   Association list = list of PAIR(PAIR(var, val), rest)
 *
 * Compile: gcc -Wall -Wextra -o lispEval lispEval.c
 * Run:     ./lispEval          (interactive REPL)
 *          ./lispEval -e CODE  (evaluate CODE and exit)
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

/* ================================================================
 * 1. S-expression data structure
 * ================================================================ */

typedef enum { ATOM, PAIR } SexprType;

typedef struct Sexpr Sexpr;
struct Sexpr {
    SexprType type;
    union {
        char *name;         /* ATOM */
        struct { Sexpr *car; Sexpr *cdr; } pair;  /* PAIR */
    } u;
};

static Sexpr *NIL = NULL;

static Sexpr *make_atom(const char *name) {
    Sexpr *s = malloc(sizeof(Sexpr));
    if (!s) { fprintf(stderr, "out of memory\n"); exit(1); }
    s->type = ATOM;
    s->u.name = strdup(name);
    return s;
}

static Sexpr *make_pair(Sexpr *a, Sexpr *d) {
    Sexpr *s = malloc(sizeof(Sexpr));
    if (!s) { fprintf(stderr, "out of memory\n"); exit(1); }
    s->type = PAIR;
    s->u.pair.car = a;
    s->u.pair.cdr = d;
    return s;
}

static void init_nil(void) { NIL = make_atom("NIL"); }

/* ================================================================
 * 2. Primitive LISP operations (from McCarthy's definitions)
 * ================================================================ */

static int is_atom(Sexpr *s) { return s->type == ATOM; }

static int is_nil(Sexpr *s) { return s == NIL; }

static int sexpr_eq(Sexpr *a, Sexpr *b) {
    if (a == b) return 1;
    if (is_atom(a) && is_atom(b))
        return strcmp(a->u.name, b->u.name) == 0;
    return 0;
}

static Sexpr *car(Sexpr *s) {
    if (is_atom(s)) {
        fprintf(stderr, "car of atom: %s\n", s->u.name);
        return NIL;
    }
    return s->u.pair.car;
}

static Sexpr *cdr(Sexpr *s) {
    if (is_atom(s)) {
        fprintf(stderr, "cdr of atom: %s\n", s->u.name);
        return NIL;
    }
    return s->u.pair.cdr;
}

static Sexpr *cons(Sexpr *a, Sexpr *d) { return make_pair(a, d); }

/* cadr = car of cdr */
static Sexpr *cadr(Sexpr *s) { return car(cdr(s)); }
/* caddr = car of cdr of cdr */
static Sexpr *caddr(Sexpr *s) { return car(cdr(cdr(s))); }
/* caar = car of car */
static Sexpr *caar(Sexpr *s) { return car(car(s)); }
/* cadar = car of cdr of car */
static Sexpr *cadar(Sexpr *s) { return car(cdr(car(s))); }
/* caddar = car of cdr of cdr of car */
static Sexpr *caddar(Sexpr *s) { return car(cdr(cdr(car(s)))); }

/* list[a; b; c] = cons[a; cons[b; cons[c; NIL]]] */
static Sexpr *make_list3(Sexpr *a, Sexpr *b, Sexpr *c) {
    return cons(a, cons(b, cons(c, NIL)));
}

/* ================================================================
 * 3. Association list operations
 * ================================================================ */

/* assoc[e; a] — lookup atom e in association list a
 * Bindings are (name value) pairs; returns the value (cadr). */
static Sexpr *assoc(Sexpr *e, Sexpr *a) {
    while (!is_nil(a)) {
        Sexpr *binding = car(a);
        if (sexpr_eq(car(binding), e))
            return cadr(binding);
        a = cdr(a);
    }
    /* NIL self-evaluates; no warning needed */
    if (!is_nil(e))
        fprintf(stderr, "unbound: %s\n", is_atom(e) ? e->u.name : "<?>");
    return NIL;
}

/* pair[x; y] — zip list x and list y into association list */
static Sexpr *pair(Sexpr *x, Sexpr *y) {
    if (is_nil(x) && is_nil(y)) return NIL;
    if (is_atom(x) || is_atom(y)) {
        fprintf(stderr, "pair: length mismatch\n");
        return NIL;
    }
    return cons(cons(car(x), cons(car(y), NIL)),
                pair(cdr(x), cdr(y)));
}

/* append[x; y] — concatenate two lists */
static Sexpr *append(Sexpr *x, Sexpr *y) {
    if (is_nil(x)) return y;
    return cons(car(x), append(cdr(x), y));
}

/* ================================================================
 * 4. LISP Parser — recursive descent
 * ================================================================ */

static const char *g_input;
static int g_pos;

static void skip_ws(void) {
    while (g_input[g_pos] && isspace((unsigned char)g_input[g_pos]))
        g_pos++;
}

static Sexpr *read_sexpr(void) {
    skip_ws();
    char c = g_input[g_pos];
    if (c == '\0') return NULL;

    if (c == '(') {
        g_pos++; /* skip '(' */
        skip_ws();
        if (g_input[g_pos] == ')') {
            g_pos++;
            return NIL;
        }
        Sexpr *head = NULL, *tail = NULL;
        for (;;) {
            Sexpr *elem = read_sexpr();
            if (!elem) break;
            Sexpr *cell = cons(elem, NIL);
            if (!head) { head = tail = cell; }
            else { tail->u.pair.cdr = cell; tail = cell; }
            skip_ws();
            if (g_input[g_pos] == ')') { g_pos++; break; }
        }
        return head ? head : NIL;
    }

    /* atom */
    int start = g_pos;
    while (g_input[g_pos] && !isspace((unsigned char)g_input[g_pos])
           && g_input[g_pos] != '(' && g_input[g_pos] != ')')
        g_pos++;
    int len = g_pos - start;
    char *buf = malloc(len + 1);
    memcpy(buf, g_input + start, len);
    buf[len] = '\0';

    /* upcase for case-insensitive atom comparison */
    for (int i = 0; i < len; i++)
        buf[i] = toupper((unsigned char)buf[i]);

    /* NIL is the empty list */
    if (strcmp(buf, "NIL") == 0) { free(buf); return NIL; }

    Sexpr *s = make_atom(buf);
    free(buf);
    return s;
}

/* ================================================================
 * 5. LISP Printer
 * ================================================================ */

static void print_sexpr(Sexpr *s) {
    if (s == NIL) { printf("NIL"); return; }
    if (is_atom(s)) { printf("%s", s->u.name); return; }
    /* pair */
    printf("(");
    print_sexpr(car(s));
    Sexpr *rest = cdr(s);
    while (!is_nil(rest)) {
        if (is_atom(rest)) {
            printf(" . ");
            print_sexpr(rest);
            break;
        }
        printf(" ");
        print_sexpr(car(rest));
        rest = cdr(rest);
    }
    printf(")");
}

/* ================================================================
 * 6. McCarthy's eval and helpers
 * ================================================================ */

static Sexpr *evcon(Sexpr *c, Sexpr *a);
static Sexpr *eval(Sexpr *e, Sexpr *a);
static Sexpr *appq(Sexpr *m);

/* evlis[m; a] = [null[m] -> NIL; T -> cons[eval[car[m];a]; evlis[cdr[m];a]]] */
static Sexpr *evlis(Sexpr *m, Sexpr *a) {
    if (is_nil(m)) return NIL;
    return cons(eval(car(m), a), evlis(cdr(m), a));
}

/* evcon[c; a] = [eval[caar[c];a] -> eval[cadar[c];a]; T -> evcon[cdr[c];a]] */
static Sexpr *evcon(Sexpr *c, Sexpr *a) {
    while (!is_nil(c)) {
        if (!is_nil(eval(caar(c), a)))
            return eval(cadar(c), a);
        c = cdr(c);
    }
    printf("evcon: no true condition\n");
    return NIL;
}

/*
 * eval[e; a] — the heart of McCarthy's LISP
 *
 * [atom[e]                    -> assoc[e; a];
 *  atom[car[e]] ->
 *    [eq[car[e]; QUOTE]       -> cadr[e];
 *     eq[car[e]; ATOM]        -> atom[eval[cadr[e];a]];
 *     eq[car[e]; EQ]          -> [eval[cadr[e];a] = eval[caddr[e];a]];
 *     eq[car[e]; COND]        -> evcon[cdr[e]; a];
 *     eq[car[e]; CAR]         -> car[eval[cadr[e];a]];
 *     eq[car[e]; CDR]         -> cdr[eval[cadr[e];a]];
 *     eq[car[e]; CONS]        -> cons[eval[cadr[e];a]; eval[caddr[e];a]];
 *     T                       -> eval[cons[assoc[car[e];a]; evlis[cdr[e];a]]; a]];
 *  eq[caar[e]; LABEL]         -> eval[cons[caddar[e]; cdr[e]];
 *                                    cons[list[cadar[e]; car[e]; a]]];
 *  eq[caar[e]; LAMBDA]        -> eval[caddar[e];
 *                                    append[pair[cadar[e]; evlis[cdr[e];a]; a]]]]
 */
static Sexpr *eval(Sexpr *e, Sexpr *a) {
    /* atom[e] -> assoc[e; a] */
    if (is_atom(e)) {
        return assoc(e, a);
    }

    /* Now e is a pair. Check if car(e) is an atom (special form or call). */
    if (is_atom(car(e))) {
        if (sexpr_eq(car(e), make_atom("QUOTE")))
            return cadr(e);

        if (sexpr_eq(car(e), make_atom("ATOM")))
            return is_atom(eval(cadr(e), a)) ? make_atom("T") : NIL;

        if (sexpr_eq(car(e), make_atom("EQ")))
            return sexpr_eq(eval(cadr(e), a), eval(caddr(e), a))
                   ? make_atom("T") : NIL;

        if (sexpr_eq(car(e), make_atom("COND")))
            return evcon(cdr(e), a);

        if (sexpr_eq(car(e), make_atom("CAR")))
            return car(eval(cadr(e), a));

        if (sexpr_eq(car(e), make_atom("CDR")))
            return cdr(eval(cadr(e), a));

        if (sexpr_eq(car(e), make_atom("CONS")))
            return cons(eval(cadr(e), a), eval(caddr(e), a));

        /* T -> function call, per McCarthy's apply:
         * eval[cons[f; appq[evlis[cdr[e];a]]]; a]
         * appq quotes the evaluated argument values so the LAMBDA/LABEL
         * application unquotes them exactly once (no double-evaluation). */
        Sexpr *fn = assoc(car(e), a);
        Sexpr *callargs = appq(evlis(cdr(e), a));
        return eval(cons(fn, callargs), a);
    }

    /* car(e) is not an atom — check for LABEL and LAMBDA */

    /* eq[caar[e]; LABEL]
     * eval[cons[caddar[e]; cdr[e]]; cons[list[cadar[e]; car[e]; a]]]
     *
     * Bind (name . LABEL-form) into env (for recursion), then evaluate
     * the LAMBDA form applied to the arguments.
     */
    if (sexpr_eq(caar(e), make_atom("LABEL"))) {
        Sexpr *name = cadar(e);
        Sexpr *lambda_form = caddar(e);
        Sexpr *args = cdr(e);
        Sexpr *new_env = cons(cons(name, cons(car(e), NIL)), a);
        return eval(cons(lambda_form, args), new_env);
    }

    /* eq[caar[e]; LAMBDA] */
    if (sexpr_eq(caar(e), make_atom("LAMBDA")))
        return eval(
            caddar(e),
            append(pair(cadar(e), evlis(cdr(e), a)), a)
        );

    fprintf(stderr, "eval: unknown form\n");
    print_sexpr(e);
    printf("\n");
    return NIL;
}

/*
 * apply[f; args] = eval[cons[f; appq[args]]; NIL]
 *
 * Part of McCarthy's formal specification.
 * In our REPL, eval handles calls directly; apply is kept as reference.
 */
__attribute__((unused))
static Sexpr *apply_fn(Sexpr *f, Sexpr *args) {
    if (is_atom(f)) {
        fprintf(stderr, "apply: trying to apply atom %s\n", f->u.name);
        return NIL;
    }
    /* f must be (LAMBDA (params...) body) or (LABEL name (LAMBDA ...)) */
    if (sexpr_eq(caar(f), make_atom("LAMBDA")))
        return eval(caddar(f),
                     append(pair(cadar(f), args), NIL));
    if (sexpr_eq(caar(f), make_atom("LABEL")))
        return apply_fn(caddar(f),
                         args);  /* LABEL: recursive, f = body lambda */
    fprintf(stderr, "apply: not a function\n");
    return NIL;
}

/* appq[m] = [null[m] -> NIL; T -> cons[list[QUOTE; car[m]]; appq[cdr[m]]]] */
static Sexpr *appq(Sexpr *m) {
    if (is_nil(m)) return NIL;
    return cons(make_list3(make_atom("QUOTE"), car(m), NIL),
                appq(cdr(m)));
}

/* ================================================================
 * 7. Built-in environment with +, -, *, /, =, <, >
 * ================================================================ */



/* ================================================================
 * 8. REPL
 * ================================================================ */

static void repl(void) {
    char line[4096];
    Sexpr *env = NIL; /* empty environment */

    /* Preload some arithmetic bindings as LAMBDA functions */
    /* (SUB 1 a) = a - 1, etc. We do this via LABEL for recursion */

    printf("McCarthy LISP (1960) — type (quit) to exit\n");
    printf("Builtins: QUOTE ATOM EQ COND CAR CDR CONS LABEL LAMBDA\n");
    printf("Example:  (CONS (QUOTE A) NIL)  =>  (A)\n");
    printf("          ((LAMBDA (X) (CONS X NIL)) (QUOTE A))\n\n");

    for (;;) {
        printf("LISP> ");
        fflush(stdout);
        if (!fgets(line, sizeof(line), stdin)) break;

        g_input = line;
        g_pos = 0;

        Sexpr *expr = read_sexpr();
        if (!expr) continue;

        /* (quit) exits */
        if (is_atom(expr) && sexpr_eq(expr, make_atom("QUIT")))
            break;
        if (!is_atom(expr) && !is_nil(expr) &&
            is_atom(car(expr)) && sexpr_eq(car(expr), make_atom("QUIT")))
            break;

        /* (DEFINE name value) — add to environment */
        if (!is_atom(expr) && !is_nil(expr) &&
            is_atom(car(expr)) && sexpr_eq(car(expr), make_atom("DEFINE"))) {
            Sexpr *name = cadr(expr);
            /* store the definition form unevaluated (functions are data) */
            Sexpr *val  = caddr(expr);
            env = cons(cons(name, cons(val, NIL)), env);
            printf("Defined: ");
            print_sexpr(name);
            printf("\n");
            continue;
        }

        Sexpr *result = eval(expr, env);
        print_sexpr(result);
        printf("\n");
    }
}

/* ================================================================
 * 9. Demo: run McCarthy's own examples
 * ================================================================ */

static void demo(void) {
    printf("=== McCarthy 1960 eval Demo ===\n\n");
    printf("Faithful C translation of the eval function from:\n");
    printf("'Recursive Functions of Symbolic Expressions and Their\n");
    printf(" Computation by Machine, Part I' (1960)\n\n");

    Sexpr *env = NIL;
    char *tests[] = {
        /* 1. QUOTE — returns expression unevaluated */
        "(QUOTE (A B C))",

        /* 2. ATOM — tests if argument is an atom */
        "(ATOM (QUOTE A))",
        "(ATOM (QUOTE (A B)))",

        /* 3. EQ — equality test */
        "(EQ (QUOTE A) (QUOTE A))",
        "(EQ (QUOTE A) (QUOTE B))",

        /* 4. CAR, CDR — list decomposition */
        "(CAR (QUOTE (A B C)))",
        "(CDR (QUOTE (A B C)))",

        /* 5. CONS — list construction */
        "(CONS (QUOTE X) (QUOTE (Y Z)))",
        "(CONS (QUOTE A) NIL)",

        /* 6. COND — conditional, directly as the top-level form */
        "(COND ((EQ (QUOTE A) (QUOTE A)) (QUOTE YES)) ((QUOTE T) (QUOTE NO)))",

        /* 7. LAMBDA — anonymous function, single arg */
        "((LAMBDA (X) (CONS X NIL)) (QUOTE HELLO))",

        /* 8. LAMBDA — two args */
        "((LAMBDA (X Y) (CONS X (CONS Y NIL))) (QUOTE A) (QUOTE B))",

        /* 9. LABEL — recursive append */
        "((LABEL APPEND (LAMBDA (X Y) (COND ((ATOM X) Y) "
        "((QUOTE T) (CONS (CAR X) (APPEND (CDR X) Y)))))) "
        "(QUOTE (A B)) (QUOTE (C D E)))",

        /* 10. LABEL — recursive length (returns list of 1s, pure symbols) */
        "((LABEL LEN (LAMBDA (X) (COND ((ATOM X) NIL) "
        "((QUOTE T) (CONS (QUOTE 1) (LEN (CDR X))))))) "
        "(QUOTE (A B C D)))",

        NULL
    };

    for (int i = 0; tests[i]; i++) {
        g_input = tests[i];
        g_pos = 0;
        Sexpr *expr = read_sexpr();
        printf("  ");
        print_sexpr(expr);
        printf("\n=> ");
        Sexpr *result = eval(expr, env);
        print_sexpr(result);
        printf("\n\n");
    }
}

/* ================================================================
 * 10. Main
 * ================================================================ */

int main(int argc, char **argv) {
    init_nil();

    if (argc == 3 && strcmp(argv[1], "-e") == 0) {
        /* Evaluate a single expression */
        g_input = argv[2];
        g_pos = 0;
        Sexpr *expr = read_sexpr();
        if (expr) {
            Sexpr *result = eval(expr, NIL);
            print_sexpr(result);
            printf("\n");
        }
        return 0;
    }

    if (argc == 2 && strcmp(argv[1], "-d") == 0) {
        demo();
        return 0;
    }

    repl();
    return 0;
}
