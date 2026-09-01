# plot3_parametric.py
from sympy import symbols, cos, sin
from sympy.plotting import plot_parametric
from sympy import pi

def main():
    u = symbols('u')

    # 1. 繪製圓形
    # x = cos(u), y = sin(u)
    print("繪製參數圓形...")
    plot_parametric((cos(u), sin(u)), (u, -pi, pi), title="Circle")

    # 2. 繪製螺旋線 (Butterfly curve 簡化版)
    # x = u * cos(u), y = u * sin(u)
    print("繪製螺旋線...")
    plot_parametric((u*cos(u), u*sin(u)), (u, 0, 10*pi), title="Spiral")

if __name__ == "__main__":
    main()