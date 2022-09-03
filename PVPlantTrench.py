# /**********************************************************************
# *                                                                     *
# * Copyright (c) 2021 Javier Braña <javier.branagutierrez@gmail.com>   *
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

import PVPlantResources
from PVPlantResources import DirIcons as DirIcons


def makeTrench(base=None):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Trench")
    _Trench(obj)
    _ViewProviderTrench(obj.ViewObject)
    obj.Base = base
    FreeCAD.ActiveDocument.recompute()
    return obj

def SplitTrench(wire, point):
    import BOPTools.SplitAPI as splitter

    plane = Part.Plane(Location, Normal)
    wires = splitter.slice(wire, [plane, ], "Split")

class _Trench(ArchComponent.Component):
    def __init__(self, obj):
        # Definición de Variables:
        ArchComponent.Component.__init__(self, obj)
        self.setProperties(obj)
        self.obj = obj

        self.route = False

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

        pl = obj.PropertiesList

        # Editable properties:
        if not ("Width" in pl):
            obj.addProperty("App::PropertyLength",
                            "Width",
                            "Trench",
                            QT_TRANSLATE_NOOP("App::Property", "Connection")).Width = 800

        if not ("Height" in pl):
            obj.addProperty("App::PropertyLength",
                            "Height",
                            "Trench",
                            QT_TRANSLATE_NOOP("App::Property", "Connection")).Height = 1200

        # Outputs: ------------------------
        if not ("Length" in pl):
            obj.addProperty("App::PropertyLength",
                            "Length",
                            "Outputs",
                            "Length")
        obj.setEditorMode("Length", 1)

        if not ("Volume" in pl):
            obj.addProperty("App::PropertyVolume",
                            "Volume",
                            "Outputs",
                            "Volume")
        obj.setEditorMode("Volume", 1)

        self.Type = "Trench"
        obj.Proxy = self
        obj.IfcType = "Civil Element"  ## puede ser: Cable Carrier Segment
        # obj.setEditorMode("IfcType", 1)

    def onDocumentRestored(self, obj):
        """Method run when the document is restored.
        Re-adds the component, and object properties."""

        ArchComponent.Component.onDocumentRestored(self, obj)
        self.setProperties(obj)

    def execute(self, obj):
        import Part, DraftGeomUtils, math
        import Draft

        def makeoffsets(w1, width):
            import DraftGeomUtils
            vec = w1.Vertexes[1].Point - w1.Vertexes[0].Point
            vec1 = FreeCAD.Vector(vec.y, -vec.x, 0)
            vec1 = vec1.normalize()
            vec1.Length = width / 2
            off1 = DraftGeomUtils.offsetWire(w1.Wires[0], vec1)
            vec1.Length = -width / 2
            off2 = DraftGeomUtils.offsetWire(w1.Wires[0], vec1)
            return off1, off2

        obj.Base.Visibility = False
        w = self.calculatePathWire(obj)
        land = FreeCAD.ActiveDocument.Site.Terrain.Shape
        w = Part.Wire(land.makeParallelProjection(w, FreeCAD.Vector(0, 0, 1)).Edges)
        #Part.show(w, "Projected_wire")

        # Opción 2: Con offset:
        pts = [ver.Point for ver in w.Vertexes]
        for point in pts:
            point.z = 0
        w1 = Part.makePolygon(pts)
        off1, off2 = makeoffsets(w1, obj.Width.Value)
        off1 = [ver.Point for ver in off1.Vertexes]
        off2 = [ver.Point for ver in off2.Vertexes]

        h = obj.Height.Value
        for i in range(len(w.Vertexes)):
            off1[i].z = w.Vertexes[i].Point.z - h
            off2[i].z = w.Vertexes[i].Point.z - h

        #h *= 2
        pols = []
        for i, ver in enumerate(w.Vertexes):
            pol = Part.makePolygon([off1[i], off1[i] + FreeCAD.Vector(0, 0, h),
                                    off2[i] + FreeCAD.Vector(0, 0, h), off2[i],
                                    ])
            pols.append(pol.Wires[0])

        sh = Part.makeLoft(pols, True, True)
        #land = FreeCAD.ActiveDocument.Terrain.Shape
        #common = sh.common(land)
        #Part.show(common)
        #common = common.extrude(FreeCAD.Vector(0, 0, h))
        #sh = sh.cut(common)

        obj.Shape = Part.makeCompound([sh, w])
        obj.Volume = sh.Volume
        obj.Length = w.Length

    def calculatePathWire(self, obj):
        if obj.Base:
            wire = None
            if hasattr(obj.Base.Shape, 'Wires') and obj.Base.Shape.Wires:
                wire = obj.Base.Shape.Wires[0]
            elif obj.Base.Shape.Edges:
                wire = Part.Wire(obj.Base.Shape.Edges)

            return wire
        return None

    def calculateLoft(self, obj, profile, center, wire):
        import DraftGeomUtils
        shapes = []
        usenew = False

        delta = wire.Vertexes[0].Point - center
        profile.translate(delta)

        if Draft.getType(obj.Base) == "BezCurve":
            v1 = obj.Base.Placement.multVec(obj.Base.Points[1]) - w.Vertexes[0].Point
        else:
            v1 = wire.Vertexes[1].Point - wire.Vertexes[0].Point
        v2 = DraftGeomUtils.getNormal(profile)
        rot = FreeCAD.Rotation(v2, v1)
        ang = rot.toEuler()[0]
        profile.Placement.Rotation = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), ang)
        ed = profile.Edges[0]
        profile = Part.makeLine(ed.Vertexes[0].Point, ed.Vertexes[1].Point)

        for pw in profile.Edges:
            sh = wire.makePipeShell([pw], True, False, 1)
            shapes.append(sh)

        shape = shapes.pop(0)
        if len(shapes) > 0:
            shape = shape.fuse(shapes)
        return shape


class _ViewProviderTrench(ArchComponent.ViewProviderComponent):
    def __init__(self, vobj):
        ArchComponent.ViewProviderComponent.__init__(self, vobj)

    def getIcon(self):
        return str(os.path.join(PVPlantResources.DirIcons, "trench.svg"))



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


class _TrenchTaskPanel:
    def __init__(self, obj=None):
        self.obj = obj
        self.new = False

        if obj is None:
            self.new = True

        self.form = FreeCADGui.PySideUic.loadUi(os.path.join(PVPlantResources.__dir__, "PVPlantTrench.ui"))
        self.form.buttonAddLayer.clicked.connect(self.addLayer)
        self.form.buttonDeleteLayer.clicked.connect(self.removeLayer)
        self.form.buttonUp.clicked.connect(self.moveUp)
        self.form.buttonDown.clicked.connect(self.moveDown)

        self.path = None
        #self.ui = None
        self.node = []
        self.pos = None
        self.support = None
        self.info = None
        self.view = FreeCADGui.ActiveDocument.ActiveView
        self.call = self.view.addEventCallback("SoEvent", self.action)

    def featureName(self):
        return "Trench"

    def action(self, arg):
        """Handle the 3D scene events.

        This is installed as an EventCallback in the Inventor view.

        Parameters
        ----------
        arg: dict
            Dictionary with strings that indicates the type of event received
            from the 3D view.
        """

        print(arg)

        if arg["Type"] == "SoKeyboardEvent" and arg["Key"] == "ESCAPE":
            self.finish()

        elif arg["Type"] == "SoLocation2Event":
            self.point, ctrlPoint, self.info = gui_tool_utils.getPoint(self, arg)
            gui_tool_utils.redraw3DView()

        elif (arg["Type"] == "SoMouseButtonEvent" and
              arg["State"] == "DOWN" and
              arg["Button"] == "BUTTON1"):

            if arg["Position"] == self.pos:
                return self.finish(False, cont=True)

            if (not self.node) and (not self.support):
                gui_tool_utils.getSupport(arg)
                self.point, ctrlPoint, self.info = gui_tool_utils.getPoint(self, arg)
                print(gui_tool_utils.getPoint(self, arg))

            if self.point:
                self.point = FreeCAD.Vector(self.info["x"], self.info["y"], self.info["z"])
                # self.ui.redraw()
                self.pos = arg["Position"]
                self.node.append(self.point)
                self.drawSegment(self.point)
                if len(self.node) > 2:
                    # The wire is closed
                    if (self.point - self.node[0]).Length < utils.tolerance():
                        self.undolast()
                        if len(self.node) > 2:
                            self.finish(True, cont=True)
                        else:
                            self.finish(False, cont=True)

    def finish(self, closed=False, cont=False):
        """Terminate the operation and close the polyline if asked.

        Parameters
        ----------
        closed: bool, optional
            Close the line if `True`.
        """
        self.removeTemporaryObject()
        if self.oldWP:
            App.DraftWorkingPlane = self.oldWP
            if hasattr(Gui, "Snapper"):
                Gui.Snapper.setGrid()
                Gui.Snapper.restack()
        self.oldWP = None

        if len(self.node) > 1:

            if True:
                FreeCADGui.addModule("Draft")
                # The command to run is built as a series of text strings
                # to be committed through the `draftutils.todo.ToDo` class.
                if (len(self.node) == 2
                        and utils.getParam("UsePartPrimitives", False)):
                    # Insert a Part::Primitive object
                    p1 = self.node[0]
                    p2 = self.node[-1]

                    _cmd = 'FreeCAD.ActiveDocument.'
                    _cmd += 'addObject("Part::Line", "Line")'
                    _cmd_list = ['line = ' + _cmd,
                                 'line.X1 = ' + str(p1.x),
                                 'line.Y1 = ' + str(p1.y),
                                 'line.Z1 = ' + str(p1.z),
                                 'line.X2 = ' + str(p2.x),
                                 'line.Y2 = ' + str(p2.y),
                                 'line.Z2 = ' + str(p2.z),
                                 'Draft.autogroup(line)',
                                 'FreeCAD.ActiveDocument.recompute()']
                    self.commit(translate("draft", "Create Line"),
                                _cmd_list)
                else:
                    # Insert a Draft line
                    rot, sup, pts, fil = self.getStrings()

                    _base = DraftVecUtils.toString(self.node[0])
                    _cmd = 'Draft.makeWire'
                    _cmd += '('
                    _cmd += 'points, '
                    _cmd += 'placement=pl, '
                    _cmd += 'closed=' + str(closed) + ', '
                    _cmd += 'face=' + fil + ', '
                    _cmd += 'support=' + sup
                    _cmd += ')'
                    _cmd_list = ['pl = FreeCAD.Placement()',
                                 'pl.Rotation.Q = ' + rot,
                                 'pl.Base = ' + _base,
                                 'points = ' + pts,
                                 'line = ' + _cmd,
                                 'Draft.autogroup(line)',
                                 'FreeCAD.ActiveDocument.recompute()']
                    self.commit(translate("draft", "Create Wire"),
                                _cmd_list)
            else:
                import Draft
                self.path = Draft.makeWire(self.node, closed=False, face=False)

        if self.ui and self.ui.continueMode:
            self.Activated()

        self.makeTrench()

    def removeTemporaryObject(self):
        """Remove temporary object created."""
        if self.obj:
            try:
                old = self.obj.Name
            except ReferenceError:
                # object already deleted, for some reason
                pass
            else:
                todo.ToDo.delay(self.doc.removeObject, old)
        self.obj = None

    def undolast(self):
        """Undoes last line segment."""
        import Part
        if len(self.node) > 1:
            self.node.pop()
            # last = self.node[-1]
            if self.obj.Shape.Edges:
                edges = self.obj.Shape.Edges
                if len(edges) > 1:
                    newshape = Part.makePolygon(self.node)
                    self.obj.Shape = newshape
                else:
                    self.obj.ViewObject.hide()
                # DNC: report on removal
                # _msg(translate("draft", "Removing last point"))
                _msg(translate("draft", "Pick next point"))

    def drawSegment(self, point):
        """Draws new line segment."""
        import Part
        if self.planetrack and self.node:
            self.planetrack.set(self.node[-1])
        if len(self.node) == 1:
            _msg(translate("draft", "Pick next point"))
        elif len(self.node) == 2:
            last = self.node[len(self.node) - 2]
            newseg = Part.LineSegment(last, point).toShape()
            self.obj.Shape = newseg
            self.obj.ViewObject.Visibility = True
            _msg(translate("draft", "Pick next point"))
        else:
            currentshape = self.obj.Shape.copy()
            last = self.node[len(self.node) - 2]
            if not DraftVecUtils.equals(last, point):
                newseg = Part.LineSegment(last, point).toShape()
                newshape = currentshape.fuse(newseg)
                self.obj.Shape = newshape
            _msg(translate("draft", "Pick next point"))

    def wipe(self):
        """Remove all previous segments and starts from last point."""
        if len(self.node) > 1:
            # self.obj.Shape.nullify()  # For some reason this fails
            self.obj.ViewObject.Visibility = False
            self.node = [self.node[-1]]
            if self.planetrack:
                self.planetrack.set(self.node[0])
            _msg(translate("draft", "Pick next point"))

    def numericInput(self, numx, numy, numz):
        """Validate the entry fields in the user interface.

        This function is called by the toolbar or taskpanel interface
        when valid x, y, and z have been entered in the input fields.
        """
        self.point = App.Vector(numx, numy, numz)
        self.node.append(self.point)
        self.drawSegment(self.point)
        self.ui.setNextFocus()

    def makeTrench(self):
        makeTrench(self.path)

    def addLayer(self):
        num = self.form.listLayers.count() + 1
        self.form.listLayers.addItem("Layer" + str(num))
        # TODO: add property to obj
        layer = "Layer" + str(num)
        self.obj.addProperty("App::PropertyIntegerList",
                             "Name",
                             layer,
                             layer + " Name"
                             )
        setattr(self.obj, "Name", layer)

        self.obj.addProperty("App::PropertyIntegerList",
                             "Description",
                             layer,
                             layer + " description"
                             )

        self.obj.addProperty("App::PropertyIntegerList",
                             "Height",
                             layer,
                             layer + " Height"
                             )
        setattr(self.obj, "Heigth", 100)

    def removeLayer(self):
        # TODO: remove property to obj
        currentRow = self.form.listLayers.currentRow()
        currentItem = self.form.listLayers.takeItem(currentRow)
        del(currentItem)

    def moveUp(self):
        currentRow = self.form.listLayers.currentRow()
        currentItem = self.form.listLayers.takeItem(currentRow)
        self.form.listLayers.insertItem(currentRow - 1, currentItem)

    def moveDown(self):
        currentRow = self.form.listLayers.currentRow()
        currentItem = self.form.listLayers.takeItem(currentRow)
        self.form.listLayers.insertItem(currentRow + 1, currentItem)

    def accept(self):
        self.closingForm()
        return True

    def reject(self):
        if self.new:
            FreeCAD.ActiveDocument.removeObject(self.obj.Name)
        self.closingForm()
        return True

    def closingForm(self):
        self.view.removeEventCallback("SoEvent", self.call)
        FreeCADGui.Control.closeDialog()






class _CommandTrench_V0(gui_base_original.Creator):
    """Gui command for the Line tool."""

    def __init__(self):
        gui_base_original.Creator.__init__(self)
        self.path = None

    def GetResources(self):
        """Set icon, menu and tooltip."""
        return {'Pixmap': str(os.path.join(DirIcons, "trench.svg")),
                'MenuText': QtCore.QT_TRANSLATE_NOOP("PVPlantTrench", "Trench"),
                'Accel': "C, T",
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("PVPlantTrench",
                                                    "Creates a Trench object from setup dialog.")}

    def Activated(self, name=translate("draft", "Line")):
        """Execute when the command is called."""
        # super(_CommandTrench, self).Activated(name)
        gui_base_original.Creator.Activated(self, name=translate("draft", "Line"))

        if not self.doc:
            return
        self.obj = None  # stores the temp shape
        self.oldWP = None  # stores the WP if we modify it

        """
        if sys.version_info.major < 3:
            if isinstance(self.featureName, unicode):
                self.featureName = self.featureName.encode("utf8")
        """

        sel = FreeCADGui.Selection.getSelection()
        done = False
        self.existing = []
        if len(sel) > 0:
            print("Crear una zanja desde un objeto wire existente")
            # TODO: buscar por el primer "WIRE" en los objetos seleccionados
            import Draft
            if Draft.getType(sel[0]) == "Wire":
                self.path = sel[0]
                done = True

        if not done:
            self.ui.wireUi(name)
            self.ui.setTitle("Trench")
            self.obj = self.doc.addObject("Part::Feature", self.featureName)
            gui_utils.format_object(self.obj)

            self.call = self.view.addEventCallback("SoEvent", self.action)
            _msg(translate("draft", "Pick first point"))

    def action(self, arg):
        """Handle the 3D scene events.

        This is installed as an EventCallback in the Inventor view.

        Parameters
        ----------
        arg: dict
            Dictionary with strings that indicates the type of event received
            from the 3D view.
        """

        print(arg)

        if arg["Type"] == "SoKeyboardEvent" and arg["Key"] == "ESCAPE":
            self.finish()

        elif arg["Type"] == "SoLocation2Event":
            self.point, ctrlPoint, self.info = gui_tool_utils.getPoint(self, arg)
            gui_tool_utils.redraw3DView()

        elif (arg["Type"] == "SoMouseButtonEvent" and
              arg["State"] == "DOWN" and
              arg["Button"] == "BUTTON1"):

            if arg["Position"] == self.pos:
                return self.finish(False, cont=True)

            if (not self.node) and (not self.support):
                gui_tool_utils.getSupport(arg)
                self.point, ctrlPoint, self.info = gui_tool_utils.getPoint(self, arg)
                print(gui_tool_utils.getPoint(self, arg))

            if self.point:
                self.point = FreeCAD.Vector(self.info["x"], self.info["y"], self.info["z"])
                self.ui.redraw()
                self.pos = arg["Position"]
                self.node.append(self.point)
                self.drawSegment(self.point)
                if len(self.node) > 2:
                    # The wire is closed
                    if (self.point - self.node[0]).Length < utils.tolerance():
                        self.undolast()
                        if len(self.node) > 2:
                            self.finish(True, cont=True)
                        else:
                            self.finish(False, cont=True)

    def finish(self, closed=False, cont=False):
        """Terminate the operation and close the polyline if asked.

        Parameters
        ----------
        closed: bool, optional
            Close the line if `True`.
        """
        self.removeTemporaryObject()
        if self.oldWP:
            App.DraftWorkingPlane = self.oldWP
            if hasattr(Gui, "Snapper"):
                Gui.Snapper.setGrid()
                Gui.Snapper.restack()
        self.oldWP = None

        if len(self.node) > 1:

            if False:
                Gui.addModule("Draft")
                # The command to run is built as a series of text strings
                # to be committed through the `draftutils.todo.ToDo` class.
                if (len(self.node) == 2
                        and utils.getParam("UsePartPrimitives", False)):
                    # Insert a Part::Primitive object
                    p1 = self.node[0]
                    p2 = self.node[-1]

                    _cmd = 'FreeCAD.ActiveDocument.'
                    _cmd += 'addObject("Part::Line", "Line")'
                    _cmd_list = ['line = ' + _cmd,
                                 'line.X1 = ' + str(p1.x),
                                 'line.Y1 = ' + str(p1.y),
                                 'line.Z1 = ' + str(p1.z),
                                 'line.X2 = ' + str(p2.x),
                                 'line.Y2 = ' + str(p2.y),
                                 'line.Z2 = ' + str(p2.z),
                                 'Draft.autogroup(line)',
                                 'FreeCAD.ActiveDocument.recompute()']
                    self.commit(translate("draft", "Create Line"),
                                _cmd_list)
                else:
                    # Insert a Draft line
                    rot, sup, pts, fil = self.getStrings()

                    _base = DraftVecUtils.toString(self.node[0])
                    _cmd = 'Draft.makeWire'
                    _cmd += '('
                    _cmd += 'points, '
                    _cmd += 'placement=pl, '
                    _cmd += 'closed=' + str(closed) + ', '
                    _cmd += 'face=' + fil + ', '
                    _cmd += 'support=' + sup
                    _cmd += ')'
                    _cmd_list = ['pl = FreeCAD.Placement()',
                                 'pl.Rotation.Q = ' + rot,
                                 'pl.Base = ' + _base,
                                 'points = ' + pts,
                                 'line = ' + _cmd,
                                 'Draft.autogroup(line)',
                                 'FreeCAD.ActiveDocument.recompute()']
                    self.commit(translate("draft", "Create Wire"),
                                _cmd_list)
            else:
                import Draft
                self.path = Draft.makeWire(self.node, closed=False, face=False)

        # super(_CommandTrench, self).finish()
        gui_base_original.Creator.finish(self)
        if self.ui and self.ui.continueMode:
            self.Activated()

        self.makeTrench()

    def makeTrench(self):
        makeTrench(self.path)

    def removeTemporaryObject(self):
        """Remove temporary object created."""
        if self.obj:
            try:
                old = self.obj.Name
            except ReferenceError:
                # object already deleted, for some reason
                pass
            else:
                todo.ToDo.delay(self.doc.removeObject, old)
        self.obj = None

    def undolast(self):
        """Undoes last line segment."""
        import Part
        if len(self.node) > 1:
            self.node.pop()
            # last = self.node[-1]
            if self.obj.Shape.Edges:
                edges = self.obj.Shape.Edges
                if len(edges) > 1:
                    newshape = Part.makePolygon(self.node)
                    self.obj.Shape = newshape
                else:
                    self.obj.ViewObject.hide()
                # DNC: report on removal
                # _msg(translate("draft", "Removing last point"))
                _msg(translate("draft", "Pick next point"))

    def drawSegment(self, point):
        """Draws new line segment."""
        import Part
        if self.planetrack and self.node:
            self.planetrack.set(self.node[-1])
        if len(self.node) == 1:
            _msg(translate("draft", "Pick next point"))
        elif len(self.node) == 2:
            last = self.node[len(self.node) - 2]
            newseg = Part.LineSegment(last, point).toShape()
            self.obj.Shape = newseg
            self.obj.ViewObject.Visibility = True
            _msg(translate("draft", "Pick next point"))
        else:
            currentshape = self.obj.Shape.copy()
            last = self.node[len(self.node) - 2]
            if not DraftVecUtils.equals(last, point):
                newseg = Part.LineSegment(last, point).toShape()
                newshape = currentshape.fuse(newseg)
                self.obj.Shape = newshape
            _msg(translate("draft", "Pick next point"))

    def wipe(self):
        """Remove all previous segments and starts from last point."""
        if len(self.node) > 1:
            # self.obj.Shape.nullify()  # For some reason this fails
            self.obj.ViewObject.Visibility = False
            self.node = [self.node[-1]]
            if self.planetrack:
                self.planetrack.set(self.node[0])
            _msg(translate("draft", "Pick next point"))

    def orientWP(self):
        """Orient the working plane."""
        import DraftGeomUtils
        if hasattr(App, "DraftWorkingPlane"):
            if len(self.node) > 1 and self.obj:
                n = DraftGeomUtils.getNormal(self.obj.Shape)
                if not n:
                    n = App.DraftWorkingPlane.axis
                p = self.node[-1]
                v = self.node[-2].sub(self.node[-1])
                v = v.negative()
                if not self.oldWP:
                    self.oldWP = App.DraftWorkingPlane.copy()
                App.DraftWorkingPlane.alignToPointAndAxis(p, n, upvec=v)
                if hasattr(Gui, "Snapper"):
                    Gui.Snapper.setGrid()
                    Gui.Snapper.restack()
                if self.planetrack:
                    self.planetrack.set(self.node[-1])

    def numericInput(self, numx, numy, numz):
        """Validate the entry fields in the user interface.

        This function is called by the toolbar or taskpanel interface
        when valid x, y, and z have been entered in the input fields.
        """
        self.point = App.Vector(numx, numy, numz)
        self.node.append(self.point)
        self.drawSegment(self.point)
        self.ui.setNextFocus()


class _CommandTrench:  # V1:
    """Gui command for the Line tool."""

    def GetResources(self):
        """Set icon, menu and tooltip."""
        return {'Pixmap': str(os.path.join(DirIcons, "trench.svg")),
                'MenuText': "Trench",
                'Accel': "C, T",
                'ToolTip': "Creates a Trench object from setup dialog."}

    def IsActive(self):
        if FreeCAD.ActiveDocument:
            return True
        else:
            return False

    def Activated(self):
        """Execute when the command is called."""

        sel = FreeCADGui.Selection.getSelection()
        done = False

        if len(sel) > 0:
            print("Crear una zanja desde un objeto wire existente")
            # TODO: buscar por el primer "WIRE" en los objetos seleccionados
            import Draft
            if Draft.getType(sel[0]) == "Wire":
                path = sel[0]
                makeTrench(path)
                done = True

        if not done:
            taskd = _TrenchTaskPanel()
            if taskd:
                FreeCADGui.Control.showDialog(taskd)
            else:
                print(" No ha sido posible crear el formulario")


if FreeCAD.GuiUp:
    FreeCADGui.addCommand('PVPlantTrench', _CommandTrench())
