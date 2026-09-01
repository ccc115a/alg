# crypto1_classical.py
from sympy.crypto.crypto import encipher_shift, decipher_shift
from sympy.crypto.crypto import encipher_vigenere, decipher_vigenere

def main():
    # --- 1. 凱撒密碼 (Shift Cipher) ---
    # 原理：將字母表移動 k 個位置
    plaintext = "THEQUICKBROWNFOX"
    key_shift = 1  # A -> B, B -> C ...

    # 加密
    cipher_shift = encipher_shift(plaintext, key_shift)
    print(f"原始訊息: {plaintext}")
    print(f"凱撒加密: {cipher_shift}")

    # 解密
    decrypted_shift = decipher_shift(cipher_shift, key_shift)
    print(f"凱撒解密: {decrypted_shift}")
    print("-" * 30)

    # --- 2. 維吉尼亞密碼 (Vigenère Cipher) ---
    # 原理：使用關鍵字進行多表代換
    key_vigenere = "LEMON"
    
    # 加密
    cipher_vig = encipher_vigenere(plaintext, key_vigenere)
    print(f"維吉尼亞密鑰: {key_vigenere}")
    print(f"維吉尼亞加密: {cipher_vig}")

    # 解密
    decrypted_vig = decipher_vigenere(cipher_vig, key_vigenere)
    print(f"維吉尼亞解密: {decrypted_vig}")

if __name__ == "__main__":
    main()