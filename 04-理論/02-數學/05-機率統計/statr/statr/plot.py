"""Statistical visualization - R style plots for hypothesis tests"""

import math
from typing import List, Optional, Tuple, Dict
from .distributions import dt, pt, qnorm, pnorm

def plot_t_ci(x: List[float], ci: Tuple[float, float],
              mean: float, alpha: float = 0.05,
              title: Optional[str] = None):
    """Plot t-test confidence interval visualization

    Args:
        x: Sample data
        ci: Confidence interval (lower, upper)
        mean: Sample mean
        alpha: Significance level
        title: Plot title
    """
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("matplotlib required: pip install matplotlib")
        return

    n = len(x)
    df = n - 1
    t_crit = pt(1 - alpha/2, df, lower_tail=False)

    se = (ci[1] - mean) / t_crit

    x_range = np.linspace(mean - 4*se, mean + 4*se, 500)
    y = [dt((xi - mean)/se, df)/se for xi in x_range]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(x_range, y, 'b-', lw=2)
    ax.fill_between(x_range, y, alpha=0.3)

    ax.axvline(mean, color='blue', lw=2, label=f'Sample mean = {mean:.4f}')
    ax.axvline(ci[0], color='red', lw=2, linestyle='--', label=f'CI lower = {ci[0]:.4f}')
    ax.axvline(ci[1], color='red', lw=2, linestyle='--', label=f'CI upper = {ci[1]:.4f}')

    ax.set_xlabel('Value')
    ax.set_ylabel('Density')
    ax.set_title(title or f'{(1-alpha)*100:.0f}% Confidence Interval for Mean\nn={n}, df={df}')
    ax.legend()
    plt.tight_layout()
    plt.show()

def plot_z_ci(mean: float, se: float, ci: Tuple[float, float],
              alpha: float = 0.05, title: Optional[str] = None):
    """Plot Z-test confidence interval visualization

    Args:
        mean: Sample mean
        se: Standard error
        ci: Confidence interval
        alpha: Significance level
        title: Plot title
    """
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("matplotlib required: pip install matplotlib")
        return

    x_range = np.linspace(mean - 4*se, mean + 4*se, 500)
    y = [pnorm((xi - mean)/se, lower_tail=False) for xi in x_range]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(x_range, y, 'b-', lw=2)

    ax.axvline(mean, color='blue', lw=2, label=f'Mean = {mean:.4f}')
    ax.axvline(ci[0], color='red', lw=2, linestyle='--', label=f'CI = [{ci[0]:.4f}, {ci[1]:.4f}]')

    ax.set_xlabel('Value')
    ax.set_ylabel('P(X > x)')
    ax.set_title(title or f'{(1-alpha)*100:.0f}% Confidence Interval for Mean')
    ax.legend()
    plt.tight_layout()
    plt.show()

def plot_chisq_ci(chisq_stat: float, df: int, alpha: float = 0.05):
    """Plot chi-square test visualization"""
    try:
        import matplotlib.pyplot as plt
        import numpy as np
        from .distributions import dchisq
    except ImportError:
        print("matplotlib required")
        return

    x_range = np.linspace(0, max(3*df, chisq_stat + 10), 500)
    y = [dchisq(xi, df) for xi in x_range]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(x_range, y, 'b-', lw=2)
    ax.fill_between(x_range, y, alpha=0.3)

    crit_val = qnorm(1 - alpha/2)
    ax.axvline(chisq_stat, color='blue', lw=2, label=f'χ² = {chisq_stat:.4f}')

    ax.set_xlabel('Chi-square value')
    ax.set_ylabel('Density')
    ax.set_title(f'Chi-square Test (df={df})\nStatistic = {chisq_stat:.4f}, p = {1-pchisq(chisq_stat, df):.4f}')
    ax.legend()
    plt.tight_layout()
    plt.show()

def plot_anova_ci(group_means: List[float], group_ses: List[float],
                  labels: List[str], alpha: float = 0.05):
    """Plot ANOVA group means with confidence intervals"""
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("matplotlib required")
        return

    fig, ax = plt.subplots(figsize=(10, 6))
    x_pos = np.arange(len(group_means))

    for i, (m, se, label) in enumerate(zip(group_means, group_ses, labels)):
        ax.errorbar(i, m, yerr=se, fmt='o', markersize=10, capsize=5, label=label)

    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels)
    ax.set_ylabel('Group Mean')
    ax.set_title(f'ANOVA Group Means with {(1-alpha)*100:.0f}% Confidence Intervals')
    ax.legend()
    plt.tight_layout()
    plt.show()

def plot_distribution(dist: str, params: Dict, statistic: float,
                      p_value: float, alpha: float = 0.05):
    """Generic plot for any test distribution"""
    try:
        import matplotlib.pyplot as plt
        import numpy as np
        from .distributions import dnorm, dt as dt_dist, dchisq, df as df_dist
    except ImportError:
        print("matplotlib required")
        return

    dist_funcs = {
        "normal": (dnorm, params.get("mean", 0), params.get("sd", 1)),
        "t": (dt_dist, params.get("df", 10)),
        "chisq": (dchisq, params.get("df", 10)),
        "F": (df_dist, params.get("df1", 10), params.get("df2", 10))
    }

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_title(f'{dist.upper()} Distribution Test\nStatistic={statistic:.4f}, p-value={p_value:.4f}')
    ax.set_xlabel('Value')
    ax.set_ylabel('Density')
    plt.tight_layout()
    plt.show()