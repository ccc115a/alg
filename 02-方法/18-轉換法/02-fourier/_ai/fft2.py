import numpy as np
import matplotlib.pyplot as plt

# --- 1. 創建原始時域訊號 f(t) ---
sampling_rate = 1000  # 採樣頻率 (Hz)
duration = 1.0        # 訊號長度 (秒)
N = int(sampling_rate * duration) # 採樣點數

t = np.linspace(0.0, duration, N, endpoint=False)

# 創建一個複雜的訊號 f(t)：由 5 Hz 和 50 Hz 的正弦波疊加而成
f1 = 5.0  # 頻率 1 (Hz)
f2 = 50.0 # 頻率 2 (Hz)
f_t = 2.0 * np.sin(2 * np.pi * f1 * t) + 1.5 * np.sin(2 * np.pi * f2 * t)

# --- 2. 進行快速傅立葉轉換 (FFT) ---
F_omega = np.fft.fft(f_t)

# --- 3. 處理頻率軸和頻譜數據 (用於繪圖) ---
# 計算實際的頻率軸 (Hz)
frequencies = np.fft.fftfreq(N, 1.0/sampling_rate)

# 將 FFT 結果和頻率軸都進行位移，將零頻率移到中心
F_omega_shifted = np.fft.fftshift(F_omega)
frequencies_shifted = np.fft.fftshift(frequencies)

# 繪圖時通常使用頻譜的振幅 (絕對值)
amplitude_spectrum = np.abs(F_omega_shifted) / N # 振幅正規化

# --- 4. 進行快速傅立葉反轉換 (IFFT) ---
f_recovered_t = np.fft.ifft(F_omega)
f_recovered_t = np.real(f_recovered_t)

# --- 5. 驗證與視覺化 ---

# 檢查原訊號與還原訊號之間的差異 (誤差)
max_error = np.max(np.abs(f_t - f_recovered_t))
print(f"原始訊號與還原訊號的最大絕對誤差為: {max_error:.10f}")
if max_error < 1e-9:
    print("\n✅ 傅立葉轉換是可逆的：反轉換成功還原了原始訊號。")
else:
    print("\n❌ 驗證失敗：誤差超出預期。")


plt.figure(figsize=(14, 10))

# --- 第一張圖：原始時域訊號 ---
plt.subplot(3, 1, 1)
plt.plot(t, f_t, label='$f(t)$ (原始訊號)', color='blue')
plt.title('1. 時域訊號 $f(t)$ (原始輸入)')
plt.xlabel('時間 (秒)')
plt.ylabel('振幅')
plt.grid(True)
plt.legend()


# --- 第二張圖：頻域訊號 (中間結果) ---
plt.subplot(3, 1, 2)
# 只顯示正頻率部分，因為對於實數訊號，負頻率是正頻率的鏡像
positive_freq_indices = frequencies_shifted >= 0
plt.plot(
    frequencies_shifted[positive_freq_indices], 
    amplitude_spectrum[positive_freq_indices] * 2, # 乘以 2 恢復實際振幅
    color='red'
)
# 標記出我們已知的頻率
plt.axvline(x=f1, color='gray', linestyle='--', linewidth=0.8, label=f'{f1} Hz')
plt.axvline(x=f2, color='gray', linestyle='--', linewidth=0.8, label=f'{f2} Hz')

plt.title('2. 頻域訊號 $F(\\omega)$ 振幅頻譜 (FFT 結果)')
plt.xlabel('頻率 (Hz)')
plt.ylabel('振幅')
plt.xlim(0, 100) # 僅顯示低頻範圍，使重點突出
plt.grid(True)
plt.legend()


# --- 第三張圖：還原後的時域訊號 ---
plt.subplot(3, 1, 3)
plt.plot(t, f_t, label='$f(t)$ (原始訊號)', color='blue', linestyle='--')
plt.plot(t, f_recovered_t, label='$f_{recovered}(t)$ (還原訊號)', color='green', alpha=0.7)
plt.title('3. IFFT 還原訊號 $f_{recovered}(t)$')
plt.xlabel('時間 (秒)')
plt.ylabel('振幅')
plt.grid(True)
plt.legend()


plt.tight_layout()
plt.show()