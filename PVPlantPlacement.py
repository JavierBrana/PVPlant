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


def getTerrain():
    for ob in FreeCAD.ActiveDocument.Objects:
        if ob.Name[:4] == "Site":
            return ob.Terrain

def makeRectangleFromRack(rack):
    pl = rack.Placement
    pl.Base.z = 0
    return Draft.makeRectangle(length=sel.Shape.BoundBox.XLength, height=sel.Shape.BoundBox.YLength, placement=pl)

def calculatePlacement(globalRotation, edge, offset, RefPt, xlate,
                       normal=None, Orientation = 0):
    """Orient shape to tangent at parm offset along edge."""
    import functools
    import DraftVecUtils
    import math

    placement = FreeCAD.Placement()
    placement.Rotation = globalRotation
    placement.move(RefPt + xlate)

    # unit +Z  Probably defined elsewhere?
    z = FreeCAD.Vector(0, 0, 1)
    # y = FreeCAD.Vector(0, 1, 0)               # unit +Y
    x = FreeCAD.Vector(1, 0, 0)                 # unit +X
    nullv = FreeCAD.Vector(0, 0, 0)

    # get local coord system - tangent, normal, binormal, if possible
    t = edge.tangentAt(get_parameter_from_v0(edge, offset))
    t.normalize()

    try:
        if normal:
            n = normal
        else:
            n = edge.normalAt(get_parameter_from_v0(edge, offset))
            n.normalize()
        b = (t.cross(n))
        b.normalize()
    # no normal defined here
    except FreeCAD.Base.FreeCADError:
        n = nullv
        b = nullv
        FreeCAD.Console.PrintLog("Draft PathArray.orientShape - Cannot calculate Path normal.\n")

    lnodes = z.cross(b)

    try:
        # Can't normalize null vector.
        lnodes.normalize()
    except:
        # pathological cases:
        pass

    if n == nullv:                                              # 1) can't determine normal, don't align.
        print(" 1) can't determine normal, don't align.")
        psi = 0.0
        theta = 0.0
        phi = 0.0
        FreeCAD.Console.PrintWarning("Draft PathArray.orientShape - Path normal is Null. Cannot align.\n")
    elif abs(b.dot(z)) == 1.0:                                  # 2) binormal is || z
        # align shape to tangent only
        print(" # 2) binormal is || z")
        psi = math.degrees(DraftVecUtils.angle(x, t, z))
        theta = 0.0
        phi = 0.0
        FreeCAD.Console.PrintWarning("Draft PathArray.orientShape - Gimbal lock. Infinite lnodes. Change Path or Base.\n")
    else:                                                        # 3) regular case
        psi = 0 #math.degrees(DraftVecUtils.angle(x, lnodes, z))
        theta = 0 #math.degrees(DraftVecUtils.angle(z, b, lnodes))
        phi = math.degrees(DraftVecUtils.angle(lnodes, t, b)) #* Orientation  ??

    rotations = [placement.Rotation]

    if psi != 0.0:
        rotations.insert(0, FreeCAD.Rotation(z, psi))
    if theta != 0.0:
        rotations.insert(0, FreeCAD.Rotation(lnodes, theta))
    if phi != 0.0:
        rotations.insert(0, FreeCAD.Rotation(b, phi))

    if len(rotations) == 1:
        finalRotation = rotations[0]
    else:
        finalRotation = functools.reduce(lambda rot1, rot2: rot1.multiply(rot2), rotations)

    placement.Rotation = finalRotation

    return placement

def calculatePlacementsOnPath(shapeRotation, pathwire, xlate, rackLength = 0, Spacing = 0, Orientation = 0,
                              _offset_ = 0):
    """Calculates the placements of a shape along a given path so that each copy will be distributed evenly"""
    import Part
    import DraftGeomUtils

    def getInd(ends, comp):
        for i in range(0, len(ends)):
            if comp <= ends[i]:
                return i
        return len(ends) - 1

    '''
    normal = DraftGeomUtils.getNormal(pathwire.Shape)
    if normal.z < 0:    # asegurarse de que siempre se dibuje por encima del suelo
        normal.z *= -1
        
    '''
    normal = FreeCAD.Vector(0, 0, 1)

    path = Part.__sortEdges__(pathwire.Shape.Edges)
    ends = []
    cdist = 0

    for e in path:  # find cumulative edge end distance
        cdist += e.Length
        ends.append(cdist)

    placements = []

    # TODO: Resisar que la estructura esté dentro del area del terreno
    newver = 2


    if newver == 0:
        step = rackLength + Spacing
        travel = rackLength / 2

        while ((travel + rackLength / 2) <= cdist):  # Cambiar esto
            # which edge in path should contain this shape?
            # avoids problems with float math travel > ends[-1]
            iend = getInd(ends, travel)

            # place shape at proper spot on proper edge
            remains = ends[iend] - travel
            offset = path[iend].Length - remains
            pt = path[iend].valueAt(get_parameter_from_v0(path[iend], offset))

            placements.append(calculatePlacement(shapeRotation,
                                                 path[iend],
                                                 offset,
                                                 pt, xlate, normal,
                                                 Orientation))
            travel += step

    elif newver == 1:
        travel = _offset_
        pro = False
        pts=[]

        while ((travel + rackLength / 2) <= cdist):  # Cambiar esto
            iend = getInd(ends, travel)
            remains = ends[iend] - travel
            offset = path[iend].Length - remains
            pt = path[iend].valueAt(get_parameter_from_v0(path[iend], offset))
            pts.append(pt)

            if pro:
                travel += Spacing

                l = Part.LineSegment()
                l.StartPoint = pts[len(pts) - 2]
                l.EndPoint = pts[len(pts) - 1]
                edge = l.toShape()
                print(edge.Length, " vs ", rackLength)
                placements.append(calculatePlacement(shapeRotation, edge, edge.Length / 2,
                                                     edge.CenterOfMass, xlate, normal,
                                                     Orientation))
                del l
                del edge
            else:
                travel += rackLength

            pro = not pro

        Draft.makeWire(pts, closed=False, face=None, support=None)
        del pts[:]

    elif newver == 2:

        pts = pathwire.Shape.discretize(Distance = Spacing + rackLength, First = _offset_)
        if len(pts) > 1:
            for i in range(0, len(pts) - 2):
                l = Part.LineSegment()
                l.StartPoint = pts[i]
                l.EndPoint = pts[i + 1]
                edge = l.toShape()
                print(edge.Length, " vs ", rackLength)
                placements.append(calculatePlacement(shapeRotation, edge, edge.Length / 2,
                                                     edge.CenterOfMass, xlate, normal,
                                                     Orientation))

                del l
                del edge

        path = Draft.makeWire(pts, closed=False, face=None, support=None)
        path.Label = "Wire_cut"

        #del pts[:]
    return placements, pts

def get_parameter_from_v0(edge, offset):
    """Return parameter at distance offset from edge.Vertexes[0].
    sb method in Part.TopoShapeEdge???
    """
    import DraftVecUtils

    lpt = edge.valueAt(edge.getParameterByLength(0))
    vpt = edge.Vertexes[0].Point

    if not DraftVecUtils.equals(vpt, lpt):
        # this edge is flipped
        length = edge.Length - offset
    else:
        # this edge is right way around
        length = offset
    return edge.getParameterByLength(length)


def calculateSections(frame, Placements):

    for placement in Placements:
        cp = FreeCAD.ActiveDocument.copyObject(frame, False)
        #FreeCADGuiGui.runCommand('Std_DuplicateSelection', 0)
        cp.Placement = placement
        cp.CloneOf = frame
        del cp


class _PVPlantPlacementTaskPanel:
    '''The editmode TaskPanel for Schedules'''

    def __init__(self, obj=None):
        self.Terrain = None
        self.Rack = None
        self.PVArea = None

        import os

        # self.form:
        self.form = FreeCADGui.PySideUic.loadUi(os.path.join(PVPlantResources.__dir__, "PVPlantPlacement.ui"))
        self.form.setWindowIcon(QtGui.QIcon(os.path.join(PVPlantResources.DirIcons, "way.svg")))
        self.form.editGapcols.setText("400 mm")
        self.form.editGapCols.setText("5000 mm")
        self.form.editOffsetHorizontal.setText("0 mm")
        self.form.editOffsetVertical.setText("0 mm")

        self.form.buttonPVArea.clicked.connect(self.addPVArea)
        self.form.buttonFrame.clicked.connect(self.addRack)

    def addTerrain(self):
        sel = FreeCADGui.Selection.getSelection()
        if len(sel) > 0:
            self.Terrain = sel[0]
            lineTerrain.setText(self.Terrain.Label)

    def addPVArea(self):
        sel = FreeCADGui.Selection.getSelection()
        if len(sel) > 0:
            self.PVArea = sel[0]
            self.form.editPVArea.setText(self.PVArea.Label)
            print(self.PVArea)

    def addRack(self):
        selection = FreeCADGui.Selection.getSelection()
        if len(selection) > 0:
            self.Rack = selection[0]
            self.form.editFrame.setText(self.Rack.Label)

    def accept(self):
        if self.Terrain is None:
            self.Terrain = getTerrain()

        if self.Terrain is not None and self.Rack is not None and self.PVArea is not None:
            if True:   # sin hilos
                placement3D_v1(Mesh = self.Terrain.Mesh,
                               Rack = self.Rack,
                               PVArea = self.PVArea,
                               ColSpacing = FreeCAD.Units.Quantity(self.form.editGapCols.text()).Value,
                               colSpacing = FreeCAD.Units.Quantity(self.form.editGapcols.text()).Value,
                               Orientation = self.form.comboOrientation.currentIndex(),
                               DirH = self.form.comboDirH.currentIndex(),
                               DirV = self.form.comboDirV.currentIndex(),
                               OffsetX = FreeCAD.Units.Quantity(self.form.editOffsetHorizontal.text()).Value,
                               OffsetY = FreeCAD.Units.Quantity(self.form.editOffsetVertical.text()).Value)

            else:       # con hilos
                import threading
                hilo = threading.Thread(target=placement3D, args=(self.Terrain.Mesh,
                            self.Rack,
                            self.PVArea,
                            FreeCAD.Units.Quantity(self.form.editGapCols.text()).Value,
                            FreeCAD.Units.Quantity(self.form.editGapcols.text()).Value,
                            self.form.comboOrientation.currentIndex(),
                            FreeCAD.Units.Quantity(self.form.editOffsetHorizontal.text()).Value,
                            FreeCAD.Units.Quantity(self.form.editOffsetHorizontal.text()).Value))
                hilo.start()

        return True


## TODO: multiprocessionado
#import multiprocessing as mp
#pool = mp.Pool(mp.cpu_count())
#pool.apply_async(función, args=(argumento1, argumento2 ...), callback = callback)
#pool.close()
#pool.join()

def placement3D(Mesh, Rack, PVArea, ColSpacing, colSpacing, Orientation, DirH=0, DirV=0, OffsetX=0, OffsetY=0):
    ## Info: ----------------------------------------------------------------------------------------------------------
    # 1. Orientation (Orientación de la estructura):
    #    -- 0 => Norte-Sur
    #    -- 1 => Este-Oeste
    # 2. DirH (Dirección Horizontal):
    #    -- 0: Izquierda
    #    -- 1: Derecha
    #    -- 2: Centro
    # 3. DirV (Dirección Vertical):
    #    -- 0: Arriba
    #    -- 1: Abajo
    #    -- 2: Centro
    ## ----------------------------------------------------------------------------------------------------------------

    # Debug: --------------------
    method = False
    # Debug fin -----------------

    from scipy.spatial import distance
    import math
    import PVPlantUtils
    import DraftGeomUtils, Part
    import MeshPart as mp

    NOrientation = 1 - Orientation
    PVArea2D = Draft.makeShape2DView(PVArea, FreeCAD.Vector(0, 0, 1))
    FreeCAD.activeDocument().recompute()
    DistCols = ColSpacing + (Rack.Shape.BoundBox.XLength if Orientation == 1 else Rack.Shape.BoundBox.YLength)

    paths = []
    inc = (PVArea.Shape.BoundBox.XMin + Rack.Shape.BoundBox.YLength / 2 + OffsetX) if Orientation == 0 else (
                PVArea.Shape.BoundBox.YMin + Rack.Shape.BoundBox.XLength / 2 + OffsetY)
    vecB = (float(1 * NOrientation), float(1 * Orientation), 0.0)
    stop = PVArea.Shape.BoundBox.XMax if Orientation == 0 else PVArea.Shape.BoundBox.YMax  ## original
    count = 0
    while inc < stop:
        vecA = (float(inc * NOrientation), float(inc * Orientation), 0.0)

        ## 25/12/2020  Idea: ------------------------------------------------------------------------------------------------------
        ## TODO: hacer intersecar un plano con el PVArea2D para sacar el path y proyectar al terreno
        line1 = Part.LineSegment(FreeCAD.Vector(inc, PVArea2D.Shape.BoundBox.YMin - 10000, 0),
                                 FreeCAD.Vector(inc, PVArea2D.Shape.BoundBox.YMax + 10000, 0)).toShape()

        if method:  ## TODO: Revisar qué metodo e mejor
            inter = PVArea2D.Shape.section(line1)
            FreeCAD.activeDocument().recompute()
            if len(inter.Vertexes) > 1:
                lis = []
                for vertex in inter.Vertexes:
                    lis.append(vertex.Point)
                #lis = list(dict.fromkeys(lis))
                lis = [ii for n, ii in enumerate(lis) if ii not in lis[:n]]

                for i in range(0, len(inter.Vertexes), 2):
                    try:
                        import MeshPart as mp
                        edge = Part.LineSegment(inter.Vertexes[i].Point, inter.Vertexes[i + 1].Point).toShape()
                        if edge.Length >= Rack.Shape.BoundBox.XLength:
                            plist = mp.projectShapeOnMesh(edge, Mesh, FreeCAD.Vector(0, 0, 1))
                            PointList = []
                            for pl in plist:
                                PointList += pl
                            PointList = sorted(PointList, key=lambda k: (k[NOrientation], k[Orientation], k[2]),
                                               reverse=True)

                            path = Draft.makeWire(PointList, closed=False, face=None, support=None)
                            #path.MakeFace = False
                            path.Label = "col(" + str(count) + ")"
                            paths.append(path)
                        del edge
                    except:
                        print("Error: ", len(inter.Vertexes), " ---  ", lis)
                        pass

            '''
            # distToShape: más lento.
            distance, solutions, support = PVArea2D.Shape.distToShape(line1) 
            if len(solutions) > 1:
                try:
                    for i in range(0, len(solutions), 2):
                        if(solutions[i][0] != solutions[i+1][0]):
                            edge = Part.LineSegment(solutions[i][0], solutions[i+1][0]).toShape()
                            if edge.Length >= Rack.Shape.BoundBox.XLength:
                                #print("Dentro: ", edge.Length)
                                #Part.show(edge)

                                plist = mp.projectShapeOnMesh(edge, Mesh, FreeCAD.Vector(0, 0, 1))
                                PointList = []
                                for pl in plist:
                                    PointList += pl
                                PointList = sorted(PointList, key=lambda k: (k[NOrientation], k[Orientation], k[2]), reverse=True)

                                path = Draft.makeWire(PointList, closed=False, face=None, support=None)
                                path.MakeFace = False
                                path.Label = "col(" + str(count) + ")"
                                paths.append(path)
                            del edge
                except:
                    print("   ------------- Error: ", solutions[i][0], solutions[i+1][0])
                    pass
            '''
        else:
            CrossSections = Mesh.crossSections([(vecA, vecB)], 0.000001)
            for PointList in CrossSections[0]:
                if len(PointList) > 1:
                    #  Sort points:
                    PointList = sorted(PointList, key=lambda k: (k[NOrientation], k[Orientation], k[2]), reverse=True)

                    # Chequear si los puntos están dentro del BoundBox
                    pl = []
                    if Orientation == 0:
                        for point in PointList:
                            if PVArea.Shape.BoundBox.YMin <= point.y <= PVArea.Shape.BoundBox.YMax:
                                pl.append(point)
                        #if len(pl) > 0:
                        #    pl[0].y = PVArea.Shape.BoundBox.YMax
                    else:
                        for point in PointList:
                            if PVArea.Shape.BoundBox.XMin <= point.x <= PVArea.Shape.BoundBox.XMax:
                                pl.append(point)
                        #if len(pl) > 0:
                        #    pl[0].x = PVArea.Shape.BoundBox.XMax

                    del PointList
                    PointList = pl
                    del pl

                    # 1. Smooth the points?

                    # 2. Make the path
                    if len(PointList) > 1:
                        path = Draft.makeWire(PointList, closed=False, face=None, support=None)
                        path.MakeFace = False
                        path.Label = "col(" + str(count) + ")"
                        paths.append(path)

                    del PointList
                    del path

        inc += DistCols
        count += 1

    FreeCAD.activeDocument().recompute()

    for path in paths:
        # Posicionar las estructuras en la línea:
        rotation = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), 90 * NOrientation)
        transself.formationVector = FreeCAD.Vector(0, 0, 0)

        placements = calculatePlacementsOnPath(rotation, path,
                                               transself.formationVector,
                                               Rack.Shape.BoundBox.XLength,
                                               ColSpacing if Orientation == 1 else colSpacing,
                                               Orientation, OffsetY)

        calculateSections(Rack, placements)
        del placements

    del paths
    FreeCAD.activeDocument().recompute()


def placement3D_v1(Mesh, Rack, PVArea, ColSpacing, colSpacing, Orientation, DirH=0, DirV=0, OffsetX=0, OffsetY=0):
    ## Info: ----------------------------------------------------------------------------------------------------------
    # 1. Orientation (Orientación de la estructura):
    #    -- 0 => Norte-Sur
    #    -- 1 => Este-Oeste
    # 2. DirH (Dirección Horizontal):
    #    -- 0: Izquierda
    #    -- 1: Derecha
    #    -- 2: Centro
    # 3. DirV (Dirección Vertical):
    #    -- 0: Arriba
    #    -- 1: Abajo
    #    -- 2: Centro
    ## ----------------------------------------------------------------------------------------------------------------

    # Debug: --------------------
    method = True
    # Debug fin -----------------

    from scipy.spatial import distance
    import math
    import PVPlantUtils
    import DraftGeomUtils, Part
    import MeshPart as mp

    NOrientation = 1 - Orientation
    DistCols = ColSpacing + (Rack.Shape.BoundBox.XLength if Orientation == 1 else Rack.Shape.BoundBox.YLength)
    PVArea2D = Draft.makeShape2DView(PVArea, FreeCAD.Vector(0, 0, 1))

    paths = []
    vecB = (float(1 * NOrientation), float(1 * Orientation), 0.0)
    count = 0

    if Orientation == 0: # orientación Norte - Sur
        ord = False
        if DirV == 1:
            ord = True

        if DirH == 0:   # Dirección izquierda - derecha
            inc = (PVArea.Shape.BoundBox.XMin + Rack.Shape.BoundBox.YLength / 2 + OffsetX)
            stop = PVArea.Shape.BoundBox.XMax

            while inc < stop:
                ## 25/12/2020  Idea: ------------------------------------------------------------------------------------------------------
                ## TODO: hacer intersecar un plano con el PVArea2D para sacar el path y proyectar al terreno

                if method:  ## TODO: Revisar qué metodo e mejor
                    print("Nuevo método ------------------------------------------------------------------")
                    FreeCAD.activeDocument().recompute()
                    line1 = Part.LineSegment(FreeCAD.Vector(inc, PVArea2D.Shape.BoundBox.YMin - 1000, 0),
                                             FreeCAD.Vector(inc, PVArea2D.Shape.BoundBox.YMax + 1000, 0)).toShape()
                    inter = PVArea2D.Shape.section(line1)
                    FreeCAD.activeDocument().recompute()

                    if len(inter.Vertexes) > 1:
                        lis = []
                        for vertex in inter.Vertexes:
                            lis.append(vertex.Point)
                        lis = [ii for n, ii in enumerate(lis) if ii not in lis[:n]]

                        for i in range(0, len(inter.Vertexes), 2):
                            try:
                                import MeshPart as mp
                                edge = Part.LineSegment(inter.Vertexes[i].Point, inter.Vertexes[i + 1].Point).toShape()
                                if edge.Length >= Rack.Shape.BoundBox.XLength:
                                    plist = mp.projectShapeOnMesh(edge, Mesh, FreeCAD.Vector(0, 0, 1))
                                    PointList = []
                                    for pl in plist:
                                        PointList += pl
                                    PointList = sorted(PointList, key=lambda k: (k[NOrientation], k[Orientation], k[2]),
                                                       reverse=True)

                                    path = Draft.makeWire(PointList, closed=False, face=None, support=None)
                                    # path.MakeFace = False
                                    path.Label = "col(" + str(count) + ")"
                                    paths.append(path)
                                    count += 1
                                del edge
                            except:
                                print("Error: ", len(inter.Vertexes), " ---  ", lis)
                                pass
                    inc += DistCols
                else:
                    vecA = (float(inc), 0.0, 0.0)
                    CrossSections = Mesh.crossSections([(vecA, vecB)], 0.000001)
                    for PointList in CrossSections[0]:
                        if len(PointList) > 1:
                            #  Sort points:
                            PointList = sorted(PointList, key=lambda k: (k[1], k[0], k[2]), reverse = ord)

                            # Chequear si los puntos están dentro del BoundBox
                            pl = []
                            for point in PointList:
                                if PVArea.Shape.BoundBox.YMin <= point.y <= PVArea.Shape.BoundBox.YMax:
                                    pl.append(point)

                            del PointList
                            PointList = pl
                            del pl

                            # 2. Make the path
                            if len(PointList) > 1:
                                path = Draft.makeWire(PointList, closed=False, face=None, support=None)
                                path.MakeFace = False
                                path.Label = "col(" + str(count) + ")"
                                paths.append(path)
                                count += 1

                            del PointList
                            del path
                    inc += DistCols

        elif DirH == 1: # Dirección derecha - izquierda
            inc = PVArea.Shape.BoundBox.XMax - Rack.Shape.BoundBox.YLength / 2 - OffsetX
            stop = PVArea.Shape.BoundBox.XMin

            while inc > stop:
                vecA = (float(inc), 0.0, 0.0)
                CrossSections = Mesh.crossSections([(vecA, vecB)], 0.000001)
                for PointList in CrossSections[0]:
                    if len(PointList) > 1:
                        #  Sort points:
                        PointList = sorted(PointList, key=lambda k: (k[1], k[0], k[2]), reverse=ord)

                        # Chequear si los puntos están dentro del BoundBox
                        pl = []
                        for point in PointList:
                            if PVArea.Shape.BoundBox.YMin <= point.y <= PVArea.Shape.BoundBox.YMax:
                                pl.append(point)

                        del PointList
                        PointList = pl
                        del pl

                        # 2. Make the path
                        if len(PointList) > 1:
                            path = Draft.makeWire(PointList, closed=False, face=None, support=None)
                            path.MakeFace = False
                            path.Label = "col(" + str(count) + ")"
                            paths.append(path)
                            count += 1

                        del PointList
                        del path
                inc -= DistCols
    else:
        inc = (PVArea.Shape.BoundBox.XMin + Rack.Shape.BoundBox.YLength / 2 + OffsetX) if Orientation == 0 else (
                PVArea.Shape.BoundBox.YMin + Rack.Shape.BoundBox.XLength / 2 + OffsetY)
        stop = PVArea.Shape.BoundBox.XMax if Orientation == 0 else PVArea.Shape.BoundBox.YMax

        while inc < stop:
            vecA = (float(inc * NOrientation), float(inc * Orientation), 0.0)

            # line1 = Part.LineSegment(FreeCAD.Vector(inc, PVArea2D.Shape.BoundBox.YMin - 10000, 0),
            #                         FreeCAD.Vector(inc, PVArea2D.Shape.BoundBox.YMax + 10000, 0)).toShape()

            CrossSections = Mesh.crossSections([(vecA, vecB)], 0.000001)
            for PointList in CrossSections[0]:
                if len(PointList) > 1:
                    #  Sort points:
                    PointList = sorted(PointList, key=lambda k: (k[NOrientation], k[Orientation], k[2]), reverse=True)

                    # Chequear si los puntos están dentro del BoundBox
                    pl = []
                    if Orientation == 0:
                        for point in PointList:
                            if PVArea.Shape.BoundBox.YMin <= point.y <= PVArea.Shape.BoundBox.YMax:
                                pl.append(point)
                        if len(pl) > 0:
                            pl[0].y = PVArea.Shape.BoundBox.YMax
                    else:
                        for point in PointList:
                            if PVArea.Shape.BoundBox.XMin <= point.x <= PVArea.Shape.BoundBox.XMax:
                                pl.append(point)
                            if len(pl) > 0:
                                pl[0].x = PVArea.Shape.BoundBox.XMax

                    PointList = pl
                    del pl

                    # 1. Smooth the points?

                    # 2. Make the path
                    if len(PointList) > 1:
                        path = Draft.makeWire(PointList, closed=False, face=None, support=None)
                        path.MakeFace = False
                        path.Name = "col(" + str(count) + ")"
                        path.Label = path.Name
                        paths.append(path)

                    del PointList
                    del path

            inc += DistCols

    FreeCAD.activeDocument().recompute()

    pts = []
    for path in paths:
        # Posicionar las estructuras en la línea:
        rotation = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), 90 * NOrientation)
        formationVector = FreeCAD.Vector(0, 0, 0)

        placements, pts = calculatePlacementsOnPath(rotation, path,
                                               formationVector,
                                               Rack.Shape.BoundBox.XLength,
                                               ColSpacing if Orientation == 1 else colSpacing,
                                               Orientation, OffsetY)

        calculateSections(Rack, placements)
        del placements

    del paths
    FreeCAD.activeDocument().recompute()

def placement2D_3D(Terrain, Rack, PVArea, ColSpacing, colSpacing, Orientation, DirH=0, DirV=0, OffsetX=0, OffsetY=0):

    ## Info: ----------------------------------------------------------------------------------------------------------
    # 1. Orientation (Orientación de la estructura):
    #    -- 0 => Norte-Sur
    #    -- 1 => Este-Oeste
    # 2. DirH (Dirección Horizontal):
    #    -- 0: Izquierda
    #    -- 1: Derecha
    #    -- 2: Centro
    # 3. DirV (Dirección Vertical):
    #    -- 0: Arriba
    #    -- 1: Abajo
    #    -- 2: Centro
    ## ----------------------------------------------------------------------------------------------------------------

    NOrientation = 1 - Orientation
    DistCols = ColSpacing + (Rack.Shape.BoundBox.XLength if Orientation == 1 else Rack.Shape.BoundBox.YLength)
    frameFootprint = makeRectangleFromRack(Rack)
    PVArea2D = Draft.makeShape2DView(PVArea, FreeCAD.Vector(0, 0, 1))

    if Orientation == 0:
        aux = frameFootprint.Length
        frameFootprint.Length = frameFootprint.Height
        frameFootprint.Height = aux
        del aux

    frameFootprint.Placement.Base.x = Terrain.Shape.BoundBox.XMin
    frameFootprint.Placement.Base.y = Terrain.Shape.BoundBox.YMin
    Distcols = frameFootprint.Height.Value + colSpacing

    if Orientation == 0:
        rec = Draft.makeRectangle(length=Rack.Width, height=Terrain.Shape.BoundBox.YLength, face=True, support=None)
        rec.Placement.Base.x = Terrain.Shape.BoundBox.XMin + Rack.Width / 2 + OffsetX
        rec.Placement.Base.y = Terrain.Shape.BoundBox.YMin
    else:
        rec = Draft.makeRectangle(length=Terrain.Shape.BoundBox.XLength, height=Rack.Height, face=True, support=None)
        rec.Placement.Base.x = Terrain.Shape.BoundBox.XMin
        rec.Placement.Base.y = Terrain.Shape.BoundBox.YMin

    while rec.Shape.BoundBox.XMax <= Terrain.Shape.BoundBox.XMax:
        common = Terrain.Shape.common(rec.Shape)
        for shape in common.Faces:
            if shape.Area >= frameFootprint.Shape.Area:
                frameFootprint.Placement.Base.x = shape.BoundBox.XMin
                frameFootprint.Placement.Base.y = shape.BoundBox.YMin

                while (frameFootprint.Shape.BoundBox.XMax <= shape.BoundBox.XMax):
                    common1 = shape.common(frameFootprint.Shape)
                    if common1.Area >= 0:
                        raise
                    else:
                        # ajuste fino hasta encontrar el primer sitio:
                        frameFootprint.Placement.Base.x += 500  # un metro
                    del common1

        # ajuste fino hasta encontrar el primer sitio:
        rec.Placement.Base.y += 100
        del common

    FreeCAD.ActiveDocument.removeObject(rec.Name)

    from datetime import datetime
    starttime = datetime.now()

    if Orientation == 0:
        # Código para crear Columnas:
        while Rack.Placement.Base.x > Terrain.Shape.BoundBox.XMin:
            Rack.Placement.Base.x -= DistCols
    else:
        # Código para crear Filas:
        Rack.Placement.Base.x = Terrain.Shape.BoundBox.XMin
        i = 1
        yy = Rack.Placement.Base.y
        while yy < Terrain.Shape.BoundBox.YMax:
            Createcol1(Rack.Placement.Base.x, yy, Rack, Terrain, DistCols, area, i)
            i += 1
            yy += Distcols

    FreeCAD.activeDocument().recompute()
    print("Placing OK (", datetime.now() - starttime, ")")


def placement2D(self):
    if valueTypeStructure.currentIndex() == 0:  # Fixed
        print("Rack")
    else:
        print("Tracker")
        if Rack.Height < Rack.Length:
            print("rotar")
            aux = Rack.Length
            Rack.Length = Rack.Height
            Rack.Height = aux

    Rack.Placement.Base.x = Terrain.Shape.BoundBox.XMin
    Rack.Placement.Base.y = Terrain.Shape.BoundBox.YMin

    DistColls = Rack.Length.Value + ColSpacing
    Distcols = Rack.Height.Value + colSpacing
    area = Rack.Shape.Faces[0].Area  # * 0.999999999

    rec = Draft.makeRectangle(length=Terrain.Shape.BoundBox.XLength, height=Rack.Height, face=True,
                              support=None)
    rec.Placement.Base.x = Terrain.Shape.BoundBox.XMin
    rec.Placement.Base.y = Terrain.Shape.BoundBox.YMin

    try:
        while rec.Shape.BoundBox.YMax <= Terrain.Shape.BoundBox.YMax:
            common = Terrain.Shape.common(rec.Shape)
            for shape in common.Faces:
                if shape.Area >= area:
                    if False:
                        minorPoint = FreeCAD.Vector(0, 0, 0)
                        for spoint in shape.OuterWire.Vertexes:
                            if minorPoint.y >= spoint.Point.y:
                                if minorPoint.x >= spoint.x:
                                    minorPoint = spoint
                                    Rack.Placement.Base = spoint
                    else:
                        # más rápido
                        Rack.Placement.Base.x = shape.BoundBox.XMin
                        Rack.Placement.Base.y = shape.BoundBox.YMin

                    while (Rack.Shape.BoundBox.XMax <= shape.BoundBox.XMax):
                        if checkInside(Rack, shape):
                            raise
                        else:
                            # ajuste fino hasta encontrar el primer sitio:
                            rackClone.Placement.Base.x += 500  # medio metro

                        '''old version 1
                        # Chequear si está dentro: --------------------------------------------------------
                        verts = [v.Point for v in rackClone.Shape.OuterWire.OrderedVertexes]
                        inside = True
                        for vert in verts:
                            if not shape.isInside(vert, 0, True):
                                inside = False
                                break
                        # Chequear si está dentro fin --------------------------------------------------------

                        if inside:
                            raise
                        else:
                            # ajuste fino hasta encontrar el primer sitio:
                            rackClone.Placement.Base.x += 500  # medio metro
                        '''

                        '''old version 0
                        common1 = shape.common(Rack.Shape)
                        if common1.Area >= area:
                            raise
                        else:
                            # ajuste fino hasta encontrar el primer sitio:
                            Rack.Placement.Base.x += 500  # un metro
                        del common1
                        '''
            # ajuste fino hasta encontrar el primer sitio:
            rec.Placement.Base.y += 100
            del common
    except:
        pass
        #print("Found")

    FreeCAD.ActiveDocument.removeObject(rec.Name)

    from datetime import datetime
    starttime = datetime.now()

    if valueOrientation.currentIndex() == 0:
        # Código para crear filas:
        Rack.Placement.Base.x = Terrain.Shape.BoundBox.XMin
        i = 1
        yy = Rack.Placement.Base.y
        while yy < Terrain.Shape.BoundBox.YMax:
            Createcol1(Rack.Placement.Base.x, yy, Rack, Terrain, DistColls, area, i)
            i += 1
            yy += Distcols
    elif valueOrientation.currentIndex() == 2:
        # Código para crear columnas:
        while Rack.Placement.Base.x > Terrain.Shape.BoundBox.XMin:
            Rack.Placement.Base.x -= DistColls
    else:
        xx = Rack.Placement.Base.x
        while xx < Terrain.Shape.BoundBox.XMax:
            CreateGrid(xx, Rack.Placement.Base.y, Rack, Terrain, Distcols, area)
            xx += DistColls

    FreeCAD.activeDocument().recompute()
    print("Everything OK (", datetime.now() - starttime, ")")

def checkInside(obj, area):
    verts = [v.Point for v in obj.Shape.OuterWire.OrderedVertexes]
    inside = True
    for vert in verts:
        if not area.isInside(vert, 0, True):
            inside = False
            break
    return inside

# Alinear solo filas. las columnas donde se pueda
def Createcol(XX, YY, rack, land, ColSpacing, area, colNumber):
    rackClone = Draft.makeRectangle(length=rack.Length, height=rack.Height, face=True, support=None)
    rackClone.Label = 'rackClone{a}'.self.format(a=colNumber)
    rackClone.Placement.Base.x = XX
    rackClone.Placement.Base.y = YY

    rec = Draft.makeRectangle(length=land.Shape.BoundBox.XLength, height=rack.Height, face=True, support=None)
    rec.Placement.Base.x = land.Shape.BoundBox.XMin
    rec.Placement.Base.y = YY
    FreeCAD.activeDocument().recompute()

    common = land.Shape.common(rec.Shape)
    for shape in common.Faces:
        if shape.Area >= area:
            rackClone.Placement.Base.x = shape.BoundBox.XMin
            rackClone.Placement.Base.y = shape.BoundBox.YMin
            while rackClone.Shape.BoundBox.XMax <= shape.BoundBox.XMax:
                common1 = shape.common(rackClone.Shape)
                if common1.Area >= area:
                    tmp = Draft.makeRectangle(length=rack.Length, height=rack.Height, placement=rackClone.Placement,
                                              face=True, support=None)
                    tmp.Label = 'R{:03}-000'.self.format(colNumber)
                    rackClone.Placement.Base.x += ColSpacing
                else:
                    # ajuste fino hasta encontrar el primer sitio:
                    rackClone.Placement.Base.x += 500  # un metro
                del common1
    del common
    FreeCAD.ActiveDocument.removeObject(rackClone.Name)
    FreeCAD.ActiveDocument.removeObject(rec.Name)


# Alinear solo filas. las columnas donde se pueda
def Createcol1(XX, YY, rack, land, ColSpacing, area, colNumber):
    rackClone = Draft.makeRectangle(length=rack.Length, height=rack.Height, face=True, support=None)
    rackClone.Label = 'rackClone{a}'.self.format(a=colNumber)
    rackClone.Placement.Base.x = XX
    rackClone.Placement.Base.y = YY

    rec = Draft.makeRectangle(length=land.Shape.BoundBox.XLength, height=rack.Height, face=True, support=None)
    rec.Placement.Base.x = land.Shape.BoundBox.XMin
    rec.Placement.Base.y = YY
    FreeCAD.activeDocument().recompute()

    common = land.Shape.common(rec.Shape)
    for shape in common.Faces:
        if shape.Area >= area:
            if False:
                minorPoint = FreeCAD.Vector(0, 0, 0)
                for spoint in shape.OuterWire.Vertexes:
                    if minorPoint.y >= spoint.Point.y:
                        if minorPoint.x >= spoint.x:
                            minorPoint = spoint
                            rackClone.Placement.Base = spoint
            else:
                # más rápido
                rackClone.Placement.Base.x = shape.BoundBox.XMin
                rackClone.Placement.Base.y = shape.BoundBox.YMin

            while rackClone.Shape.BoundBox.XMax <= shape.BoundBox.XMax:
                verts = [v.Point for v in rackClone.Shape.OuterWire.OrderedVertexes]
                inside = True
                for vert in verts:
                    if not shape.isInside(vert, 0, True):
                        inside = False
                        break
                if inside:
                    #tmp = rack.Shape.copy()
                    #tmp.Placement = rack.Placement
                    tmp = Draft.makeRectangle(length=rack.Length, height=rack.Height, placement=rackClone.Placement,
                                              face=True, support=None)
                    tmp.Label = 'R{:03}-000'.self.format(colNumber)

                    rackClone.Placement.Base.x += ColSpacing
                else:
                    # ajuste fino hasta encontrar el primer sitio:
                    rackClone.Placement.Base.x += 500  # medio metro
    del common
    FreeCAD.ActiveDocument.removeObject(rackClone.Name)
    FreeCAD.ActiveDocument.removeObject(rec.Name)

# Alinear columna y fila (grid perfecta)
def CreateGrid(XX, YY, rack, land, ColSpacing, area):
    print("CreateGrid")
    rackClone = Draft.makeRectangle(length=rack.Length, height=rack.Height, face=True, support=None)
    rackClone.Label = 'rackClone{a}'.self.format(a=XX)
    rackClone.Placement.Base.x = XX
    rackClone.Placement.Base.y = YY

    # if False:
    while rackClone.Shape.BoundBox.YMax < land.Shape.BoundBox.YMax:
        common = land.Shape.common(rackClone.Shape)

        if common.Area >= area:
            tmp = Draft.makeRectangle(length=rack.Length, height=rack.Height,
                                      placement=rackClone.Placement, face=True, support=None)
            tmp.Label = 'rackClone{a}'.self.format(a=XX)
        rackClone.Placement.Base.y += ColSpacing
        # else:
        #    # ajuste fino hasta encontrar el primer sitio:
        #    rackClone.Placement.Base.y += 1000
    FreeCAD.ActiveDocument.removeObject(rackClone.Name)


# Alinear solo filas. las columnas donde se pueda
def CreateCol(XX, YY, rack, land, ColSpacing, area):
    rackClone = Draft.makeRectangle(length=rack.Length, height=rack.Height, face=True, support=None)
    rackClone.Label = 'rackClone{a}'.self.format(a=XX)
    rackClone.Placement.Base.x = XX
    rackClone.Placement.Base.y = YY

    while rackClone.Shape.BoundBox.YMax < land.Shape.BoundBox.YMax:
        common = land.Shape.common(rackClone.Shape)

        if common.Area >= area:
            tmp = Draft.makeRectangle(length=rack.Length, height=rack.Height,
                                      placement=rackClone.Placement, face=True, support=None)
            tmp.Label = 'rackClone{a}'.self.format(a=XX)
            rackClone.Placement.Base.y += ColSpacing
        else:
            # ajuste fino hasta encontrar el primer sitio:
            rackClone.Placement.Base.y += 100

    FreeCAD.ActiveDocument.removeObject(rackClone.Name)



#-----------------------------------------------------------------------------------------------------------------------
# function AdjustToTerrain
#   Take a group of objects and adjust it to the slope and altitude of the terrain mesh. It detects the terrain mesh
#
#   Inputs:
#   1. frames: group of objest to adjust
#-----------------------------------------------------------------------------------------------------------------------
def AdjustToTerrain_V1_(sel):
    import MeshPart as mp
    import functools
    import math
    import Part

    terrain = getTerrain().Mesh

    for obj in sel:
        points = []
        if obj.isDerivedFrom("Part::Feature"):
            points.append(obj.Shape.BoundBox.Center)
        elif obj.isDerivedFrom("Mesh::Feature"):
            points.append(obj.Mesh.BoundBox.Center)

        for point in points:
            c = 0
            while True:
                point3D = mp.projectPointsOnMesh([point, ], terrain, FreeCAD.Vector(0, 0, 1))
                if len(point3D) > 0:
                    obj.Placement.Base = point3D[0]
                    break
                point.y += 100
                c += 1
                if c == 10:
                    break


def AdjustToTerrain_V0(frames):
    import MeshPart as mp
    import functools
    import math
    import Part

    terrain = getTerrain().Mesh

    for frame in frames:
        if frame.Shape.BoundBox.XLength > frame.Shape.BoundBox.YLength:
            p1 = FreeCAD.Vector(frame.Shape.BoundBox.XMin, frame.Shape.BoundBox.Center.y, 0.0)
            p2 = FreeCAD.Vector(frame.Shape.BoundBox.XMax, frame.Shape.BoundBox.Center.y, 0.0)
        else:
            p1 = FreeCAD.Vector(frame.Shape.BoundBox.Center.x, frame.Shape.BoundBox.YMin, 0.0)
            p2 = FreeCAD.Vector(frame.Shape.BoundBox.Center.x, frame.Shape.BoundBox.YMax, 0.0)

        l = Part.LineSegment()
        l.StartPoint = p1
        l.EndPoint = p2
        edge = l.toShape()
        list = mp.projectShapeOnMesh(edge, terrain, FreeCAD.Vector(0, 0, 1))[0]

        if len(list) > 1:
            p1 = list[0]
            p2 = list[-1]
            vec = p2 - p1
            angle = math.degrees(vec.getAngle(FreeCAD.Vector(0, 1, 0)))

            zz = ((p2 + p1) / 2).z

            if angle > 90:
                angle = angle - 180

            placement = FreeCAD.Placement()
            placement.move(FreeCAD.Vector(frame.Placement.Base.x, frame.Placement.Base.y, zz))
            placement.Rotation = frame.Placement.Rotation.multiply(FreeCAD.Rotation(FreeCAD.Vector(1, 0, 0), angle))
            frame.Placement = placement

        del l
        del edge



def AdjustToTerrain_V1(frames):
    import MeshPart as mp
    import math
    import Part

    terrain = getTerrain().Mesh.copy()
    cols = getCols(frames)
    for col in cols:
        for group in col:
            frame1 = group[0]  # Norte
            frame_1 = group[-1]  # Sur

            points = []
            ed = frame1.Shape.Edges[1]
            points.append(ed.valueAt(ed.FirstParameter + 0.5 * (ed.LastParameter - ed.FirstParameter)))
            for ind in range(0, len(group) - 1):
                ed1 = group[ind].Shape.Edges[3]
                ed2 = group[ind + 1].Shape.Edges[1]
                middlepoint = (ed1.valueAt(ed1.FirstParameter + 0.5 * (ed1.LastParameter - ed1.FirstParameter)) +
                               ed2.valueAt(ed2.FirstParameter + 0.5 * (ed2.LastParameter - ed2.FirstParameter))) / 2
                points.append(middlepoint)
            ed = frame_1.Shape.Edges[3]
            points.append(ed.valueAt(ed.FirstParameter + 0.5 * (ed.LastParameter - ed.FirstParameter)))

            # TODO: esperar a que funcione bien esta función. Mientras tanto se usa el código que va a continuación
            # Otra opción: hacer un crucen entre la vertical y la horizontal para ver donde se cortan
            #points3D = mp.projectPointsOnMesh(points, terrain, FreeCAD.Vector(0, 0, 1))
            points3D = []
            for point in points:
                c = 0
                while True:
                    point3D = mp.projectPointsOnMesh([point, ], terrain, FreeCAD.Vector(0, 0, 1))
                    if len(point3D) > 0:
                        points3D.append(point3D[0])
                        break
                    point.y += 100
                    c += 1
                    if c == 10:
                        break

            for ind in range(0, len(points3D) - 1):
                vec = points3D[ind] - points3D[ind + 1]
                angle = math.degrees(vec.getAngle(FreeCAD.Vector(0, 1, 0)))
                if angle > 90:
                    angle =  angle - 180
                if vec.z >= 0:
                    angle *= -1
                frame = group[ind]
                p = (points3D[ind] + points3D[ind + 1]) / 2
                frame.Placement.Base = FreeCAD.Vector(frame.Placement.Base.x, frame.Placement.Base.y, p.z)
                frame.Placement.Rotation = FreeCAD.Rotation(frame.Placement.Rotation.toEuler()[0], angle, 0)
            Draft.makeWire(points3D) # Hace falta??
    FreeCAD.activeDocument().recompute()


def getCols(sel, tolerance = 2000):
    cols = []
    while len(sel) > 0:
        obj = sel[0]
        p = obj.Shape.BoundBox.Center   # TODO: Cambiar por centro de gravedad??
        n = FreeCAD.Vector(1, 0, 0)     # TODO: como se consigue la verdadera normal a la estructura??

        # 1. Detectar los objetos que están en una misma columna
        col = []
        newsel = []
        for obj1 in sel:
            if obj1.Shape.BoundBox.isCutPlane(p, n):
                col.append(obj1)
            else:
                newsel.append(obj1)

        sel = newsel.copy()
        col = sorted(col, key = lambda k: k.Placement.Base.y, reverse = True) #Orden Norte - Sur (Arriba a abajo)

        # 2. Detectar y separar los grupos dentro de una misma columna:
        group = []
        newcol = []
        if len(col) > 1:
            distances = []
            for ind in range(0, len(col)-1):
                vec1 = col[ind + 1].Placement.Base
                vec1.z = 0
                vec2 = col[ind].Placement.Base
                vec2.z = 0
                distances.append((vec1 - vec2).Length)
            distmin = tolerance
            group.append(col[0])
            for ind in range(0, len(col) - 1):
                #len1 = col[ind].Shape.Edges[0].Length
                #len2 = col[ind + 1].Shape.Edges[0].Length
                #len3 = (col[ind + 1].Placement.Base - col[ind].Placement.Base).Length - (len1 + len2) / 2 # TODO: Cambiar esto

                ed1 = col[ind].Shape.Edges[3]
                ed2 = col[ind + 1].Shape.Edges[1]
                len3 = (ed1.valueAt(ed1.FirstParameter + 0.5 * (ed1.LastParameter - ed1.FirstParameter)) -
                        ed2.valueAt(ed2.FirstParameter + 0.5 * (ed2.LastParameter - ed2.FirstParameter))).Length

                if len3 <= distmin:
                    group.append(col[ind + 1])
                else:
                    newcol.append(group.copy())
                    group.clear()
                    group.append(col[ind + 1])
        else:
            group.append(col[0])

        newcol.append(group)
        cols.append(newcol)
    cols = sorted(cols, key = lambda k: k[0][0].Placement.Base.x, reverse = False) #Orden Oeste - Este  (Izquierda a derecha)
    return cols

def setrename():
    yy = 0
    for col in cols:
        for obj in col:
            obj.Label = "Col(" + str(yy) +")"
        yy += 1

def select(val):
    col = ols[val]
    for group in col:
        for obj in group:
            FreeCADGui.Selection.addSelection(obj)

#-----------------------------------------------------------------------------------------------------------------------
# Convert
#
#
#-----------------------------------------------------------------------------------------------------------------------
class _PVPlantConvertTaskPanel:
    '''The editmode TaskPanel for Schedules'''

    def __init__(self):
        import os

        self.To = None

        # self.form:
        self.form = FreeCADGui.PySideUic.loadUi(os.path.join(PVPlantResources.__dir__, "PVPlantPlacementConvert.ui"))
        self.form.setWindowIcon(QtGui.QIcon(os.path.join(PVPlantResources.DirIcons, "convert.svg")))

        self.form.buttonTo.clicked.connect(self.addTo)

    def addTo(self):
        sel = FreeCADGui.Selection.getSelection()
        if len(sel) > 0:
            self.To = sel[0]
            self.form.editTo.setText(self.To.Label)

    def accept(self):
        sel = FreeCADGui.Selection.getSelection()
        if sel == self.To:
            return False

        if len(sel) > 0 and self.To is not None:
            ConvertObjectsTo(sel, self.To)
            return True
        return False

#-----------------------------------------------------------------------------------------------------------------------
# function ConvertObjectsTo
#
#
#-----------------------------------------------------------------------------------------------------------------------

def ConvertObjectsTo(sel, objTo):
    import math
    import PVPlantRack


    if hasattr(objTo, "Proxy"):
        isFrame = objTo.Proxy.__class__ is PVPlantRack._Tracker
        #isFrame = issubclass(objTo.Proxy.__class__, PVPlantRack._Frame)
    isFrame = True

    for obj in sel:
        #if obj.Proxy.__class__ is PVPlantRack._Tracker:
        if isFrame:
            if hasattr(obj, "Proxy"):
                if obj.Proxy.__class__ is PVPlantRack._Tracker:
                #if issubclass(obj.Proxy.__class__, PVPlantRack._Frame):             # 1. Si los dos son Frames
                    cp = FreeCAD.ActiveDocument.copyObject(objTo, False)
                    cp.Placement = obj.Placement
                    cp.CloneOf = objTo
            else:                                                               # 2. De un objeto no Frame a Frame
                place = FreeCAD.Placement() #obj.Placement
                place.Rotation = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), 90)      # TODO: rotar conforme a lados más largos
                bb = None
                if obj.isDerivedFrom("Part::Feature"):
                    bb = obj.Shape.BoundBox
                elif obj.isDerivedFrom("Mesh::Feature"):
                    bb = obj.Mesh.BoundBox
                place.Base = bb.Center
                cp = FreeCAD.ActiveDocument.copyObject(objTo, False)
                cp.Placement = place
                if isFrame:
                    cp.CloneOf = objTo
        else:                                                                   # 3. De un objeto a otro objeto (cualesquieran que sean)
            place = FreeCAD.Placement()  # obj.Placement
            bb = None
            if obj.isDerivedFrom("Part::Feature"):
                bb = obj.Shape.BoundBox
            elif obj.isDerivedFrom("Mesh::Feature"):
                bb = obj.Mesh.BoundBox
            place.Base = bb.Center
            cp = FreeCAD.ActiveDocument.copyObject(objTo, False)
            cp.Placement = place
            if isFrame:
                cp.CloneOf = objTo
        FreeCAD.ActiveDocument.removeObject(obj.Name)
    FreeCAD.activeDocument().recompute()



## Comandos: -----------------------------------------------------------------------------------------------------------
class _CommandPVPlantPlacement:

    def GetResources(self):
        return {'Pixmap': str(os.path.join(PVPlantResources.DirIcons, "way.svg")),
                'Accel': "P, S",
                'MenuText': QT_TRANSLATE_NOOP("Placement", "Placement"),
                'ToolTip': QT_TRANSLATE_NOOP("Placement", "Crear un campo fotovoltaico")}

    def Activated(self):
        taskd = _PVPlantPlacementTaskPanel(None)
        FreeCADGui.Control.showDialog(taskd)

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        else:
            return False

class _CommandAdjustToTerrain:

    def GetResources(self):
        return {'Pixmap': str(os.path.join(PVPlantResources.DirIcons, "way.svg")),
                'Accel': "P, S",
                'MenuText': QT_TRANSLATE_NOOP("Placement", "Placement"),
                'ToolTip': QT_TRANSLATE_NOOP("Placement", "Crear un campo fotovoltaico")}

    def Activated(self):
        sel = FreeCADGui.Selection.getSelection()
        if len(sel) > 0:
            AdjustToTerrain_V1(sel)
            #AdjustToTerrain__(sel)
        else:
            print("No selected object")

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        else:
            return False

class _CommandConvert:

    def GetResources(self):
        return {'Pixmap': str(os.path.join(PVPlantResources.DirIcons, "convert.svg")),
                'Accel': "P, C",
                'MenuText': QT_TRANSLATE_NOOP("Placement", "Convert"),
                'ToolTip': QT_TRANSLATE_NOOP("Placement", "Convertir un objeto en otro")}

    def Activated(self):
        taskd = _PVPlantConvertTaskPanel()
        FreeCADGui.Control.showDialog(taskd)

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        else:
            return False

if FreeCAD.GuiUp:
    FreeCADGui.addCommand('PVPlantPlacement', _CommandPVPlantPlacement())
    FreeCADGui.addCommand('PVPlantAdjustToTerrain', _CommandAdjustToTerrain())
    FreeCADGui.addCommand('PVPlantConvertTo', _CommandConvert())
