from dgeom.num import TangentVector, Form, d, HyperCube, integrate_form, d
import numpy as np

if __name__ == "__main__":
    p = np.array([1, 2])

    # 定義地形函數 f
    def f(p):
        x, y = p
        return x**2 + y**2

    # 用法：
    def wind_func(p):
        x, y = p
        return [2*x, y] # v = (2x, y)

    v_field = TangentVector(wind_func)
    val = v_field(f)(p)
    print(f"在位置 p={p}，向量場 v_field 對 f 的作用結果為: {val}")
