# plot2_multi.py
from sympy import symbols, plot, sin, cos, exp

def main():
    x = symbols('x')

    # 繪製 f(x) = sin(x) 和 g(x) = cos(x)
    # legend=True 會顯示圖例
    p = plot(sin(x), cos(x), (x, -5, 5), show=False, legend=True)
    
    # 修改曲線顏色
    p[0].line_color = 'blue'  # sin(x)
    p[1].line_color = 'red'   # cos(x)
    
    p.title = "Sin(x) vs Cos(x)"
    print("顯示多函數圖形...")
    p.show()

    # 另外一種寫法：使用 extend
    p_base = plot(x, show=False)
    p_add = plot(x**2, show=False)
    p_base.extend(p_add) # 將 p_add 合併到 p_base
    # p_base.show()

if __name__ == "__main__":
    main()