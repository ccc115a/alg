import cmath

def dft(x):
    """
    計算離散傅立葉變換 (DFT)。
    參數:
    x: 包含實數或複數的列表或元組。

    回傳:
    包含複數的列表，為 DFT 結果。
    """
    N = len(x)
    X = []
    for k in range(N):  # 頻域的索引 k
        re = 0.0
        im = 0.0
        for n in range(N):  # 時域的索引 n
            angle = -2 * cmath.pi * k * n / N
            re += x[n] * cmath.cos(angle)
            im += x[n] * cmath.sin(angle)
        X.append(complex(re, im))
    return X


def idft(X):
    """
    計算反離散傅立葉變換 (IDFT)。
    參數:
    X: 包含複數的列表，為 DFT 結果。

    回傳:
    包含複數的列表，為 IDFT 結果。
    """
    N = len(X)
    x = []
    for n in range(N):  # 時域的索引 n
        re = 0.0
        im = 0.0
        for k in range(N):  # 頻域的索引 k
            angle = 2 * cmath.pi * k * n / N
            re += X[k].real * cmath.cos(angle) - X[k].imag * cmath.sin(angle)
            im += X[k].real * cmath.sin(angle) + X[k].imag * cmath.cos(angle)
        x_n = complex(re / N, im / N)
        x.append(x_n)
    return x

# --- 驗證程式 ---
def verify_transform(original_sequence):
    """
    驗證 DFT 後再 IDFT 能否還原原始序列。
    """
    print("--- 原始序列 ---")
    # print([round(val, 4) for val in original_sequence])
    rounded_sequence = [complex(round(c.real, 4), round(c.imag, 4)) for c in original_sequence]
    print()

    # 正向傅立葉變換
    X = dft(original_sequence)
    print("\n--- 傅立葉正變換結果（頻域）---")
    print([f"{c.real:.4f} + {c.imag:.4f}j" for c in X])
    
    # 反向傅立葉變換
    reconstructed_x = idft(X)
    print("\n--- 傅立葉逆變換結果（時域）---")
    print([f"{c.real:.4f} + {c.imag:.4f}j" for c in reconstructed_x])

    # 檢查還原是否成功
    # 由於浮點數誤差，我們檢查實部是否接近原始值，虛部是否接近 0
    success = True
    tolerance = 1e-9
    for i in range(len(original_sequence)):
        original_val = original_sequence[i]
        reconstructed_val_real = reconstructed_x[i].real
        reconstructed_val_imag = reconstructed_x[i].imag

        if abs(original_val - reconstructed_val_real) > tolerance or abs(reconstructed_val_imag) > tolerance:
            success = False
            break

    print("\n--- 驗證結果 ---")
    if success:
        print("驗證成功：序列經過正變換與逆變換後，被成功還原。")
    else:
        print("驗證失敗：還原序列與原始序列不符。")

# 範例 1: 簡單的實數序列
sequence1 = [1, 2, 3, 4]
verify_transform(sequence1)

print("\n" + "="*50 + "\n")

# 範例 2: 包含正弦波的序列
# 這裡使用 cmath.sin 等函數來產生訊號
sequence2 = [cmath.sin(2 * cmath.pi * n / 8) for n in range(8)]
verify_transform(sequence2)