import pytest
from lean4py import Prop, implies, and_, or_, not_, iff
from lean4py.prover import (
    Prover, truth_table_prove, tableau_prove,
    is_valid, is_satisfiable, find_counterexample
)

class TestTruthTableProve:
    def test_valid_p_implies_p(self):
        p = Prop('p')
        assert truth_table_prove(implies(p, p)) is True

    def test_valid_excluded_middle(self):
        p = Prop('p')
        assert truth_table_prove(or_(p, not_(p))) is True

    def test_valid_double_neg(self):
        p = Prop('p')
        assert truth_table_prove(implies(not_(not_(p)), p)) is True

    def test_valid_modus_ponens_form(self):
        p = Prop('p')
        q = Prop('q')
        formula = implies(and_(p, implies(p, q)), q)
        assert truth_table_prove(formula) is True

    def test_invalid_p_implies_q(self):
        p = Prop('p')
        q = Prop('q')
        assert truth_table_prove(implies(p, q)) is False

    def test_invalid_contradiction(self):
        p = Prop('p')
        assert truth_table_prove(and_(p, not_(p))) is False

    def test_valid_and_commute(self):
        p = Prop('p')
        q = Prop('q')
        assert truth_table_prove(iff(and_(p, q), and_(q, p))) is True

    def test_valid_or_commute(self):
        p = Prop('p')
        q = Prop('q')
        assert truth_table_prove(iff(or_(p, q), or_(q, p))) is True

    def test_valid_de_morgan_1(self):
        p = Prop('p')
        q = Prop('q')
        assert truth_table_prove(not_(and_(p, q))) is True or truth_table_prove(iff(not_(and_(p, q)), or_(not_(p), not_(q)))) is True

    def test_valid_de_morgan_2(self):
        p = Prop('p')
        q = Prop('q')
        assert truth_table_prove(iff(not_(or_(p, q)), and_(not_(p), not_(q)))) is True

class TestIsValid:
    def test_valid_reflexive(self):
        p = Prop('p')
        assert is_valid(implies(p, p)) is True

    def test_valid_excluded_middle(self):
        p = Prop('p')
        assert is_valid(or_(p, not_(p))) is True

    def test_invalid_form(self):
        p = Prop('p')
        q = Prop('q')
        assert is_valid(implies(p, q)) is False

class TestIsSatisfiable:
    def test_satisfiable_atom(self):
        p = Prop('p')
        assert is_satisfiable(p) is True

    def test_unsatisfiable_contradiction(self):
        p = Prop('p')
        assert is_satisfiable(and_(p, not_(p))) is False

    def test_satisfiable_conjunction(self):
        p = Prop('p')
        q = Prop('q')
        assert is_satisfiable(and_(p, q)) is True

    def test_satisfiable_or(self):
        p = Prop('p')
        q = Prop('q')
        assert is_satisfiable(or_(p, q)) is True

class TestFindCounterexample:
    def test_counterexample_simple(self):
        p = Prop('p')
        q = Prop('q')
        ce = find_counterexample(implies(p, q))
        assert ce is not None

    def test_no_counterexample_valid(self):
        p = Prop('p')
        assert find_counterexample(implies(p, p)) is None

class TestTableauProve:
    def test_tableau_valid_p_implies_p(self):
        p = Prop('p')
        assert tableau_prove(implies(p, p)) is True

    def test_tableau_valid_excluded_middle(self):
        p = Prop('p')
        assert tableau_prove(or_(p, not_(p))) is True

    def test_tableau_invalid(self):
        p = Prop('p')
        q = Prop('q')
        assert tableau_prove(implies(p, q)) is False

class TestProver:
    def test_prover_init(self):
        prover = Prover()
        assert prover is not None
        assert len(prover.theorems) == 0

    def test_prover_add_theorem(self):
        prover = Prover()
        p = Prop('p')
        t = prover.add_theorem('test', implies(p, p))
        assert t.name == 'test'
        assert 'test' in prover.theorems

    def test_prover_prove_truth_table(self):
        prover = Prover()
        p = Prop('p')
        result = prover.prove(implies(p, p), method='truth_table')
        assert result is not None

    def test_prover_prove_invalid(self):
        prover = Prover()
        p = Prop('p')
        q = Prop('q')
        result = prover.prove(implies(p, q), method='truth_table')
        assert result is None

    def test_prove_with_steps(self):
        prover = Prover()
        p = Prop('p')
        result, ce = prover.prove_with_steps(implies(p, p))
        assert result is True
        assert ce is None

class TestNewTactics:
    def test_intros(self):
        from lean4py.tactics import intros
        step = intros(['x', 'y'])
        assert step.tactic == 'intros'

    def test_by_contra(self):
        from lean4py.tactics import by_contra
        p = Prop('p')
        step = by_contra('h', not_(p))
        assert step.tactic == 'by_contra'

    def test_cases(self):
        from lean4py.tactics import cases
        p = Prop('p')
        q = Prop('q')
        step = cases('h', [p, q])
        assert step.tactic == 'cases'

    def test_split(self):
        from lean4py.tactics import split
        step = split()
        assert step.tactic == 'split'

    def test_left(self):
        from lean4py.tactics import left
        step = left()
        assert step.tactic == 'left'

    def test_right(self):
        from lean4py.tactics import right
        step = right()
        assert step.tactic == 'right'

    def test_use(self):
        from lean4py.tactics import use
        step = use('x')
        assert step.tactic == 'use'

    def test_show(self):
        from lean4py.tactics import show
        p = Prop('p')
        step = show(p)
        assert step.tactic == 'show'

    def test_by(self):
        from lean4py.tactics import by, tactic_simp, tactic_exact
        p = Prop('p')
        step = by([tactic_simp(), tactic_exact(p)])
        assert step.tactic == 'by'

    def test_sorry(self):
        from lean4py.tactics import sorry
        step = sorry()
        assert step.tactic == 'sorry'

    def test_rewrite(self):
        from lean4py.tactics import rewrite
        step = rewrite('h', sym=True)
        assert step.tactic == 'rewrite'

    def test_induction(self):
        from lean4py.tactics import induction
        base = []
        ind = []
        step = induction('n', base, ind)
        assert step.tactic == 'induction'

    def test_calc(self):
        from lean4py.tactics import calc, tactic_rfl
        step = calc([tactic_rfl()])
        assert step.tactic == 'calc'

    def test_intro(self):
        from lean4py.tactics import intro
        step = intro('x')
        assert step.tactic == 'intro'

class TestTacticState:
    def test_tactic_state_init(self):
        from lean4py.tactics import TacticState
        state = TacticState()
        assert len(state.goals) == 0
        assert len(state.hypotheses) == 0

    def test_add_hypothesis(self):
        from lean4py.tactics import TacticState
        p = Prop('p')
        state = TacticState()
        state.add_hypothesis('h', p)
        assert 'h' in state.hypotheses
        assert state.get_hypothesis('h') == p

    def test_pop_goal(self):
        from lean4py.tactics import TacticState
        p = Prop('p')
        state = TacticState(goals=[p])
        goal = state.pop_goal()
        assert goal == p
        assert len(state.goals) == 0