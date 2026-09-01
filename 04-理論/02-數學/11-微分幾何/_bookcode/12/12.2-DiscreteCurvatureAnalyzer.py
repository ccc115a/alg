import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm

class DiscreteCurvatureAnalyzer:
    def __init__(self, vertices, faces):
        """
        初始化離散曲率分析器
        Args:
            vertices: (N, 3) 頂點座標陣列
            faces: (M, 3) 面索引陣列 (三角形)
        """
        self.vertices = vertices
        self.faces = faces
        self.num_vertices = len(vertices)
        
        # 儲存計算結果
        self.gaussian_curvature = np.zeros(self.num_vertices)
        
        print(f"--- 載入網格模型 ---")
        print(f"  頂點數: {self.num_vertices}")
        print(f"  面數:   {len(faces)}")
        
    def compute_curvature(self):
        """
        計算離散高斯曲率 (Angle Deficit Method)
        """
        print("正在計算離散曲率...")
        
        # 1. 初始化累加器
        # 每個頂點周圍的角度和
        angle_sum = np.zeros(self.num_vertices)
        # 每個頂點的關聯面積 (Barycentric area)
        area_sum = np.zeros(self.num_vertices)
        
        # 2. 遍歷所有三角形面
        # 雖然 Python 迴圈慢，但為了教學清晰，我們直接遍歷
        # (優化版可用向量化操作)
        for face in self.faces:
            # 取得三角形的三個頂點索引
            idx = [face[0], face[1], face[2]]
            
            # 取得座標 P0, P1, P2
            P = [self.vertices[i] for i in idx]
            
            # 計算邊向量
            # v0 = P1 - P0, v1 = P2 - P1, v2 = P0 - P2
            edges = [
                P[1] - P[0], # 邊 0
                P[2] - P[1], # 邊 1
                P[0] - P[2]  # 邊 2
            ]
            
            # 計算邊長
            lengths = [np.linalg.norm(e) for e in edges]
            
            # 計算三角形面積 (海龍公式或外積)
            # Area = 0.5 * |edge0 x edge2| (注意方向)
            cross_prod = np.cross(edges[0], -edges[2])
            area_tri = 0.5 * np.linalg.norm(cross_prod)
            
            # 將面積的 1/3 分配給三個頂點
            for i in idx:
                area_sum[i] += area_tri / 3.0
            
            # 計算三個內角 (使用餘弦定理或點積)
            # Angle at P0: between edge0 and -edge2
            # Angle at P1: between edge1 and -edge0
            # Angle at P2: between edge2 and -edge1
            
            # 定義一個輔助函數算夾角
            def get_angle(v_a, v_b):
                # 歸一化
                ua = v_a / np.linalg.norm(v_a)
                ub = v_b / np.linalg.norm(v_b)
                # 限制範圍避免浮點數誤差導致 NaN
                cos_val = np.clip(np.dot(ua, ub), -1.0, 1.0)
                return np.arccos(cos_val)

            angles = [
                get_angle(edges[0], -edges[2]), # Angle at P0
                get_angle(edges[1], -edges[0]), # Angle at P1
                get_angle(edges[2], -edges[1])  # Angle at P2
            ]
            
            # 累加角度
            for k in range(3):
                angle_sum[idx[k]] += angles[k]
                
        # 3. 計算最終曲率 K = (2pi - sum_angles) / Area
        # 注意：對於邊界頂點，這個公式需要修正，但我們的球體是封閉曲面，暫不考慮邊界
        
        # 避免除以零
        area_sum[area_sum == 0] = 1.0 
        
        self.gaussian_curvature = (2 * np.pi - angle_sum) / area_sum
        
        print("計算完成。")

    def visualize(self):
        """繪製帶有曲率熱圖的 3D 網格"""
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        # 設定顏色映射
        # 我們希望 0 是白色/灰色，正為紅，負為藍
        # 需要限制範圍，因為離散計算可能有極端值
        K = self.gaussian_curvature
        vmax = np.percentile(np.abs(K), 95) # 取 95% 分位數作為顯示上限，避免噪聲
        norm = plt.Normalize(-vmax, vmax)
        cmap = cm.coolwarm
        
        # 使用 plot_trisurf
        # 它需要 x, y, z 和 triangles 索引
        surf = ax.plot_trisurf(
            self.vertices[:,0], 
            self.vertices[:,1], 
            self.vertices[:,2], 
            triangles=self.faces,
            cmap=cmap,
            norm=norm,
            array=K, # 顏色數據
            edgecolor='none',
            alpha=0.9,
            shade=True
        )
        
        # Colorbar
        m = cm.ScalarMappable(cmap=cmap, norm=norm)
        m.set_array(K)
        cbar = fig.colorbar(m, ax=ax, shrink=0.6, aspect=15, label='Gaussian Curvature')
        
        ax.set_title("Discrete Gaussian Curvature on Bumped Sphere")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        
        # 保持比例
        limit = np.max(np.abs(self.vertices))
        ax.set_xlim(-limit, limit)
        ax.set_ylim(-limit, limit)
        ax.set_zlim(-limit, limit)
        ax.set_box_aspect([1,1,1])
        
        plt.axis('off')
        plt.show()

# ==========================================
# 網格生成器：波浪球體
# ==========================================
def generate_bumped_sphere(radius=1.0, bumps=6, resolution=40):
    """
    生成一個表面凹凸不平的球體網格
    """
    # 使用經緯度網格
    u = np.linspace(0, 2 * np.pi, resolution)
    v = np.linspace(0, np.pi, resolution)
    U, V = np.meshgrid(u, v)
    
    # 定義半徑變化 (波浪)
    # R(u, v) = R0 + amp * sin(k*u) * sin(k*v)
    amp = 0.2
    R = radius + amp * np.sin(bumps * U) * np.sin(bumps * V)
    
    # 參數化方程
    X = R * np.sin(V) * np.cos(U)
    Y = R * np.sin(V) * np.sin(U)
    Z = R * np.cos(V)
    
    # --- 將網格轉換為頂點列表 ---
    # vertices: (N_pts, 3)
    vertices = np.column_stack([X.flatten(), Y.flatten(), Z.flatten()])
    
    # --- 生成三角形面索引 ---
    faces = []
    rows, cols = resolution, resolution
    
    for i in range(rows - 1):
        for j in range(cols - 1):
            # 當前格子的四個頂點索引
            # p1 -- p2
            # |     |
            # p3 -- p4
            p1 = i * cols + j
            p2 = i * cols + (j + 1)
            p3 = (i + 1) * cols + j
            p4 = (i + 1) * cols + (j + 1)
            
            # 分割成兩個三角形: (p1, p3, p2) 和 (p2, p3, p4)
            faces.append([p1, p3, p2])
            faces.append([p2, p3, p4])
            
    return vertices, np.array(faces)

# ==========================================
# 主程式
# ==========================================
if __name__ == "__main__":
    # 1. 生成模型
    print("生成波浪球體 (Bumped Sphere)...")
    verts, faces = generate_bumped_sphere(bumps=4, resolution=60)
    
    # 2. 分析曲率
    analyzer = DiscreteCurvatureAnalyzer(verts, faces)
    analyzer.compute_curvature()
    
    # 3. 視覺化
    print("繪製熱圖中...")
    analyzer.visualize()