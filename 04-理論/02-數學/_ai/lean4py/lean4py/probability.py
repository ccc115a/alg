from typing import Callable, Dict, List, Optional, Set, Tuple, Any
import math
import random

class ProbabilitySpace:
    def __init__(self, sample_space: Set[Any], event_space: Optional[Set['Event']] = None, prob_func: Optional[Callable[[Any], float]] = None):
        self.sample_space = sample_space
        self.event_space = event_space or set()
        self.prob_func = prob_func or (lambda x: 1.0 / len(sample_space) if x in sample_space else 0.0)

    def __repr__(self):
        return f"ProbabilitySpace(Ω={self.sample_space})"

    @staticmethod
    def uniform(sample_space: Set[Any]) -> 'ProbabilitySpace':
        n = len(sample_space)
        return ProbabilitySpace(sample_space, prob_func=lambda x: 1.0 / n if x in sample_space else 0.0)

    @staticmethod
    def dice(n_sides: int = 6) -> 'ProbabilitySpace':
        return ProbabilitySpace.uniform(set(range(1, n_sides + 1)))

    def probability(self, event: Any) -> float:
        if isinstance(event, Event):
            elements = event.elements
        elif isinstance(event, set):
            elements = event
        else:
            return self.prob_func(event)
        return sum(self.prob_func(e) for e in elements)

    def conditional_probability(self, event: Any, given: Any) -> float:
        p_given = self.probability(given)
        if p_given == 0:
            return 0.0
        p_both = self.probability(self.intersection(event, given))
        return p_both / p_given

    def intersection(self, event1: Any, event2: Any) -> Set:
        if isinstance(event1, Event):
            e1 = event1.elements
        else:
            e1 = event1
        if isinstance(event2, Event):
            e2 = event2.elements
        else:
            e2 = event2
        return e1 & e2

    def union(self, event1: Any, event2: Any) -> Set:
        if isinstance(event1, Event):
            e1 = event1.elements
        else:
            e1 = event1
        if isinstance(event2, Event):
            e2 = event2.elements
        else:
            e2 = event2
        return e1 | e2

    def complement(self, event: Any) -> Set:
        if isinstance(event, Event):
            e = event.elements
        else:
            e = event
        return self.sample_space - e

class Event:
    def __init__(self, elements: Set, name: str = ""):
        self.elements = elements
        self.name = name

    def __repr__(self):
        return f"Event({self.elements})" if not self.name else f"Event({self.name}: {self.elements})"

    def __and__(self, other):
        return Event(self.elements & other.elements)

    def __or__(self, other):
        return Event(self.elements | other.elements)

    def __invert__(self):
        return Event(self.complement)

    def complement(self, sample_space: Set) -> 'Event':
        return Event(sample_space - self.elements)

    def probability(self, ps: ProbabilitySpace) -> float:
        return ps.probability(self.elements)

class RandomVariable:
    def __init__(self, name: str, values: Dict[Any, float]):
        self.name = name
        self.values = values
        self._expected = None
        self._variance = None

    def __repr__(self):
        return f"RandomVariable({self.name})"

    def __call__(self, outcome: Any) -> Any:
        return self.values.get(outcome, 0)

    def support(self) -> List[Any]:
        return [k for k, v in self.values.items() if v > 0]

    def expected_value(self) -> float:
        if self._expected is not None:
            return self._expected
        self._expected = sum(k * v for k, v in self.values.items())
        return self._expected

    def variance(self) -> float:
        if self._variance is not None:
            return self._variance
        mu = self.expected_value()
        self._variance = sum(((k - mu) ** 2) * v for k, v in self.values.items())
        return self._variance

    def std_dev(self) -> float:
        return math.sqrt(self.variance())

    def e(self, g: Callable[[Any], float]) -> float:
        return sum(g(k) * v for k, v in self.values.items())

def ExpectedValue(X: RandomVariable) -> float:
    return X.expected_value()

def Variance(X: RandomVariable) -> float:
    return X.variance()

def StandardDeviation(X: RandomVariable) -> float:
    return X.std_dev()

def Covariance(X: RandomVariable, Y: RandomVariable) -> float:
    EX = X.expected_value()
    EY = Y.expected_value()
    return X.e(lambda k: Y.values.get(k, 0) * (k - EX) * (Y.values.get(k, 0) - EY))

def Correlation(X: RandomVariable, Y: RandomVariable) -> float:
    cov = Covariance(X, Y)
    std_x = X.std_dev()
    std_y = Y.std_dev()
    if std_x == 0 or std_y == 0:
        return 0.0
    return cov / (std_x * std_y)

class Distribution:
    def pdf(self, x: float) -> float:
        raise NotImplementedError

    def cdf(self, x: float) -> float:
        raise NotImplementedError

    def mean(self) -> float:
        raise NotImplementedError

    def variance(self) -> float:
        raise NotImplementedError

class NormalDistribution(Distribution):
    def __init__(self, mu: float = 0, sigma2: float = 1):
        self.mu = mu
        self.sigma2 = sigma2
        self.sigma = math.sqrt(sigma2)
        self._normalizing_constant = 1.0 / (self.sigma * math.sqrt(2 * math.pi))

    def __repr__(self):
        return f"Normal(μ={self.mu}, σ²={self.sigma2})"

    def pdf(self, x: float) -> float:
        z = (x - self.mu) / self.sigma
        return self._normalizing_constant * math.exp(-0.5 * z * z)

    def cdf(self, x: float) -> float:
        return 0.5 * (1 + math.erf((x - self.mu) / (self.sigma * math.sqrt(2))))

    def mean(self) -> float:
        return self.mu

    def variance(self) -> float:
        return self.sigma2

    def sample(self, n: int = 1) -> List[float]:
        return [random.gauss(self.mu, self.sigma) for _ in range(n)]

class BinomialDistribution(Distribution):
    def __init__(self, n: int, p: float):
        self.n = n
        self.p = p
        self.q = 1 - p

    def __repr__(self):
        return f"Binomial(n={self.n}, p={self.p})"

    def pdf(self, k: int) -> float:
        if k < 0 or k > self.n:
            return 0.0
        return math.comb(self.n, k) * (self.p ** k) * (self.q ** (self.n - k))

    def cdf(self, k: int) -> float:
        return sum(self.pdf(i) for i in range(int(k) + 1))

    def mean(self) -> float:
        return self.n * self.p

    def variance(self) -> float:
        return self.n * self.p * self.q

    def sample(self, n: int = 1) -> List[int]:
        return [sum(random.random() < self.p for _ in range(self.n)) for _ in range(n)]

class PoissonDistribution(Distribution):
    def __init__(self, lam: float):
        self.lam = lam

    def __repr__(self):
        return f"Poisson(λ={self.lam})"

    def pdf(self, k: int) -> float:
        if k < 0:
            return 0.0
        return math.exp(-self.lam) * (self.lam ** k) / math.factorial(k)

    def cdf(self, k: int) -> float:
        return sum(self.pdf(i) for i in range(int(k) + 1))

    def mean(self) -> float:
        return self.lam

    def variance(self) -> float:
        return self.lam

    def sample(self, n: int = 1) -> List[int]:
        import numpy as np
        try:
            return list(np.random.poisson(self.lam, n))
        except:
            return [max(0, int(random.gauss(self.lam, math.sqrt(self.lam)))) for _ in range(n)]

class UniformDistribution(Distribution):
    def __init__(self, a: float, b: float):
        self.a = a
        self.b = b
        self.length = b - a

    def __repr__(self):
        return f"Uniform({self.a}, {self.b})"

    def pdf(self, x: float) -> float:
        if self.a <= x <= self.b:
            return 1.0 / self.length
        return 0.0

    def cdf(self, x: float) -> float:
        if x < self.a:
            return 0.0
        elif x >= self.b:
            return 1.0
        return (x - self.a) / self.length

    def mean(self) -> float:
        return (self.a + self.b) / 2

    def variance(self) -> float:
        return (self.length ** 2) / 12

    def sample(self, n: int = 1) -> List[float]:
        return [random.uniform(self.a, self.b) for _ in range(n)]

def bayes_theorem(p_a_given_b: float, p_b_given_a: float, p_a: float, p_b: float) -> float:
    return (p_b_given_a * p_a) / p_b if p_b > 0 else 0.0

def law_of_total_probability(p_b_given_a_i: List[float], p_a_i: List[float]) -> float:
    return sum(pb * pa for pb, pa in zip(p_b_given_a_i, p_a_i))

def hypothesis_test(test_type: str, sample: List[float], mu: float = 0, sigma: float = None, alpha: float = 0.05) -> Dict[str, float]:
    n = len(sample)
    sample_mean = sum(sample) / n
    s = math.sqrt(sum((x - sample_mean) ** 2 for x in sample) / (n - 1)) if sigma is None else sigma

    if test_type == 'z':
        z_stat = (sample_mean - mu) / (s / math.sqrt(n))
        p_value = 2 * (1 - NormalDistribution(0, 1).cdf(abs(z_stat)))
        return {'z': z_stat, 'p_value': p_value, 'reject': p_value < alpha}
    elif test_type == 't':
        if sigma is not None:
            s = sigma
        t_stat = (sample_mean - mu) / (s / math.sqrt(n))
        from scipy.stats import t as t_dist
        p_value = 2 * (1 - t_dist.cdf(abs(t_stat), n - 1))
        return {'t': t_stat, 'p_value': p_value, 'reject': p_value < alpha}
    elif test_type == 'chi-square':
        expected = [mu] * n
        chi2_stat = sum((obs - exp) ** 2 / exp for obs, exp in zip(sample, expected))
        from scipy.stats import chi2 as chi2_dist
        p_value = 1 - chi2_dist.cdf(chi2_stat, n - 1)
        return {'chi2': chi2_stat, 'p_value': p_value, 'reject': p_value < alpha}
    else:
        return {'error': 'Unknown test type'}

def confidence_interval(sample: List[float], confidence: float = 0.95) -> Tuple[float, float]:
    n = len(sample)
    mean = sum(sample) / n
    s = math.sqrt(sum((x - mean) ** 2 for x in sample) / (n - 1))
    from scipy.stats import t as t_dist
    t_val = t_dist.ppf((1 + confidence) / 2, n - 1)
    margin = t_val * s / math.sqrt(n)
    return (mean - margin, mean + margin)

def chi_square_test(observed: List[float], expected: List[float]) -> Dict[str, float]:
    chi2_stat = sum((obs - exp) ** 2 / exp for obs, exp in zip(observed, expected))
    df = len(observed) - 1
    from scipy.stats import chi2 as chi2_dist
    p_value = 1 - chi2_dist.cdf(chi2_stat, df)
    return {'chi2': chi2_stat, 'df': df, 'p_value': p_value}

def t_test_independent(sample1: List[float], sample2: List[float]) -> Dict[str, float]:
    n1, n2 = len(sample1), len(sample2)
    mean1, mean2 = sum(sample1) / n1, sum(sample2) / n2
    var1 = sum((x - mean1) ** 2 for x in sample1) / (n1 - 1)
    var2 = sum((x - mean2) ** 2 for x in sample2) / (n2 - 1)
    pooled_se = math.sqrt(var1 / n1 + var2 / n2)
    t_stat = (mean1 - mean2) / pooled_se
    df = n1 + n2 - 2
    from scipy.stats import t as t_dist
    p_value = 2 * (1 - t_dist.cdf(abs(t_stat), df))
    return {'t': t_stat, 'df': df, 'p_value': p_value}