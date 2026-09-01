# 數學原理解說 -- 
from dgeom.sym import riemann_tensor, ricci_tensor, ricci_scalar, einstein_tensor
import sympy as sp

def test_minkowski():
    # --- 重新定義符號和度量 (Minkowski Metric) ---
    # 使用 (t, x, y, z) 笛卡爾座標
    t, x, y, z = sp.symbols('t x y z')
    coords = [t, x, y, z]

    # 閔可夫斯基協變度規 G_cov (-+++)
    G_cov = sp.Matrix([
        [-1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])

    # 逆變度規 G_cont
    G_cont = G_cov.inv()

    print("## 1. 閔可夫斯基時空 (狹義相對論) 的度規:")
    print(f"G_cov =")
    print(G_cov)
    print("-" * 50)

    print("## 2. 黎曼曲率張量 R^rho_{sigma mu nu} (示範):")
    # 計算 R^t_{x t x} (rho=0, sigma=1, mu=0, nu=1)
    R_t_xtx = riemann_tensor(0, 1, 0, 1, G_cont, G_cov, coords)
    print(f"R^t_{{xtx}} = {R_t_xtx}")
    print("-" * 50)

    print("## 3. 里奇張量 R_mn:")
    # [修正] 現在 ricci_tensor 直接回傳整個矩陣
    R_mn = ricci_tensor(G_cont, G_cov, coords)
    print(f"R_mn =")
    print(R_mn)
    
    # 驗證是否全為 0
    if R_mn == sp.zeros(4, 4):
        print(">> 驗證成功：Ricci 張量所有分量皆為 0")
    print("-" * 50)

    print("## 4. 里奇純量 R:")
    # [修正] 呼叫方式改為 (R_mn, G_cont)
    R_scalar = ricci_scalar(R_mn, G_cont)
    print(f"R = {R_scalar}")
    print("-" * 50)

    print("## 5. 愛因斯坦張量 G_mn:")
    # [修正] 現在 einstein_tensor 也是矩陣運算，傳入 (R_mn, R_scalar, G_cov)
    G_mn = einstein_tensor(R_mn, R_scalar, G_cov)
    print(f"G_mn =")
    print(G_mn)
    
    if G_mn == sp.zeros(4, 4):
        print(">> 驗證成功：愛因斯坦張量所有分量皆為 0")
    print("-" * 50)

    print("結論：平坦時空的所有曲率張量均為 0。")


if __name__ == "__main__":
    test_minkowski()

