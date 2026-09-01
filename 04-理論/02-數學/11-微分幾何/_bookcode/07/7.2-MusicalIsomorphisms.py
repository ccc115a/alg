import numpy as np

class MusicalMapper:
    """
    音樂同構映射器：負責指標升降 (Raising and Lowering Indices)
    """
    def __init__(self, g_matrix):
        """
        初始化時傳入度量張量 g_{ij}
        """
        self.g = np.array(g_matrix, dtype=float)
        
        # 檢查是否對稱
        if not np.allclose(self.g, self.g.T):
            raise ValueError("度量張量必須是對稱矩陣！")
            
        # 計算逆度量 g^{ij} (用於升指標)
        try:
            self.g_inv = np.linalg.inv(self.g)
        except np.linalg.LinAlgError:
            raise ValueError("度量張量必須是可逆的 (非退化)！")
            
        self.dim = self.g.shape[0]

    def flat(self, vector):
        """
        音樂降號 (Flat ♭): v^i -> v_i
        運算: v_i = g_{ij} v^j
        物理意義: 將「速度」轉換為「動量」(或功的微分形式)
        """
        # 使用矩陣乘法: G * v
        return self.g @ vector

    def sharp(self, covector):
        """
        音樂升號 (Sharp ♯): ω_i -> ω^i
        運算: ω^i = g^{ij} ω_j
        物理意義: 將「梯度」轉換為「梯度向量」
        """
        # 使用矩陣乘法: G_inv * ω
        return self.g_inv @ covector

    def norm(self, vector):
        """
        計算向量的黎曼長度 (Norm)
        |v|^2 = g_{ij} v^i v^j = v^i v_i
        """
        v_down = self.flat(vector)
        # 內積
        return np.sqrt(np.dot(vector, v_down))

    def angle(self, v1, v2):
        """
        計算兩個向量的夾角 (基於黎曼度量)
        cos(theta) = <v1, v2> / (|v1| |v2|)
        """
        # 內積 <v1, v2> = g_{ij} v1^i v2^j
        inner_prod = np.dot(v1, self.flat(v2))
        
        norms = self.norm(v1) * self.norm(v2)
        
        # 避免浮點數誤差導致 cos > 1
        cos_theta = np.clip(inner_prod / norms, -1.0, 1.0)
        return np.arccos(cos_theta)

# ==========================================
# 演示：龐加萊半平面上的升降操作
# ==========================================

def run_musical_demo():
    print("--- 專案 7.2: 音樂同構 (Flat ♭ & Sharp ♯) ---")
    
    # 假設我們在龐加萊半平面 M = {(x,y) | y>0}
    # 度量: g = [[1/y^2, 0], [0, 1/y^2]]
    
    # 定義兩個不同的點
    y_low = 1.0  # 低處 (度量係數 = 1)
    y_high = 10.0 # 高處 (度量係數 = 0.01)
    
    # 建立這兩個點處的映射器
    # 點 P1 (y=1)
    g_P1 = [[1/y_low**2, 0], [0, 1/y_low**2]]
    mapper_P1 = MusicalMapper(g_P1)
    
    # 點 P2 (y=10)
    g_P2 = [[1/y_high**2, 0], [0, 1/y_high**2]]
    mapper_P2 = MusicalMapper(g_P2)
    
    print(f"\n[場景設定]")
    print(f"  點 P1 (y={y_low}): 度量 g ≈ I (歐幾里得)")
    print(f"  點 P2 (y={y_high}): 度量 g ≈ 0.01 * I (非常稀疏)")
    
    # 定義一個切向量 v = (1, 0)
    # 這代表向右移動的單位速度
    v = np.array([1.0, 0.0])
    print(f"\n[輸入向量 v^i]: {v} (向右移動)")

    # ------------------------------------------------
    # 1. 執行 Flat (降號) 操作
    # ------------------------------------------------
    v_flat_P1 = mapper_P1.flat(v)
    v_flat_P2 = mapper_P2.flat(v)
    
    print(f"\n[1. Flat 操作 (v -> v_flat)]")
    print(f"  在 P1: v_i = {v_flat_P1}")
    print(f"  在 P2: v_i = {v_flat_P2}")
    print("  -> 觀察: 同樣的向量 v，在 P2 對應的 1-形式變得非常小。")
    print("     (物理意義: 在高空 P2 移動同樣快，動能/動量卻很小)")

    # ------------------------------------------------
    # 2. 執行 Sharp (升號) 操作
    # ------------------------------------------------
    # 假設我們有一個梯度場 df = (1, 0)
    # 這代表函數 f 在 x 方向變化率為 1
    df = np.array([1.0, 0.0])
    
    grad_P1 = mapper_P1.sharp(df)
    grad_P2 = mapper_P2.sharp(df)
    
    print(f"\n[2. Sharp 操作 (df -> grad f)]")
    print(f"  輸入 1-形式 ω_i: {df}")
    print(f"  在 P1 的梯度向量: {grad_P1}")
    print(f"  在 P2 的梯度向量: {grad_P2}")
    print("  -> 觀察: 同樣的變化率 df，在 P2 對應的梯度向量巨大無比。")
    print("     (幾何意義: 因為 P2 的尺子刻度很密(長度縮短)，要達成同樣的函數變化量，需要跨越更'多'的坐標格)")

    # ------------------------------------------------
    # 3. 驗證同構性質 (Inverse Check)
    # ------------------------------------------------
    print(f"\n[3. 驗證同構 (Sharp(Flat(v)) == v)]")
    v_restored = mapper_P2.sharp(v_flat_P2)
    print(f"  還原結果: {v_restored}")
    print(f"  是否相等: {np.allclose(v, v_restored)}")

    # ------------------------------------------------
    # 4. 長度計算
    # ------------------------------------------------
    len_P1 = mapper_P1.norm(v)
    len_P2 = mapper_P2.norm(v)
    print(f"\n[4. 黎曼長度 |v|]")
    print(f"  在 P1 長度: {len_P1:.4f}")
    print(f"  在 P2 長度: {len_P2:.4f}")
    print("  -> 這解釋了為什麼上一章的測地線喜歡往上跑 (長度變短)。")

if __name__ == "__main__":
    run_musical_demo()