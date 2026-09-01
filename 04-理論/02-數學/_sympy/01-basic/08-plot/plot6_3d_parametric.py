# plot6_3d_line.py
from sympy import symbols, cos, sin
from sympy.plotting import plot3d_parametric_line
from sympy import pi

def main():
    t = symbols('t')

    # 繪製 3D 螺旋線 (Helix)
    # x = cos(t)
    # y = sin(t)
    # z = t
    print("繪製 3D 螺旋線...")
    
    plot3d_parametric_line(
        (cos(t), sin(t), t), 
        (t, 0, 4*pi),
        title="3D Helix",
        xlabel='X', ylabel='Y' # 標記軸
    )

if __name__ == "__main__":
    main()