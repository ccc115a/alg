def df(f, x, h=0.00001):
    # return (f(x+h)-f(x))/h
    return (f(x+h)-f(x-h))/(2*h)

def dfn(f, x, n, h=0.00001):
    if n==0: return f(x)
    if n==1: return df(f, x, h)
    return (dfn(f, x+h, n-1, h)-dfn(f, x, n-1, h))/h

def integral(f, a, b, h=0.001):
	area = 0
	x = a
	while x<b:
		area += f(x)*h
		x+=h
	return area

if __name__ == "__main__":
    def f(x):
        return x**3
    
    print('df(f, 2)=', df(f, 2))
    print('integral(f, 0, 2)=', integral(f, 0, 2))