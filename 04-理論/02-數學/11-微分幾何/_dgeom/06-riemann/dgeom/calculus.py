import numpy as np

# ==========================================
# Part 1: 通用外微分算子 d (沿用上一版核心)
# ==========================================

def partial_derivative(f, p, index, h=1e-5):
    p_arr = np.array(p, dtype=float)
    p_plus = p_arr.copy(); p_plus[index] += h
    p_minus = p_arr.copy(); p_minus[index] -= h
    return (f(p_plus) - f(p_minus)) / (2 * h)

def gradient(f, p):
    return np.array([partial_derivative(f, p, i) for i in range(len(p))])
