import FreeCAD
import Part

if FreeCAD.GuiUp:
    import FreeCADGui, os
    from PySide import QtCore, QtGui
    from DraftTools import translate
    from PySide.QtCore import QT_TRANSLATE_NOOP
else:
    # \cond
    def translate(ctxt, txt):
        return txt


    def QT_TRANSLATE_NOOP(ctxt, txt):
        return txt
    # \endcond

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s


def partToWire(obj):
    path = Part.__sortEdges__(obj.Shape.Edges)
    points = []
    for ed in path:
        for ver in ed.Vertexes:
            points.append(ver.Point)

    path1 = points
    path1.MakeFace = False
    path1.Label = path.Label

    return path1


'''
def isInside(border, target):
    degree = 0
    for i in range(len(border) - 1):
        a = border[i]
        b = border[i + 1]

        # calculate distance of vector
        A = getDistance(a[0], a[1], b[0], b[1]);
        B = getDistance(target[0], target[1], a[0], a[1])
        C = getDistance(target[0], target[1], b[0], b[1])

        # calculate direction of vector
        ta_x = a[0] - target[0]
        ta_y = a[1] - target[1]
        tb_x = b[0] - target[0]
        tb_y = b[1] - target[1]

        cross = tb_y * ta_x - tb_x * ta_y
        clockwise = cross < 0

        # calculate sum of angles
        if(clockwise):
            degree = degree + math.degrees(math.acos((B * B + C * C - A * A) / (2.0 * B * C)))
        else:
            degree = degree - math.degrees(math.acos((B * B + C * C - A * A) / (2.0 * B * C)))

    if(abs(round(degree) - 360) <= 3):
        return True
    return False
'''

def VectorToPoint(vector):
    from shapely.geometry import Point
    if True:
        return Point(vector.x, vector.y)
    else:
        return Point(vector.x, vector.y, vector.z)

def PolygonToPolygon(poly):
    from shapely.geometry import Polygon
    coords = []
    for ver in poly.Shape.Vertexes:
        coords.append(VectorToPoint(ver.Point))

    return Polygon(coords)

def isPointInsidePolygon(vector, aPoly):

    useshapely = True

    if useshapely:
        from shapely.geometry import Polygon
        import shapely.speedups

        shapely.speedups.enable()

        point = VectorToPoint(vector)
        poly = PolygonToPolygon(aPoly)
        p = point.within(poly)
        return p

        pip_mask = point.within(poly.loc[0, 'geometry'])
        print("mask: ", pip_mask)
        print("   --------------------   ")
        return pip_mask

        '''
        polya = Polygon([(0, 0), (0, 1), (1, 1), (1, 0)])
        polyb = Polygon([(0.5, 0.5), (0.5, 0.8), (0.8, 0.8), (0.8, 0.5)])

        return polya.contains(polyb)
        '''

def isPolygonInsidePolygon(polygon1, polygon2):
    useshapely = True

    if useshapely:
        from shapely.geometry import Polygon

        polya = Polygon([(0, 0), (0, 1), (1, 1), (1, 0)])
        polyb = Polygon([(0.5, 0.5), (0.5, 0.8), (0.8, 0.8), (0.8, 0.5)])

        return polya.contains(polyb)


# -------------------------------------------------------------------------------
# This function gives the answer whether the given point is inside or outside the predefined polygon
# Unlike standard ray-casting algorithm, this one works on edges! (with no performance cost)
# According to performance tests - this is the best variant.

# arguments:
# Polygon - searched polygon
# Point - an arbitrary point that can be inside or outside the polygon
# length - the number of point in polygon (Attention! The list itself has an additional member - the last point coincides with the first)

# return value:
# 0 - the point is outside the polygon
# 1 - the point is inside the polygon
# 2 - the point is one edge (boundary)

def is_inside_sm(polygon, point):
    length = len(polygon) - 1
    dy2 = point[1] - polygon[0][1]
    intersections = 0
    ii = 0
    jj = 1

    while ii < length:
        dy = dy2
        dy2 = point[1] - polygon[jj][1]

        # consider only lines which are not completely above/below/right from the point
        if dy * dy2 <= 0.0 and (point[0] >= polygon[ii][0] or point[0] >= polygon[jj][0]):

            # non-horizontal line
            if dy < 0 or dy2 < 0:
                F = dy * (polygon[jj][0] - polygon[ii][0]) / (dy - dy2) + polygon[ii][0]

                if point[0] > F:  # if line is left from the point - the ray moving towards left, will intersect it
                    intersections += 1
                elif point[0] == F:  # point on line
                    return 2

            # point on upper peak (dy2=dx2=0) or horizontal line (dy=dy2=0 and dx*dx2<=0)
            elif dy2 == 0 and (point[0] == polygon[jj][0] or (
                    dy == 0 and (point[0] - polygon[ii][0]) * (point[0] - polygon[jj][0]) <= 0)):
                return 2

            # there is another possibility: (dy=0 and dy2>0) or (dy>0 and dy2=0). It is skipped
            # deliberately to prevent break-points intersections to be counted twice.

        ii = jj
        jj += 1

    # print 'intersections =', intersections
    return intersections & 1


# buscar el camino más corto:
from collections import defaultdict
class Graph():
    def __init__(self):
        """
        self.edges is a dict of all possible next nodes
        e.g. {'X': ['A', 'B', 'C', 'E'], ...}
        self.weights has all the weights between two nodes,
        with the two nodes as a tuple as the key
        e.g. {('X', 'A'): 7, ('X', 'B'): 2, ...}
        """
        self.edges = defaultdict(list)
        self.weights = {}

    def add_edge(self, from_node, to_node, weight):
        # Note: assumes edges are bi-directional
        self.edges[from_node].append(to_node)
        self.edges[to_node].append(from_node)
        self.weights[(from_node, to_node)] = weight
        self.weights[(to_node, from_node)] = weight



def dijsktra(graph, initial, end):
    # shortest paths is a dict of nodes
    # whose value is a tuple of (previous node, weight)
    shortest_paths = {initial: (None, 0)}
    current_node = initial
    visited = set()

    while current_node != end:
        visited.add(current_node)
        destinations = graph.edges[current_node]
        weight_to_current_node = shortest_paths[current_node][1]

        for next_node in destinations:
            weight = graph.weights[(current_node, next_node)] + weight_to_current_node
            if next_node not in shortest_paths:
                shortest_paths[next_node] = (current_node, weight)
            else:
                current_shortest_weight = shortest_paths[next_node][1]
                if current_shortest_weight > weight:
                    shortest_paths[next_node] = (current_node, weight)

        next_destinations = {node: shortest_paths[node] for node in shortest_paths if node not in visited}
        if not next_destinations:
            return "Route Not Possible"
        # next node is the destination with the lowest weight
        current_node = min(next_destinations, key=lambda k: next_destinations[k][1])

    # Work back through destinations in shortest path
    path = []
    while current_node is not None:
        path.append(current_node)
        next_node = shortest_paths[current_node][0]
        current_node = next_node
    # Reverse path
    path = path[::-1]
    return path


def makeProfileFromTerrein(path):
    terrain = FreeCAD.ActiveDocument.Terrain
    points = []
    if terrain.isDerivedFrom("Part::Feature"):
        tmp = terrain.Shape.makeParallelProjection(path, FreeCAD.Vector(0, 0, 1))
        points.extend([ver.Point for ver in tmp.Vertexes])
    elif terrain.isDerivedFrom("Mesh::Feature"):
        points.append(terrain.Mesh.BoundBox.Center)

    return Part.makePolygon(points)

'''
Flatten a wire to 2 axis: X - Y
'''
def FlattenWire(wire):
    pts = []
    xx = 0
    for i, ver in enumerate(wire.Vertexes):
        if i == 0:
            pts.append(FreeCAD.Vector(xx, ver.Point.z, 0))
        else:
            xx += (ver.Point - wire.Vertexes[i - 1].Point).Length
            pts.append(FreeCAD.Vector(xx, ver.Point.z, 0))
    return Part.makePolygon(pts)






