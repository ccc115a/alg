# plot1_basic.py
from sympy import symbols, plot, sin
from sympy import pi

def main():
    x = symbols('x')

    # 1. 基本繪圖: y = x^2
    # 預設範圍通常是 -10 到 10
    print("繪製 y = x^2 ...")
    p1 = plot(x**2, show=False)
    p1.title = "Basic Plot: y = x^2"
    p1.show()

    # 2. 指定範圍與樣式
    # 繪製 sin(x)，範圍 -2π 到 2π
    print("繪製 y = sin(x) ...")
    p2 = plot(sin(x), (x, -2*pi, 2*pi), title="Sin(x)", show=True)

if __name__ == "__main__":
    main()