import sympy as sp

class ChristoffelGenerator:
    def __init__(self, coords, metric):
        """
        初始化生成器
        Args:
            coords: 坐標符號列表 [t, r, theta, phi]
            metric: SymPy 矩陣 g_ij
        """
        self.coords = coords
        self.dim = len(coords)
        self.g = metric
        
        print(f"--- 初始化 (維度 {self.dim}) ---")
        print("1. 計算逆度量 g^{ij}...")
        self.g_inv = self.g.inv()
        
        print("2. 計算克里斯托費爾符號 Γ^k_ij ...")
        self.Gamma = self._compute_gamma()

    def _compute_gamma(self):
        # 建立一個 3D 列表來儲存結果 Gamma[k][i][j]
        # 使用列表推導式初始化
        G = [[[sp.Integer(0) for _ in range(self.dim)] 
              for _ in range(self.dim)] 
             for _ in range(self.dim)]
        
        # 遍歷所有指標 k, i, j
        for k in range(self.dim):
            for i in range(self.dim):
                for j in range(self.dim):
                    
                    # 對稱性優化: Gamma^k_ij = Gamma^k_ji
                    # 如果我們已經算過 [k][j][i]，直接複製即可
                    if i > j and G[k][j][i] != 0:
                         G[k][i][j] = G[k][j][i]
                         continue

                    # 開始求和計算
                    val = sp.Integer(0)
                    for l in range(self.dim):
                        # 公式: 1/2 * g^kl * (∂_i g_lj + ∂_j g_li - ∂_l g_ij)
                        
                        term = 0.5 * self.g_inv[k, l] * (
                            self.g[l, j].diff(self.coords[i]) +
                            self.g[i, l].diff(self.coords[j]) -
                            self.g[i, j].diff(self.coords[l])
                        )
                        val += term
                    
                    G[k][i][j] = sp.simplify(val)
                    
        return G

    def print_results(self):
        """只印出非零的分量，使用漂亮的數學格式"""
        print("\n=== 非零克里斯托費爾符號 (Non-zero Christoffel Symbols) ===")
        print("格式: Γ^k_ij (上標 k, 下標 i, j)\n")
        
        count = 0
        for k in range(self.dim):
            for i in range(self.dim):
                for j in range(self.dim):
                    val = self.Gamma[k][i][j]
                    if val != 0:
                        # 格式化輸出
                        k_sym = self.coords[k]
                        i_sym = self.coords[i]
                        j_sym = self.coords[j]
                        print(f"Γ^{k_sym}_{i_sym},{j_sym} = ")
                        sp.pprint(val)
                        print("-" * 20)
                        count += 1
        
        if count == 0:
            print("所有分量均為 0 (平直空間)")
        else:
            print(f"\n總共找到 {count} 個非零分量。")

# ==========================================
# 實戰：史瓦西度量 (Schwarzschild Metric)
# ==========================================

def run_gr_calculation():
    # 1. 定義符號
    # t: 時間, r: 半徑, theta: 極角, phi: 方位角
    t, r, theta, phi = sp.symbols('t r theta phi')
    
    # 物理常數
    rs = sp.Symbol('r_s', real=True) # 史瓦西半徑 (2GM/c^2)
    
    # 2. 定義度量矩陣 g_uv
    # A(r) = 1 - rs/r
    A = 1 - rs/r
    
    # g = diag(-A, 1/A, r^2, r^2 sin^2(theta))
    g_matrix = sp.Matrix([
        [-A, 0, 0, 0],
        [0, 1/A, 0, 0],
        [0, 0, r**2, 0],
        [0, 0, 0, r**2 * sp.sin(theta)**2]
    ])
    
    # 3. 執行生成器
    print(">>> 分析史瓦西黑洞 (Schwarzschild Black Hole) <<<")
    generator = ChristoffelGenerator([t, r, theta, phi], g_matrix)
    
    # 4. 輸出結果
    generator.print_results()

if __name__ == "__main__":
    sp.init_printing(use_unicode=True)
    run_gr_calculation()