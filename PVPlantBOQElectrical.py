# /**********************************************************************
# *                                                                     *
# * Copyright (c) 2021 Javier Braña <javier.branagutierrez@gmail.com>  *
# *                                                                     *
# * This program is free software; you can redistribute it and/or modify*
# * it under the terms of the GNU Lesser General Public License (LGPL)  *
# * as published by the Free Software Foundation; either version 2 of   *
# * the License, or (at your option) any later version.                 *
# * for detail see the LICENCE text file.                               *
# *                                                                     *
# * This program is distributed in the hope that it will be useful,     *
# * but WITHOUT ANY WARRANTY; without even the implied warranty of      *
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the       *
# * GNU Library General Public License for more details.                *
# *                                                                     *
# * You should have received a copy of the GNU Library General Public   *
# * License along with this program; if not, write to the Free Software *
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307*
# * USA                                                                 *
# *                                                                     *
# ***********************************************************************

import FreeCAD, Draft
import ArchComponent
import PVPlantSite
import copy

if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore, QtGui, QtSvg
    from DraftTools import translate
    from PySide.QtCore import QT_TRANSLATE_NOOP
    import draftguitools.gui_trackers as DraftTrackers

    import Part
    import pivy
    from pivy import coin
    import os
else:
    # \cond
    def translate(ctxt, txt):
        return txt


    def QT_TRANSLATE_NOOP(ctxt, txt):
        return txt
    # \endcond

__title__ = "PVPlant Trench"
__author__ = "Javier Braña"
__url__ = "http://www.sogos-solar.com"

from PVPlantResources import DirIcons as DirIcons
from PVPlantResources import DirDocuments as DirDocuments
import openpyxl
from openpyxl.styles import Alignment, Border, Side, PatternFill, GradientFill, Font


def alpha_shape(points, alpha):
    """
    Compute the alpha shape (concave hull) of a set
    of points.
    @param points: Iterable container of points.
    @param alpha: alpha value to influence the
        gooeyness of the border. Smaller numbers
        don't fall inward as much as larger numbers.
        Too large, and you lose everything!
    """
    if len(points) < 4:
        # When you have a triangle, there is no sense
        # in computing an alpha shape.
        return geometry.MultiPoint(list(points)).convex_hull

    coords = np.array([point.coords[0] for point in points])
    tri = Delaunay(coords)
    triangles = coords[tri.vertices]
    a = ((triangles[:,0,0] - triangles[:,1,0]) ** 2 + (triangles[:,0,1] - triangles[:,1,1]) ** 2) ** 0.5
    b = ((triangles[:,1,0] - triangles[:,2,0]) ** 2 + (triangles[:,1,1] - triangles[:,2,1]) ** 2) ** 0.5
    c = ((triangles[:,2,0] - triangles[:,0,0]) ** 2 + (triangles[:,2,1] - triangles[:,0,1]) ** 2) ** 0.5
    s = ( a + b + c ) / 2.0
    areas = (s*(s-a)*(s-b)*(s-c)) ** 0.5
    circums = a * b * c / (4.0 * areas)
    filtered = triangles[circums < (1.0 / alpha)]
    edge1 = filtered[:,(0,1)]
    edge2 = filtered[:,(1,2)]
    edge3 = filtered[:,(2,0)]
    edge_points = np.unique(np.concatenate((edge1,edge2,edge3)), axis = 0).tolist()
    m = geometry.MultiLineString(edge_points)
    triangles = list(polygonize(m))
    return cascaded_union(triangles), edge_points


def makeBOQElectrical():
    ''' create a excel '''

    # export layout to Excel:

    # V0:
    import PVPlantPlacement

    sel = FreeCADGui.Selection.getSelection()
    MaxY = max(sel, key=lambda obj: obj.Placement.Base.y)
    MinY = min(sel, key=lambda obj: obj.Placement.Base.y)
    MaxX = max(sel, key=lambda obj: obj.Placement.Base.x)
    MinX = max(sel, key=lambda obj: obj.Placement.Base.x)

    cols = PVPlantPlacement.getCols(sel)
    for col in cols:
        for group in col:
            for frame in group:
                ''''''


    return

    ''' tmp: probar a exportar a excel - hacer el layout en excel'''
    print(" ------- Prueba de hacer layout en excel: ")
    if FreeCADGui.Selection.hasSelection():
        sel = FreeCADGui.Selection.getSelection()
        MaxY = max(sel, key=lambda p: p.Placement.Base.y).Placement.Base.y
        MinY = min(sel, key=lambda p: p.Placement.Base.y).Placement.Base.y
        MaxX = max(sel, key=lambda p: p.Placement.Base.x).Placement.Base.x
        MinX = max(sel, key=lambda p: p.Placement.Base.x).Placement.Base.x


    return

    print(" ------- Prueba dibujar contorno de los objetos seleccionados:  ")
    from scipy.spatial import ConvexHull
    from scipy.spatial import Delaunay
    import numpy as np

    # contorno:
    maxdist = 5000
    if FreeCADGui.Selection.hasSelection():
        sel = FreeCADGui.Selection.getSelection()
        pts = []
        for obj in sel:
            if False:
                for vert in obj.Shape.Vertexes:
                    point = vert.Point
                    pts.append(point)
            else:
                for ed in obj.Shape.Edges:
                    pts.extend(ed.discretize(Distance = maxdist))

        tmp = np.array(pts)
        hull = ConvexHull(tmp[:, :2])

        pts = []
        for ver in hull.vertices:
            point = tmp[ver]
            pts.append(FreeCAD.Vector(point[0], point[1], 0))
        Draft.makeWire(pts)

        alpha = alpha_shape(tmp, 10000)
        pts = []
        for edge in alpha:
            for ver in edge:
                point = tmp[ver]
                pts.append(FreeCAD.Vector(point[0], point[1]))
        Draft.makeWire(pts)

from scipy.spatial import Delaunay
import numpy as np

# https://stackoverflow.com/questions/23073170/calculate-bounding-polygon-of-alpha-shape-from-the-delaunay-triangulation
'''Alpha shapes is defined as a delaunay triangulation without edges exceeding alpha. First of remove all interior 
triangles and then all edges exceeding alpha.'''


def alpha_shape(points, alpha, only_outer=True):
    """
    Compute the alpha shape (concave hull) of a set of points.
    :param points: np.array of shape (n,2) points.
    :param alpha: alpha value.
    :param only_outer: boolean value to specify if we keep only the outer border
    or also inner edges.
    :return: set of (i,j) pairs representing edges of the alpha-shape. (i,j) are
    the indices in the points array.
    """
    assert points.shape[0] > 3, "Need at least four points"

    def add_edge(edges, i, j):
        """
        Add a line between the i-th and j-th points,
        if not in the list already
        """
        if (i, j) in edges or (j, i) in edges:
            # already added
            assert (j, i) in edges, "Can't go twice over same directed edge right?"
            if only_outer:
                # if both neighboring triangles are in shape, it is not a boundary edge
                edges.remove((j, i))
            return
        edges.add((i, j))

    def MaxLength(P1, P2, P3, MaxlengthLE):
        """
        Calculation of the 2D length between triangle edges
        """

        p1 = FreeCAD.Vector(P1[0], P1[1], 0)
        p2 = FreeCAD.Vector(P2[0], P2[1], 0)
        p3 = FreeCAD.Vector(P3[0], P3[1], 0)

        List = [[p1, p2], [p2, p3], [p3, p1]]
        for i, j in List:
            vec = i.sub(j)
            if vec.Length > MaxlengthLE:
                return False

        return True

    tri = Delaunay(points[:, :2])
    edges = set()
    # Loop over triangles:
    # ia, ib, ic = indices of corner points of the triangle
    if False:
        for ia, ib, ic in tri.simplices:
            pa = points[ia]
            pb = points[ib]
            pc = points[ic]
            # Computing radius of triangle circumcircle
            # www.mathalino.com/reviewer/derivation-of-formulas/derivation-of-formula-for-radius-of-circumcircle
            a = np.sqrt((pa[0] - pb[0]) ** 2 + (pa[1] - pb[1]) ** 2)
            b = np.sqrt((pb[0] - pc[0]) ** 2 + (pb[1] - pc[1]) ** 2)
            c = np.sqrt((pc[0] - pa[0]) ** 2 + (pc[1] - pa[1]) ** 2)
            s = (a + b + c) / 2.0
            area = np.sqrt(s * (s - a) * (s - b) * (s - c))
            circum_r = a * b * c / (4.0 * area)
            if circum_r < alpha:
                add_edge(edges, ia, ib)
                add_edge(edges, ib, ic)
                add_edge(edges, ic, ia)
    else:
        faces = tri.simplices
        from stl import mesh
        wireframe = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
        for i, f in enumerate(faces):
            if MaxLength(points[f[0]], points[f[1]], points[f[2]], alpha):
                for j in range(3):
                    wireframe.vectors[i][j] = points[f[j], :]

        import Mesh
        MeshObject = Mesh.Mesh(wireframe.vectors.tolist())
        #MeshObject.Placement.move(nbase)
        MeshObject.harmonizeNormals()
        Surface = FreeCAD.ActiveDocument.addObject("Mesh::Feature")
        Surface.Mesh = MeshObject

    return edges


'''
>>> import matplotlib.pyplot as plt
>>> plt.plot(points[:,0], points[:,1], 'o')
>>> for simplex in hull.simplices:
>>>     plt.plot(points[simplex,0], points[simplex,1], 'k-')
'''







class _CommandBOQElectrical:

    def GetResources(self):
        return {'Pixmap': str(os.path.join(DirIcons, "boqe.svg")),
                'Accel': "R, E",
                'MenuText': "BOQ Electrical",
                'ToolTip': ""}

    def Activated(self):
        makeBOQElectrical()

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        else:
            return False

if FreeCAD.GuiUp:
    FreeCADGui.addCommand('BOQElectrical', _CommandBOQElectrical())
