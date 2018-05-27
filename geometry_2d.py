import numpy

# -----------------------Essential Transformations-----------------------


def move(points, x, y, absolute=False, refpoint=None):
    """
    If absolute = True:
    Applies the transformation that would get the reference point to the coordinates (x,y)
    If the referencepoint is None the centeroid of the points will be used as reference\n
    If absolute = False:
    adds x,y to all the points
    (Ignores the reference point)\n
    Format for points: ((x1,y1),(x2,y2),(x3,y3))
    """
    if absolute:
        if refpoint is None:
            refpoint = get_centeroid(points)
        x = x - refpoint[0]
        y = y - refpoint[1]
    rpoints = []
    for px, py in points:
        rx = px + x
        ry = py + y
        rpoints += [(rx, ry)]
    return rpoints


def scale(points, x, y, absolute=False, refpoint=None):
    """
    If absolute = True:
    Uses x and y as width and height respectively of the straight bounding box
    If the reference point is None the centeroid of the points will be used as reference\n
    If absolute = False:
    Uses x and y as factors for scaling width and height respectively
    If the reference point is None the centeroid of the points will be used as reference\n
    Format for points: ((x1,y1),(x2,y2),(x3,y3))
    """
    if refpoint is None:
        refpoint = get_centeroid(points)
    if absolute:
        xlength, ylength = get_bbox_size(points)
        x = x / xlength
        y = y / ylength
    rpoints = []
    for px, py in points:
        rx = (px-refpoint[0]) * x + refpoint[0]
        ry = (py-refpoint[1]) * y + refpoint[1]
        rpoints += [(rx, ry)]
    return rpoints


def rotate(points, angle, absolute=False, refpoint=None, refline=None):
    """
    Angle in radians
    If absolute = True:
    Applies the transformation that rotates around the reference point
    which makes the reference line have the angle from the positive x axis counter clock wise
    If the reference point is None the centeroid of the points will be used as reference
    If the reference line is None an error will occur\n
    If absolute = False:
    rotates the point counter clock wise a certain amount around a reference point
    If the reference point is None the centeroid of the points will be used as reference
    (Ignores the reference line)\n
    Format for points: ((x1,y1),(x2,y2),(x3,y3))
    """
    if refpoint is None:
        refpoint = get_centeroid(points)
    if absolute:
        angle = angle - get_angle(*refline)
    rpoints = []
    for px, py in points:
        rx = numpy.cos(angle) * (px - refpoint[0]) - numpy.sin(angle) * (py - refpoint[1]) + refpoint[0]
        ry = numpy.sin(angle) * (px - refpoint[0]) + numpy.cos(angle) * (py - refpoint[1]) + refpoint[1]
        rpoints += [(rx, ry)]
    return tuple(rpoints)

# -----------------------Essential calculations-----------------------


def get_angle(p, o=(0, 0), principal=True):
    """
    Calculates the angle the point makes with an origin
    The angle is in radians counter clock wise from the positive x-axis
    """
    x = p[0] - o[0]
    y = p[1] - o[1]
    # Check if the point lies on an axis
    if x == 0 and y == 0:
        return 0
    if x == 0:
        if y > 0:
            return numpy.pi * 1/2
        else:
            return numpy.pi * 3/2
    elif y == 0:
        if x > 0:
            return 0
        else:
            return numpy.pi
    theta = numpy.arctan(abs(y) / abs(x))
    # Check the point's quarter
    if x > 0 and y > 0:  # 1st
        return theta
    elif x < 0 and y > 0:  # 2nd
        return numpy.pi - theta
    elif x < 0 and y < 0:  # 3rd
        if principal:
            return -numpy.pi + theta
        else:
            return numpy.pi + theta
    else:  # 4th
        if principal:
            return -theta
        else:
            return numpy.pi * 2 - theta


def get_length(points, closed=False):
    """
    Calculates the length of the path described by the list of ordered points
    """
    if closed:
        points = _first_last_point(points, add=True)
    length = 0
    for i in range(len(points)-1):
        (x1, y1), (x2, y2) = (points[i], points[i+1])
        length += numpy.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return length


def get_bbox_size(points, mbbox=False):
    """
    Returns a tuple (height, width) of the bounding box for the points
    Uses the minimum bounding box if mbbox = True
    In the case of the minumum oriented bbox the height and width are determined by max and min functions
    In the case of the straight bbox the height is the length in the y axis and the width is the length in the x axis
    """
    if mbbox:
        bbox = get_mbbox(points)
    else:
        bbox = get_sbbox(points)
    a = get_length(bbox[0:2])
    b = get_length(bbox[1:3])
    if mbbox:
        return max(a, b), min(a, b)
    else:
        return b, a


def get_area(points, signed=False):
    """
    Calculates the area of an arbitary closed shape using the shoelace formula\n
    Format for points: ((x1,y1),(x2,y2),(x3,y3))\n
    """
    points = _first_last_point(points, add=True)
    sum = 0
    x, y = zip(*points)
    for i in range(len(points)-1):
        sum += x[i]*y[i+1] - y[i] * x[i+1]
    if signed:
        return 0.5*sum
    else:
        return 0.5*abs(sum)


# -----------------------Other calculations-----------------------


def get_mbbox(points):
    """
    Computes the minimum oriented bounding box\n
    Format for points: ((x1,y1),(x2,y2),(x3,y3))
    """
    points = _first_last_point(points, add=True)
    lowest_bbox = None
    lowest_area = None
    for i in range(len(points)-1):
        p = points[i+1]
        o = points[i]
        theta = get_angle(p, o)
        nps = rotate(points, -theta, refpoint=o)
        bbox = get_sbbox(nps)
        area = get_area(bbox)
        if lowest_area is None or area < lowest_area:
            bbox = rotate(bbox, theta, refpoint=o)
            lowest_bbox = bbox
            lowest_area = area
    return lowest_bbox


def get_sbbox(points):
    """
    Computes the straight un oriented bounding box\n
    Format for points: ((x1,y1),(x2,y2),(x3,y3))
    """
    p = tuple(zip(*points))
    xmax = max(p[0])
    xmin = min(p[0])
    ymax = max(p[1])
    ymin = min(p[1])
    return (xmin, ymin), (xmin, ymax), (xmax, ymax), (xmax, ymin)


def get_line_center(point1, point2):
    """ Returns the center point between two points """
    x1, y1 = point1
    x2, y2 = point2
    rx = (x1 + x2) / 2
    ry = (y1 + y2) / 2
    return rx, ry


def get_centeroid(points, shape=True):
    """
    Returns the centeroid of a cluster of points or a shape\n
    Format for points: ((x1,y1),(x2,y2),(x3,y3))\n
    """
    if shape:
        area = get_area(points, signed = True)
        points = _first_last_point(points, add=True)
        xsum = 0
        ysum = 0
        for i in range(len(points) - 1):
            (x1, y1), (x2, y2) = points[i:i+2]
            xsum += (x1 + x2) * (x1 * y2 - x2 * y1)
            ysum += (y1 + y2) * (x1 * y2 - x2 * y1)
        return xsum/(6*area), ysum/(6*area)
    else:
        points = _first_last_point(points, add=False)
        points = tuple(zip(*points))
        x = sum(points[0])/len(points[0])
        y = sum(points[1]) / len(points[1])
        return x, y


def get_visual_center():
    pass


def get_intersections(shape1, shape2):
    """
    Returns the intersection points of the 2 shapes\n
    Format for shapes: ((x1,y1),(x2,y2),(x3,y3))\n
    """
    shape1 = _first_last_point(shape1, add=True)
    shape2 = _first_last_point(shape2, add=True)
    # Start with a line from the first shape then go through all
    # the lines in the other shape and see if there is an intersection.
    points = []
    for i in range(len(shape1)-1):
        for j in range(len(shape2) - 1):
            p = get_line_intersections((shape1[i], shape1[i+1]), (shape2[j], shape2[j+1]))
            if p is not None:
                points += [p]
    return points


def get_line_intersections(line1, line2, segment=True):
    """
    Calculates the intersecting points of the two straight lines
    if segment = False then the lines are considered infinite
    Line format: ((x1,y1),(x2,y2))
    """
    (x1, y1), (x2, y2) = line1
    (x3, y3), (x4, y4) = line2
    det = (y2-y1) * (x3-x4) - (x1-x2) * (y4-y3)
    if det == 0:
        return None
    xdet = (x1*y2-y1*x2) * (x3-x4) - (x1-x2) * (x3*y4-y3*x4)
    ydet = (y2-y1) * (x3*y4-y3*x4) - (x1*y2-y1*x2) * (y4-y3)
    x = xdet/det
    y = ydet/det
    if not segment:
        return x, y
    elif min(x1, x2) <= x <= max(x1, x2) and min(x3, x4) <= x <= max(x3, x4)\
    and  min(y1, y2) <= y <= max(y1, y2) and min(y3, y4) <= y <= max(y3, y4):
        return x, y


def is_inside(inner_points, outer_points):
    """
    Returns True if all the inner_points are enclosed by the outer_points' shape\n
    Format for points: ((x1,y1),(x2,y2),(x3,y3))
    """
    pass


def is_overlapping(points1, points2, tolerance=0):
    pass


def get_similarity(points1, points2, tolerance=0, rotation=False, scale=False):
    """
    return the similarity percentage between the two group of points
    """
    pass


def get_shortest_path(moving_shape, pivot_line, obstacles, destination, pivot_point=None, tolerance=0, refpoint=None):
    pass

# -----------------------Small utility functions-----------------------


def _first_last_point(points, add=True):
    if points[0] == points[-1] and not add:
        return points[0:-1]
    elif points[0] != points[-1] and add:
        return tuple(list(points) + [points[0]])
    else:
        return points


def principal_angle(angle):
    while angle > 180:
        angle -= 360
    while angle <= -180:
        angle += 360
    return angle


def signed_angle_dif(target,source):
    return (target-source+180) % 360 -180


def to_polar(x, y):
    return numpy.sqrt(x**2 + y**2), get_angle((x, y))


def to_cartesian(magnitude, angle):
    return magnitude * numpy.cos(angle), magnitude * numpy.sin(angle)
