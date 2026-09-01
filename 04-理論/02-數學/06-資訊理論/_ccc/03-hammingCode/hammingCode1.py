# https://gemini.google.com/app/32ca6a3278d7b321
import numpy as np

def hamming_encode_7_4(data_bits: list) -> list:
    """
    (7, 4) 漢明碼編碼器。
    
    參數:
        data_bits (list): 4 位元資訊，格式為 [D7, D6, D5, D3]。
                           例如：[1, 0, 1, 1]
                           
    返回:
        list: 7 位元碼字 [C7, C6, C5, C4, C3, C2, C1]。
    """
    if len(data_bits) != 4:
        raise ValueError("輸入資料必須是 4 位元。")

    # D7, D6, D5, D3 按照位元索引順序排列 (從高位到低位，P位是0)
    D7, D6, D5, D3 = data_bits[0], data_bits[1], data_bits[2], data_bits[3]

    # 1. 計算校驗位 (Parity bits)
    # 使用偶校驗 (Even Parity)
    P1 = D3 ^ D5 ^ D7  # P1 檢查 C1, C3, C5, C7 (奇數和 1)
    P2 = D3 ^ D6 ^ D7  # P2 檢查 C2, C3, C6, C7 (位元 2 的和 2)
    P4 = D5 ^ D6 ^ D7  # P4 檢查 C4, C5, C6, C7 (位元 4 的和 4)

    # 2. 組成 7 位元碼字 [C7, C6, C5, C4, C3, C2, C1]
    # C7=D7, C6=D6, C5=D5, C4=P4, C3=D3, C2=P2, C1=P1
    codeword = [D7, D6, D5, P4, D3, P2, P1]
    
    return codeword

def hamming_decode_7_4(codeword: list) -> tuple:
    """
    (7, 4) 漢明碼解碼器與糾錯機制。

    參數:
        codeword (list): 接收到的 7 位元碼字 [C7, C6, C5, C4, C3, C2, C1]。

    返回:
        tuple: (data_bits, error_position)
               - data_bits (list): 糾正後的 4 位元資訊 [D7, D6, D5, D3]。
               - error_position (int): 錯誤位元的位置 (1-7)，若為 0 則表示無錯誤或多位元錯誤。
    """
    if len(codeword) != 7:
        raise ValueError("接收到的碼字必須是 7 位元。")

    # 碼字位元 C7, C6, C5, C4, C3, C2, C1
    C7, C6, C5, C4, C3, C2, C1 = codeword

    # 1. 計算三個校驗和 (Syndrome)
    # 每個 S_i 檢查對應的校驗位 P_i 檢查的位元組是否仍保持偶校驗
    
    # S1 檢查 C1, C3, C5, C7 (對應 P1)
    S1 = C1 ^ C3 ^ C5 ^ C7
    
    # S2 檢查 C2, C3, C6, C7 (對應 P2)
    S2 = C2 ^ C3 ^ C6 ^ C7
    
    # S4 檢查 C4, C5, C6, C7 (對應 P4)
    S4 = C4 ^ C5 ^ C6 ^ C7
    
    # 2. 確定錯誤位元位置 (Error Position)
    # 錯誤位元位置 E = 4*S4 + 2*S2 + 1*S1
    error_position = 4 * S4 + 2 * S2 + 1 * S1
    
    corrected_codeword = list(codeword)
    
    if error_position != 0:
        print(f"-> 偵測到單一位元錯誤，位置：{error_position}。")
        # 3. 糾正錯誤
        # 將錯誤位元翻轉 (0 變 1，1 變 0)。由於索引是從 0 開始，而位置是從 1 開始，
        # 且碼字是 [C7...C1]，所以索引需要轉換 (7 - error_position)。
        # 或者直接用 error_position 從右邊數過來 (C1 是 index 6, C7 是 index 0)
        # 由於我們定義的碼字是 [C7, C6, C5, C4, C3, C2, C1]，索引如下：
        # C7(0), C6(1), C5(2), C4(3), C3(4), C2(5), C1(6)
        
        # 映射關係：位置 (1-7) -> 列表索引 (0-6)
        # 1 -> 6, 2 -> 5, 3 -> 4, 4 -> 3, 5 -> 2, 6 -> 1, 7 -> 0
        index_to_flip = 7 - error_position
        
        # 翻轉位元 (XOR 1)
        if 0 <= index_to_flip < 7:
             corrected_codeword[index_to_flip] = corrected_codeword[index_to_flip] ^ 1
        else:
             print("錯誤：計算的錯誤位置超出範圍。")
             
    else:
        print("-> 未偵測到單一位元錯誤 (可能是無錯誤或多位元錯誤)。")

    # 4. 提取資訊位
    # 資訊位位於 corrected_codeword 的 C7, C6, C5, C3 (索引 0, 1, 2, 4)
    D7 = corrected_codeword[0]
    D6 = corrected_codeword[1]
    D5 = corrected_codeword[2]
    D3 = corrected_codeword[4]
    
    data_bits = [D7, D6, D5, D3]
    
    return data_bits, error_position

# --- 範例應用 ---
if __name__ == "__main__":
    
    # 原始 4 位元資訊
    original_data = [1, 0, 1, 1]  # D7=1, D6=0, D5=1, D3=1
    print(f"原始資料 (D7 D6 D5 D3): {original_data}")
    print("-" * 30)

    # 1. 執行編碼
    encoded_codeword = hamming_encode_7_4(original_data)
    print(f"編碼結果 (C7 C6 C5 C4 C3 C2 C1): {encoded_codeword}") 
    # 預期 P1 = 1^1^1 = 1; P2 = 1^0^1 = 0; P4 = 1^0^1 = 0
    # 預期碼字: [1, 0, 1, 0, 1, 0, 1]

    print("\n" + "=" * 40 + "\n")

    # 2. 模擬傳輸錯誤 (解碼驗證)
    
    # 情況 A: 無錯誤
    received_A = encoded_codeword
    decoded_data_A, error_pos_A = hamming_decode_7_4(received_A)
    print(f"接收碼字 A: {received_A}")
    print(f"解碼結果 A: {decoded_data_A}")
    print(f"原始 == 解碼？ {original_data == decoded_data_A}")

    print("\n" + "-" * 30)

    # 情況 B: 發生一位元錯誤 (假設 C3 發生錯誤，即位置 3 發生錯誤)
    # C3 位於索引 4
    error_index = 4  # 翻轉 C3
    received_B = list(encoded_codeword)
    received_B[error_index] = received_B[error_index] ^ 1 # 模擬翻轉
    
    print(f"模擬傳輸錯誤 B (位置 3 錯誤): {received_B}")
    
    decoded_data_B, error_pos_B = hamming_decode_7_4(received_B)
    print(f"錯誤位置偵測結果: {error_pos_B}")
    print(f"解碼結果 B: {decoded_data_B}")
    print(f"原始 == 解碼？ {original_data == decoded_data_B} (應為 True)")

    print("\n" + "-" * 30)
    
    # 情況 C: 發生一位元錯誤 (假設 C7 發生錯誤，即位置 7 發生錯誤)
    error_index_C = 0  # 翻轉 C7
    received_C = list(encoded_codeword)
    received_C[error_index_C] = received_C[error_index_C] ^ 1 # 模擬翻轉
    
    print(f"模擬傳輸錯誤 C (位置 7 錯誤): {received_C}")
    
    decoded_data_C, error_pos_C = hamming_decode_7_4(received_C)
    print(f"錯誤位置偵測結果: {error_pos_C}")
    print(f"解碼結果 C: {decoded_data_C}")
    print(f"原始 == 解碼？ {original_data == decoded_data_C} (應為 True)")
