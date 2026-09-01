def theorem1(f, x):
    r = df(lambda x:integral(f, 0, x), x)
    print('r=', r, 'f(x)=', f(x))
    print('abs(r-f(x))<0.01 = ', abs(r-f(x))<0.01)
    assert abs(r-f(x))<0.01

def f(x):
    return x**3

if __name__ == "__main__":
    theorem1(f, 2)