from .riemann import *
import sympy as sp

import sympy as sp

# 移除舊的逐分量定義，改用矩陣運算
def einstein_tensor(R_mn, R_scalar, G_cov):
    """
    計算愛因斯坦張量 G_{mu nu} (矩陣形式)
    公式: G = R_mn - 1/2 * R * g_mn
    
    參數:
    - R_mn: Ricci 張量 (SymPy Matrix)
    - R_scalar: Ricci 純量 (SymPy Expression)
    - G_cov: 協變度規張量 (SymPy Matrix)
    """
    
    # SymPy 支援矩陣與純量的直接運算
    # 0.5 * R_scalar * G_cov 會自動對 G_cov 的每個元素進行乘法
    G_matrix = R_mn - 0.5 * R_scalar * G_cov
    
    # 對矩陣每個元素進行化簡
    return sp.simplify(G_matrix)
