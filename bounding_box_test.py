from coordinate_system_utils import *
import matplotlib.pyplot as plt

points = (0, 0), (0, 1), (0.5, 2), (1, 1), (1, 0)
center = get_centeroid(points)
poly = plt.Polygon(points)
poly.set_color('grey')
axes = plt.subplot(111)
axes.set_xlim(left=-1,right=3)
axes.set_ylim(bottom=-1,top=3)
axes.add_patch(poly)
sbbox_points = get_sbbox(points)
sbbox, = axes.plot(*tuple(zip(*(sbbox_points+(sbbox_points[0],)))),'ro--')
mbbox_points = get_mbbox(points)
mbbox, = axes.plot(*tuple(zip(*(mbbox_points + (mbbox_points[0],)))), 'bs--')

while True:
    points = rotate_points(points, center, 0.01 * numpy.pi)
    poly.set_xy(points)
    sbbox_points = get_sbbox(points)
    sbx,sby = tuple(zip(*(sbbox_points+(sbbox_points[0],))))
    sbbox.set_xdata(sbx)
    sbbox.set_ydata(sby)
    mbbox_points = get_mbbox(points)
    mbx,mby = tuple(zip(*(mbbox_points + (mbbox_points[0],))))
    mbbox.set_xdata(mbx)
    mbbox.set_ydata(mby)
    plt.pause(0.001)