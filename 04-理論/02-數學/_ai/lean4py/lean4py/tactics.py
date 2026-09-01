from lean4py.logic import Prop, ProofStep, Theorem, _PropBinOp, _PropUnOp
from typing import Optional, List, Union, Dict

class Tactic:
    def __init__(self, name: str, *args):
        self.name = name
        self.args = args

    def __repr__(self):
        if self.args:
            args_str = ", ".join(repr(a) for a in self.args)
            return f"tactic.{self.name}({args_str})"
        return f"tactic.{self.name}"

def tactic_rfl() -> Tactic:
    return Tactic("rfl")

def tactic_exact(p: Prop) -> Tactic:
    return Tactic("exact", p)

def tactic_apply(h: str) -> Tactic:
    return Tactic("apply", h)

def tactic_simp() -> Tactic:
    return Tactic("simp")

def tactic_assume(name: str) -> Tactic:
    return Tactic("assume", name)

def tactic_have(name: str) -> Tactic:
    return Tactic("have", name)

def intros(names: Union[str, List[str]]) -> ProofStep:
    if isinstance(names, str):
        names = [names]
    return ProofStep("intros", names)

def intros_tactic(names: Union[str, List[str]]) -> Tactic:
    if isinstance(names, str):
        names = [names]
    return Tactic("intros", names)

def by_contra(name: str, prop: Prop) -> ProofStep:
    return ProofStep("by_contra", name, prop)

def by_contra_tactic(name: str, prop: Prop) -> Tactic:
    return Tactic("by_contra", name, prop)

def cases(h: str, cases_list: List[Prop]) -> ProofStep:
    return ProofStep("cases", h, cases_list)

def cases_tactic(h: str, cases_list: List[Prop]) -> Tactic:
    return Tactic("cases", h, cases_list)

def induction(var: str, base: List[ProofStep], ind: List[ProofStep]) -> ProofStep:
    return ProofStep("induction", var, base, ind)

def induction_tactic(var: str, base: List[Tactic], ind: List[Tactic]) -> Tactic:
    return Tactic("induction", var, base, ind)

def rewrite(eq: str, sym: bool = False) -> ProofStep:
    return ProofStep("rewrite", eq, sym)

def rewrite_tactic(eq: str, sym: bool = False) -> Tactic:
    return Tactic("rewrite", eq, sym)

def split() -> ProofStep:
    return ProofStep("split")

def split_tactic() -> Tactic:
    return Tactic("split")

def left() -> ProofStep:
    return ProofStep("left")

def left_tactic() -> Tactic:
    return Tactic("left")

def right() -> ProofStep:
    return ProofStep("right")

def right_tactic() -> Tactic:
    return Tactic("right")

def use(witness) -> ProofStep:
    return ProofStep("use", witness)

def use_tactic(witness) -> Tactic:
    return Tactic("use", witness)

def show(prop: Prop) -> ProofStep:
    return ProofStep("show", prop)

def show_tactic(prop: Prop) -> Tactic:
    return Tactic("show", prop)

def by(tactics_list: List) -> ProofStep:
    return ProofStep("by", tactics_list)

def by_tactic(tactics_list: List[Tactic]) -> Tactic:
    return Tactic("by", tactics_list)

def sorry() -> ProofStep:
    return ProofStep("sorry")

def sorry_tactic() -> Tactic:
    return Tactic("sorry")

def calc(tactics_list: List) -> ProofStep:
    return ProofStep("calc", tactics_list)

def calc_tactic(tactics_list: List[Tactic]) -> Tactic:
    return Tactic("calc", tactics_list)

def intro(name: str) -> ProofStep:
    return ProofStep("intro", name)

def intro_tactic(name: str) -> Tactic:
    return Tactic("intro", name)

def apply_tactic(h: str) -> Tactic:
    return Tactic("apply", h)

class TacticProof:
    def __init__(self, steps: list = None):
        self.steps = steps or []

    def add(self, step):
        self.steps.append(step)

    def __repr__(self):
        return "\n".join(f" {s}" for s in self.steps)

class TacticState:
    def __init__(self, goals: List = None, hypotheses: Dict = None):
        self.goals = goals or []
        self.hypotheses = hypotheses or {}

    def add_hypothesis(self, name: str, prop: Prop):
        self.hypotheses[name] = prop

    def get_hypothesis(self, name: str) -> Optional[Prop]:
        return self.hypotheses.get(name)

    def pop_goal(self):
        if self.goals:
            return self.goals.pop(0)
        return None

    def __repr__(self):
        return f"TacticState(goals={self.goals}, hypotheses={list(self.hypotheses.keys())})"