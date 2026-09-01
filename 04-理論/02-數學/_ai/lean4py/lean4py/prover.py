from itertools import product
from typing import Optional, List, Dict, Any

class _PropBinOp:
    def __init__(self, op: str, left, right):
        self.op = op
        self.left = left
        self.right = right

class _PropUnOp:
    def __init__(self, op: str, operand):
        self.op = op
        self.operand = operand

def _eval_prop(prop, assignment: Dict[str, bool]) -> bool:
    if not hasattr(prop, 'name'):
        return bool(prop)

    name = prop.name

    if hasattr(prop, 'op') and hasattr(prop, 'left') and hasattr(prop, 'right'):
        left_val = _eval_prop(prop.left, assignment)
        right_val = _eval_prop(prop.right, assignment)
        op = prop.op
        if op == '→':
            return (not left_val) or right_val
        elif op == '∧':
            return left_val and right_val
        elif op == '∨':
            return left_val or right_val

    if hasattr(prop, 'op') and hasattr(prop, 'operand'):
        operand_val = _eval_prop(prop.operand, assignment)
        op = prop.op
        if op == '¬':
            return not operand_val

    if name in assignment:
        return assignment[name]
    for key in assignment:
        if f"Prop('{key}')" == name:
            return assignment[key]

    return False

def _extract_var_names(prop) -> List[str]:
    import re
    if not hasattr(prop, 'name'):
        return []
    vars = set()

    def extract(p):
        if hasattr(p, 'left') and hasattr(p, 'right'):
            extract(p.left)
            extract(p.right)
        elif hasattr(p, 'operand'):
            extract(p.operand)
        else:
            if re.match(r"^[a-zA-Z]$", p.name):
                vars.add(p.name)

    extract(prop)
    return sorted(list(vars))

def truth_table_prove(prop) -> bool:
    var_names = _extract_var_names(prop)
    if not var_names:
        try:
            result = bool(prop)
            return result
        except:
            return False

    for assignment in product([False, True], repeat=len(var_names)):
        assign_dict = dict(zip(var_names, assignment))
        if not _eval_prop(prop, assign_dict):
            return False
    return True

def is_valid(prop) -> bool:
    return truth_table_prove(prop)

def is_satisfiable(prop) -> bool:
    var_names = _extract_var_names(prop)
    if not var_names:
        try:
            return bool(prop)
        except:
            return False

    for assignment in product([False, True], repeat=len(var_names)):
        assign_dict = dict(zip(var_names, assignment))
        if _eval_prop(prop, assign_dict):
            return True
    return False

def find_counterexample(prop) -> Optional[Dict[str, bool]]:
    var_names = _extract_var_names(prop)
    if not var_names:
        if not bool(prop):
            return {}
        return None

    for assignment in product([False, True], repeat=len(var_names)):
        assign_dict = dict(zip(var_names, assignment))
        if not _eval_prop(prop, assign_dict):
            return assign_dict
    return None

class TableauNode:
    def __init__(self, label: str, children: Optional[List['TableauNode']] = None):
        self.label = label
        self.children = children or []
        self.closed = False

    def __repr__(self):
        return f"TableauNode({self.label!r})"

class TableauBranch:
    def __init__(self, formulas: List[Any] = None):
        self.formulas = formulas or []
        self.closed = False

    def add(self, formula):
        self.formulas.append(formula)

    def __repr__(self):
        return f"Branch({self.formulas})"

def _negate_formula(prop):
    if hasattr(prop, 'op') and prop.op == '¬':
        return prop.operand
    else:
        from lean4py.logic import not_
        return not_(prop)

def _get_literal_info(prop):
    if hasattr(prop, 'op') and prop.op == '¬':
        inner = prop.operand
        if hasattr(inner, 'op') and inner.op == '¬':
            return ('double_neg', inner.operand)
        return ('negated', inner)
    return ('positive', prop)

def _expand_branch(branch: TableauBranch) -> List[TableauBranch]:
    if branch.closed:
        return [branch]

    unexpanded = [f for f in branch.formulas if not getattr(f, '_expanded', False)]
    if not unexpanded:
        return [branch]

    formula = unexpanded[0]
    formula._expanded = True
    new_branches = []

    if hasattr(formula, 'op'):
        op = formula.op

        if op == '∧':
            new_formulas = [f for f in branch.formulas if f is not formula]
            new_formulas.append(formula.left)
            new_formulas.append(formula.right)
            new_branches.append(TableauBranch(new_formulas))

        elif op == '∨':
            branch1 = TableauBranch([f for f in branch.formulas if f is not formula])
            branch2 = TableauBranch([f for f in branch.formulas if f is not formula])
            branch1.add(formula.left)
            branch2.add(formula.right)
            new_branches.extend([branch1, branch2])

        elif op == '→':
            branch1 = TableauBranch([f for f in branch.formulas if f is not formula])
            branch2 = TableauBranch([f for f in branch.formulas if f is not formula])
            branch1.add(_negate_formula(formula.left))
            branch2.add(formula.right)
            new_branches.extend([branch1, branch2])

        elif op == '¬':
            neg_type, inner = _get_literal_info(formula)
            if neg_type == 'double_neg':
                new_formulas = [f for f in branch.formulas if f is not formula]
                new_formulas.append(inner)
                new_branches.append(TableauBranch(new_formulas))
            elif neg_type == 'negated':
                if hasattr(inner, 'op') and inner.op in ('∧', '∨', '→'):
                    new_formulas = [f for f in branch.formulas if f is not formula]
                    if inner.op == '→':
                        new_formulas.append(inner.left)
                        new_formulas.append(_negate_formula(inner.right))
                        new_branches.append(TableauBranch(new_formulas))
                    elif inner.op == '∨':
                        new_formulas.append(_negate_formula(inner.left))
                        new_formulas.append(_negate_formula(inner.right))
                        new_branches.append(TableauBranch(new_formulas))
                    elif inner.op == '∧':
                        branch2 = TableauBranch([f for f in branch.formulas if f is not formula])
                        new_formulas.append(_negate_formula(inner.left))
                        branch2.add(_negate_formula(inner.right))
                        new_branches.append(TableauBranch(new_formulas))
                        new_branches.append(branch2)
                else:
                    pass

    if not new_branches:
        return [branch]

    return new_branches

def _is_complementary(prop1, prop2) -> bool:
    if hasattr(prop1, 'op') and prop1.op == '¬' and prop1.operand == prop2:
        return True
    if hasattr(prop2, 'op') and prop2.op == '¬' and prop2.operand == prop1:
        return True
    return False

def _close_branch(branch: TableauBranch) -> bool:
    for i, f1 in enumerate(branch.formulas):
        for f2 in branch.formulas[i+1:]:
            if _is_complementary(f1, f2):
                return True
    return False

def tableau_prove(prop) -> bool:
    initial = TableauBranch([_negate_formula(prop)])
    branches = [initial]
    max_iterations = 1000
    iteration = 0

    while branches and iteration < max_iterations:
        iteration += 1
        new_branches = []
        for branch in branches:
            if _close_branch(branch):
                continue
            expanded = _expand_branch(branch)
            for b in expanded:
                if _close_branch(b):
                    continue
                new_branches.append(b)

        if not new_branches:
            branches = []
            break

        branches = new_branches

    for branch in branches:
        if not _close_branch(branch):
            return False
    return True

class Prover:
    def __init__(self):
        self.theorems = {}

    def add_theorem(self, name: str, prop, proof: Optional[list] = None):
        from lean4py.logic import Theorem
        theorem = Theorem(name, prop, proof)
        self.theorems[name] = theorem
        return theorem

    def prove(self, prop, method: str = 'truth_table') -> Any:
        from lean4py.logic import Theorem, ProofStep

        if method == 'truth_table':
            result = truth_table_prove(prop)
        elif method == 'tableau':
            result = tableau_prove(prop)
        else:
            result = truth_table_prove(prop)

        if result:
            return Theorem(f"proved_{id(prop)}", prop, [ProofStep('by', method)])
        return None

    def prove_with_steps(self, prop) -> tuple:
        from lean4py.logic import Theorem, ProofStep

        result = truth_table_prove(prop)
        counterexample = None
        if not result:
            counterexample = find_counterexample(prop)

        return result, counterexample

    def __repr__(self):
        return f"Prover(theorems={list(self.theorems.keys())})"