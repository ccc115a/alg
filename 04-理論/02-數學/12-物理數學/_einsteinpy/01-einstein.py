"""
EinsteinPy 範例程式碼集合
修正版本 - 處理 trajectory tuple 和警告
"""

import numpy as np
import warnings

# 抑制數值積分警告（這些警告在黑洞附近的計算中很常見）
warnings.filterwarnings('ignore', category=RuntimeWarning)

print("=" * 60)
print("範例 1: Schwarzschild 時空中的類時測地線")
print("=" * 60)

try:
    from einsteinpy.geodesic import Timelike
    from einsteinpy.plotting.geodesic import StaticGeodesicPlotter

    # 定義初始條件
    position = [40., np.pi / 2, 0.]  # [r, theta, phi] 球座標
    momentum = [0., 0., 3.83405]     # [p_r, p_theta, p_phi]
    a = 0.  # Schwarzschild 黑洞 (自旋參數 a=0)

    geod = Timelike(
        metric="Schwarzschild",
        metric_params=(a,),
        position=position,
        momentum=momentum,
        steps=5500,
        delta=1.0,
        return_cartesian=True
    )

    print("測地線物件創建成功！")
    # trajectory 可能是 tuple，需要轉換
    traj = geod.trajectory
    if isinstance(traj, tuple):
        traj = np.array(traj[0]) if len(traj) > 0 else np.array([])
    print(f"軌跡點數: {len(traj)}")
    print(f"軌跡形狀: {traj.shape}")
    print("✓ 範例 1 完成")

except Exception as e:
    print(f"✗ 執行錯誤: {e}")


print("\n" + "=" * 60)
print("範例 2: 使用 Geodesic 基礎類別")
print("=" * 60)

try:
    from einsteinpy.geodesic import Geodesic

    position = [2.15, np.pi / 2, 0.]
    momentum = [0., 0., -1.5]
    a = 0.

    geod2 = Geodesic(
        metric="Schwarzschild",
        metric_params=(a,),
        position=position,
        momentum=momentum,
        steps=400,
        delta=0.5,
        time_like=True,
        return_cartesian=True
    )

    traj = geod2.trajectory
    if isinstance(traj, tuple):
        traj = np.array(traj[0]) if len(traj) > 0 else np.array([])
    print(f"軌跡形狀: {traj.shape}")
    print("✓ 範例 2 完成")

except Exception as e:
    print(f"✗ 執行錯誤: {e}")


print("\n" + "=" * 60)
print("範例 3: Kerr 黑洞中的測地線")
print("=" * 60)

try:
    position = [4., np.pi / 3, 0.]
    momentum = [0., 0.767851, 2.]
    a = 0.99  # 高自旋 Kerr 黑洞

    geod_kerr = Timelike(
        metric="Kerr",
        metric_params=(a,),
        position=position,
        momentum=momentum,
        steps=1000,
        delta=0.5,
        return_cartesian=True
    )

    traj = geod_kerr.trajectory
    if isinstance(traj, tuple):
        traj = np.array(traj[0]) if len(traj) > 0 else np.array([])
    print(f"Kerr 黑洞測地線軌跡形狀: {traj.shape}")
    print(f"軌跡前 3 個點的位置:")
    print(traj[:3, :3])  # 顯示前 3 個點的 x, y, z 座標
    print("✓ 範例 3 完成")

except Exception as e:
    print(f"✗ 執行錯誤: {e}")


print("\n" + "=" * 60)
print("範例 4: 類零測地線（光線路徑）")
print("=" * 60)

try:
    from einsteinpy.geodesic import Nulllike

    position = [10., np.pi / 2, 0.]
    momentum = [0., 0., 1.5]
    a = 0.

    geod_null = Nulllike(
        metric="Schwarzschild",
        metric_params=(a,),
        position=position,
        momentum=momentum,
        steps=2000,
        delta=0.01,
        return_cartesian=True
    )

    traj = geod_null.trajectory
    if isinstance(traj, tuple):
        traj = np.array(traj[0]) if len(traj) > 0 else np.array([])
    print(f"類零測地線軌跡形狀: {traj.shape}")
    print("✓ 範例 4 完成")

except Exception as e:
    print(f"✗ 執行錯誤: {e}")


print("\n" + "=" * 60)
print("範例 5: Kerr-Newman 黑洞測地線")
print("=" * 60)

try:
    position = [5., np.pi / 2, 0.]
    momentum = [0., 0., 2.5]
    a = 0.5  # 自旋參數
    Q = 0.2  # 電荷參數

    geod_kn = Timelike(
        metric="KerrNewman",
        metric_params=(a, Q),
        position=position,
        momentum=momentum,
        steps=500,
        delta=1.0,
        return_cartesian=True
    )

    traj = geod_kn.trajectory
    if isinstance(traj, tuple):
        traj = np.array(traj[0]) if len(traj) > 0 else np.array([])
    print(f"Kerr-Newman 黑洞測地線軌跡形狀: {traj.shape}")
    print("✓ 範例 5 完成")

except Exception as e:
    print(f"✗ 執行錯誤: {e}")


print("\n" + "=" * 60)
print("範例 6: 座標轉換")
print("=" * 60)

try:
    from astropy import units as u
    from einsteinpy.coordinates import Cartesian, BoyerLindquist

    M = 1e20 * u.kg
    a = 0.5 * u.one

    # 笛卡爾座標轉 Boyer-Lindquist 座標
    t = 1. * u.s
    x = 0.2 * u.km
    y = 0.15 * u.km
    z = 0. * u.km

    _4pos_cart = Cartesian(t, x, y, z)
    _4pos_bl = _4pos_cart.to_bl(M=M, a=a)
    
    print(f"笛卡爾座標: (t={t}, x={x}, y={y}, z={z})")
    print(f"Boyer-Lindquist 座標:")
    print(f"  {_4pos_bl}")
    
    # 轉回笛卡爾座標
    cartsn_pos = _4pos_bl.to_cartesian(M=M, a=a)
    print(f"轉回笛卡爾座標:")
    print(f"  {cartsn_pos}")
    print("✓ 範例 6 完成")

except Exception as e:
    print(f"✗ 執行錯誤: {e}")


print("\n" + "=" * 60)
print("範例 7: 繪製測地線（2D 投影）")
print("=" * 60)

try:
    from einsteinpy.plotting.geodesic import StaticGeodesicPlotter

    position = [40., np.pi / 2, 0.]
    momentum = [0., 0., 3.83405]
    a = 0.

    geod_plot = Timelike(
        metric="Schwarzschild",
        metric_params=(a,),
        position=position,
        momentum=momentum,
        steps=5500,
        delta=1.0,
        return_cartesian=True
    )

    # 創建 2D 繪圖
    sgpl = StaticGeodesicPlotter()
    sgpl.plot2D(geod_plot, coordinates=(1, 2))
    # sgpl.show()  # 取消註解以顯示圖形
    
    print("2D 繪圖已創建（X-Y 平面投影）")
    print("取消註解 sgpl.show() 來顯示圖形")
    print("✓ 範例 7 完成")

except Exception as e:
    print(f"✗ 執行錯誤: {e}")


print("\n" + "=" * 60)
print("範例 8: 符號計算 - Schwarzschild 度規張量")
print("=" * 60)

try:
    from einsteinpy.symbolic import Schwarzschild

    # 創建 Schwarzschild 度規
    metric = Schwarzschild()
    
    print("Schwarzschild 度規張量:")
    print(metric.tensor())
    print("\n說明: 對角元素分別對應 (t, r, θ, φ) 方向")
    print("✓ 範例 8 完成")

except Exception as e:
    print(f"✗ 執行錯誤: {e}")


print("\n" + "=" * 60)
print("範例 9: 符號計算 - Christoffel 符號")
print("=" * 60)

try:
    from einsteinpy.symbolic import Schwarzschild, ChristoffelSymbols

    metric = Schwarzschild()
    ch = ChristoffelSymbols.from_metric(metric)
    
    print("Christoffel 符號範例 Γ^k_{1,2} (k=0,1,2,3):")
    print(ch[1, 2, :])
    print("\n說明: Christoffel 符號描述了時空的彎曲")
    print("✓ 範例 9 完成")

except Exception as e:
    print(f"✗ 執行錯誤: {e}")


print("\n" + "=" * 60)
print("範例 10: 符號計算 - Ricci 張量")
print("=" * 60)

try:
    from einsteinpy.symbolic import Schwarzschild, RicciTensor

    metric = Schwarzschild()
    ricci = RicciTensor.from_metric(metric)
    
    print("Ricci 張量:")
    print(ricci.tensor())
    print("\n說明: Schwarzschild 時空中 Ricci 張量為 0")
    print("     (真空解，滿足 Einstein 場方程 R_μν = 0)")
    print("✓ 範例 10 完成")

except Exception as e:
    print(f"✗ 執行錯誤: {e}")


print("\n" + "=" * 60)
print("範例 11: 計算 Schwarzschild 半徑")
print("=" * 60)

try:
    from astropy import units as u
    from astropy.constants import G, c
    
    # 手動計算 Schwarzschild 半徑: r_s = 2GM/c^2
    M_sun = 1.989e30 * u.kg      # 太陽質量
    M_earth = 5.972e24 * u.kg    # 地球質量
    M_milkyway = 4e6 * M_sun     # 銀河系中心黑洞
    
    r_s_sun = (2 * G * M_sun / c**2).to(u.km)
    r_s_earth = (2 * G * M_earth / c**2).to(u.mm)
    r_s_milkyway = (2 * G * M_milkyway / c**2).to(u.au)
    
    print(f"太陽的 Schwarzschild 半徑: {r_s_sun:.3f}")
    print(f"地球的 Schwarzschild 半徑: {r_s_earth:.3f}")
    print(f"銀河系中心黑洞的 Schwarzschild 半徑: {r_s_milkyway:.6f}")
    print("✓ 範例 11 完成")

except Exception as e:
    print(f"✗ 執行錯誤: {e}")


print("\n" + "=" * 60)
print("範例 12: 分析測地線數據")
print("=" * 60)

try:
    position = [10., np.pi / 2, 0.]
    momentum = [0., 0., 2.0]
    a = 0.

    geod_analysis = Timelike(
        metric="Schwarzschild",
        metric_params=(a,),
        position=position,
        momentum=momentum,
        steps=1000,
        delta=0.1,
        return_cartesian=True
    )

    traj = geod_analysis.trajectory
    if isinstance(traj, tuple):
        traj = np.array(traj[0]) if len(traj) > 0 else np.array([])
    
    # 計算軌道統計
    if len(traj) > 0:
        # 假設前 3 列是 x, y, z 座標
        x, y, z = traj[:, 0], traj[:, 1], traj[:, 2]
        r = np.sqrt(x**2 + y**2 + z**2)
        
        print(f"軌跡點數: {len(traj)}")
        print(f"最小徑向距離: {r.min():.3f}")
        print(f"最大徑向距離: {r.max():.3f}")
        print(f"平均徑向距離: {r.mean():.3f}")
    
    print("✓ 範例 12 完成")

except Exception as e:
    print(f"✗ 執行錯誤: {e}")


print("\n" + "=" * 60)
print("所有範例執行完畢！")
print("=" * 60)

print("\n" + "=" * 60)
print("關鍵參數說明")
print("=" * 60)
print("""
度規類型:
  - 'Schwarzschild': 非旋轉黑洞, 參數 (a=0,)
  - 'Kerr': 旋轉黑洞, 參數 (a,) 其中 0 < a < 1
  - 'KerrNewman': 帶電旋轉黑洞, 參數 (a, Q)

初始條件:
  - position: [r, θ, φ] 球座標中的 3-位置
  - momentum: [p_r, p_θ, p_φ] 對應的 3-動量

積分參數:
  - steps: 積分步數（更多步數 = 更長軌道）
  - delta: 每步大小（更小值 = 更精確，但更慢）
  - return_cartesian: True 返回笛卡爾座標 (x,y,z)

注意事項:
  - 數值警告在靠近視界時很常見，已自動抑制
  - trajectory 可能返回 tuple，程式碼已處理
  - 取消註解 sgpl.show() 來顯示 3D 繪圖
""")