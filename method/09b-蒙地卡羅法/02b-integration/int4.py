import numpy as np

step = 0.1

def integrate(f, rx, ry, rz, rw):
    area = 0.0
    for x in np.arange(rx[0], rx[1], step):
        for y in np.arange(ry[0], ry[1], step):
            for z in np.arange(rz[0], rz[1], step):
                for w in np.arange(rw[0], rw[1], step):
                    area += f(x,y,z,w)*step**4
    return area

def f(x,y,z,w):
    return x**2+y**2+z**2+w**2

print(integrate(f, [0,1], [0,1], [0,1], [0,1]))
