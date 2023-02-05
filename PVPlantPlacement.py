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

import PVPlantResources
import Utils.PVPlantTrace as PVPlantTrace
from PVPlantResources import DirIcons as DirIcons
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
        obj.Proxy = self

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

    def __setstate__(self, state):
        """
        Get variables from file.
        """
        return None


class _PVPlantPlacementTaskPanel:
    '''The editmode TaskPanel for Schedules'''

    def __init__(self, obj=None):
        self.Terrain = None
        self.Rack = None
        self.PVArea = None
        self.Area = None
        self.gap_col = .0
        self.gap_row = .0
        self.offsetX = .0
        self.offsetY = .0
        self.Dir = FreeCAD.Vector(0, -1, 0)  # Norte a sur

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
        self.form.buttonAddProhivitedAreas.clicked.connect(self.addProhivitedAreas)

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

    def addProhivitedAreas(self):
        objname = FreeCADGui.Selection.getSelection()[0].Name

        self.form.listProhivitedAreas.addItem(objname)

    def addDirection(self):
        ''' '''

    def createFrameFromPoints(self, placements, edges=None):
        import PVPlantRack
        def createFrame(pl):
            #newrack = FreeCAD.ActiveDocument.copyObject(self.Rack)
            newrack = PVPlantRack.makeTracker()
            newrack.Label = "Tracker"
            newrack.Placement = pl
            newrack.Visibility = True
            MechanicalGroup.addObject(newrack)

        try:
            MechanicalGroup = FreeCAD.ActiveDocument.Frames
        except:
            MechanicalGroup = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroup", 'Frames')
            MechanicalGroup.Label = "Frames"

        if isinstance(placements, list):
            for place in placements:
                createFrame(place)
        else:
            createFrame(placements)

        FreeCAD.ActiveDocument.Site.addObject(MechanicalGroup)

    def calculateWorkingArea(self):
        self.Area = self.PVArea.Shape
        ProhibitedAreas = [FreeCAD.ActiveDocument.getObject(self.form.listProhivitedAreas.item(i).text()).Shape
                           for i in range(self.form.listProhivitedAreas.count())]
        if len(ProhibitedAreas) > 0:
            self.Area = self.Area.cut(ProhibitedAreas)

    def getAligments(self):
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

        steps = int((refv.BoundBox.XMax - self.Area.BoundBox.XMin + self.offsetX) / self.gap_col)
        startx = refv.BoundBox.XMax + self.offsetX - self.gap_col * steps
        steps = int((refh.BoundBox.YMin - self.Area.BoundBox.YMax + self.offsetY) / self.gap_row)
        starty = refh.BoundBox.YMin + self.offsetY + self.gap_row * steps
        # todo end ----------------------------------------------------------------------------------

        return np.arange(startx, self.Area.BoundBox.XMax, self.gap_col), \
               np.arange(starty, self.Area.BoundBox.YMin, -self.gap_row)

    def adjustToTerrain(self, coordinates, width):
        placements = list()
        dist = FreeCAD.Units.Quantity(self.form.editGapRows.text()).Value * 1.50
        vec1 = FreeCAD.Vector(self.Dir)
        vec1.Length = (width / 2)
        mode = 1
        terrain = PVPlantSite.get().Terrain.Mesh
        type = 0

        #01. Grouping:
        from skimage import measure
        arr = np.array(coordinates, dtype=object)
        labeled_im = measure.label(arr != 0)
        for region in measure.regionprops(labeled_im):
            label = region['label']
            cols, rows = np.where(labeled_im == label)
            tmpC = cols[0]
            tmpR = rows[0]
            for ind in range(len(cols)):
                print(coordinates[cols[ind]][rows[ind]])


        '''properties = ['label', 'area']
        table = measure.regionprops_table(labeled_im, properties=properties)
        print (table)
        import pandas as pd
        table = pd.DataFrame(table)
        print(table)'''

        def placeonregion(frames):
            for colnum, col in enumerate(frames):
                print (col)
                groups = list()
                groups.append([col[0]])
                for i in range(1, len(col)):
                    group = groups[-1]
                    long = (col[i].sub(group[-1])).Length
                    long -= width
                    if long <= dist:
                        group.append(col[i])
                    else:
                        groups.append([col[i]])

                for group in groups:
                    points = list()
                    points.append(group[0].sub(vec1))
                    for ind in range(0, len(group) - 1):
                        points.append((group[ind].sub(vec1) + group[ind + 1].add(vec1)) / 2)
                    points.append(group[-1].add(vec1))

                    points3D = list()
                    '''
                    # v0
                    for ind in range(len(points) - 1):
                        line = Part.LineSegment(points[ind], points[ind + 1])
                        tmp = terrain.makeParallelProjection(line.toShape(), FreeCAD.Vector(0, 0, 1))
                        if len(tmp.Vertexes) > 0:
                            if ind == 0:
                                points3D.append(tmp.Vertexes[0].Point)
                            points3D.append(tmp.Vertexes[-1].Point)
                    '''
                    # V1
                    if type == 0:   # Mesh:
                        import MeshPart as mp
                        for point in points:
                            point3D = mp.projectPointsOnMesh([point, ], terrain, FreeCAD.Vector(0, 0, 1))
                            if len(point3D) > 0:
                                points3D.append(point3D[0])

                    else:           # Shape:
                        line = Part.LineSegment(points[0], points[-1])
                        tmp = terrain.makeParallelProjection(line.toShape(), FreeCAD.Vector(0, 0, 1))
                        if len(tmp.Vertexes) > 0:
                            tmppoints = [ver.Point for ver in tmp.Vertexes]
                            if mode == 1:  # mode = normal
                                for point in points:
                                    '''# OPTION 1:
                                    line = Part.Line(point, point + FreeCAD.Vector(0, 0, 10))
                                    for i in range(len(tmppoints) - 1):
                                        seg = Part.LineSegment(tmppoints[i], tmppoints[i + 1])
                                        inter = line.intersect(seg)
                                        print(inter)
                                        if len(inter) > 0:
                                            points3D.append(FreeCAD.Vector(inter[0].X, inter[0].Y, inter[0].Z))
                                    '''
                                    # OPTION 2:
                                    plane = Part.Plane(point, self.Dir)
                                    for i in range(len(tmppoints) - 1):
                                        seg = Part.LineSegment(tmppoints[i], tmppoints[i + 1])
                                        inter = plane.intersect(seg)
                                        if len(inter) > 0:
                                            if len(inter[0]):
                                                inter = inter[0]
                                                points3D.append(FreeCAD.Vector(inter[0].X, inter[0].Y, inter[0].Z))
                                                break
                            else:  # TODO: mode = Trend
                                # TODO: check:
                                from scipy import stats
                                xx = list()
                                yy = list()
                                zz = list()

                                for pts in tmppoints:
                                    xx.append(pts.x)
                                    yy.append(pts.y)
                                    zz.append(pts.z)

                                slope, intercept, r, p, std_err = stats.linregress(yy, zz)

                                def myfunc(x):
                                    return slope * x + intercept

                                x = list()
                                x.append(yy[0])
                                x.append(yy[-1])
                                newzz = list(map(myfunc, x))
                                points3D.append(FreeCAD.Vector(xx[0], yy[0], newzz[0]))
                                points3D.append(FreeCAD.Vector(xx[-1], yy[-1], newzz[1]))
                    '''
                    if len(points) != len(points3D):
                        i = 0
                        while i < len(points3D) - 1:
                            vec = points3D[i + 1].sub(points3D[i])
                            if (vec.x == 0) and (vec.y == 0):
                                if vec.z >= 0:
                                    points3D.pop(i)
                                else:
                                    points3D.pop(i + 1)
                                continue
                            i += 1
                    '''
                    '''
                    if len(points3D) > 0:
                        line = PVPlantTrace.makeTrace(points3D, "LineCol" + str(colnum))
                        line.ProjectionPoints = points
                    else:
                        print(" Error: No 3d points: \n", points)
                    '''

                    for ind in range(0, len(points3D) - 1):
                        pl = FreeCAD.Placement()
                        vec = points3D[ind] - points3D[ind + 1]
                        pl.Base = FreeCAD.Vector(group[ind])
                        p = (points3D[ind] + points3D[ind + 1]) / 2
                        pl.Base.z = p.z
                        rot = FreeCAD.Rotation(FreeCAD.Vector(-1, 0, 0), vec)
                        pl.Rotation = FreeCAD.Rotation(rot.toEuler()[0], rot.toEuler()[1], 0)
                        placements.append(pl)
            return placements

    def isInside(self, cp):
        point = FreeCAD.Vector(x + yy_med + offsetcols, y - xx_med + offsetrows, 0.0)
        # first filter
        if self.Area.isInside(point, 10, True):
            #cp = rec.copy()
            cp.Placement.Base = point
            cut = cp.cut([self.Area])
            # second filter
            if len(cut.Vertexes) == 0:
                return True
        return False

    def calculateAlignedArray(self):
        pointsx, pointsy = self.getAligments()
        xx = self.Rack.Shape.BoundBox.XLength
        yy = self.Rack.Shape.BoundBox.YLength
        xx_med = xx / 2
        yy_med = yy / 2
        rec = Part.makePolygon([FreeCAD.Vector(-xx_med, -yy_med, 0),
                                FreeCAD.Vector(xx_med, -yy_med, 0),
                                FreeCAD.Vector(xx_med, yy_med, 0),
                                FreeCAD.Vector(-xx_med, yy_med, 0),
                                FreeCAD.Vector(-xx_med, -yy_med, 0)])
        rec.Placement.Rotation = FreeCAD.Rotation(FreeCAD.Vector(1, 0, 0),
                                                  FreeCAD.Vector(0, 1, 0))
        # variables for corridors:
        countcols = 0
        countrows = 0
        offsetcols = 0
        offsetrows = 0
        valcols = FreeCAD.Units.Quantity(self.form.editColGap.text()).Value - (self.gap_col - yy)

        pl = []
        cols = []
        cnt = 0
        for x in pointsx:
            col = []
            for y in pointsy:
                cnt += 1
                point = FreeCAD.Vector(x + yy_med + offsetcols, y - xx_med + offsetrows, 0.0)
                # first filter
                if self.Area.isInside(point, 10, True):
                    rec.Placement.Base = point
                    cut = rec.cut([self.Area])
                    # second filter
                    if len(cut.Vertexes) == 0:
                        pl.append(point)
                        col.append(point)
                        Part.show(rec)
                        continue
                col.append(0)
            cols.append(col)

            if len(col) > 0:
                # code for vertical corridors:
                if self.form.groupCorridor.isChecked():
                    if self.form.editColCount.value() > 0:
                        countcols += 1
                        if countcols == self.form.editColCount.value():
                            offsetcols += valcols
                            countcols = 0
        ''' old:
        pl = []
        cols = []
        cnt = 0
        for x in pointsx:
            col = []
            for y in pointsy:
                cnt += 1
                point = FreeCAD.Vector(x + yy_med + offsetcols, y - xx_med + offsetrows, 0.0)
                # first filter
                if self.Area.isInside(point, 10, True):
                    rec.Placement.Base = point
                    cut = rec.cut([self.Area])
                    # second filter
                    if len(cut.Vertexes) == 0:
                        pl.append(point)
                        col.append(point)
                        continue
                #col.append(None)

            if len(col) > 0:
                cols.append(col)
                # code for vertical corridors:
                if self.form.groupCorridor.isChecked():
                    if self.form.editColCount.value() > 0:
                        countcols += 1
                        if countcols == self.form.editColCount.value():
                            offsetcols += valcols
                            countcols = 0'''

        return self.adjustToTerrain(cols, xx)

    # TODO: cambiar esto código para adaptarlo al "calculateAlignedArray":
    def calculateNonAlignedArray(self):
        gap_col = FreeCAD.Units.Quantity(self.form.editGapCols.text()).Value
        gap_row = FreeCAD.Units.Quantity(self.form.editGapRows.text()).Value + max(self.Rack.Shape.BoundBox.XLength,
                                                                                   self.Rack.Shape.BoundBox.YLength)
        offset_x = FreeCAD.Units.Quantity(self.form.editOffsetHorizontal.text()).Value
        offset_y = FreeCAD.Units.Quantity(self.form.editOffsetVertical.text()).Value

        Area = self.calculateWorkingArea()

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

        if self.form.groupCorridor.isChecked():
            if (self.form.editColCount.value() > 0):
                xlen = len(pointsx)
                count = self.form.editColCount.value()
                val = FreeCAD.Units.Quantity(self.form.editColGap.text()).Value - (
                        gap_col - min(self.Rack.Shape.BoundBox.XLength, self.Rack.Shape.BoundBox.YLength))
                while count <= xlen:
                    for i, point in enumerate(pointsx):
                        if i >= count:
                            pointsx[i] += val
                    count += self.form.editColCount.value()

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
                        if len(cut.Vertexes) == 0:
                            Part.show(cp)
                            pl.append(point)
        return pl

    def accept(self):
        from datetime import datetime
        starttime = datetime.now()

        self.gap_col = FreeCAD.Units.Quantity(self.form.editGapCols.text()).Value
        self.gap_row = FreeCAD.Units.Quantity(self.form.editGapRows.text()).Value + \
                       max(self.Rack.Shape.BoundBox.XLength, self.Rack.Shape.BoundBox.YLength)
        self.offsetX = FreeCAD.Units.Quantity(self.form.editOffsetHorizontal.text()).Value
        self.offsetY = FreeCAD.Units.Quantity(self.form.editOffsetVertical.text()).Value

        if self.Terrain is None:
            self.Terrain = PVPlantSite.get().Terrain.Shape

        FreeCAD.ActiveDocument.openTransaction("Create Placement")
        self.calculateWorkingArea()
        placements = None
        if self.form.cbAlignFrames.isChecked():
            placements = self.calculateAlignedArray()
        else:
            placements = self.calculateNonAlignedArray()

        # last step: ------------------------------
        self.createFrameFromPoints(placements)

        total_time = datetime.now() - starttime
        print(" -- Tiempo tardado:", total_time)
        FreeCADGui.Control.closeDialog()
        return True

def algo(terrain, frames):
    line = Part.LineSegment(begin, end).toShape()
    pts = mp.projectShapeOnMesh(line, terrain, FreeCAD.Vector(0, 0, 1))

def getMaxSlope(frames, relation):
    xx = 0
    separation = 0
    yy = 0
    for i in range(len(frames)):
        xx += frames[i].length
        if i > 0:
            tmp = (frames[i].BoundBox.Center - frames[i-1].BoundBox.Center).Length - \
                  (frames[i].length + frames[i-1].length) / 2
            separation += tmp
            yy += tmp * relation
    return yy/xx

# ----------------------------------------------------------------------------------------------------------------------
# function AdjustToTerrain
#   Take a group of objects and adjust it to the slope and altitude of the terrain mesh. It detects the terrain mesh
#
#   Inputs:
#   1. frames: group of objest to adjust
# ----------------------------------------------------------------------------------------------------------------------
class adjustToTerrainTaskPanel:
    def __init__(self, obj=None):
        self.obj = obj

        # -------------------------------------------------------------------------------------------------------------
        # Module widget form
        # -------------------------------------------------------------------------------------------------------------
        self.form = FreeCADGui.PySideUic.loadUi(PVPlantResources.__dir__ + "/PVPlantPlacementAdjust.ui")

    def accept(self):
        FreeCADGui.Control.closeDialog()
        adjustToTerrain(FreeCADGui.Selection.getSelection(), self.form.checkTrenck, self.form.editStepSize)
        return True

    def reject(self):
        FreeCADGui.Control.closeDialog()
        return True

def adjustToTerrain(frames, trend = True, stepSize = 0):
    from datetime import datetime
    starttime = datetime.now()

    from scipy import stats
    import MeshPart as mp

    FreeCAD.ActiveDocument.openTransaction("Adjust to terrain")
    terrain = None
    type = 0
    if hasattr(PVPlantSite.get().Terrain, "Mesh") and (PVPlantSite.get().Terrain.Mesh.Area>0):
        terrain = PVPlantSite.get().Terrain.Mesh
    else:
        terrain = PVPlantSite.get().Terrain.Shape
        type = 1

    cols = getCols(frames)
    for col in cols:
        for group in col:
            # 1. Get lines/points to project on land
            frame1 = group[0]  # Norte
            frame2 = group[-1]  # Sur
            # TODO: revisar esta parte:
            p0 = FreeCAD.Vector(frame1.Shape.BoundBox.Center.x, frame1.Shape.BoundBox.YMax, 0)
            pf = FreeCAD.Vector(frame2.Shape.BoundBox.Center.x, frame2.Shape.BoundBox.YMin, 0)

            points = []
            vec = (pf - p0).normalize()
            points.append(p0)
            for ind in range(0, len(group) - 1):
                frame1 = group[ind]
                frame2 = group[ind + 1]
                vec1 = FreeCAD.Vector(frame1.Placement.Base)
                vec2 = FreeCAD.Vector(frame2.Placement.Base)
                vec1.z = 0
                vec2.z = 0
                vec3 = vec2.sub(vec1)
                c = vec3.Length / 2 + (frame1.Length.Value - frame2.Length.Value) / 4
                v = FreeCAD.Vector(vec)
                v.Length = c
                v = vec1.add(v)
                v.z = 0
                points.append(v)
            points.append(pf)

            # 2. Get 3D points of the line:
            points3D = []
            if type == 0:   # Mesh:
                import MeshPart as mp
                points3D = mp.projectPointsOnMesh(points, terrain, FreeCAD.Vector(0, 0, 1))
            else:           # Shape:
                line = Part.LineSegment(points[0], points[-1])
                tmp = terrain.makeParallelProjection(line.toShape(), FreeCAD.Vector(0, 0, 1))
                if len(tmp.Vertexes) > 0:
                    tmppoints = [ver.Point for ver in tmp.Vertexes]
                    for point in points:
                        plane = Part.Plane(point, vec)
                        for i in range(len(tmppoints) - 1):
                            seg = Part.LineSegment(tmppoints[i], tmppoints[i + 1])
                            inter = plane.intersect(seg)
                            if len(inter) > 0:
                                if len(inter[0]):
                                    inter = inter[0]
                                    points3D.append(FreeCAD.Vector(inter[0].X, inter[0].Y, inter[0].Z))
                                    break

            # 3. Calculate trend:
            points3Dtrend = []
            if trend:
                def getNewZ(x):
                    return slope * x + intercept
                if type == 0:  # Mesh:
                    tmp_points3D = list()
                    for ind in range(0, len(points3D) - 1):
                        line = Part.LineSegment(points3D[ind], points3D[ind + 1]).toShape()
                        tmppoints = mp.projectShapeOnMesh(line, terrain, FreeCAD.Vector(0, 0, 1))
                        xx = list()
                        yy = list()
                        zz = list()
                        for point in tmppoints[0]:
                            xx.append(point.x)
                            yy.append(point.y)
                            zz.append(point.z)
                        slope, intercept, r, p, std_err = stats.linregress(yy, zz)
                        newzz = list(map(getNewZ, [yy[0], yy[-1]]))
                        if ind == 0:
                            tmp_points3D.append(FreeCAD.Vector(xx[0], yy[0], newzz[0]))
                        else:
                            tmp_points3D[ind] = (tmp_points3D[ind] + FreeCAD.Vector(xx[0], yy[0], newzz[0])) / 2
                        tmp_points3D.append(FreeCAD.Vector(xx[-1], yy[-1], newzz[-1]))
                        points3Dtrend.append((FreeCAD.Vector(xx[0], yy[0], newzz[0]),
                                              FreeCAD.Vector(xx[-1], yy[-1], newzz[-1])))
                    points3D = tmp_points3D.copy()

            for ind in range(0, len(points3D) - 1):
                p = (points3D[ind] + points3D[ind + 1]) / 2
                group[ind].Placement.Base.z = p.z
                vec = points3D[ind] - points3D[ind + 1]
                rot = FreeCAD.Rotation(FreeCAD.Vector(-1, 0, 0), vec)
                group[ind].Placement.Rotation = FreeCAD.Rotation(rot.toEuler()[0], rot.toEuler()[1], 0)

    total_time = datetime.now() - starttime
    print(" -- Tiempo tardado en ajustar al terreno:", total_time)
    FreeCAD.activeDocument().recompute()

def getAxis(sel):
    site = FreeCAD.ActiveDocument.Site.Terrain.Shape
    for rack in sel:
        poles = rack.Shape.SubShapes[1].SubShapes
        line = Part.LineSegment(poles[0].BoundBox.Center, poles[-1].BoundBox.Center)
        Part.show(line.toShape())
        pro = site.makeParallelProjection(line.toShape(), FreeCAD.Vector(0, 0, 1))
        Part.show(pro)

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
            p2 = FreeCAD.Vector(frame.Shape.BoundBowirex.Center.x, frame.Shape.BoundBox.YMax, 0.0)

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
            points.append(FreeCAD.Vector(frame_1.Shape.BoundBox.Center.x, frame_1.Shape.BoundBox.YMin, 0))

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

def getCols(sel, tolerance=4000, sort = True):
    # TODO: get only frames from de selection
    if not sel:
        return
    if len(sel) == 0:
        return

    cols = []
    while len(sel) > 0:
        obj = sel[0]
        p = obj.Shape.BoundBox.Center
        vec = obj.Shape.SubShapes[1].SubShapes[1].BoundBox.Center - \
              obj.Shape.SubShapes[1].SubShapes[0].BoundBox.Center
        n = FreeCAD.Vector(vec.y, -vec.x, 0)

        # 1. Detectar los objetos que están en una misma columna
        col = []
        newsel = []
        for obj1 in sel:
            if obj1.Shape.BoundBox.isCutPlane(p, n): #todo: esto no es del todo correcto. buscar otra manera
                col.append(obj1)
            else:
                newsel.append(obj1)
        sel = newsel.copy()
        col = sorted(col, key=lambda k: k.Placement.Base.y, reverse=True)  #Orden Norte - Sur (Arriba a abajo)

        # 2. Detectar y separar los grupos dentro de una misma columna:
        group = []
        newcol = []
        group.append(col[0])
        if len(col) > 1:
            for ind in range(0, len(col) - 1):
                vec1 = FreeCAD.Vector(col[ind].Placement.Base)
                vec1.z = 0
                vec2 = FreeCAD.Vector(col[ind + 1].Placement.Base)
                vec2.z = 0
                distance = abs((vec1 - vec2).Length) - (col[ind].Width.Value + col[ind + 1].Width.Value) / 2
                if distance > tolerance:
                    newcol.append(group.copy())
                    group.clear()
                group.append(col[ind + 1])
        newcol.append(group)
        cols.append(newcol)

    if sort:
        cols = sorted(cols, key=lambda k: k[0][0].Placement.Base.x, reverse=False)

    return cols

def getGroups(columns, tolerance = 4000):
    newColumns = list()
    for column in columns:
        groups = getGroupsIncolumn(column, tolerance)
        newColumns.append(groups)
    return newColumns

    
def getGroupsInColumn(column, tolerance = 4000):
    group = list()
    groups = list()
    group.append(column[0])
    if len(column) > 1:
        for ind in range(0, len(column) - 1):
            vec1 = FreeCAD.Vector(column[ind + 1].Placement.Base)
            vec1.z = 0
            vec2 = FreeCAD.Vector(column[ind].Placement.Base)
            vec2.z = 0
            distance = (vec1 - vec2).Length - (column[ind].Length.Value + column[ind + 1].Length.Value) / 2
            if distance > tolerance:
                groups.append(group.copy())
                group.clear()
            group.append(column[ind + 1])
    groups.append(group)
    return groups

# -----------------------------------------------------------------------------------------------------------------------
# Convert
# -----------------------------------------------------------------------------------------------------------------------
class _PVPlantConvertTaskPanel:
    '''The editmode TaskPanel for Conversions'''

    def __init__(self):
        self.To = None
        # self.form:
        self.form = FreeCADGui.PySideUic.loadUi(os.path.join(PVPlantResources.__dir__, "PVPlantPlacementConvert.ui"))
        self.form.setWindowIcon(QtGui.QIcon(os.path.join(PVPlantResources.DirIcons, "Trace.svg")))

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
            FreeCAD.ActiveDocument.openTransaction("Convert to")
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
        return {'Pixmap': str(os.path.join(PVPlantResources.DirIcons, "adjust.svg")),
                'Accel': "P, S",
                'MenuText': QT_TRANSLATE_NOOP("Placement", "Adjust"),
                'ToolTip': QT_TRANSLATE_NOOP("Placement", "Adjust object to terrain")}

    def Activated(self):
        sel = FreeCADGui.Selection.getSelection()
        if len(sel) > 0:
            #adjustToTerrain(sel)
            FreeCADGui.Control.showDialog(adjustToTerrainTaskPanel())
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
