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

def pointsfromlines(paths):
    points = []
    for path in paths:
        for point in path:
            points.append(point)
    return points

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
function calculateEarthWorks2D:

- Description: 

- Inputs:
    1. crossPoints:
    2. PointList:
    
- Outputs:
    1. cutSection:
    2. newPath:
------------------------------------------------------------------------------------------------------------------------
'''


def calculateEarthWorks2D(trackerPath, Terrain, offsetup=200, offsetdown=200):
    Cuts = None
    Fills = None
    newPath = None
    if offsetup == 0:
        offsetup = 1
    if offsetdown == 0:
        offsetdown = 1
    limitTop = makeOffset(trackerPath, offsetup)
    limitBottom = makeOffset(trackerPath, -offsetdown)

    # TODO: hacer genérico terrainProfile no points3D
    points3D = list()
    if Terrain.isDerivedFrom("Part::Feature"):
        tmp_pts = Terrain.Shape.makeParallelProjection(trackerPath.Shape.Wires[0], FreeCAD.Vector(0, 0, 1))
        points3D = VertexesToPoints(tmp_pts.Vertexes)
    elif Terrain.isDerivedFrom("Mesh::Feature"):
        import MeshPart as mp
        points3D = mp.projectShapeOnMesh(trackerPath.Shape, Terrain.Mesh, FreeCAD.Vector(0, 0, 1))

    points3D = sorted(points3D, key=lambda k: k.y, reverse=True)
    terrainProfile = Part.makePolygon(points3D)
    # Part.show(terrainProfile)

    sectionTop = terrainProfile.section(limitTop)
    crossTopPoints = VertexesToPoints(sectionTop.Vertexes)
    cutPoints, PointList = getCuts(crossTopPoints, points3D)

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
        self.To = None

        # self.form:
        self.form = FreeCADGui.PySideUic.loadUi(os.path.join(PVPlantResources.__dir__, "PVPlantEarthworks.ui"))
        self.form.setWindowIcon(QtGui.QIcon(os.path.join(PVPlantResources.DirIcons, "convert.svg")))

    def accept(self):
        from datetime import datetime
        starttime = datetime.now()

        from multiprocessing import cpu_count
        from multiprocessing.pool import ThreadPool

        FreeCAD.ActiveDocument.openTransaction("Calculate EarthWorks")
        terrain = FreeCAD.ActiveDocument.Site.Terrain
        terrain = None
        type = 0
        if False:  # prueba
            terrain = FreeCAD.ActiveDocument.Mesh005.Mesh
        else:
            import PVPlantSite
            if PVPlantSite.get().Terrain.TypeId == 'Mesh::Feature':
                terrain = PVPlantSite.get().Terrain.Mesh
            else:
                terrain = PVPlantSite.get().Terrain.Shape
                type = 1

        sel = FreeCADGui.Selection.getSelection()
        # TODO: check if selection objects are frames and get their placement axis

        '''  2D:
        Cuts = []
        Fills = []
        newPaths = []
        if not self.form.edit3D.isChecked():
            for obj in sel:
                cut, fill, newpath = calculateEarthWorks2D(obj, terrain,
                                                         self.form.editToleranceCut.value(),
                                                         self.form.editToleranceFill.value())
                if not (cut is None):
                    Cuts.extend(cut)
                if not (fill is None):
                    Fills.append(fill.Points)
                    makeMesh(pointsfromlines(Fills))
                if not (newpath is None):
                    newPaths.append(newpath.Points)
                    makeMesh(pointsfromlines(newPaths), 0)
            # makeMesh(Cuts)
        '''

        def makeSolidTerrain(pol):
            import BOPTools.SplitAPI as splitter
            ext = pol.extrude(FreeCAD.Vector(0, 0, terrain.BoundBox.ZMax + 1000))
            sp = splitter.slice(ext, [terrain, ], "Split")
            return sp.childShapes()[0]

        def calculatetools(column):
            lines = []
            faces = []
            #v1:
            for group in column:
                ''''''

            #V0:
            for group in column:
                for frame in group:
                    ptn = frame.Length.Value / 2 + 1000
                    p1 = FreeCAD.Vector(-ptn, 0, 0)
                    p2 = FreeCAD.Vector( ptn, 0, 0)
                    line = Part.LineSegment(p1, p2).toShape()
                    line.Placement = frame.Placement
                    lines.append(line)

                    dist = frame.Width.Value + 2 * self.form.editOffset.value()
                    rec = line.extrude(FreeCAD.Vector(dist, 0, 0))
                    rec.Placement.Base.x = rec.Placement.Base.x - dist / 2
                    faces.append(rec)
            return faces

        def showObjects(obj):
            Part.show(obj[0], obj[1])

        # 1. step: create a solid terrain:
        #if terrain.isDerivedFrom("Part::TopoShape"): # if it is a shell
        results = ThreadPool(cpu_count() - 1).imap_unordered(makeSolidTerrain, FreeCAD.ActiveDocument.Fusion.Shape.childShapes())
        tmp = []
        for result in results:
            #FreeCAD.Console.PrintWarning(result)
            tmp.append(result)
        terrain = Part.makeCompound(tmp)
        #Part.show(terrain, "t3d")
        print(" -- Generación de terreno:", datetime.now() - starttime)
        # 2. step: calculate earthworks:
        sel = sorted(sel, key=lambda k: k.Shape.Vertexes[0].Point.x, reverse=False)
        height = 10000
        from PVPlantPlacement import getCols as getCols
        cols = getCols(sel)
        # 2.1. Crear las trayectorias:
        results = ThreadPool(cpu_count() - 1).imap_unordered(calculatetools, cols)
        tmp.clear()
        for result in results:
            for face in result:
                tmp.append(face)
        tool = Part.makeCompound(tmp)
        #Part.show(tool, "tool2D")
        tool = tool.extrude(FreeCAD.Vector(0, 0, height))
        s1 = tool.Solids.pop()
        tool = s1.fuse(tool.Solids)
        #Part.show(tool, "tool3D")
        z_initial = tool.Placement.Base.z

        ''' not multiprocessing:
        stime = datetime.now()
        tool.Placement.Base.z = z_initial + self.form.editToleranceCut.value()
        cut = tool.cut(terrain)
        cut = tool.cut(cut)
        #Part.show(cut)
        print(" -- Generación de cuts:", datetime.now() - stime)
        stime = datetime.now()
        tool.Placement.Base.z = z_initial - self.form.editToleranceFill.value() - height
        fill = tool.cut([terrain, ])
        print(" -- Generación de fills:", datetime.now() - stime)
        '''
        def calculateCutFill(ind):
            if ind==0:
                tool.Placement.Base.z = z_initial + self.form.editToleranceCut.value()
                return tool.common([terrain, ])
            else:
                tool.Placement.Base.z = z_initial - self.form.editToleranceFill.value() - height
                return tool.cut([terrain, ])
        cnt = [0,1]
        results = ThreadPool(cpu_count() - 1).imap_unordered(calculateCutFill, cnt)
        tmp.clear()
        for result in results:
            tmp.append(result)
        cut, fill = tmp

        stime = datetime.now()
        terrain = terrain.cut([cut])
        print(" -- Generación de cutted terrain:", datetime.now() - stime)
        stime = datetime.now()
        terrain = terrain.fuse([fill])
        print(" -- Generación de filled terrain:", datetime.now() - stime)

        '''
        Part.show(cut, "cut3d")
        Part.show(fill, "fill3d")
        Part.show(terrain, "Modified_Surface")
        '''

        objects = [[cut, "cut3d"], [fill, "fill3d"]]
        ThreadPool(cpu_count() - 1).imap_unordered(showObjects, objects)

        #FreeCAD.activeDocument().recompute()
        total_time = datetime.now() - starttime
        print(" -- Tiempo tardado:", total_time)
        self.closeForm()
        return True

    def reject(self):
        self.closeForm()
        return True

    def closeForm(self):
        FreeCADGui.Control.closeDialog()

def ShapeToMesh(shape):
    facets = list()
    for face in shape.Faces:
        pt = [ver.Point for ver in face.Vertexes]

def MeshToShape(mesh):
    faces = list()
    for facet in mesh.Facets:
        pt = facet.Points.copy()
        pt.append(pt[0])
        faces.append(Part.Face(Part.makePolygon(pt)))
    shape = faces.pop()
    shape = shape.fuse([faces])
    return shape

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
