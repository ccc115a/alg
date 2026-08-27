#!/usr/bin/env python3
"""Lambda Calculus Python Implementation"""

TRUE = lambda t: lambda f: t
FALSE = lambda t: lambda f: f
AND = lambda p: lambda q: p(q)(p)
OR = lambda p: lambda q: p(p)(q)
NOT = lambda p: lambda a: lambda b: p(b)(a)
IF = lambda p: lambda a: lambda b: p(a)(b)

def church_to_bool(b): return b(True)(False)

ZERO = lambda f: lambda x: x
ONE = lambda f: lambda x: f(x)
TWO = lambda f: lambda x: f(f(x))
THREE = lambda f: lambda x: f(f(f(x)))
FOUR = lambda f: lambda x: f(f(f(f(x))))
FIVE = lambda f: lambda x: f(f(f(f(f(x)))))
SIX = lambda f: lambda x: f(f(f(f(f(f(x))))))
SEVEN = lambda f: lambda x: f(f(f(f(f(f(f(x)))))))
EIGHT = lambda f: lambda x: f(f(f(f(f(f(f(f(x))))))))
NINE = lambda f: lambda x: f(f(f(f(f(f(f(f(f(x)))))))))
TEN = lambda f: lambda x: f(f(f(f(f(f(f(f(f(f(x))))))))))

def church_to_int(n): return n(lambda x: x + 1)(0)

def int_to_church(n):
    if n == 0: return ZERO
    result = ZERO
    for _ in range(n): result = SUCC(result)
    return result

SUCC = lambda n: lambda f: lambda x: f(n(f)(x))
PLUS = lambda m: lambda n: lambda f: lambda x: m(f)(n(f)(x))
MULT = lambda m: lambda n: lambda f: m(n(f))
POWER = lambda m: lambda n: n(m)

IS_ZERO = lambda n: n(lambda _: FALSE)(TRUE)
PRED = lambda n: lambda f: lambda x: n(lambda g: lambda h: h(g(f)))(lambda _: x)(lambda a: a)
SUB = lambda m: lambda n: n(PRED)(m)
LEQ = lambda m: lambda n: IS_ZERO(SUB(m)(n))

Y = lambda f: (lambda x: f(lambda v: x(x)(v)))(lambda x: f(lambda v: x(x)(v)))

def test():
    print("Testing Church numbers:")
    for n, name in [(ZERO,"ZERO"),(ONE,"ONE"),(TWO,"TWO"),(THREE,"THREE"),(FOUR,"FOUR"),(FIVE,"FIVE"),(SIX,"SIX"),(SEVEN,"SEVEN"),(EIGHT,"EIGHT"),(NINE,"NINE"),(TEN,"TEN")]:
        print(f"{name} = {church_to_int(n)}")
    print()
    print("Testing operations:")
    print(f"PLUS(TWO, THREE) = {church_to_int(PLUS(TWO)(THREE))}")
    print(f"MULT(TWO, THREE) = {church_to_int(MULT(TWO)(THREE))}")
    print(f"POWER(TWO, THREE) = {church_to_int(POWER(TWO)(THREE))}")
    print()
    print("Testing arithmetic:")
    print(f"PLUS(POWER(TWO)(THREE), MULT(THREE)(THREE)) = {church_to_int(PLUS(POWER(TWO)(THREE))(MULT(THREE)(THREE)))}")
    print(f"SUB(POWER(THREE)(TWO), MULT(TWO)(FOUR)) = {church_to_int(SUB(POWER(THREE)(TWO))(MULT(TWO)(FOUR)))}")
    print()
    print("Testing comparisons:")
    print(f"LEQ(THREE, FOUR) = {church_to_bool(LEQ(THREE)(FOUR))}")
    print(f"LEQ(FOUR, THREE) = {church_to_bool(LEQ(FOUR)(THREE))}")
    print()
    print("Testing factorial:")
    def church_factorial(n):
        if church_to_bool(IS_ZERO(n)):
            return ONE
        return MULT(n)(church_factorial(PRED(n)))
    print(f"factorial(3) = {church_to_int(church_factorial(THREE))}")
    print()
    print("Testing factorial with Y combinator:")
    CBN_Y = lambda f: (lambda x: f(lambda v: x(x)(v)))(lambda x: f(lambda v: x(x)(v)))
    CBN_FACT_STEP = lambda f: lambda n: 1 if n == 0 else n * f(n - 1)
    CBN_FACT = CBN_Y(CBN_FACT_STEP)
    print(f"factorial(3) = {CBN_FACT(3)}")
    print(f"factorial(5) = {CBN_FACT(5)}")

if __name__ == "__main__": test()
