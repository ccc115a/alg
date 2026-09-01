# plot5_3d_surface.py
from sympy import symbols
from sympy.plotting import plot3d

def main():
    x, y = symbols('x y')

    # 繪製 z = x*y
    # 這是一個典型的馬鞍面 (Saddle point)
    print("繪製 3D 曲面 z = x*y ...")
    plot3d(x*y, (x, -5, 5), (y, -5, 5), title="Saddle Surface")

    # 繪製多個 3D 曲面
    # z1 = -x^2 - y^2
    # z2 = x^2 + y^2
    # plot3d(x**2 + y**2, -x**2 - y**2, (x, -2, 2), (y, -2, 2))

if __name__ == "__main__":
    main()