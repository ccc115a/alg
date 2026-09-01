"""Information theory functions: entropy, cross-entropy, KL divergence, mutual information."""

import numpy as np


def entropy(p, base=2):
    """Compute Shannon entropy of a probability distribution.

    Args:
        p: Probability distribution (array-like). Will be normalized if not sum to 1.
        base: Logarithm base (default 2 for bits).

    Returns:
        Entropy H(p) = -sum(p_i * log(p_i)).

    Examples:
        entropy([0.5, 0.5])  # 1.0 (1 bit)
        entropy([0.25, 0.25, 0.25, 0.25])  # 2.0 (2 bits)
    """
    p = np.asarray(p, dtype=float)
    # Normalize if not already
    if not np.isclose(p.sum(), 1.0):
        p = p / p.sum()
    # Remove zero probabilities
    p = p[p > 0]
    if base == 2:
        log = np.log2
    elif base == np.e or base == "e":
        log = np.log
    elif base == 10:
        log = np.log10
    else:
        log = lambda x: np.log(x) / np.log(base)
    return -np.sum(p * log(p))


def cross_entropy(p, q, base=2):
    """Compute cross-entropy between two distributions.

    H(p, q) = -sum(p_i * log(q_i))

    Args:
        p: True distribution.
        q: Predicted distribution.
        base: Logarithm base.

    Returns:
        Cross-entropy.

    Examples:
        cross_entropy([0.5, 0.5], [0.5, 0.5])  # 1.0
    """
    p = np.asarray(p, dtype=float)
    q = np.asarray(q, dtype=float)
    if not np.isclose(p.sum(), 1.0):
        p = p / p.sum()
    if not np.isclose(q.sum(), 1.0):
        q = q / q.sum()
    # Align dimensions
    if p.shape != q.shape:
        raise ValueError("p and q must have same shape")
    # Remove zero probabilities in q (since log(q) used)
    mask = q > 0
    p_masked = p[mask]
    q_masked = q[mask]
    if base == 2:
        log = np.log2
    elif base == np.e or base == "e":
        log = np.log
    elif base == 10:
        log = np.log10
    else:
        log = lambda x: np.log(x) / np.log(base)
    return -np.sum(p_masked * log(q_masked))


def kl_divergence(p, q, base=2):
    """Compute Kullback-Leibler divergence D(p || q).

    D(p || q) = sum(p_i * log(p_i / q_i))

    Args:
        p: True distribution.
        q: Approximating distribution.
        base: Logarithm base.

    Returns:
        KL divergence.

    Examples:
        kl_divergence([0.5, 0.5], [0.5, 0.5])  # 0.0
    """
    p = np.asarray(p, dtype=float)
    q = np.asarray(q, dtype=float)
    if not np.isclose(p.sum(), 1.0):
        p = p / p.sum()
    if not np.isclose(q.sum(), 1.0):
        q = q / q.sum()
    if p.shape != q.shape:
        raise ValueError("p and q must have same shape")
    mask = (p > 0) & (q > 0)
    p_masked = p[mask]
    q_masked = q[mask]
    if base == 2:
        log = np.log2
    elif base == np.e or base == "e":
        log = np.log
    elif base == 10:
        log = np.log10
    else:
        log = lambda x: np.log(x) / np.log(base)
    return np.sum(p_masked * log(p_masked / q_masked))


def mutual_information(joint, base=2):
    """Compute mutual information from joint distribution.

    I(X;Y) = H(X) + H(Y) - H(X,Y)

    Args:
        joint: Joint probability matrix P(X,Y). Will be normalized.
        base: Logarithm base.

    Returns:
        Mutual information.

    Examples:
        joint = [[0.25, 0.25], [0.25, 0.25]]  # independent
        mutual_information(joint)  # ~0
    """
    joint = np.asarray(joint, dtype=float)
    if not np.isclose(joint.sum(), 1.0):
        joint = joint / joint.sum()
    # Marginal distributions
    p_x = joint.sum(axis=1)
    p_y = joint.sum(axis=0)
    H_x = entropy(p_x, base)
    H_y = entropy(p_y, base)
    H_xy = entropy(joint.flatten(), base)
    return H_x + H_y - H_xy
