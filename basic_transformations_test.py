from geometry_2d import *
from geometry_2d import _first_last_point
import matplotlib.pyplot as plt

def rearrange(points):
    return tuple(zip(*_first_last_point(points)))

axes = plt.subplot(111)
axes.set_xlim(left=-2, right=7)
axes.set_ylim(bottom=-2, top=7)
plt.grid()

points = (0, 0), (0, 1), (0.5, 2), (1, 1), (1, 0)
first, = axes.plot(*rearrange(points), 'ro--')
second, = axes.plot(*rearrange(points), 'bs--')
for i in numpy.arange(1, 2, 0.05):
    rpoints = scale(points, i, 2, absolute=True)
    rx, ry = rearrange(rpoints)
    second.set_xdata(rx)
    second.set_ydata(ry)
    plt.pause(0.1)
third, = axes.plot(*rearrange(rpoints), 'g*--')
for i in numpy.arange(0,2,0.1):
    rpoints = move(rpoints, 0.05, 0.1, refpoint=rpoints[0])
    rx, ry = rearrange(rpoints)
    second.set_xdata(rx)
    second.set_ydata(ry)
    plt.pause(0.1)
fourth, = axes.plot(*rearrange(rpoints), 'yp--')
for i in numpy.arange(0,numpy.pi * 3/4, 0.1):
    rpoints = rotate(rpoints, 0.1, refpoint=rpoints[2])
    rx, ry = rearrange(rpoints)
    second.set_xdata(rx)
    second.set_ydata(ry)
    plt.pause(0.1)
plt.show()

