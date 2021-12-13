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

import FreeCAD, Draft, Part
import BOPTools.SplitAPI as splitter
import ArchComponent
import PVPlantSite
import math
import copy

if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore, QtGui, QtSvg
    from DraftTools import translate
    from PySide.QtCore import QT_TRANSLATE_NOOP

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

import PVPlantResources
from PVPlantResources import DirIcons as DirIcons


def makePad(base=None):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Pad")
    _Pad(obj)
    _ViewProviderPad(obj.ViewObject)
    obj.Base = base

    '''
    if FreeCAD.ActiveDocument.Pads:
        FreeCAD.ActiveDocument.Pads.addObject(obj)
    '''

    return obj


class _Pad(ArchComponent.Component):
    def __init__(self, obj):
        # Definición de Variables:
        ArchComponent.Component.__init__(self, obj)
        self.obj = obj
        self.base = None

        self.setProperties(obj)
        self.Type = "Pad"

        obj.Proxy = self
        obj.IfcType = "Civil Element"
        obj.setEditorMode("IfcType", 1)


    def setProperties(self, obj):
        # Definicion de Propiedades:
        '''[
        'App::PropertyBool',
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
        'Mesh::PropertyNormalList',
        'Mesh::PropertyCurvatureList',
        'Mesh::PropertyMeshKernel',
        'Sketcher::PropertyConstraintList'
        ]'''


        #TODO: Los parametros width y length desaparecerán. Se tiene que selecionar objeto base
        obj.addProperty("App::PropertyLength",
                        "Width",
                        "Pad",
                        QT_TRANSLATE_NOOP("App::Property", "Connection")).Width = 5000

        obj.addProperty("App::PropertyLength",
                        "Length",
                        "Pad",
                        QT_TRANSLATE_NOOP("App::Property", "Connection")).Length = 10000

        obj.addProperty("App::PropertyAngle",
                        "FillSlope",
                        "Pad",
                        QT_TRANSLATE_NOOP("App::Property", "Connection")).FillSlope = 45.00

        obj.addProperty("App::PropertyAngle",
                        "CutSlope",
                        "Pad",
                        QT_TRANSLATE_NOOP("App::Property", "Connection")).CutSlope = 60.00

        obj.addProperty("App::PropertyBool",
                        "TopsoilCalculation",
                        "Pad",
                        QT_TRANSLATE_NOOP("App::Property", "Connection")).TopsoilCalculation = False

        obj.addProperty("App::PropertyLength",
                        "TopsoilHeight",
                        "Pad",
                        QT_TRANSLATE_NOOP("App::Property", "Connection")).TopsoilHeight = 300

        # Output values:
        obj.addProperty("App::PropertyVolume",
                        "CutVolume",
                        "Output",
                        QT_TRANSLATE_NOOP("App::Property", "Connection"))
        obj.setEditorMode("CutVolume", 1)

        obj.addProperty("App::PropertyVolume",
                        "FillVolume",
                        "Output",
                        QT_TRANSLATE_NOOP("App::Property", "Connection"))
        obj.setEditorMode("FillVolume", 1)

        obj.addProperty("App::PropertyArea",
                        "PadArea",
                        "Output",
                        QT_TRANSLATE_NOOP("App::Property", "Connection"))
        obj.setEditorMode("PadArea", 1)

        obj.addProperty("App::PropertyArea",
                        "TopSoilArea",
                        "Output",
                        QT_TRANSLATE_NOOP("App::Property", "Connection"))
        obj.setEditorMode("TopSoilArea", 1)

        obj.addProperty("App::PropertyVolume",
                        "TopSoilVolume",
                        "Output",
                        QT_TRANSLATE_NOOP("App::Property", "Connection"))
        obj.setEditorMode("TopSoilVolume", 1)

    def onDocumentRestored(self, obj):
        """Method run when the document is restored.
        Re-adds the Arch component, and object properties."""

        ArchComponent.Component.onDocumentRestored(self, obj)
        self.obj = obj
        self.Type = "Pad"
        obj.Proxy = self

    def onChanged(self, fp, prop):
        '''Do something when a property has changed'''

        '''
        if prop == "Tilt":
            if not hasattr(self, "obj"):
                return
            if hasattr(self.obj, "MaxPhi"):
        '''

    def execute(self, obj):
        from datetime import datetime
        starttime = datetime.now()

        pb = obj.Placement.Base
        pr = obj.Placement.Rotation
        land = PVPlantSite.get().Terrain
        shapes = []
        pad = None

        if obj.Base:
            if hasattr(obj.Base.Shape, 'Wires') and obj.Base.Shape.Wires:
                pad = obj.Base.Shape.Wires[0]
            elif obj.Base.Shape.Edges:
                pad = Part.Wire(obj.Base.Shape.Edges)
            pb = obj.Base.Placement.Base
        else:
            # Si no hay una base seleccionada se crea una rectangular:
            halfWidth = obj.Width.Value / 2
            halfLength = obj.Length.Value / 2

            p1 = FreeCAD.Vector(-halfLength, -halfWidth, 0)
            p2 = FreeCAD.Vector( halfLength, -halfWidth, 0)
            p3 = FreeCAD.Vector( halfLength,  halfWidth, 0)
            p4 = FreeCAD.Vector(-halfLength,  halfWidth, 0)
            pad = Part.makePolygon([p1, p2, p3, p4, p1])

        # 1. Terraplén (embankment / fill):
        fill = None
        fillcommon = None
        if land.Shape.BoundBox.ZMin < pb.z:
            print("- PAD: Calcalete fill solid:")
            fill = self.createSolid(obj, pad, land, -1)
            fill.Placement.Base += pb
            print("-- Fill: ", fill)
            fillcommon, fill = self.calculateFill(obj, fill)
            print("--- Fill: ", fill)
        else:
            print("- PAD: NOOOO  Calcalete fill solid:")

        # 2. Desmonte (cut):
        cut = None
        cutcommon = None
        if land.Shape.BoundBox.ZMax > pb.z:
            print("- PAD: Calcalete cut solid:")
            cut = self.createSolid(obj, pad, land, 1)
            cut.Placement.Base += pb
            print("-- Cut: ", cut)
            cutcommon, cut = self.calculateCut(obj, cut)
            print("--- Cut: ", cut)
        else:
            print("- PAD: NOOOO Calcalete cut solid:")

        topsoilArea = 0
        topsoilVolume = 0
        if fill:
            if obj.TopsoilCalculation:
                filltopsoil = fillcommon.extrude(FreeCAD.Vector(0, 0, -obj.TopsoilHeight))
                topsoilVolume += filltopsoil.Volume
                filltopsoil.Placement.Base -= pb
                shapes.append(filltopsoil)
            fill.Placement.Base -= pb
            shapes.append(fill)
            topsoilArea += fill.Area
        if cut:
            cut.Placement.Base -= pb
            shapes.append(cut)
            topsoilArea += cut.Area
            if obj.TopsoilCalculation:
                cuttopsoil = cutcommon.extrude(FreeCAD.Vector(0, 0, -obj.TopsoilHeight))
                topsoilVolume += cuttopsoil.Volume
                self.obj.CutVolume = self.obj.CutVolume.Value - cuttopsoil.Volume

        pad = Part.Face(pad)
        if len(shapes) == 0:
            shapes.append(pad)

        obj.Shape = Part.makeCompound(shapes)
        self.obj.PadArea = pad.Area
        self.obj.TopSoilArea = topsoilArea
        self.obj.TopSoilVolume = topsoilVolume

        total_time = datetime.now() - starttime
        print(" -- Tiempo tardado:", total_time)

    def createSolid(self, obj, base, land, dir = -1):
        zz = .0
        angle = .0
        height = .0
        if dir == -1:
            zz = land.Shape.BoundBox.ZMin
            angle = obj.FillSlope.Value
        else:
            zz = land.Shape.BoundBox.ZMax
            angle = obj.CutSlope.Value
        height = abs(zz - obj.Placement.Base.z)

        offset = base.makeOffset2D(height / math.tan(math.radians(angle)), join=0)
        offset.Placement.Base = base.Placement.Base + FreeCAD.Vector(0, 0, zz - obj.Placement.Base.z)

        if False: # old code
            offset1 = base.makeOffset2D(10 / math.tan(math.radians(angle)), join=0)
            offset1.Placement.Base = base.Placement.Base + FreeCAD.Vector(0, 0, 10 * dir)

            loft1 = Part.makeLoft([base, offset1, offset], True, True)
            if False:
                return loft1
            else:
                loft2 = Part.makeLoft([offset1, offset], True, True)
                print(" ---loft1: ", loft1)
                print(" ---loft2: ", loft2)
                return loft1.fuse([loft2, ])
        else:
            import DraftGeomUtils
            base_fillet = DraftGeomUtils.filletWire(base, 1) #trip to get a nice shape: (fillet of 1 mm)
            return Part.makeLoft([base_fillet, offset], True)


    def calculateFill(self, obj, solid):
        common = solid.common(PVPlantSite.get().Terrain.Shape)
        if common.Area > 0:
            sp = splitter.slice(solid, [common, ], "Split")
            commoncopy = common.copy()
            commoncopy.Placement.Base.z += 10
            volume = 0
            fills = []
            for sol in sp.Solids:
                common1 = sol.common(commoncopy)
                if common1.Area > 0:
                    volume += sol.Volume
                    fills.append(sol)
            obj.FillVolume = volume
            if len(fills) > 0:
                base = fills.pop(0)
                if len(fills) > 0:
                    base = base.fuse(fills)
                return common, base
        else:
            obj.FillVolume = 0
            print("--- Fill: no common Area --------------------------")
        return None, None

    def calculateCut(self, obj, solid):
        common = solid.common(PVPlantSite.get().Terrain.Shape)
        if common.Area > 0:
            sp = splitter.slice(solid, [common, ], "Split")
            shells = []
            volume = 0
            commoncopy = common.copy()
            commoncopy.Placement.Base.z -= 1
            for sol in sp.Solids:
                common1 = sol.common(commoncopy)
                if common1.Area > 0:
                    volume += sol.Volume
                    shell = sol.Shells[0]
                    shell = shell.cut(common)
                    shells.append(shell)
            obj.CutVolume = volume
            if len(shells) > 0:
                base = shells.pop(0)
                if len(shells) > 0:
                    base = base.fuse(shells)
                return common, base
        else:
            obj.CutVolume = 0
            print("--- Cut: no common Area --------------------------")

        return None, None

class _ViewProviderPad(ArchComponent.ViewProviderComponent):
    def __init__(self, vobj):
        ArchComponent.ViewProviderComponent.__init__(self, vobj)

    def getIcon(self):
        return str(os.path.join(PVPlantResources.DirIcons, "slope.svg"))
"""
    def attach(self, vobj):
        '''
        Create Object visuals in 3D view.
        '''

        print("+ attach")
        # GeoCoords Node.
        self.geo_coords = coin.SoGeoCoordinate()

        # Surface features.
        self.triangles = coin.SoIndexedFaceSet()
        self.face_material = coin.SoMaterial()
        self.edge_material = coin.SoMaterial()
        self.edge_color = coin.SoBaseColor()
        self.edge_style = coin.SoDrawStyle()
        self.edge_style.style = coin.SoDrawStyle.LINES

        shape_hints = coin.SoShapeHints()
        shape_hints.vertex_ordering = coin.SoShapeHints.COUNTERCLOCKWISE
        mat_binding = coin.SoMaterialBinding()
        mat_binding.value = coin.SoMaterialBinding.PER_FACE
        offset = coin.SoPolygonOffset()

        # Face root.
        faces = coin.SoSeparator()
        faces.addChild(shape_hints)
        faces.addChild(self.face_material)
        faces.addChild(mat_binding)
        faces.addChild(self.geo_coords)
        faces.addChild(self.triangles)

        # Highlight for selection.
        highlight = coin.SoType.fromName('SoFCSelection').createInstance()
        highlight.style = 'EMISSIVE_DIFFUSE'
        faces.addChild(shape_hints)
        highlight.addChild(self.edge_material)
        highlight.addChild(mat_binding)
        highlight.addChild(self.edge_style)
        highlight.addChild(self.geo_coords)
        highlight.addChild(self.triangles)

    def updateData(self, obj, prop):
        '''
        Update Object visuals when a data property changed.
        '''
        origin = PVPlantSite.get()
        base = copy.deepcopy(origin.Origin)
        base.z = 0

        if prop == "Shape":
            shape = obj.getPropertyByName(prop)

            # Get GeoOrigin.
            points = [ver.Point for ver in shape.Vertexes]

            # Set GeoCoords.
            geo_system = ["UTM", origin.UtmZone, "FLAT"]
            self.geo_coords.geoSystem.setValues(geo_system)
            self.geo_coords.point.values = points
"""


class _PadTaskPanel:

    def __init__(self, obj=None):

        if obj is None:
            self.new = True
            self.obj = makeTrench()
        else:
            self.new = False
            self.obj = obj

        self.form = FreeCADGui.PySideUic.loadUi(os.path.join(PVPlantResources.__dir__, "PVPlantTrench.ui"))

    def accept(self):
        FreeCAD.ActiveDocument.openTransaction("Create Pad")
        FreeCADGui.Control.closeDialog()
        return True

    def reject(self):
        FreeCAD.ActiveDocument.removeObject(self.obj.Name)
        if self.new:
            FreeCADGui.Control.closeDialog()
        return True


import sys
from PySide.QtCore import QT_TRANSLATE_NOOP

import FreeCAD as App
import FreeCADGui as Gui
import DraftVecUtils
import draftutils.utils as utils
import draftutils.gui_utils as gui_utils
import draftutils.todo as todo
import draftguitools.gui_base_original as gui_base_original
import draftguitools.gui_tool_utils as gui_tool_utils

from draftutils.messages import _msg, _err
from draftutils.translate import translate


class _CommandPad(gui_base_original.Creator):
    """Gui command for the Line tool."""

    def __init__(self):
        # super(_CommandTrench, self).__init__()
        gui_base_original.Creator.__init__(self)
        self.path = None
        self.obj = None

    def GetResources(self):
        """Set icon, menu and tooltip."""
        return {'Pixmap': str(os.path.join(DirIcons, "slope.svg")),
                'MenuText': QtCore.QT_TRANSLATE_NOOP("PVPlantPad", "Pad"),
                'Accel': "C, P",
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("PVPlantPad",
                                                    "Creates a Pad object from setup dialog.")}

    def Activated(self, name=translate("draft", "Line")):
        """Execute when the command is called."""

        sel = FreeCADGui.Selection.getSelection()
        base = None
        needbase = True
        if len(sel) > 0:
            needbase = False
            base = sel[0]
        self.obj = makePad(base)

        if needbase:
            gui_base_original.Creator.Activated(self, name=translate("draft", "Line"))
            self.ui.wireUi(name)
            self.ui.setTitle("Pad")
            #self.obj = self.doc.addObject("Part::Feature", self.featureName)
            #gui_utils.format_object(self.obj)
            self.call = self.view.addEventCallback("SoEvent", self.action)

    def action(self, arg):
        """Handle the 3D scene events.

        This is installed as an EventCallback in the Inventor view.

        Parameters
        ----------
        arg: dict
            Dictionary with strings that indicates the type of event received
            from the 3D view.
        """

        print(self.obj)
        if arg["Type"] == "SoKeyboardEvent" and arg["Key"] == "ESCAPE":
            self.finish()
            FreeCAD.ActiveDocument.removeObject(self.obj.Name)

        elif arg["Type"] == "SoLocation2Event":
            self.point, ctrlPoint, self.info = gui_tool_utils.getPoint(self, arg)
            gui_tool_utils.redraw3DView()
            self.obj.Placement.Base = FreeCAD.Vector(self.info["x"], self.info["y"], self.info["z"])

        elif (arg["Type"] == "SoMouseButtonEvent"
              and arg["State"] == "DOWN"
              and arg["Button"] == "BUTTON1"):

            gui_tool_utils.getSupport(arg)
            self.point, ctrlPoint, self.info = gui_tool_utils.getPoint(self, arg)

            if self.point:
                self.point = FreeCAD.Vector(self.info["x"], self.info["y"], self.info["z"])
                self.ui.redraw()
                self.obj.Placement.Base = FreeCAD.Vector(self.info["x"], self.info["y"], self.info["z"])
                self.finish()
                FreeCAD.ActiveDocument.recompute()

    def finish(self, closed=False, cont=False):
        """Terminate the operation and close the polyline if asked.

        Parameters
        ----------
        closed: bool, optional
            Close the line if `True`.
        """

        # super(_CommandTrench, self).finish()
        gui_base_original.Creator.finish(self)
        if self.ui and self.ui.continueMode:
            self.Activated()

if FreeCAD.GuiUp:
    FreeCADGui.addCommand('PVPlantPad', _CommandPad())
