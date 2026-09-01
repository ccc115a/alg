"""Statistical hypothesis tests"""

from typing import List, Optional, Tuple
import math
from dataclasses import dataclass
from .stats import mean, var, sd
from .distributions import pt, pnorm, pf, pchisq, dt, df as f_df

@dataclass
class TestResult:
    statistic: float
    p_value: float
    df: Optional[int] = None
    ci: Optional[Tuple[float, float]] = None
    ci_level: Optional[float] = None
    conf_level: Optional[float] = None

def t_test(x: List[float], y: Optional[List[float]] = None,
           mu: float = 0, alpha: float = 0.05,
           alternative: str = "two.sided", paired: bool = False,
           conf_interval: bool = True) -> dict:
    """One-sample or two-sample t-test

    Args:
        x: Sample data
        y: Second sample (for two-sample test)
        mu: Hypothesized mean (for one-sample)
        alpha: Significance level
        alternative: "two.sided", "greater", "less"
        paired: If True, paired t-test
        conf_interval: If True, compute confidence interval
    """
    if y is None:
        return _t_test_one_sample(x, mu, alpha, alternative, conf_interval)
    elif paired:
        return _t_test_paired(x, y, alpha, alternative, conf_interval)
    else:
        return _t_test_two_sample(x, y, alpha, alternative, conf_interval)

def _t_test_one_sample(x, mu, alpha, alternative, conf_interval):
    n = len(x)
    x_mean = mean(x)
    x_sd = sd(x)
    se = x_sd / math.sqrt(n)
    t_stat = (x_mean - mu) / se
    df = n - 1

    if alternative == "two.sided":
        p_value = 2 * (1 - pt(abs(t_stat), df))
    elif alternative == "greater":
        p_value = 1 - pt(t_stat, df)
    else:
        p_value = pt(t_stat, df)

    result = {"statistic": t_stat, "df": df, "p_value": p_value,
              "estimate": x_mean, "null_value": mu}

    if conf_interval:
        t_crit = pt(1 - alpha/2, df)
        ci = (x_mean - t_crit * se, x_mean + t_crit * se)
        result["ci"] = ci
        result["ci_level"] = 1 - alpha

    return result

def _t_test_paired(x, y, alpha, alternative, conf_interval):
    diff = [x[i] - y[i] for i in range(len(x))]
    return _t_test_one_sample(diff, 0, alpha, alternative, conf_interval)

def _t_test_two_sample(x, y, alpha, alternative, conf_interval):
    n1, n2 = len(x), len(y)
    m1, m2 = mean(x), mean(y)
    v1, v2 = var(x), var(y)
    df = n1 + n2 - 2

    pooled_se = math.sqrt(v1/n1 + v2/n2)
    t_stat = (m1 - m2) / pooled_se

    if alternative == "two.sided":
        p_value = 2 * (1 - pt(abs(t_stat), df))
    elif alternative == "greater":
        p_value = 1 - pt(t_stat, df)
    else:
        p_value = pt(t_stat, df)

    result = {"statistic": t_stat, "df": df, "p_value": p_value,
              "estimate": m1 - m2}

    if conf_interval:
        t_crit = pt(1 - alpha/2, df)
        diff = m1 - m2
        ci = (diff - t_crit * pooled_se, diff + t_crit * pooled_se)
        result["ci"] = ci
        result["ci_level"] = 1 - alpha

    return result

def z_test(x: List[float], sigma: float, mu: float = 0,
           alpha: float = 0.05, alternative: str = "two.sided",
           conf_interval: bool = True) -> dict:
    """One-sample Z-test (known population standard deviation)

    Args:
        x: Sample data
        sigma: Population standard deviation
        mu: Hypothesized mean
        alpha: Significance level
        alternative: "two.sided", "greater", "less"
        conf_interval: If True, compute confidence interval
    """
    n = len(x)
    x_mean = mean(x)
    se = sigma / math.sqrt(n)
    z_stat = (x_mean - mu) / se

    if alternative == "two.sided":
        p_value = 2 * (1 - pnorm(abs(z_stat)))
    elif alternative == "greater":
        p_value = 1 - pnorm(z_stat)
    else:
        p_value = pnorm(z_stat)

    result = {"statistic": z_stat, "p_value": p_value,
              "estimate": x_mean, "null_value": mu}

    if conf_interval:
        z_crit = pnorm(1 - alpha/2)
        ci = (x_mean - z_crit * se, x_mean + z_crit * se)
        result["ci"] = ci
        result["ci_level"] = 1 - alpha

    return result

def chisq_test(observed: List[List[float]],
               expected: Optional[List[List[float]]] = None,
               alpha: float = 0.05) -> dict:
    """Chi-square goodness-of-fit or independence test

    Args:
        observed: Observed frequencies matrix
        expected: Expected frequencies (if None, assumes equal distribution)
        alpha: Significance level
    """
    if expected is None:
        total = sum(sum(row) for row in observed)
        n_cols = len(observed[0])
        n_rows = len(observed)
        expected_val = total / (n_rows * n_cols)
        expected = [[expected_val] * n_cols for _ in range(n_rows)]

    chisq = 0
    for i in range(len(observed)):
        for j in range(len(observed[0])):
            chisq += (observed[i][j] - expected[i][j])**2 / expected[i][j]

    df = (len(observed) - 1) * (len(observed[0]) - 1)
    p_value = 1 - pchisq(chisq, df)

    return {
        "statistic": chisq,
        "df": df,
        "p_value": p_value,
        "observed": observed,
        "expected": expected
    }

def anova(*groups: List[float]) -> dict:
    """One-way ANOVA

    Args:
        *groups: Variable number of sample groups
    """
    all_data = [x for g in groups for x in g]
    grand_mean = mean(all_data)

    ss_between = sum(len(g) * (mean(g) - grand_mean)**2 for g in groups)
    df_between = len(groups) - 1

    ss_within = sum(sum((x - mean(g))**2 for x in g) for g in groups)
    df_within = len(all_data) - len(groups)

    ms_between = ss_between / df_between
    ms_within = ss_within / df_within
    f_stat = ms_between / ms_within
    p_value = 1 - pf(f_stat, df_between, df_within)

    return {
        "statistic": f_stat,
        "df1": df_between,
        "df2": df_within,
        "p_value": p_value,
        "ss_between": ss_between,
        "ss_within": ss_within,
        "ms_between": ms_between,
        "ms_within": ms_within
    }

def conf_interval(x: List[float], sigma: Optional[float] = None,
                  alpha: float = 0.05, paired: bool = False) -> dict:
    """Calculate confidence interval for mean

    Args:
        x: Sample data
        sigma: Population std (if None, use t-distribution)
        alpha: Significance level
        paired: If True, compute paired CI
    """
    n = len(x)
    x_mean = mean(x)

    if sigma is not None:
        se = sigma / math.sqrt(n)
        z_crit = pnorm(1 - alpha/2)
        dist = "z"
    else:
        se = sd(x) / math.sqrt(n)
        z_crit = pt(1 - alpha/2, n - 1)
        dist = "t"

    ci = (x_mean - z_crit * se, x_mean + z_crit * se)

    return {
        "estimate": x_mean,
        "ci": ci,
        "ci_level": 1 - alpha,
        "distribution": dist,
        "se": se
    }