# crypto3_elgamal.py
from sympy.crypto.crypto import encipher_elgamal, decipher_elgamal
from sympy import primitive_root, randprime
import random

def main():
    # 1. 設置參數
    # 選擇一個質數 p 和一個原根 g
    p = randprime(100, 500)
    g = primitive_root(p)
    
    # 2. 生成金鑰
    # 私鑰 a: 隨機整數
    a = random.randint(2, p - 2)
    # 公鑰 ha: g^a mod p
    ha = pow(g, a, p)
    
    # 公鑰結構通常為 (p, g, ha)
    pk = (p, g, ha) 
    
    print(f"系統參數: p={p}, g={g}")
    print(f"私鑰 a: {a}")
    print(f"公鑰 ha: {ha}")

    # 3. 加密
    # 訊息 m 必須小於 p
    msg = 42
    print(f"\n原始訊息: {msg}")
    
    # r 是一個隨機數 (用於每次產生不同的密文)
    r = random.randint(2, p - 2)
    ciphertext = encipher_elgamal(msg, pk, r)
    print(f"加密後 (c1, c2): {ciphertext}")

    # 4. 解密
    # 修正重點：SymPy 預期的私鑰結構也是 (p, g, a)，即使 g 在解密時用不到
    decrypted_msg = decipher_elgamal(ciphertext, (p, g, a))
    
    print(f"解密後: {decrypted_msg}")
    
    # 驗證
    assert msg == decrypted_msg
    print("驗證成功！")

if __name__ == "__main__":
    main()