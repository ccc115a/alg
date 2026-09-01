import numpy as np
import matplotlib.pyplot as plt

# --- 1. 創建原始時域訊號 f(t) ---
# 設置參數
sampling_rate = 1000  # 採樣頻率 (Hz)
duration = 1.0        # 訊號長度 (秒)
N = int(sampling_rate * duration) # 採樣點數

# 建立時間向量 t
t = np.linspace(0.0, duration, N, endpoint=False)

# 創建一個複雜的訊號 f(t)：由 5 Hz 和 50 Hz 的正弦波疊加而成
f1 = 5.0  # 頻率 1 (Hz)
f2 = 50.0 # 頻率 2 (Hz)
f_t = 2.0 * np.sin(2 * np.pi * f1 * t) + 1.5 * np.sin(2 * np.pi * f2 * t)

# --- 2. 進行快速傅立葉轉換 (FFT) ---
# np.fft.fft 執行離散傅立葉轉換
F_omega = np.fft.fft(f_t)

# --- 3. 進行快速傅立葉反轉換 (IFFT) ---
# np.fft.ifft 執行反離散傅立葉轉換
f_recovered_t = np.fft.ifft(F_omega)

# IFFT 的結果是複數，但對於實數輸入，虛數部分應該非常接近零。
# 我們只取實數部分作為還原訊號。
f_recovered_t = np.real(f_recovered_t)

# --- 4. 驗證與視覺化 ---

# 檢查原訊號與還原訊號之間的差異 (誤差)
max_error = np.max(np.abs(f_t - f_recovered_t))
print(f"原始訊號與還原訊號的最大絕對誤差為: {max_error:.10f}")

# 傅立葉轉換的性質：轉換再反轉換，能還原訊號
if max_error < 1e-9:
    print("\n✅ 驗證成功：最大誤差極小，傅立葉反轉換成功還原了原始訊號。")
else:
    print("\n❌ 驗證失敗：誤差超出預期。")


# 繪圖比較
plt.figure(figsize=(12, 6))

# 原始訊號
plt.subplot(2, 1, 1)
plt.plot(t, f_t, label='$f(t)$ (原始訊號)', color='blue')
plt.title('原始時域訊號 $f(t)$')
plt.xlabel('時間 (秒)')
plt.ylabel('振幅')
plt.legend()

# 還原訊號（並將其疊加在原始訊號上）
plt.subplot(2, 1, 2)
# 繪製還原訊號，因為它們幾乎重合，所以我們放大一點點來看差異
plt.plot(t, f_t, label='$f(t)$ (原始訊號)', color='blue', linestyle='--')
plt.plot(t, f_recovered_t, label='$f_{recovered}(t)$ (還原訊號)', color='red', alpha=0.6)
plt.title('原始訊號與還原訊號的比較')
plt.xlabel('時間 (秒)')
plt.ylabel('振幅')
plt.legend()
plt.tight_layout()
plt.show()