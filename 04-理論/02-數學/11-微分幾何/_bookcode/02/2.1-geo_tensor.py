import numpy as np

class GeoTensor:
    def __init__(self, data, indices_config):
        """
        初始化幾何張量。
        
        Args:
            data (list or np.ndarray): 張量的數值數據
            indices_config (str): 指標配置字串。
                                  'u' (up) 代表逆變/上指標
                                  'd' (down) 代表協變/下指標
                                  例如: 'ud' 代表 T^i_j
        """
        self.data = np.array(data)
        self.config = indices_config
        self.rank = len(indices_config)
        
        # 檢查維度是否匹配
        if self.data.ndim != self.rank:
            raise ValueError(f"數據維度 ({self.data.ndim}) 與指標配置長度 ({self.rank}) 不符！")

    def __repr__(self):
        """物件的文字表示，方便除錯"""
        return f"GeoTensor(rank={self.rank}, config='{self.config}', shape={self.data.shape})\n{self.data}"

    def __add__(self, other):
        """實作張量加法: A + B"""
        if self.config != other.config:
            raise ValueError(f"無法相加不同指標類型的張量: {self.config} vs {other.config}")
        return GeoTensor(self.data + other.data, self.config)

    def tensor_product(self, other):
        """
        實作張量積: self (x) other
        數學: C^{...}_{...} = A^{...}_{...} * B^{...}_{...}
        結果的階數是兩者之和。
        """
        # 使用 numpy 的 outer product 擴展維度
        # np.tensordot axes=0 等同於 outer product
        new_data = np.tensordot(self.data, other.data, axes=0)
        new_config = self.config + other.config
        return GeoTensor(new_data, new_config)

    def contract(self, idx1, idx2):
        """
        實作張量縮並 (Contraction)。
        指定兩個指標位置進行求和。
        
        Args:
            idx1 (int): 第一個指標的位置 (0-based)
            idx2 (int): 第二個指標的位置 (0-based)
        """
        if idx1 == idx2:
            raise ValueError("不能對同一個指標位置進行縮並")
        
        # 幾何檢查：通常我們只允許縮並一個 'u' 和一個 'd'
        # 這裡為了演示彈性，僅發出警告或嚴格限制
        type1, type2 = self.config[idx1], self.config[idx2]
        if type1 == type2:
            print(f"⚠️ 警告: 您正在縮並兩個相同類型的指標 ({type1} 和 {type2})，這在非歐幾何中通常是不合法的。")

        # 使用 numpy.trace 來縮並? 
        # 不，trace 只能處理 2D。對於高維張量，einsum 最合適。
        # 這裡我們動態生成 einsum 字串。
        
        # 生成指標標籤列表: ['a', 'b', 'c', ...]
        chars = [chr(97 + i) for i in range(self.rank)]
        
        # 讓要縮並的兩個位置使用相同的字元
        target_char = chars[idx1] # 取出第一個位置的字元
        chars[idx2] = target_char # 將第二個位置也設為該字元
        
        # 構建 einsum 字串，例如 "abc, -> ac" (若 b 被縮並)
        input_str = "".join(chars)
        
        # 輸出字串應排除被縮並的字元
        # 注意: 這裡 chars 裡有重複的字元，我們需要一個只包含唯一字元且排除了 target_char 的列表
        output_chars = [c for i, c in enumerate(chars) if i != idx1 and i != idx2]
        output_str = "".join(output_chars)
        
        einsum_cmd = f"{input_str}->{output_str}"
        # print(f"DEBUG: 執行縮並 {einsum_cmd}") 
        
        new_data = np.einsum(einsum_cmd, self.data)
        
        # 更新配置字串，移除被縮並的指標
        # 注意索引變化：移除一個後，後面的索引會位移，所以要小心處理
        indices_to_remove = sorted([idx1, idx2], reverse=True)
        new_config_list = list(self.config)
        for idx in indices_to_remove:
            del new_config_list[idx]
        new_config = "".join(new_config_list)
        
        return GeoTensor(new_data, new_config)

# ==========================================
# 測試與演示區
# ==========================================

if __name__ == "__main__":
    print("--- 1. 建立向量與 1-形式 ---")
    # 逆變向量 v^i (上指標)
    v = GeoTensor([1, 2, 3], 'u')
    print(f"向量 v^i: \n{v}")
    
    # 協變向量 (對偶向量/1-形式) w_j (下指標)
    w = GeoTensor([4, 5, 6], 'd')
    print(f"1-形式 w_j: \n{w}")

    print("\n--- 2. 張量積 (Tensor Product) ---")
    # T^i_j = v^i * w_j
    T = v.tensor_product(w)
    print(f"張量 T = v (x) w (預期配置 'ud'):")
    print(T)
    
    print("\n--- 3. 縮並 (Contraction) ---")
    # 計算標量 s = v^i w_i
    # 在 T^i_j ('ud') 中，縮並第 0 個和第 1 個指標
    s = T.contract(0, 1)
    print(f"縮並 T 的兩個指標 (相當於 v dot w):")
    print(s) # 應該是 1*4 + 2*5 + 3*6 = 32
    
    print("\n--- 4. 複雜案例: 黎曼度量縮並 ---")
    # 假設有一個度量張量 g_{ij} ('dd')
    g_data = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]) # 歐幾里得度量
    g = GeoTensor(g_data, 'dd')
    
    # 兩個向量 u^k, v^l
    u = GeoTensor([1, 0, 0], 'u')
    
    # 構造一個巨大的張量 M = g (x) u (x) v
    # 結構: g_{ij} u^k v^l -> 配置 'dduu'
    M = g.tensor_product(u).tensor_product(v)
    print(f"複合張量 M (g_{{ij}} u^k v^l): {M.config}")
    
    # 我們想計算內積 <u, v> = g_{ij} u^i v^j
    # 這需要兩次縮並
    
    # 目前 M 的指標: 0:d, 1:d, 2:u, 3:u
    # 第一次縮並: 讓 g 的第 2 個下指標 (idx 1) 吃掉 v 的上指標 (idx 3)
    # 注意: 我們要小心選擇指標。讓我們模擬 g_{ij} v^j -> v_i
    step1 = M.contract(1, 3) 
    print(f"縮並一次後 (g_{{ij}} u^k v^j -> ...): {step1.config}")
    # 剩餘指標來源: 原來的 0(d), 2(u)。 原來的 1 和 3 消失了。
    # 現在 step1 的配置是 'du' (第0個是原本的g_i, 第1個是原本的u^k)
    
    # 第二次縮並: 讓 g 的第 1 個下指標 (現在 step1 的 idx 0) 吃掉 u 的上指標 (現在 step1 的 idx 1)
    result = step1.contract(0, 1)
    print(f"縮並兩次後 (結果應為純量):")
    print(result)