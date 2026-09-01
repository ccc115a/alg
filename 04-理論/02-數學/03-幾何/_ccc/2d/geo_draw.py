import math
import matplotlib.pyplot as plt # 引入 Matplotlib

# --- 點、線、圓的類定義 (與原始檔案相同) ---
class Point:
    """代表二維平面上的點 (x, y)。"""
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
    
    def __repr__(self):
        return f"Point({self.x:.4f}, {self.y:.4f})"

class Line:
    """
    代表直線，由兩個點 P1, P2 定義。
    內部轉換為一般式 Ax + By = C。
    """
    def __init__(self, P1: Point, P2: Point):
        self.P1 = P1
        self.P2 = P2
        
        # 轉換為一般式 Ax + By = C
        self.A = P2.y - P1.y
        self.B = P1.x - P2.x
        self.C = self.A * P1.x + self.B * P1.y

        if abs(self.A) < 1e-9 and abs(self.B) < 1e-9:
             # 兩個點相同時會拋出 ValueError，但由於我們要繪圖，
             # 這裡我們允許繪製，只是直線的定義會失效。
             pass

    def __repr__(self):
        return f"Line(P1={self.P1}, P2={self.P2}, Eq:{self.A:.2f}x + {self.B:.2f}y = {self.C:.2f})"

class Circle:
    """
    代表圓，由圓心 (center) 和半徑 (radius) 定義。
    """
    def __init__(self, center: Point, radius):
        self.center = center
        self.radius = float(radius)
        
        if self.radius <= 0:
             raise ValueError("半徑必須為正數")

        # 內部儲存一般式參數 (這裡繪圖不需要，但保留以維持與原檔一致性)
        self.D = -2 * center.x
        self.E = -2 * center.y
        self.F = center.x**2 + center.y**2 - self.radius**2

    def __repr__(self):
        return f"Circle(Center={self.center}, Radius={self.radius:.4f})"
# --- 輔助函式 (solve_quadratic, intersect_two_lines 等) 保持不變，為保持程式碼簡潔，這裡省略 ---
# 由於繪圖只需要點、線、圓的類定義，此處僅保留類定義。

# --- 距離函式 (為繪圖邊界判斷作準備) ---
def distance(P1: Point, P2: Point):
    """計算兩點 P1 和 P2 之間的歐幾里得距離。"""
    dx = P2.x - P1.x
    dy = P2.y - P1.y
    return math.sqrt(dx**2 + dy**2)

# --- 新增繪圖函式 ---
def plot_geometry(points=None, lines=None, circles=None, intersections=None):
    """
    繪製給定的點、線和圓。
    """
    fig, ax = plt.subplots()
    ax.set_aspect('equal', adjustable='box') # 確保 x, y 軸比例尺一致
    
    all_x = []
    all_y = []

    # 1. 繪製點 (Point)
    if points:
        for name, P in points.items():
            ax.plot(P.x, P.y, 'o', label=f'Point {name}', markersize=5)
            ax.text(P.x + 0.1, P.y + 0.1, name)
            all_x.append(P.x)
            all_y.append(P.y)

    # 2. 繪製圓 (Circle)
    if circles:
        for name, C in circles.items():
            circle_patch = plt.Circle((C.center.x, C.center.y), C.radius, 
                                      color='g', fill=False, linestyle='-', label=f'Circle {name}')
            ax.add_patch(circle_patch)
            ax.text(C.center.x + C.radius, C.center.y, f"Ctr {name}", color='g')
            
            # 調整繪圖邊界以包含圓
            all_x.extend([C.center.x - C.radius, C.center.x + C.radius])
            all_y.extend([C.center.y - C.radius, C.center.y + C.radius])


    # 3. 繪製直線 (Line)
    # 為了繪製直線，我們需要根據軸的範圍來計算線段的兩端點
    if lines and all_x and all_y:
        # 確定一個繪圖範圍的粗略估計
        x_min, x_max = min(all_x) - 1, max(all_x) + 1
        y_min, y_max = min(all_y) - 1, max(all_y) + 1
        
        # 稍微擴大範圍以應對直線
        x_range = x_max - x_min
        y_range = y_max - y_min
        
        if x_range < 5: 
             x_min, x_max = x_min - 5, x_max + 5
        if y_range < 5: 
             y_min, y_max = y_min - 5, y_max + 5
        
        
        for name, L in lines.items():
            A, B, C_L = L.A, L.B, L.C
            
            # 處理鉛直線 (B ≈ 0)
            if abs(B) < 1e-9:
                if abs(A) > 1e-9:
                    x_val = C_L / A
                    ax.plot([x_val, x_val], [y_min, y_max], 'r--', label=f'Line {name} (Vertical)')
                
            # 處理水平線 (A ≈ 0)
            elif abs(A) < 1e-9:
                if abs(B) > 1e-9:
                    y_val = C_L / B
                    ax.plot([x_min, x_max], [y_val, y_val], 'r-', label=f'Line {name} (Horizontal)')
                    
            # 處理一般直線
            else:
                # 繪製 x=x_min 和 x=x_max 處的 y 值
                y1 = (C_L - A * x_min) / B
                y2 = (C_L - A * x_max) / B
                
                # 繪製 y=y_min 和 y=y_max 處的 x 值 (用於控制邊界)
                x3 = (C_L - B * y_min) / A
                x4 = (C_L - B * y_max) / A
                
                # 收集所有邊界交點
                coords = []
                # (x_min, y1)
                if y_min <= y1 <= y_max: coords.append((x_min, y1))
                # (x_max, y2)
                if y_min <= y2 <= y_max: coords.append((x_max, y2))
                # (x3, y_min)
                if x_min < x3 < x_max: coords.append((x3, y_min)) # 避免重複角點
                # (x4, y_max)
                if x_min < x4 < x_max: coords.append((x4, y_max)) # 避免重複角點
                
                # 去除重複點並只取兩個端點
                coords = list(set(coords))
                
                if len(coords) >= 2:
                    # 排序並取最遠的兩個點作為繪圖線段
                    p_start = min(coords, key=lambda p: p[0]**2 + p[1]**2)
                    p_end = max(coords, key=lambda p: p[0]**2 + p[1]**2)
                    
                    # 確保是兩個不同的點
                    if distance(Point(p_start[0], p_start[1]), Point(p_end[0], p_end[1])) > 1e-6:
                        ax.plot([p_start[0], p_end[0]], [p_start[1], p_end[1]], 'b-', label=f'Line {name}')
                
    # 4. 繪製交點 (Intersection)
    if intersections:
        for name, P_intersect in intersections.items():
            if isinstance(P_intersect, Point):
                ax.plot(P_intersect.x, P_intersect.y, 'x', label=f'Intersection {name}', markersize=8, color='black')
                ax.text(P_intersect.x + 0.1, P_intersect.y - 0.5, f"INT {name}", color='black')
                all_x.append(P_intersect.x)
                all_y.append(P_intersect.y)
                

    # 設置標籤和圖例
    if all_x and all_y:
        x_min, x_max = min(all_x) - 1, max(all_x) + 1
        y_min, y_max = min(all_y) - 1, max(all_y) + 1
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
    
    ax.set_xlabel('X Axis')
    ax.set_ylabel('Y Axis')
    ax.set_title('2D Geometry Plot')
    ax.grid(True)
    # ax.legend() # 太多物件時圖例會混亂，這裡先註釋掉
    
    plt.show()

# --- 原始檔案中的測試區塊 (簡化後用於繪圖) ---
if __name__ == "__main__":
    
    # 1. 定義幾何物件
    P_1 = Point(1, 2)
    P_2 = Point(4, 5)
    P_out = Point(10, 1)
    Center_C1 = Point(2, 3)
    Center_C2 = Point(5, 3)
    
    # 直線
    L1 = Line(P_1, P_2) # x-y=-1
    L2 = Line(Point(1, 5), Point(7, 1)) # 2x+3y=17
    L3 = Line(Point(5, 0), Point(5, 1)) # x=5 (切線)
    L4 = Line(Point(0, 3), Point(1, 3)) # y=3 (割線)
    
    # 圓
    C1 = Circle(Center_C1, 3) # (x-2)^2 + (y-3)^2 = 9
    C2 = Circle(Center_C2, 3) # (x-5)^2 + (y-3)^2 = 9

    # 2. 計算交點和垂足 (使用原檔案中的邏輯，這裡省略函式實作)
    
    # L1 和 L2 的交點 (2.8, 3.8)
    # 由於我們只繪圖，我們只定義結果點
    I_L1_L2 = Point(2.8, 3.8) 

    # L1 和 P_out 的垂足 (5, 6)
    I_Foot = Point(5, 6)
    
    # 3. 準備傳給繪圖函式的資料結構
    points = {
        "P1": P_1,
        "P2": P_2,
        "P_out": P_out,
        "C1_Center": Center_C1,
        "C2_Center": Center_C2,
    }

    lines = {
        "L1": L1,
        "L2": L2,
        "L3(x=5)": L3,
        "L4(y=3)": L4,
    }

    circles = {
        "C1": C1,
        "C2": C2,
    }

    intersections = {
        "L1/L2": I_L1_L2,
        "Foot(L1/P_out)": I_Foot
    }

    # 4. 執行繪圖
    print("生成幾何圖形...")
    plot_geometry(points, lines, circles, intersections)
    print("繪圖完成。")