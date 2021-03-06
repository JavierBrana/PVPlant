import FreeCAD, Draft
import ArchComponent
import wire3D

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


class _Trench(ArchComponent.Component):
    def __init__(self, obj):
        # Definición de Variables:
        ArchComponent.Component.__init__(self, obj)
        self.obj = obj
        self.setProperties(obj)
        self.Type = "Trench"
        obj.Proxy = self

        self.route = False

        obj.IfcType = "Civil Element"  ## puede ser: Cable Carrier Segment
        obj.setEditorMode("IfcType", 1)


        self.count = 0

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

        obj.addProperty("App::PropertyLength",
                        "Width",
                        "Trench",
                        QT_TRANSLATE_NOOP("App::Property", "Connection")).Width = 300

        obj.addProperty("App::PropertyLength",
                        "Height",
                        "Trench",
                        QT_TRANSLATE_NOOP("App::Property", "Connection")).Height = 700

        obj.addProperty("App::PropertyLength",
                        "Sand_Height",
                        "Trench",
                        QT_TRANSLATE_NOOP("App::Property", "Connection")).Sand_Height = 400

    def onDocumentRestored(self, obj):
        """Method run when the document is restored.
        Re-adds the Arch component, and object properties."""

        ArchComponent.Component.onDocumentRestored(self, obj)
        self.obj = obj
        self.Type = "Trench"
        obj.Proxy = self

    def execute(self, obj):
        import Part, DraftGeomUtils, math
        import Draft

        self.count += 1
        print("         ########     Trench - execute: ", self.count)

        w = None
        w = obj.Base.Shape
        land = FreeCAD.ActiveDocument.Shape
        w = land.Shape.makeParallelProjection(obj.Base.Shape, FreeCAD.Vector(0, 0, 1))
        po = []
        for ver in w.Vertexes:
            po.append(ver.Point)
        #w = w.Wires[0]
        w = Draft.makeWire(po)
        FreeCAD.ActiveDocument.recompute()


        vec_down_left = FreeCAD.Vector(-obj.Width.Value / 2, 0, -obj.Height.Value)
        vec_down_right = FreeCAD.Vector(obj.Width.Value / 2, 0, -obj.Height.Value)
        vec_up_left = FreeCAD.Vector(-obj.Width.Value / 2, 0, 0)
        vec_up_right = FreeCAD.Vector(obj.Width.Value / 2, 0, 0)
        vec_sand_left = FreeCAD.Vector(-obj.Width.Value / 2, 0, -obj.Height.Value + obj.Sand_Height.Value)
        vec_sand_right = FreeCAD.Vector(obj.Width.Value / 2, 0, -obj.Height.Value + obj.Sand_Height.Value)

        edge1 = Part.makeLine(vec_down_left, vec_down_right)
        edge2 = Part.makeLine(vec_down_right, vec_up_right)
        edge3 = Part.makeLine(vec_up_right, vec_up_left)
        edge4 = Part.makeLine(vec_up_left, vec_down_left)
        p = Part.Wire([edge1, edge2, edge3, edge4])

        # 1. Perfil original del cual salen todos los demás:
        #p = Part.makePolygon([vec_down_left, vec_down_right, vec_up_right])

        shapes = []
        usenew = False

        if usenew:
            profiles = []
            c = p.CenterOfMass #(vec_up_right + vec_up_left) / 2
            for ed in w.Edges:
                p1 = p.copy()
                delta = ed.CenterOfMass - c
                p1.translate(delta)

                if Draft.getType(obj.Base) == "BezCurve":
                    v1 = obj.Base.Placement.multVec(obj.Base.Points[1]) - w.Vertexes[0].Point
                else:
                    v1 = ed.Vertexes[1].Point - ed.Vertexes[0].Point

                v2 = DraftGeomUtils.getNormal(p1)
                rot = FreeCAD.Rotation(v2, v1)
                print (" +++++ rot: ", rot.toEuler())
                #p1.rotate(ed.CenterOfMass, rot.Axis, math.degrees(rot.Angle))
                p1.Placement.Rotation = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), rot.toEuler()[0])

                profiles.append(p1)
                Part.show(p1, "Perfil")

            for ind in range(len(w.Edges) - 1):
                e1 = w.Edges[ind]
                e2 = w.Edges[ind + 1]

                vec1 = e1.Vertexes[1].Point - e1.Vertexes[0].Point
                vec1.normalize()
                vec2 = e2.Vertexes[1].Point - e2.Vertexes[0].Point
                vec2.normalize()
                vec3 = vec1.add(vec2)
                plane = Part.Plane(e1.Vertexes[1].Point, vec3)
                plane = Part.makePlane(10000,10000, e1.Vertexes[1].Point, vec3)
                plane.translate(e1.Vertexes[1].Point - plane.CenterOfMass)
                Part.show(plane)

                myWiresOut3 = []
                for w in p.Wires:
                    newWire = plane.makeParallelProjection(w, vec1)
                    myWiresOut3.append(newWire)
                print(myWiresOut3)
                Part.show(myWiresOut3)
                #f_new = Part.Wire(myWiresOut3)
                #Part.show(f_new)

                profiles.append(p1)
                Part.show(p1, "Perfil")


            if p.Faces:
                for f in p.Faces:
                    sh = w.makePipeShell([f.OuterWire], True, False, 2)
                    for shw in f.Wires:
                        if shw.hashCode() != f.OuterWire.hashCode():
                            sh2 = w.makePipeShell([shw], True, False, 2)
                            sh = sh.cut(sh2)
                    shapes.append(sh)
            elif p.Wires:
                for pw in p.Wires:
                    sh = w.makePipeShell(profiles, True, False, 2)
                    shapes.append(sh)
        else:
            if hasattr(p, "CenterOfMass"):
                c = p.CenterOfMass
            else:
                c = p.BoundBox.Center
            c = (vec_up_right + vec_up_left) / 2
            delta = w.Vertexes[0].Point - c
            p.translate(delta)

            if Draft.getType(obj.Base) == "BezCurve":
                v1 = obj.Base.Placement.multVec(obj.Base.Points[1]) - w.Vertexes[0].Point
            else:
                v1 = w.Vertexes[1].Point - w.Vertexes[0].Point
            v2 = DraftGeomUtils.getNormal(p)
            rot = FreeCAD.Rotation(v2, v1)
            print (rot, " - ", math.degrees(rot.Angle))
            #p.rotate(w.Vertexes[0].Point, rot.Axis, math.degrees(rot.Angle))
            ang = rot.toEuler()[0]
            p.Placement.Rotation = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), ang)

            Part.show(p, "UN_Perfil")

            if p.Faces:
                for f in p.Faces:
                    sh = w.makePipeShell([f.OuterWire], True, False, 2)
                    for shw in f.Wires:
                        if shw.hashCode() != f.OuterWire.hashCode():
                            sh2 = w.makePipeShell([shw], True, False, 2)
                            sh = sh.cut(sh2)
                    shapes.append(sh)
            elif p.Wires:
                for pw in p.Wires:
                    sh = w.makePipeShell([pw], True, False, 1)
                    shapes.append(sh)

        obj.Shape = Part.makeCompound(shapes)


class _ViewProviderTrench(ArchComponent.ViewProviderComponent):
    def __init__(self, vobj):
        ArchComponent.ViewProviderComponent.__init__(self, vobj)

    def getIcon(self):
        return str(os.path.join(PVPlantResources.DirIcons, "trench.svg"))

class _TrenchTaskPanel:

    def __init__(self, obj=None):

        if obj is None:
            self.new = True
            self.obj = makeTrench()
        else:
            self.new = False
            self.obj = obj

        self.form = FreeCADGui.PySideUic.loadUi(os.path.join(PVPlantResources.__dir__, "PVPlantTrench.ui"))

    def accept(self):
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


class _CommandTrench(gui_base_original.Creator):
    """Gui command for the Line tool."""

    def __init__(self):
        # super(_CommandTrench, self).__init__()
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

        '''
        if sys.version_info.major < 3:
            if isinstance(self.featureName, unicode):
                self.featureName = self.featureName.encode("utf8")
        '''

        sel = FreeCADGui.Selection.getSelection()
        done = False
        self.existing = []
        if len(sel) > 0:
            print("Crear una zanja desde un objeto wire existente")
            # TODO: chequear que el objeto seleccionado sea un "wire"
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
        if arg["Type"] == "SoKeyboardEvent" and arg["Key"] == "ESCAPE":
            self.finish()
        elif arg["Type"] == "SoLocation2Event":
            self.point, ctrlPoint, self.info = gui_tool_utils.getPoint(self, arg)
            gui_tool_utils.redraw3DView()
        elif (arg["Type"] == "SoMouseButtonEvent"
              and arg["State"] == "DOWN"
              and arg["Button"] == "BUTTON1"):
            if arg["Position"] == self.pos:
                return self.finish(False, cont=True)
            if (not self.node) and (not self.support):
                gui_tool_utils.getSupport(arg)
                self.point, ctrlPoint, self.info = gui_tool_utils.getPoint(self, arg)

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


if FreeCAD.GuiUp:
    FreeCADGui.addCommand('PVPlantTrench', _CommandTrench())
