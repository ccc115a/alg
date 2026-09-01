(py310) cccimac@cccimacdeiMac 10-diffeq % python sympy3_varsp.py 
微分方程: Eq(Derivative(y(x), x), x**2*y(x))
通解: Eq(y(x), C1*exp(x**3/3))
驗證結果: Eq(Derivative(C1*exp(x**3/3), x), C1*x**2*exp(x**3/3))