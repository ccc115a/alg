"""代數公理。

不證自明的命題，是建構代數結構的基礎。
"""

from typing import Any, Callable, Set


def closure_axiom(carrier: Set[Any], op: Callable) -> bool:
    """封閉性公理：對 carrier 中所有元素 a, b，op(a, b) 仍在 carrier 中。"""
    for a in carrier:
        for b in carrier:
            if op(a, b) not in carrier:
                return False
    return True


def associativity(carrier: Set[Any], op: Callable) -> bool:
    """結合律公理：對所有 a, b, c，op(op(a, b), c) = op(a, op(b, c))。"""
    for a in carrier:
        for b in carrier:
            for c in carrier:
                if op(op(a, b), c) != op(a, op(b, c)):
                    return False
    return True


def identity_element(carrier: Set[Any], op: Callable, e: Any) -> bool:
    """單位元公理：對所有 a，op(e, a) = a = op(a, e)。"""
    for a in carrier:
        if op(e, a) != a or op(a, e) != a:
            return False
    return True


def inverse_element(carrier: Set[Any], op: Callable, e: Any, inv: Callable) -> bool:
    """逆元公理：對所有 a，op(a, inv(a)) = e = op(inv(a), a)。"""
    for a in carrier:
        if op(a, inv(a)) != e or op(inv(a), a) != e:
            return False
    return True


def commutativity(carrier: Set[Any], op: Callable) -> bool:
    """交換律公理：對所有 a, b，op(a, b) = op(b, a)。"""
    for a in carrier:
        for b in carrier:
            if op(a, b) != op(b, a):
                return False
    return True


def distributivity(carrier: Set[Any], add: Callable, mul: Callable) -> bool:
    """分配律公理：mul(a, add(b, c)) = add(mul(a, b), mul(a, c))。"""
    for a in carrier:
        for b in carrier:
            for c in carrier:
                if mul(a, add(b, c)) != add(mul(a, b), mul(a, c)):
                    return False
    return True


__all__ = [
    "closure_axiom",
    "associativity",
    "identity_element",
    "inverse_element",
    "commutativity",
    "distributivity",
]