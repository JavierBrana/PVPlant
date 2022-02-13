import FreeCAD
import ArchComponent
import Draft
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

import PVPlantResources


def VertexesToPoints(Vertexes):
    return [ver.Point for ver in Vertexes]

def makeOffset(trackerPath, offset):
    pts = []
    for ver in trackerPath.Shape.Vertexes:
        point = ver.Point
        tmp = FreeCAD.Vector(point.x, point.y, point.z + offset)
        pts.append(tmp)
    limit = Part.makePolygon(pts)
    return limit

'''
------------------------------------------------------------------------------------------------------------------------
function getCuts:

- Description: 

- Inputs:
    1. crossPoints:
    2. PointList:
    
- Outputs:
    1. cutSection:
    2. newPath:
------------------------------------------------------------------------------------------------------------------------
'''


def getCuts(crossPoints, PointList):
    cutSection = []
    cutIndexes = []

    for ind in range(0, len(crossPoints) - 1, 2):
        Section = []
        Xmin = 0
        Xmax = 0
        Ymin = 0
        Ymax = 0

        if True:
            Xmin = min([crossPoints[ind].x, crossPoints[ind + 1].x])
            Xmax = max([crossPoints[ind].x, crossPoints[ind + 1].x])
            Ymin = min([crossPoints[ind].y, crossPoints[ind + 1].y])
            Ymax = max([crossPoints[ind].y, crossPoints[ind + 1].y])
        else:
            if crossPoints[ind].x <= crossPoints[ind + 1].x:
                Xmin = crossPoints[ind].x
                Xmax = crossPoints[ind + 1].x
            else:
                Xmin = crossPoints[ind + 1].x
                Xmax = crossPoints[ind].x

            if crossPoints[ind].y <= crossPoints[ind + 1].y:
                Ymin = crossPoints[ind].y
                Ymax = crossPoints[ind + 1].y
            else:
                Ymin = crossPoints[ind + 1].y
                Ymax = crossPoints[ind].y

        indexes = []
        Section.append(crossPoints[ind])
        for p in PointList:
            if (Xmin <= p.x <= Xmax) and (Ymin <= p.y <= Ymax):
                Section.append(p)
                indexes.append(PointList.index(p))
        Section.append(crossPoints[ind + 1])
        cutIndexes.append(indexes)
        cutSection.append(Section)

    newPath = PointList.copy()
    crossInd = len(crossPoints) - 2
    for cutRange in reversed(cutIndexes):
        if len(cutRange) > 0:
            ind = min(cutRange)
            for i in cutRange:
                newPath.pop(ind)
            newPath.insert(cutRange[0], crossPoints[crossInd + 1])
            newPath.insert(cutRange[0], crossPoints[crossInd])
            crossInd -= 2
    return cutSection, newPath


'''
------------------------------------------------------------------------------------------------------------------------
function calculateEarthWorks:

- Description: 

- Inputs:
    1. crossPoints:
    2. PointList:
    
- Outputs:
    1. cutSection:
    2. newPath:
------------------------------------------------------------------------------------------------------------------------
'''


def calculateEarthWorks(trackerPath, Terrain, offsetup=200, offsetdown=200):
    Cuts = None
    Fills = None
    newPath = None
    if offsetup == 0:
        offsetup = 1
    if offsetdown == 0:
        offsetdown = 1
    limitTop = makeOffset(trackerPath, offsetup)
    limitBottom = makeOffset(trackerPath, -offsetdown)

    points3D = []
    if Terrain.isDerivedFrom("Part::Feature"):
        tmp_pts = Terrain.Shape.makeParallelProjection(trackerPath.Shape.Wires[0], FreeCAD.Vector(0, 0, 1))
        points3D = [ver.Point for ver in tmp_pts.Vertexes]
    elif Terrain.isDerivedFrom("Mesh::Feature"):
        import MeshPart as mp
        points3D = mp.projectShapeOnMesh(trackerPath.Shape, Terrain.Mesh, FreeCAD.Vector(0, 0, 1))

    points3D = sorted(points3D, key=lambda k: k.y, reverse=True)
    terrainProfile = Part.makePolygon(points3D)
    # Part.show(terrainProfile)

    sectionTop = terrainProfile.section(limitTop)
    crossTopPoints = VertexesToPoints(sectionTop.Vertexes)
    cutPoints, PointList = getCuts(crossTopPoints, points3D)

    # Prueba:
    '''
    lT = Part.Wire([limitTop.Vertexes[0].Point, limitTop.Vertexes[1].Point])
    tP = Part.Wire(points3D)
    '''

    Cuts = []
    for i in cutPoints:
        Cuts.extend(i)

        Cut = Draft.makeWire(i, closed=True, face=None, support=None)
        Cut.Label = "CutSections"
        Cut.ViewObject.LineColor = (1.00, 0.00, 0.00)
        Cut.ViewObject.ShapeColor = (1.00, 0.00, 0.00)
        '''
        Cuts.append(Cut)
        '''

    sectionBottom = terrainProfile.section(limitBottom)
    crossBottomPoints = VertexesToPoints(sectionBottom.Vertexes)
    fillPoints, PointList = getCuts(crossBottomPoints, PointList)

    Fills = []
    for i in fillPoints:
        Fills.extend(i)

        Fill = Draft.makeWire(i, closed=True, face=None, support=None)
        Fill.Label = "FillSections"
        Fill.ViewObject.LineColor = (0.00, 0.33, 1.00)
        Fill.ViewObject.ShapeColor = (0.00, 0.33, 1.00)
        '''
        Fills.append(Fill)
        '''

    PointList = sorted(PointList, key=lambda k: k.y, reverse=(trackerPath.Shape.Vertexes[-1].Point.y <
                                                              trackerPath.Shape.Vertexes[0].Point.y))
    # newPath = Draft.makeWire(PointList, closed=False, face=None)
    # newPath.Label = trackerPath.Label + "_NewPath"

    return Cuts, Fills, newPath


def makeMesh(Points, MaxlengthLE=10000):
    def MaxLength(P1, P2, P3, MaxlengthLE):

        new = False
        if new:
            tri = [[P1, P2], [P2, P3], [P3, P1]]
            for i, j in tri:
                vec = i.sub(j)

                # Compare with input
                if vec.Length > MaxlengthLE:
                    return False
            return True
        else:
            p1 = FreeCAD.Vector(P1[0], P1[1], 0)
            p2 = FreeCAD.Vector(P2[0], P2[1], 0)
            p3 = FreeCAD.Vector(P3[0], P3[1], 0)

            # Calculate length between triangle vertices
            List = [[p1, p2], [p2, p3], [p3, p1]]
            for i, j in List:
                vec = i.sub(j)

                # Compare with input
                if vec.Length > MaxlengthLE:
                    return False
            return True

    import numpy as np
    from scipy.spatial import Delaunay

    Data = np.array(Points)
    tri = Delaunay(Data)

    MeshList = []
    for i in tri.vertices:
        first = int(i[0])
        second = int(i[1])
        third = int(i[2])

        # Test triangle
        if MaxlengthLE == 0:
            MeshList.append(Data[first])
            MeshList.append(Data[second])
            MeshList.append(Data[third])
        elif MaxLength(Data[first], Data[second], Data[third], MaxlengthLE):  # \
            # and self.MaxAngle(Data[first], Data[second], Data[third]):
            MeshList.append(Data[first])
            MeshList.append(Data[second])
            MeshList.append(Data[third])

    import Mesh
    MeshObject = Mesh.Mesh(MeshList)

    #MeshObject.Placement.move(nbase)
    Surface = FreeCAD.ActiveDocument.addObject("Mesh::Feature")
    Surface.Mesh = MeshObject
    return Surface

class _EarthWorksTaskPanel:
    def __init__(self):
        import os

        self.To = None

        # self.form:
        self.form = FreeCADGui.PySideUic.loadUi(os.path.join(PVPlantResources.__dir__, "PVPlantEarthworks.ui"))
        self.form.setWindowIcon(QtGui.QIcon(os.path.join(PVPlantResources.DirIcons, "convert.svg")))

    def accept(self):
        from datetime import datetime
        starttime = datetime.now()

        FreeCAD.ActiveDocument.openTransaction("Calculate EarthWorks")
        terrain = FreeCAD.ActiveDocument.Site.Terrain
        sel = FreeCADGui.Selection.getSelection()
        # TODO: check if selection objects are frames and get their placement axis

        Cuts = []
        Fills = []
        newPaths = []
        for obj in sel:
            cut, fill, newpath = calculateEarthWorks(obj, terrain,
                                                     self.form.editToleranceCut.value(),
                                                     self.form.editToleranceFill.value())
            if not (cut is None):
                Cuts.extend(cut)
            '''
            if not (fill is None):
                Fills.append(fill.Points)
                makeMesh(pointsfromlines(Fills))
            if not (newpath is None):
                newPaths.append(newpath.Points)
                makeMesh(pointsfromlines(newPaths), 0)
            '''
        #makeMesh(Cuts)
        FreeCAD.activeDocument().recompute()

        total_time = datetime.now() - starttime
        print(" -- Tiempo tardado:", total_time)
        self.closeForm()
        return True

    def reject(self):
        self.closeForm()
        return True

    def closeForm(self):
        FreeCADGui.Control.closeDialog()

def pointsfromlines(paths):
    points = []
    for path in paths:
        for point in path:
            points.append(point)
    return points


class _CommandCalculateEarthworks:

    def GetResources(self):
        return {'Pixmap': str(os.path.join(PVPlantResources.DirIcons, "pico.svg")),
                'Accel': "C, E",
                'MenuText': QT_TRANSLATE_NOOP("Placement", "Movimiento de tierras"),
                'ToolTip': QT_TRANSLATE_NOOP("Placement", "Calcular el movimiento de tierras")}

    def Activated(self):
        TaskPanel = _EarthWorksTaskPanel()
        FreeCADGui.Control.showDialog(TaskPanel)

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        else:
            return False


if FreeCAD.GuiUp:
    FreeCADGui.addCommand('PVPlantEarthworks', _CommandCalculateEarthworks())
