import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm

class CurvatureEngine:
    """
    黎曼幾何核心運算引擎
    輸入: 坐標系與度量張量 g_ij
    輸出: Christoffel符號, Riemann張量, Ricci張量, 純量曲率
    """
    def __init__(self, coords, metric_matrix):
        self.coords = coords
        self.dim = len(coords)
        self.g = metric_matrix
        self.g_inv = self.g.inv()
        
        print(f"--- 啟動曲率引擎 (Dim={self.dim}) ---")
        
        # 1. 計算 Christoffel Symbols
        print("1. 計算 Christoffel Symbols...")
        self.Gamma = self._compute_christoffel()
        
        # 2. 計算 Riemann Tensor
        print("2. 計算 Riemann Curvature Tensor...")
        self.Riemann = self._compute_riemann()
        
        # 3. 計算 Ricci Tensor
        print("3. 計算 Ricci Tensor...")
        self.Ricci = self._compute_ricci()
        
        # 4. 計算 Scalar Curvature
        print("4. 計算 Scalar Curvature...")
        self.R_scalar = self._compute_scalar()
        print(">>> 計算完成 <<<\n")

    def _compute_christoffel(self):
        # 初始化
        Gamma = [[[sp.Integer(0) for _ in range(self.dim)] 
                  for _ in range(self.dim)] for _ in range(self.dim)]
        
        for k in range(self.dim):
            for i in range(self.dim):
                for j in range(self.dim):
                    term = sp.Integer(0)
                    for m in range(self.dim):
                        # Γ^k_ij = 1/2 * g^km * (∂_i g_mj + ∂_j g_im - ∂_m g_ij)
                        term += 0.5 * self.g_inv[k, m] * (
                            self.g[m, j].diff(self.coords[i]) +
                            self.g[i, m].diff(self.coords[j]) -
                            self.g[i, j].diff(self.coords[m])
                        )
                    Gamma[k][i][j] = sp.simplify(term)
        return Gamma

    def _compute_riemann(self):
        # 初始化 4D 列表 R^k_lij
        R = [[[[sp.Integer(0) for _ in range(self.dim)] 
               for _ in range(self.dim)] 
              for _ in range(self.dim)] 
             for _ in range(self.dim)]
        
        # R^k_lij = ∂_l Γ^k_ij - ∂_i Γ^k_lj + Γ^k_lm Γ^m_ij - Γ^k_im Γ^m_lj
        for k in range(self.dim):
            for l in range(self.dim):
                for i in range(self.dim):
                    for j in range(self.dim):
                        
                        term1 = self.Gamma[k][i][j].diff(self.coords[l])
                        term2 = self.Gamma[k][l][j].diff(self.coords[i])
                        
                        term3 = sp.Integer(0)
                        term4 = sp.Integer(0)
                        for m in range(self.dim):
                            term3 += self.Gamma[k][l][m] * self.Gamma[m][i][j]
                            term4 += self.Gamma[k][i][m] * self.Gamma[m][l][j]
                            
                        val = term1 - term2 + term3 - term4
                        R[k][l][i][j] = sp.simplify(val)
        return R

    def _compute_ricci(self):
        # R_ij = R^k_ikj (縮並第1和第3個指標)
        Ric = sp.zeros(self.dim, self.dim)
        for i in range(self.dim):
            for j in range(self.dim):
                val = sp.Integer(0)
                for k in range(self.dim):
                    val += self.Riemann[k][i][k][j]
                Ric[i, j] = sp.simplify(val)
        return Ric

    def _compute_scalar(self):
        # R = g^ij R_ij
        val = sp.Integer(0)
        for i in range(self.dim):
            for j in range(self.dim):
                val += self.g_inv[i, j] * self.Ricci[i, j]
        return sp.simplify(val)

# ==========================================
# 視覺化專案：環面曲率熱圖
# ==========================================

def visualize_torus_curvature():
    # 1. 符號推導
    u, v = sp.symbols('u v', real=True)
    R_sym, r_sym = sp.symbols('R r', real=True, positive=True)
    
    # 環面度量 (Torus Metric)
    # 參數式: x=(R+r cos v)cos u, y=(R+r cos v)sin u, z=r sin v
    # 計算出的度量矩陣為對角矩陣:
    metric = sp.Matrix([
        [(R_sym + r_sym * sp.cos(v))**2, 0],
        [0, r_sym**2]
    ])
    
    # 啟動引擎
    engine = CurvatureEngine([u, v], metric)
    
    print(f"--- 結果分析 ---")
    # [修正點 1] 符號修正
    # 根據我們 Riemann Tensor 的定義方式，算出的 Scalar Curvature R 在凸面時可能為負。
    # 而高斯曲率 K 的幾何定義在凸面應為正。
    # 對於 2D 曲面，通常關係為 R = 2K 或 R = -2K (視 R 定義而定)。
    # 為了讓外圈(凸)顯示為正值，我們取 K = -R / 2
    gaussian_curvature = -engine.R_scalar / 2
    
    print("環面的高斯曲率 K:")
    sp.pprint(gaussian_curvature)
    
    # 2. 數值視覺化準備
    # 將符號表達式轉為 Python 函數
    K_func = sp.lambdify((v, R_sym, r_sym), gaussian_curvature, modules='numpy')
    
    # 設定幾何參數
    R_val, r_val = 3.0, 1.0
    
    # 生成網格
    # u: 大圓角度 (0~2pi), v: 小圓角度 (0~2pi)
    u_vals = np.linspace(0, 2*np.pi, 100)
    v_vals = np.linspace(0, 2*np.pi, 100)
    U, V = np.meshgrid(u_vals, v_vals)
    
    # 計算曲率值 (數值)
    K_vals = K_func(V, R_val, r_val)
    
    # 計算 3D 坐標 (用於繪圖)
    X = (R_val + r_val * np.cos(V)) * np.cos(U)
    Y = (R_val + r_val * np.cos(V)) * np.sin(U)
    Z = r_val * np.sin(V)
    
    # 3. 繪製熱圖
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # 正規化顏色範圍
    norm = plt.Normalize(K_vals.min(), K_vals.max())
    
    # 繪製曲面
    # facecolors 參數根據 K 值決定顏色
    surf = ax.plot_surface(X, Y, Z, 
                           facecolors=cm.coolwarm(norm(K_vals)), 
                           rstride=1, cstride=1, 
                           antialiased=False, shade=False)
    
    # [修正點 2] 修正 Colorbar 錯誤
    # 建立 ScalarMappable 供 Colorbar 使用
    m = cm.ScalarMappable(cmap=cm.coolwarm, norm=norm)
    m.set_array(K_vals)
    
    # 明確指定 ax 參數，讓 matplotlib 知道要依附在哪個子圖旁
    fig.colorbar(m, ax=ax, shrink=0.6, aspect=15, label='Gaussian Curvature (K)')
    
    # 設定標題與視角
    ax.set_title(f"Torus Curvature Heatmap (R={R_val}, r={r_val})\nRed = Positive (Convex), Blue = Negative (Saddle)")
    ax.set_box_aspect([3,3,1]) # 調整顯示比例
    plt.axis('off') # 隱藏坐標軸
    
    print("正在顯示圖形...")
    plt.show()

if __name__ == "__main__":
    visualize_torus_curvature()