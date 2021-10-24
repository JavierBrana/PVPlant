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

import FreeCAD
import Part
import Draft
import numpy as np
import os
import copy
import math

if FreeCAD.GuiUp:
    import FreeCADGui, os
    from PySide import QtCore, QtGui
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
import PVPlantSite


def makePlacement():
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Placement")
    _Placement(obj)
    _ViewProviderPlacement(obj.ViewObject)
    return obj

class _Placement:
    def __init__(self, obj):
        self.setCommonProperties(obj)
        self.obj = obj

    def setCommonProperties(self, obj):
        pl = obj.PropertiesList

        if not ("NumberOfStrings" in pl):
            obj.addProperty("App::PropertyInteger",
                            "NumberOfStrings",
                            "Setup",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).NumberOfStrings = 0
            obj.setEditorMode("NumberOfStrings", 1)

        self.Type = "StringSetup"


        '''
        ['App::PropertyBool', 
         'App::PropertyBoolList', 
         'App::PropertyFloat', 
         'App::PropertyFloatList',
         'App::PropertyFloatConstraint', 
         'App::PropertyPrecision', 
         'App::PropertyQuantity',
         'App::PropertyQuantityConstraint', 
         'App::PropertyAngle', 
         'App::PropertyDistance', 
         'App::PropertyLength',
         'App::PropertyArea', 
         'App::PropertyVolume', 
         'App::PropertyFrequency', 
         'App::PropertySpeed',
         'App::PropertyAcceleration', 
         'App::PropertyForce', 
         'App::PropertyPressure', 
         'App::PropertyVacuumPermittivity',
         'App::PropertyInteger', 
         'App::PropertyIntegerConstraint', 
         'App::PropertyPercent', 
         'App::PropertyEnumeration',
         'App::PropertyIntegerList', 
         'App::PropertyIntegerSet', 
         'App::PropertyMap', 
         'App::PropertyString',
         'App::PropertyPersistentObject', 
         'App::PropertyUUID', 
         'App::PropertyFont', 
         'App::PropertyStringList',
         'App::PropertyLink', 
         'App::PropertyLinkChild', 
         'App::PropertyLinkGlobal', 
         'App::PropertyLinkHidden',
         'App::PropertyLinkSub', 
         'App::PropertyLinkSubChild',
         'App::PropertyLinkSubGlobal',
         'App::PropertyLinkSubHidden', 
         'App::PropertyLinkList', 
         'App::PropertyLinkListChild',
         'App::PropertyLinkListGlobal', 
         'App::PropertyLinkListHidden', 
         'App::PropertyLinkSubList',
         'App::PropertyLinkSubListChild', 
         'App::PropertyLinkSubListGlobal', 
         'App::PropertyLinkSubListHidden',
         'App::PropertyXLink', 
         'App::PropertyXLinkSub', 
         'App::PropertyXLinkSubList', 
         'App::PropertyXLinkList',
         'App::PropertyMatrix', 
         'App::PropertyVector', 
         'App::PropertyVectorDistance', 
         'App::PropertyPosition',
         'App::PropertyDirection', 
         'App::PropertyVectorList', 
         'App::PropertyPlacement', 
         'App::PropertyPlacementList',
         'App::PropertyPlacementLink', 
         'App::PropertyColor', 
         'App::PropertyColorList', 
         'App::PropertyMaterial',
         'App::PropertyMaterialList', 
         'App::PropertyPath', 
         'App::PropertyFile', 
         'App::PropertyFileIncluded',
         'App::PropertyPythonObject',  
         'App::PropertyExpressionEngine',  
         'Part::PropertyPartShape',
         'Part::PropertyGeometryList', 
         'Part::PropertyShapeHistory', 
         'Part::PropertyFilletEdges',
         'Points::PropertyGreyValue', 
         'Points::PropertyGreyValueList', 
         'Points::PropertyNormalList',
         'Points::PropertyCurvatureList', 
         'Points::PropertyPointKernel', 
         'Mesh::PropertyNormalList',
         'Mesh::PropertyCurvatureList', 
         'Mesh::PropertyMeshKernel']
         '''

    def addString(self, modulelist):
        stringName = "String" + str(self.StringCount)
        self.obj.addProperty("App::PropertyIntegerList",
                             stringName,
                             "Setup",
                             QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                             )
        setattr(self.obj, stringName, modulelist)
        self.obj.NumberOfStrings = self.StringCount
        self.StringCount += 1

class _ViewProviderPlacement:
    def __init__(self, vobj):
        '''
        Set view properties.
        '''
        self.Object = vobj.Object
        vobj.Proxy = self

    def attach(self, vobj):
        '''
        Create Object visuals in 3D view.
        '''
        self.Object = vobj.Object
        return

    def getIcon(self):
        '''
        Return object treeview icon.
        '''

        return str(os.path.join(DirIcons, "stringsetup.svg"))
    '''
    def claimChildren(self):
        """
        Provides object grouping
        """
        return self.Object.Group
    '''

    def setEdit(self, vobj, mode=0):
        """
        Enable edit
        """
        return True

    def unsetEdit(self, vobj, mode=0):
        """
        Disable edit
        """
        return False

    def doubleClicked(self, vobj):
        """
        Detect double click
        """
        pass

    def setupContextMenu(self, obj, menu):
        """
        Context menu construction
        """
        pass

    def edit(self):
        """
        Edit callback
        """
        pass

    def __getstate__(self):
        """
        Save variables to file.
        """
        return None

    def __setstate__(self,state):
        """
        Get variables from file.
        """
        return None


def calculatePlacement(globalRotation, edge, offset, RefPt, xlate,
                       normal=None, Orientation=0):
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
    x = FreeCAD.Vector(1, 0, 0)  # unit +X
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

    if n == nullv:  # 1) can't determine normal, don't align.
        print(" 1) can't determine normal, don't align.")
        psi = 0.0
        theta = 0.0
        phi = 0.0
        FreeCAD.Console.PrintWarning("Draft PathArray.orientShape - Path normal is Null. Cannot align.\n")
    elif abs(b.dot(z)) == 1.0:  # 2) binormal is || z
        # align shape to tangent only
        print(" # 2) binormal is || z")
        psi = math.degrees(DraftVecUtils.angle(x, t, z))
        theta = 0.0
        phi = 0.0
        FreeCAD.Console.PrintWarning(
            "Draft PathArray.orientShape - Gimbal lock. Infinite lnodes. Change Path or Base.\n")
    else:  # 3) regular case
        psi = 0  # math.degrees(DraftVecUtils.angle(x, lnodes, z))
        theta = 0  # math.degrees(DraftVecUtils.angle(z, b, lnodes))
        phi = math.degrees(DraftVecUtils.angle(lnodes, t, b))  # * Orientation  ??

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


def calculatePlacementsOnPath(shapeRotation, pathwire, xlate, rackLength=0, Spacing=0, Orientation=0,
                              _offset_=0):
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
        pts = []

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

        pts = pathwire.Shape.discretize(Distance=Spacing + rackLength, First=_offset_)
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

        # del pts[:]
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
        # FreeCADGuiGui.runCommand('Std_DuplicateSelection', 0)
        cp.Placement = placement
        cp.CloneOf = frame
        del cp


class _PVPlantPlacementTaskPanel:
    '''The editmode TaskPanel for Schedules'''

    def __init__(self, obj=None):
        self.Terrain = None
        self.Rack = None
        self.PVArea = None

        # self.form:
        self.form = FreeCADGui.PySideUic.loadUi(os.path.join(PVPlantResources.__dir__, "PVPlantPlacement.ui"))
        self.form.setWindowIcon(QtGui.QIcon(os.path.join(PVPlantResources.DirIcons, "way.svg")))
        self.form.editGapRows.setText("0.500 m")
        self.form.editGapCols.setText("5.000 m")
        # self.form.editGapRows.textEdited.connect(lambda: self.updateRows(self.form.editGapRows, self.form.editGapRows.text()))
        self.form.editOffsetHorizontal.setText("0.0 m")
        self.form.editOffsetVertical.setText("0.0 m")

        self.form.buttonPVArea.clicked.connect(self.addPVArea)
        self.form.buttonFrame.clicked.connect(self.addRack)

    '''
    def updateRows(self, sender, text):
        print(sender, text)
        val = min(self.Rack.Shape.BoundBox.XLength, self.Rack.Shape.BoundBox.YLength)
        self.form.editDistanceCols.setText("5000 mm")
        self.form.editGapRows.setText('{:.0f} mm'.format(val))
    '''

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

    def addRack(self):
        selection = FreeCADGui.Selection.getSelection()
        if len(selection) > 0:
            self.Rack = selection[0]
            self.form.editFrame.setText(self.Rack.Label)

    def createFrameFromPoints(self, pl):
        try:
            MechanicalGroup = FreeCAD.ActiveDocument.Frames
        except:
            MechanicalGroup = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroup", 'Frames')
            MechanicalGroup.Label = "Frames"


        for point in pl:
            newrack = FreeCAD.ActiveDocument.copyObject(self.Rack)
            newrack.Label = "Tracker"
            newrack.Placement.rotate(newrack.Shape.BoundBox.Center, FreeCAD.Vector(0, 0, 1), -90)
            newrack.Placement.Base = point
            newrack.Visibility = True
            MechanicalGroup.addObject(newrack)

        FreeCAD.ActiveDocument.Site.addObject(MechanicalGroup)
        # TODO: ajustar los tracker al terreno

    def calculateAlignedArray(self):
        from datetime import datetime
        starttime = datetime.now()

        gap_col = FreeCAD.Units.Quantity(self.form.editGapCols.text()).Value
        gap_row = FreeCAD.Units.Quantity(self.form.editGapRows.text()).Value + max(self.Rack.Shape.BoundBox.XLength,
                                                                                   self.Rack.Shape.BoundBox.YLength)
        offset_x = FreeCAD.Units.Quantity(self.form.editOffsetHorizontal.text()).Value
        offset_y = FreeCAD.Units.Quantity(self.form.editOffsetVertical.text()).Value

        # TODO: Chequear la forma: Ver que esté cerrada y transformarla en cara.
        Area = self.PVArea.Shape

        rec = Part.makePlane(self.Rack.Shape.BoundBox.YLength, self.Rack.Shape.BoundBox.XLength)
        # TODO: revisar todo esto: -----------------------------------------------------------------
        sel = FreeCADGui.Selection.getSelectionEx()[0]
        refh = None
        refv = None

        if len(sel.SubObjects) == 0:
            return

        if len(sel.SubObjects) == 1:
            # Todo: chequear que sea un edge. Si es otra cosa coger el edge[0] de la forma
            refh = refv = sel.SubObjects[0]

        if len(sel.SubObjects) > 1:
            # Todo: chequear que sea un edge. Si es otra cosa coger el edge[0] de la forma
            if sel.SubObjects[0].BoundBox.XLength > sel.SubObjects[1].BoundBox.XLength:
                refh = sel.SubObjects[0]
            else:
                refh = sel.SubObjects[1]

            if sel.SubObjects[0].BoundBox.YLength > sel.SubObjects[1].BoundBox.YLength:
                refv = sel.SubObjects[0]
            else:
                refv = sel.SubObjects[1]

        steps = int((refv.BoundBox.XMax - Area.BoundBox.XMin + offset_x) / gap_col)
        startx = refv.BoundBox.XMax + offset_x - gap_col * steps
        steps = int((refh.BoundBox.YMin - Area.BoundBox.YMax + offset_y) / gap_row)
        starty = refh.BoundBox.YMin + offset_y + gap_row * steps
        # todo end ----------------------------------------------------------------------------------

        pointsx = np.arange(startx, Area.BoundBox.XMax, gap_col)
        pointsy = np.arange(starty, Area.BoundBox.YMin, -gap_row)

        pl = []
        for x in pointsx:
            for y in pointsy:
                point = FreeCAD.Vector(x, y - rec.BoundBox.YLength, 0.0)
                if Area.isInside(point, 0.1, True):
                    cp = rec.copy()
                    cp.Placement.Base = point
                    cut = cp.cut([Area])
                    if cut.Area == 0:
                        pl.append(cp.BoundBox.Center)
                        #Part.show(cp)

        total_time = datetime.now() - starttime
        print(" -- Tiempo tardado:", total_time)
        print("    --  Trackers creados: ", len(pl), ", tiempo por tracker: ", total_time / len(pl))

        return pl

    def calculateNonAlignedArray(self):
        from datetime import datetime
        starttime = datetime.now()

        gap_col = FreeCAD.Units.Quantity(self.form.editGapCols.text()).Value
        gap_row = FreeCAD.Units.Quantity(self.form.editGapRows.text()).Value + max(self.Rack.Shape.BoundBox.XLength,
                                                                                   self.Rack.Shape.BoundBox.YLength)
        offset_x = FreeCAD.Units.Quantity(self.form.editOffsetHorizontal.text()).Value
        offset_y = FreeCAD.Units.Quantity(self.form.editOffsetVertical.text()).Value

        Area = self.PVArea.Shape

        rec = Part.makePlane(self.Rack.Shape.BoundBox.YLength, self.Rack.Shape.BoundBox.XLength)

        # TODO: revisar todo esto: -----------------------------------------------------------------
        sel = FreeCADGui.Selection.getSelectionEx()[0]
        refh = None
        refv = None

        if len(sel.SubObjects) == 0:
            refh = refv = Area.Edges[0]

        if len(sel.SubObjects) == 1:
            refh = refv = sel.SubObjects[0]

        if len(sel.SubObjects) == 2:
            if sel.SubObjects[0].BoundBox.XLength > sel.SubObjects[1].BoundBox.XLength:
                refh = sel.SubObjects[0]
            else:
                refh = sel.SubObjects[1]

            if sel.SubObjects[0].BoundBox.YLength > sel.SubObjects[1].BoundBox.YLength:
                refv = sel.SubObjects[0]
            else:
                refv = sel.SubObjects[1]

        steps = int((refv.BoundBox.XMax - Area.BoundBox.XMin + offset_x) / gap_col)
        startx = refv.BoundBox.XMax + offset_x - gap_col * steps
        # todo end ----------------------------------------------------------------------------------

        start = FreeCAD.Vector(startx, 0.0, 0.0)
        pointsx = np.arange(start.x, Area.BoundBox.XMax, gap_col)

        pl = []
        for point in pointsx:
            p1 = FreeCAD.Vector(point, Area.BoundBox.YMax, 0.0)
            p2 = FreeCAD.Vector(point, Area.BoundBox.YMin, 0.0)
            line = Part.makePolygon([p1, p2])

            inter = Area.section([line])
            pts = [ver.Point for ver in inter.Vertexes]  # todo: sort points
            for i in range(0, len(pts), 2):
                line = Part.LineSegment(pts[i], pts[i + 1])
                if line.length() >= rec.BoundBox.YLength:
                    y1 = pts[i].y - rec.BoundBox.YLength
                    cp = rec.copy()
                    cp.Placement.Base = FreeCAD.Vector(pts[i].x - rec.BoundBox.XLength / 2, y1, 0.0)
                    inter = cp.cut([Area])
                    y1 = min([ver.Point.y for ver in inter.Vertexes])
                    pointsy = np.arange(y1, pts[i + 1].y, -gap_row)
                    for point in pointsy:
                        cp = rec.copy()
                        cp.Placement.Base = FreeCAD.Vector(pts[i].x - rec.BoundBox.XLength / 2, point, 0.0)
                        cut = cp.cut([Area], 0)
                        if cut.Area == 0:
                            Part.show(cp)
                            pl.append(point)

        total_time = datetime.now() - starttime
        print(" -- Tiempo tardado:", total_time)
        # print("    --  Trackers creados: ", len(pl), ", tiempo por tracker: ", total_time / len(pl))

        return pl

    def accept(self):
        if self.Terrain is None:
            self.Terrain = PVPlantSite.get().Terrain.Shape


        if self.form.cbAlignFrames.isChecked():
            placements = self.calculateAlignedArray()
        else:
            placements = self.calculateNonAlignedArray()

        self.createFrameFromPoints(placements)

        FreeCADGui.Control.closeDialog()
        return True




# -----------------------------------------------------------------------------------------------------------------------
# function AdjustToTerrain
#   Take a group of objects and adjust it to the slope and altitude of the terrain mesh. It detects the terrain mesh
#
#   Inputs:
#   1. frames: group of objest to adjust
# -----------------------------------------------------------------------------------------------------------------------
def adjustToTerrain(sel):
    terrain = PVPlantSite.get().Terrain.Shape
    cols = getCols(sel)
    for col in cols:
        for group in col:
            frame1 = group[0]  # Norte
            frame_1 = group[-1]  # Sur

            points = []
            points.append(FreeCAD.Vector(frame1.Shape.BoundBox.Center.x, frame1.Shape.BoundBox.YMax, 0))
            for ind in range(0, len(group) - 1):
                middlepoint = (group[ind].Shape.BoundBox.Center + group[ind + 1].Shape.BoundBox.Center) / 2
                points.append(middlepoint)
            points.append(FreeCAD.Vector(frame_1.Shape.BoundBox.Center.x, frame_1.Shape.BoundBox.YMax, 0))

            points3D = []
            for point in points:
                p1 = copy.deepcopy(point)
                p1.z = terrain.BoundBox.ZMax
                p2 = copy.deepcopy(point)
                p2.z = terrain.BoundBox.ZMin
                print(p1, " ", p2)
                line = Part.LineSegment(p1, p2)
                section = terrain.section(line.toShape())
                if len(section.Vertexes) > 0:
                    points3D.append(section.Vertexes[0].Point)

            for ind in range(0, len(points3D) - 1):
                vec = points3D[ind] - points3D[ind + 1]
                angle = math.degrees(vec.getAngle(FreeCAD.Vector(0, 1, 0)))
                if angle > 90:
                    angle = angle - 180
                if vec.z >= 0:
                    angle *= -1
                frame = group[ind]
                p = (points3D[ind] + points3D[ind + 1]) / 2
                frame.Placement.Base = FreeCAD.Vector(frame.Placement.Base.x, frame.Placement.Base.y, p.z)
                frame.Placement.Rotation = FreeCAD.Rotation(frame.Placement.Rotation.toEuler()[0], angle, 0)

    FreeCAD.activeDocument().recompute()


def getAxis(sel):
    site = FreeCAD.ActiveDocument.Site.Terrain.Shape
    for rack in sel:
        poles = rack.Shape.SubShapes[1].SubShapes
        line = Part.LineSegment(poles[0].BoundBox.Center, poles[-1].BoundBox.Center)
        Part.show(line.toShape())
        pro = site.makeParallelProjection(line.toShape(), FreeCAD.Vector(0, 0, 1))
        Part.show(pro)


def AdjustToTerrain_V1_(sel):
    import MeshPart as mp
    import functools

    terrain = PVPlantSite.get().Terrain.Mesh

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

    terrain = PVPlantSite.get().Terrain.Mesh

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

    terrain = PVPlantSite.get().Terrain.Mesh.copy()
    cols = getCols(frames)
    for col in cols:
        for group in col:
            frame1 = group[0]  # Norte
            frame_1 = group[-1]  # Sur

            points = []
            points.append(FreeCAD.Vector(frame1.Shape.BoundBox.Center.x, frame1.Shape.BoundBox.YMax, 0))
            for ind in range(0, len(group) - 1):
                middlepoint = (group[ind].Shape.BoundBox.Center + group[ind + 1].Shape.BoundBox.Center) / 2
                points.append(middlepoint)
            points.append(FreeCAD.Vector(frame_1.Shape.BoundBox.Center.x, frame_1.Shape.BoundBox.YMax, 0))

            points3D = []
            for point in points:
                point3D = mp.projectPointsOnMesh([point, ], terrain, FreeCAD.Vector(0, 0, 1))
                if len(point3D) > 0:
                    points3D.append(point3D[0])
                    break
                point.y += 100

            for ind in range(0, len(points3D) - 1):
                vec = points3D[ind] - points3D[ind + 1]
                angle = math.degrees(vec.getAngle(FreeCAD.Vector(0, 1, 0)))
                if angle > 90:
                    angle = angle - 180
                if vec.z >= 0:
                    angle *= -1
                frame = group[ind]
                p = (points3D[ind] + points3D[ind + 1]) / 2
                frame.Placement.Base = FreeCAD.Vector(frame.Placement.Base.x, frame.Placement.Base.y, p.z)
                frame.Placement.Rotation = FreeCAD.Rotation(frame.Placement.Rotation.toEuler()[0], angle, 0)
            Draft.makeWire(points3D)  # Hace falta??
    FreeCAD.activeDocument().recompute()


def getCols(sel, tolerance=2000):
    cols = []
    while len(sel) > 0:
        obj = sel[0]
        p = obj.Shape.BoundBox.Center  # TODO: Cambiar por centro de gravedad??
        n = FreeCAD.Vector(1, 0, 0)  # TODO: como se consigue la verdadera normal a la estructura??

        # 1. Detectar los objetos que están en una misma columna
        col = []
        newsel = []
        for obj1 in sel:
            if obj1.Shape.BoundBox.isCutPlane(p, n):
                col.append(obj1)
            else:
                newsel.append(obj1)

        sel = newsel.copy()
        col = sorted(col, key=lambda k: k.Placement.Base.y, reverse=True)  # Orden Norte - Sur (Arriba a abajo)

        # 2. Detectar y separar los grupos dentro de una misma columna:
        group = []
        newcol = []
        if len(col) > 1:
            distances = []
            for ind in range(0, len(col) - 1):
                vec1 = col[ind + 1].Placement.Base
                vec1.z = 0
                vec2 = col[ind].Placement.Base
                vec2.z = 0
                distances.append((vec1 - vec2).Length)
            distmin = tolerance
            group.append(col[0])
            for ind in range(0, len(col) - 1):
                # len1 = col[ind].Shape.Edges[0].Length
                # len2 = col[ind + 1].Shape.Edges[0].Length
                # len3 = (col[ind + 1].Placement.Base - col[ind].Placement.Base).Length - (len1 + len2) / 2 # TODO: Cambiar esto

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
    cols = sorted(cols, key=lambda k: k[0][0].Placement.Base.x,
                  reverse=False)  # Orden Oeste - Este  (Izquierda a derecha)
    return cols


# -----------------------------------------------------------------------------------------------------------------------
# Convert
#
#
# -----------------------------------------------------------------------------------------------------------------------
class _PVPlantConvertTaskPanel:
    '''The editmode TaskPanel for Conversions'''

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


# -----------------------------------------------------------------------------------------------------------------------
# function ConvertObjectsTo
#
#
# -----------------------------------------------------------------------------------------------------------------------

def ConvertObjectsTo(sel, objTo):
    import math
    import PVPlantRack

    if hasattr(objTo, "Proxy"):
        isFrame = objTo.Proxy.__class__ is PVPlantRack._Tracker
        # isFrame = issubclass(objTo.Proxy.__class__, PVPlantRack._Frame)
    isFrame = True

    for obj in sel:
        # if obj.Proxy.__class__ is PVPlantRack._Tracker:
        if isFrame:
            if hasattr(obj, "Proxy"):
                if obj.Proxy.__class__ is PVPlantRack._Tracker:
                    # if issubclass(obj.Proxy.__class__, PVPlantRack._Frame):             # 1. Si los dos son Frames
                    cp = FreeCAD.ActiveDocument.copyObject(objTo, False)
                    cp.Placement = obj.Placement
                    cp.CloneOf = objTo
            else:  # 2. De un objeto no Frame a Frame
                place = FreeCAD.Placement()  # obj.Placement
                place.Rotation = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1),
                                                  90)  # TODO: rotar conforme a lados más largos
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
        else:  # 3. De un objeto a otro objeto (cualesquieran que sean)
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
            #AdjustToTerrain_V1(sel)
            # AdjustToTerrain__(sel)
            adjustToTerrain(sel)
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
