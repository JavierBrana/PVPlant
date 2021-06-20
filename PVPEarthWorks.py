import FreeCAD
import ArchComponent
import Draft

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

import threading
import PVPlantResources


def makeOffset(trackerPath, offset):
    placement = trackerPath.Placement

    limit = FreeCAD.ActiveDocument.copyObject(trackerPath, False)
    limit.Placement = placement
    limit.Placement.Base.z += offset
    limit.ViewObject.PointSize = 5.00
    limit.ViewObject.LineWidth = 5.00

    return limit

def VertexesToPoints(Vertexes):
    PointList = []
    for ver in Vertexes:
        PointList.append(ver.Point)
    return PointList


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

        indexes =[]
        Section.append(crossPoints[ind])
        for p in PointList:
            if (Xmin <= p.x <= Xmax) and (Ymin <= p.y <= Ymax):
                Section.append(p)
                indexes.append(PointList.index(p))
        Section.append(crossPoints[ind+1])
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
def calculateEarthWorks(trackerPath, TerrainMesh, offsetup = 200, offsetdown = 200):
    import MeshPart as mp

    Cuts = None
    Fills = None

    limitTop = makeOffset(trackerPath, offsetup)
    limitTop.Label = trackerPath.Label + "_LimitTop"
    limitTop.ViewObject.LineColor = (1.00, 0.00, 0.00)

    limitBottom = makeOffset(trackerPath, -offsetdown)
    limitBottom.Label = trackerPath.Label + "_LimitBotton"
    limitBottom.ViewObject.LineColor = (0.00,0.33,1.00)


    #TODO: Cambiar esto para asegurarse de que tenga todos los puntos
    points3D = mp.projectShapeOnMesh(trackerPath.Shape, TerrainMesh.Mesh, FreeCAD.Vector(0, 0, 1))
    PointList = []
    for pl in points3D:
        PointList += pl
    realPath = Draft.makeWire(PointList, closed=False, face=None, support=None)

    PointList = realPath.Points.copy()
    realPath.Label = trackerPath.Label + "_realPath"
    FreeCAD.activeDocument().recompute()

    sectionTop = realPath.Shape.section(limitTop.Shape)
    crossTopPoints = VertexesToPoints(sectionTop.Vertexes)
    cutPoints, PointList = getCuts(crossTopPoints, PointList)
    for i in cutPoints:
        Cuts = Draft.makeWire(i, closed=True, face=None, support=None)
        Cuts.Label = "CutSections"
        Cuts.ViewObject.LineColor = (1.00, 0.00, 0.00)
        Cuts.ViewObject.ShapeColor = (1.00, 0.00, 0.00)

    sectionBottom = realPath.Shape.section(limitBottom.Shape)
    crossBottomPoints = VertexesToPoints(sectionBottom.Vertexes)
    fillPoints, PointList = getCuts(crossBottomPoints, PointList)
    for i in fillPoints:
        Fills = Draft.makeWire(i, closed=True, face=None, support=None)
        Fills.Label = "FillSections"
        Fills.ViewObject.LineColor = (0.00,0.33,1.00)
        Fills.ViewObject.ShapeColor = (0.00,0.33,1.00)

    PointList = sorted(PointList, key=lambda k: k.y, reverse = (trackerPath.End.y < trackerPath.Start.y))
    newPath = Draft.makeWire(PointList, closed=False, face=None, support=None)
    newPath.Label = trackerPath.Label + "_NewPath"

    FreeCAD.ActiveDocument.removeObject(limitTop.Name)
    FreeCAD.ActiveDocument.removeObject(limitBottom.Name)
    FreeCAD.activeDocument().recompute()

    return Cuts, Fills, newPath


def makeMesh(Points, MaxlengthLE = 10000):
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
    import scipy.spatial

    # Normalize points
    fpoint = Points[0]
    nbase = fpoint # FreeCAD.Vector(fpoint[0], fpoint[1], fpoint[2])
    # scale_factor = FreeCAD.Vector(base.x / 1677.7216, base.y / 1677.7216, base.Z / 1677.7216)
    # nbase = scale_factor.multiply(1677.7216)

    data = []
    for point in Points:
        data.append([point.x - nbase.x, point.y - nbase.y, point.z - nbase.z])
    Data = np.array(data)
    del data

    # Create delaunay triangulation
    tri = scipy.spatial.Delaunay(Data[:, :2])

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
        elif MaxLength(Data[first], Data[second], Data[third], MaxlengthLE):# \
                #and self.MaxAngle(Data[first], Data[second], Data[third]):
            MeshList.append(Data[first])
            MeshList.append(Data[second])
            MeshList.append(Data[third])

    import Mesh
    MeshObject = Mesh.Mesh(MeshList)
    MeshObject.Placement.move(nbase)
    Surface = FreeCAD.ActiveDocument.addObject("Mesh::Feature")
    Surface.Mesh = MeshObject
    return Surface

def functiontmp():
        import PVPlantPlacement
        import PVPlantCreateTerrainMesh as ctm

        sel = FreeCADGui.Selection.getSelection()
        terrain = PVPlantPlacement.getTerrain()

        Cuts = []
        Fills = []
        newPaths = []
        for obj in sel:
            cut, fill, newpath = calculateEarthWorks(obj, terrain)
            if not (cut is None):
                Cuts.append(cut.Points)
            if not (fill is None):
                Fills.append(fill.Points)
            newPaths.append(newpath.Points)

        makeMesh(pointsfromlines(Cuts))
        makeMesh(pointsfromlines(Fills))
        makeMesh(pointsfromlines(newPaths), 0)

        FreeCAD.activeDocument().recompute()

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
        functiontmp()

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        else:
            return False


if FreeCAD.GuiUp:
    FreeCADGui.addCommand('PVPlantEarthworks', _CommandCalculateEarthworks())
