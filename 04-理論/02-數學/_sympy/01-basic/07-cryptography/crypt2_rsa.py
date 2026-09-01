# crypto2_rsa.py
from sympy.crypto.crypto import rsa_private_key, encipher_rsa, decipher_rsa
from sympy import randprime

def main():
    print("正在生成 RSA 金鑰 (可能需要幾秒鐘)...")
    
    # 1. 生成兩個大質數 p, q
    # 為了範例快速執行，選取較小的範圍，實際應用需更大 (如 2048 bits)
    p = randprime(1000, 2000)
    q = randprime(2000, 3000)
    e = 65537  # 常用的公鑰指數

    # 計算模數 n
    n = p * q
    
    # 2. 生成金鑰
    # 公鑰 (Public Key): (n, e)
    # 私鑰 (Private Key): (n, d)
    pub_key = (n, e)
    priv_key = rsa_private_key(p, q, e)
    
    print(f"質數 p={p}, q={q}")
    print(f"公鑰: {pub_key}")
    print(f"私鑰: {priv_key}")

    # 3. 加密訊息 (訊息必須是小於 n 的整數)
    message = 123456
    print(f"\n原始數字訊息: {message}")

    ciphertext = encipher_rsa(message, pub_key)
    print(f"加密後 (密文): {ciphertext}")

    # 4. 解密訊息
    decrypted_msg = decipher_rsa(ciphertext, priv_key)
    print(f"解密後: {decrypted_msg}")
    
    assert message == decrypted_msg

if __name__ == "__main__":
    main()