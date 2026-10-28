"""
旅行推銷員問題 (TSP) —— 五種解法，使用同一組測試資料
1. 改良法 (2-opt 全鄰域改良)
2. 爬山演算法 (隨機交換，只接受更佳解)
3. 模擬退火法
4. 梯度下降法 (連續鬆弛 + 懲罰項)
5. 貪婪演算法 (最近鄰居)
只需要 numpy 與 matplotlib(選用)。
"""
import math
import random
import time
import numpy as np

# ------------------------------------------------------------
# 測試資料：固定亂數種子，所有方法使用同一組 20 個城市
# ------------------------------------------------------------
N_CITIES = 20
rng = random.Random(42)
CITIES = [(rng.uniform(0, 100), rng.uniform(0, 100)) for _ in range(N_CITIES)]
DIST = np.array([[math.dist(a, b) for b in CITIES] for a in CITIES])


def tour_length(tour):
    return sum(DIST[tour[i], tour[(i + 1) % len(tour)]] for i in range(len(tour)))


# ------------------------------------------------------------
# 5. 貪婪演算法 (最近鄰居法)：每次走向最近的未訪問城市
# ------------------------------------------------------------
def greedy(start=0):
    unvisited = set(range(N_CITIES)) - {start}
    tour = [start]
    while unvisited:
        nxt = min(unvisited, key=lambda c: DIST[tour[-1], c])
        tour.append(nxt)
        unvisited.remove(nxt)
    return tour


# ------------------------------------------------------------
# 1. 改良法：以貪婪解為起點，反覆做 2-opt，
#    每輪檢查全部鄰域，採用最佳改善，直到無法改善
# ------------------------------------------------------------
def two_opt_improve(init=None):
    tour = list(init) if init else greedy()
    n = len(tour)
    improved = True
    while improved:
        improved = False
        best_delta, best_ij = -1e-9, None
        for i in range(n - 1):
            for j in range(i + 2, n):
                if i == 0 and j == n - 1:
                    continue
                a, b = tour[i], tour[i + 1]
                c, d = tour[j], tour[(j + 1) % n]
                delta = DIST[a, c] + DIST[b, d] - DIST[a, b] - DIST[c, d]
                if delta < best_delta:
                    best_delta, best_ij = delta, (i, j)
        if best_ij:
            i, j = best_ij
            tour[i + 1:j + 1] = reversed(tour[i + 1:j + 1])
            improved = True
    return tour


# ------------------------------------------------------------
# 2. 爬山演算法：隨機初始解，隨機交換兩城市，只接受更短的路徑
# ------------------------------------------------------------
def hill_climbing(iters=20000, seed=1):
    r = random.Random(seed)
    tour = list(range(N_CITIES))
    r.shuffle(tour)
    cur = tour_length(tour)
    for _ in range(iters):
        i, j = r.sample(range(N_CITIES), 2)
        tour[i], tour[j] = tour[j], tour[i]
        new = tour_length(tour)
        if new < cur:
            cur = new
        else:
            tour[i], tour[j] = tour[j], tour[i]  # 還原
    return tour


# ------------------------------------------------------------
# 3. 模擬退火法：允許以機率 exp(-Δ/T) 接受較差解，溫度逐步降低
# ------------------------------------------------------------
def simulated_annealing(T0=100.0, T_end=1e-3, alpha=0.995, per_temp=100, seed=1):
    r = random.Random(seed)
    tour = list(range(N_CITIES))
    r.shuffle(tour)
    cur = tour_length(tour)
    best, best_len = tour[:], cur
    T = T0
    while T > T_end:
        for _ in range(per_temp):
            i, j = sorted(r.sample(range(N_CITIES), 2))
            cand = tour[:i] + tour[i:j + 1][::-1] + tour[j + 1:]  # 2-opt 鄰域
            new = tour_length(cand)
            d = new - cur
            if d < 0 or r.random() < math.exp(-d / T):
                tour, cur = cand, new
                if cur < best_len:
                    best, best_len = tour[:], cur
        T *= alpha
    return best


# ------------------------------------------------------------
# 4. 梯度下降法：TSP 是離散問題，故先做連續鬆弛
#    P[k, i] = 第 k 步造訪城市 i 的機率 (對 W 做 row-softmax)
#    期望長度 L = Σ_k P[k]ᵀ D P[k+1]   (含環狀)
#    懲罰項   = λ Σ_i (Σ_k P[k,i] - 1)²   (每個城市恰好造訪一次)
#    以梯度下降更新 W，最後把 P 解碼成排列。
# ------------------------------------------------------------
def gradient_descent(steps=3000, lr=0.05, lam=30.0, seed=1):
    n = N_CITIES
    r = np.random.default_rng(seed)
    W = r.normal(0, 0.1, (n, n))
    Dn = DIST / DIST.mean()  # 正規化，讓梯度尺度穩定

    def softmax(x):
        e = np.exp(x - x.max(axis=1, keepdims=True))
        return e / e.sum(axis=1, keepdims=True)

    for t in range(steps):
        P = softmax(W)
        nxt, prv = np.roll(P, -1, axis=0), np.roll(P, 1, axis=0)
        # dL/dP[k] = D·P[k+1] + D·P[k-1]  (D 對稱)
        gP = nxt @ Dn + prv @ Dn
        # 懲罰項梯度
        col = P.sum(axis=0) - 1.0
        gP += 2 * lam * col[None, :]
        # 通過 row-softmax 的反向傳播
        gW = P * (gP - (gP * P).sum(axis=1, keepdims=True))
        # 退火式 learning rate 衰減
        W -= lr * (1 - t / steps * 0.9) * gW * 10

    P = softmax(W)
    # 解碼：反覆挑選最大機率的 (位置, 城市) 配對
    tour = [-1] * n
    Pm = P.copy()
    for _ in range(n):
        k, i = np.unravel_index(np.argmax(Pm), Pm.shape)
        tour[k] = int(i)
        Pm[k, :] = -1
        Pm[:, i] = -1
    return tour


# ------------------------------------------------------------
# 執行與比較
# ------------------------------------------------------------
def plot_all(results):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return
    plt.rcParams["font.sans-serif"] = ["Microsoft JhengHei", "Noto Sans CJK TC", "Arial Unicode MS", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
    for ax, (name, tour, L, _) in zip(axes.flat, results):
        xs = [CITIES[c][0] for c in tour + [tour[0]]]
        ys = [CITIES[c][1] for c in tour + [tour[0]]]
        ax.plot(xs, ys, "-o", ms=5)
        ax.set_title(f"{name}  L={L:.2f}")
    axes.flat[-1].axis("off")
    plt.tight_layout()
    plt.savefig("tsp_results.png", dpi=120)
    print("已輸出圖片 tsp_results.png")


if __name__ == "__main__":
    methods = [
        ("1.改良法(2-opt)", two_opt_improve),
        ("2.爬山演算法", hill_climbing),
        ("3.模擬退火法", simulated_annealing),
        ("4.梯度下降法", gradient_descent),
        ("5.貪婪演算法", greedy),
    ]
    results = []
    print(f"城市數量: {N_CITIES}\n")
    for name, fn in methods:
        t0 = time.time()
        tour = fn()
        assert sorted(tour) == list(range(N_CITIES)), f"{name} 產生非法路徑"
        L, sec = tour_length(tour), time.time() - t0
        results.append((name, tour, L, sec))
        print(f"{name:<14} 長度={L:8.2f}  耗時={sec:6.3f}s")
        print(f"   路徑: {tour}")
    plot_all(results)