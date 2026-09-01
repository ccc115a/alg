import cmath # 使用 cmath 模組處理複數運算 (complex math)
import math
from typing import List

# 為了簡化，我們使用 List[float] 或 List[complex] 作為資料型別

## 1. 離散傅立葉正轉換 (DFT)
def dft(f: List[float]) -> List[complex]:
    """
    計算離散傅立葉正轉換 (Discrete Fourier Transform)。
    
    參數:
        f (List[float]): 輸入的實數序列 f[n]。
        
    回傳:
        List[complex]: 轉換後的複數序列 F[k]。
    """
    N = len(f)
    F = []
    
    for k in range(N): # 輸出序列的索引 k (頻率)
        Fk = 0j # 初始化為複數 0
        for n in range(N): # 輸入序列的索引 n (時間/空間)
            # 指數部分的負角: -i * (2*pi/N) * k * n
            exponent = -2j * cmath.pi * k * n / N
            # e^exponent
            twiddle_factor = cmath.exp(exponent)
            
            Fk += f[n] * twiddle_factor
            
        F.append(Fk)
        
    return F

## 2. 離散傅立葉逆轉換 (IDFT)
def idft(F: List[complex]) -> List[complex]:
    """
    計算離散傅立葉逆轉換 (Inverse Discrete Fourier Transform)。
    
    參數:
        F (List[complex]): 輸入的複數序列 F[k] (頻率域)。
        
    回傳:
        List[complex]: 轉換後的複數序列 f[n] (時域/空間域)。
    """
    N = len(F)
    f = []
    
    for n in range(N): # 輸出序列的索引 n (時間/空間)
        fn = 0j # 初始化為複數 0
        for k in range(N): # 輸入序列的索引 k (頻率)
            # 指數部分的正角: +i * (2*pi/N) * k * n
            exponent = 2j * cmath.pi * k * n / N
            # e^exponent
            twiddle_factor = cmath.exp(exponent)
            
            fn += F[k] * twiddle_factor
            
        # 最後乘以縮放因子 1/N
        fn /= N
        f.append(fn)
        
    return f

## 3. 驗證函數 (正轉換再逆轉換)
def verify_dft_idft(f_original: List[float], tolerance: float = 1e-9):
    """
    驗證 DFT -> IDFT 的過程是否能還原原序列。
    
    參數:
        f_original (List[float]): 原始輸入的實數序列。
        tolerance (float): 浮點數比較容忍度。
    """
    print(f"--- 驗證序列長度 N = {len(f_original)} ---")
    print(f"原始序列 f_original: {[round(x, 4) for x in f_original]}")
    
    # 步驟 1: 正轉換 (DFT)
    F_transformed = dft(f_original)
    print(f"\nDFT 結果 F (部分): {[round(c.real, 4) + round(c.imag, 4) * 1j for c in F_transformed[:4]]}...")

    # 步驟 2: 逆轉換 (IDFT)
    f_reconstructed = idft(F_transformed)
    
    # 將逆轉換結果的虛部忽略 (因為原始輸入是實數，虛部應該接近 0)
    # 並只保留實數部分
    f_reconstructed_real = [c.real for c in f_reconstructed]
    print(f"IDFT 結果 f_reconstructed: {[round(x, 4) for x in f_reconstructed_real]}")

    # 步驟 3: 比較驗證
    is_restored = True
    for original, reconstructed in zip(f_original, f_reconstructed_real):
        # 檢查實數部分是否接近
        if abs(original - reconstructed) > tolerance:
            is_restored = False
            print(f"\n❌ 失敗: 原值 {original} vs. 還原值 {reconstructed} (差異太大)")
            break
        # 檢查虛數部分是否接近 0
        if abs(reconstructed - f_reconstructed[f_reconstructed_real.index(reconstructed)].real) > tolerance :
            is_restored = False
            print(f"\n❌ 失敗: 虛數部分 {f_reconstructed[f_reconstructed_real.index(reconstructed)].imag} 不接近 0")
            break

    if is_restored:
        print("\n✅ 驗證成功: 原始序列與還原序列在容忍度內匹配。")
    else:
        print("\n❌ 驗證失敗: 原始序列與還原序列不匹配。")

# --- 測試案例 ---

# 案例一: 簡單的常數序列
f1 = [1.0, 1.0, 1.0, 1.0]
verify_dft_idft(f1)

print("\n" + "="*50 + "\n")

# 案例二: 簡單的週期訊號 (餘弦波)
N2 = 8
# 這裡建立一個簡單的離散餘弦波
f2 = [math.cos(2 * math.pi * 1 * n / N2) for n in range(N2)]
verify_dft_idft(f2)

print("\n" + "="*50 + "\n")

# 案例三: 脈衝訊號
f3 = [10.0, 0.0, 0.0, 0.0, 0.0]
verify_dft_idft(f3)