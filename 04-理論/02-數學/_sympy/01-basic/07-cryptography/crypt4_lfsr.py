# crypt4_lfsr.py
from sympy.crypto.crypto import lfsr_sequence, lfsr_connection_polynomial
from sympy import FF

def main():
    # 1. 定義有限域 GF(2)
    # LFSR 通常在二進位環境下運作，即模 2 運算
    F2 = FF(2)
    
    # 2. 定義金鑰 (Key) 與 初始填充 (Fill)
    # 必須將整數列表轉換為 GF(2) 的元素列表
    raw_key = [1, 0, 0, 1]
    raw_fill = [1, 1, 0, 1]
    
    # 使用列表推導式進行轉換
    key = [F2(x) for x in raw_key]
    fill = [F2(x) for x in raw_fill]
    
    print(f"反饋係數 (Key): {key}")
    print(f"初始狀態 (Fill): {fill}")

    # 3. 生成序列
    # 生成 20 個位元
    seq = lfsr_sequence(key, fill, 20)
    print(f"生成的偽隨機序列 (20 bits): {seq}")

    # 4. 根據序列反推連接多項式 (Berlekamp-Massey 演算法)
    poly = lfsr_connection_polynomial(seq)
    print(f"反推連接多項式: {poly}")

if __name__ == "__main__":
    main()