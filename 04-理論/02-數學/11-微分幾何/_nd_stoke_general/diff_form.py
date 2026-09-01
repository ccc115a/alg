import sympy as sp
from typing import List, Tuple, Dict, Any

# ==============================================================================
# 1. 基礎類別：微分形式 (Differential Form)
# ==============================================================================
class DifferentialForm:
    def __init__(self, dim: int, degree: int, data: Dict[Tuple[int, ...], sp.Expr]):
        """
        data: 字典 { (idx1, idx2...): expression }
        例如 3D 中的 Fx dx + Fy dy -> { (0,): Fx, (1,): Fy }
        """
        self.dim = dim        # 空間維度 N
        self.degree = degree  # 形式階數 k
        self.data = data      

    def exterior_derivative(self):
        """計算外微分 dω (k -> k+1)"""
        new_data = {}
        X = [sp.symbols(f'x{i}') for i in range(self.dim)]
        
        for indices, expr in self.data.items():
            # d(f dx_I) = sum( df/dx_j ^ dx_j ^ dx_I )
            for j in range(self.dim):
                diff_expr = sp.diff(expr, X[j])
                if diff_expr == 0: continue
                
                # 形成新的指標序列 (j, i1, i2...)
                raw_indices = (j,) + indices
                
                # 如果有重複指標，楔積為 0
                if len(set(raw_indices)) != len(raw_indices):
                    continue 
                
                # 計算排序所需的交換次數以決定正負號
                # 使用冒泡排序計算逆序數
                temp_list = list(raw_indices)
                swaps = 0
                n = len(temp_list)
                for _ in range(n):
                    for k_idx in range(n - 1):
                        if temp_list[k_idx] > temp_list[k_idx + 1]:
                            temp_list[k_idx], temp_list[k_idx + 1] = temp_list[k_idx + 1], temp_list[k_idx]
                            swaps += 1
                
                sorted_indices = tuple(temp_list)
                sign = (-1) ** swaps
                
                # 累加結果
                current_term = sign * diff_expr
                if sorted_indices in new_data:
                    new_data[sorted_indices] += current_term
                else:
                    new_data[sorted_indices] = current_term
                    
        return DifferentialForm(self.dim, self.degree + 1, new_data)
