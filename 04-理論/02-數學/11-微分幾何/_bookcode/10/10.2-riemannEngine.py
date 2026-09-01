import sympy as sp

class RiemannEngine:
    def __init__(self, coords, metric, name="Manifold"):
        """
        黎曼幾何全自動計算引擎
        Args:
            coords: 坐標變數列表 [x1, x2, ...]
            metric: SymPy Matrix g_ij
            name: 流形名稱
        """
        self.coords = coords
        self.dim = len(coords)
        self.g = metric
        self.name = name
        
        print(f"=== 啟動引擎: {self.name} (Dim={self.dim}) ===")
        
        # 0. 計算逆度量
        print("0. 計算逆度量 g^{ij}...")
        self.g_inv = self.g.inv()
        
        # 1. 計算 Christoffel Symbols
        print("1. 計算 Christoffel Symbols Γ^k_ij...")
        self.Gamma = self._compute_gamma()
        
        # 2. 計算 Riemann Tensor
        print("2. 計算 Riemann Tensor R^k_lij...")
        self.Riemann = self._compute_riemann()
        
        # 3. 計算 Ricci Tensor
        print("3. 計算 Ricci Tensor R_ij...")
        self.Ricci = self._compute_ricci()
        
        # 4. 計算 Scalar Curvature
        print("4. 計算 Scalar Curvature R...")
        self.R_scalar = self._compute_scalar()
        print(">>> 計算完成 <<<\n")

    def _compute_gamma(self):
        # 初始化 3D 陣列
        G = [[[sp.Integer(0) for _ in range(self.dim)] 
              for _ in range(self.dim)] for _ in range(self.dim)]
        
        for k in range(self.dim):
            for i in range(self.dim):
                for j in range(self.dim):
                    # 對稱性優化
                    if i > j:
                        G[k][i][j] = G[k][j][i]
                        continue
                        
                    val = sp.Integer(0)
                    for l in range(self.dim):
                        term = 0.5 * self.g_inv[k, l] * (
                            self.g[l, j].diff(self.coords[i]) +
                            self.g[i, l].diff(self.coords[j]) -
                            self.g[i, j].diff(self.coords[l])
                        )
                        val += term
                    G[k][i][j] = sp.simplify(val)
        return G

    def _compute_riemann(self):
        # 初始化 4D 陣列 R[rho][sigma][mu][nu]
        # 對應 R^rho_sigma,mu,nu
        R = [[[[sp.Integer(0) for _ in range(self.dim)] 
               for _ in range(self.dim)] 
              for _ in range(self.dim)] 
             for _ in range(self.dim)]
        
        for rho in range(self.dim):
            for sigma in range(self.dim):
                for mu in range(self.dim):
                    for nu in range(self.dim):
                        # 根據定義公式
                        # term1 = d_mu Gamma^rho_nu,sigma
                        term1 = self.Gamma[rho][nu][sigma].diff(self.coords[mu])
                        # term2 = d_nu Gamma^rho_mu,sigma
                        term2 = self.Gamma[rho][mu][sigma].diff(self.coords[nu])
                        
                        term3 = sp.Integer(0)
                        term4 = sp.Integer(0)
                        for lam in range(self.dim):
                            term3 += self.Gamma[rho][mu][lam] * self.Gamma[lam][nu][sigma]
                            term4 += self.Gamma[rho][nu][lam] * self.Gamma[lam][mu][sigma]
                            
                        val = term1 - term2 + term3 - term4
                        R[rho][sigma][mu][nu] = sp.simplify(val)
        return R

    def _compute_ricci(self):
        # R_sigma,nu = R^rho_sigma,rho,nu
        Ric = sp.Matrix.zeros(self.dim, self.dim)
        for sigma in range(self.dim):
            for nu in range(self.dim):
                val = sp.Integer(0)
                for rho in range(self.dim):
                    val += self.Riemann[rho][sigma][rho][nu]
                Ric[sigma, nu] = sp.simplify(val)
        return Ric

    def _compute_scalar(self):
        # R = g^sigma,nu R_sigma,nu
        val = sp.Integer(0)
        for sigma in range(self.dim):
            for nu in range(self.dim):
                val += self.g_inv[sigma, nu] * self.Ricci[sigma, nu]
        return sp.simplify(val)

    def report(self):
        """產生運算報告"""
        print(f"--- {self.name} 幾何報告 ---")
        print("[度量張量 g]:")
        sp.pprint(self.g)
        
        print("\n[純量曲率 R]:")
        sp.pprint(self.R_scalar)
        
        print("\n[高斯曲率 K (僅對 2D 有效, K = R/2)]:")
        if self.dim == 2:
            sp.pprint(sp.simplify(self.R_scalar / 2))
        else:
            print("N/A (維度 != 2)")
        print("-" * 30 + "\n")

# ==========================================
# 驗證案例 1: 球面 (Sphere)
# ==========================================
def verify_sphere():
    theta, phi = sp.symbols('theta phi', real=True)
    r = sp.symbols('r', real=True, positive=True) # 半徑常數
    
    # S^2 Metric: diag(r^2, r^2 sin^2(theta))
    g_sphere = sp.Matrix([
        [r**2, 0],
        [0, r**2 * sp.sin(theta)**2]
    ])
    
    engine = RiemannEngine([theta, phi], g_sphere, name="Sphere S2")
    engine.report()
    
    # 預期結果: K = 1/r^2
    expected_K = 1/r**2
    calc_K = sp.simplify(engine.R_scalar / 2)
    
    if sp.simplify(calc_K - expected_K) == 0:
        print(f"✅ 驗證成功: 球面曲率 K = {calc_K} (常數正曲率)")
    else:
        print(f"❌ 驗證失敗: 預期 {expected_K}, 得到 {calc_K}")
    print("="*40 + "\n")

# ==========================================
# 驗證案例 2: 環面 (Torus)
# ==========================================
def verify_torus():
    u, v = sp.symbols('u v', real=True)
    R, r = sp.symbols('R r', real=True, positive=True)
    
    # Torus Metric (來自先前的推導)
    # u: 大圓, v: 小圓
    g_torus = sp.Matrix([
        [(R + r*sp.cos(v))**2, 0],
        [0, r**2]
    ])
    
    engine = RiemannEngine([u, v], g_torus, name="Torus T2")
    engine.report()
    
    # 預期結果: K = cos(v) / (r(R + r cos(v)))
    # 注意: R_scalar = 2K
    expected_K = sp.cos(v) / (r * (R + r*sp.cos(v)))
    calc_K = sp.simplify(engine.R_scalar / 2)
    
    if sp.simplify(calc_K - expected_K) == 0:
        print("✅ 驗證成功: 環面曲率公式正確。")
        print("   - 外圈 (v=0): K > 0 (凸)")
        print("   - 內圈 (v=pi): K < 0 (鞍)")
    else:
        print(f"❌ 驗證失敗: \n預期 {expected_K}\n得到 {calc_K}")
        
    print("="*40 + "\n")

if __name__ == "__main__":
    sp.init_printing(use_unicode=True)
    verify_sphere()
    verify_torus()