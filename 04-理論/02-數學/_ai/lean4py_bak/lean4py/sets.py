from typing import Any, Iterable, Set as _Set


class Set:
    def __init__(self, elems: Iterable[Any] = None):
        self._elems = set(elems) if elems is not None else set()

    def __repr__(self):
        if not self._elems:
            return "∅"
        return "{" + ", ".join(str(e) for e in sorted(self._elems, key=repr)) + "}"

    def __eq__(self, other):
        return isinstance(other, Set) and self._elems == other._elems

    def __hash__(self):
        return hash(frozenset(self._elems))

    def __contains__(self, elem):
        return elem in self._elems

    def __add__(self, other):
        return union(self, other)

    def __mul__(self, other):
        return intersection(self, other)

    def __invert__(self):
        return complement(self)

    def __sub__(self, other):
        return difference(self, other)

    def __le__(self, other):
        return subset(self, other)

    def __lt__(self, other):
        return subset(self, other) and self != other

    def __radd__(self, other):
        return union(other, self)

    def __rmul__(self, other):
        return intersection(other, self)

    def to_set(self):
        return self._elems


def Set_from(elems: Iterable[Any]) -> Set:
    return Set(elems)


def in_(elem: Any, s: Set) -> bool:
    return elem in s._elems


def subset(s1: Set, s2: Set) -> bool:
    return s1._elems <= s2._elems


def union(s1: Set, s2: Set) -> Set:
    return Set(s1._elems | s2._elems)


def intersection(s1: Set, s2: Set) -> Set:
    return Set(s1._elems & s2._elems)


def complement(s: Set) -> Set:
    return Set(s._elems)


def difference(s1: Set, s2: Set) -> Set:
    return Set(s1._elems - s2._elems)


def cartesian(s1: Set, s2: Set) -> Set:
    return Set((a, b) for a in s1._elems for b in s2._elems)


def power_set(s: Set) -> Set:
    if not s._elems:
        return Set([Set()])
    elems = list(s._elems)
    n = len(elems)
    result = set()
    for mask in range(1 << n):
        subset_elems = {elems[i] for i in range(n) if mask & (1 << i)}
        result.add(Set(subset_elems))
    return Set(result)


def empty_set() -> Set:
    return Set()