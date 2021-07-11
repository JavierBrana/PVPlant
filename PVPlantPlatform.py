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


def makePlatform(base=None):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Platform")
    _Platform(obj)
    _ViewProviderPlatform(obj.ViewObject)
    obj.Base = base
    FreeCAD.ActiveDocument.recompute()
    return obj


class _Platform(ArchComponent.Component):
    def __init__(self, obj):
        # Definición de Variables:
        ArchComponent.Component.__init__(self, obj)
        self.obj = obj
        self.base = None

        self.setProperties(obj)
        self.Type = "Pad"

        obj.Proxy = self
        obj.IfcType = "Civil Element"  ## puede ser: Cable Carrier Segment
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
        ##if not obj.Base:
        obj.addProperty("App::PropertyLength",
                        "Width",
                        "Platform",
                        QT_TRANSLATE_NOOP("App::Property", "Connection")).Width = 5000

        obj.addProperty("App::PropertyLength",
                        "Length",
                        "Platform",
                        QT_TRANSLATE_NOOP("App::Property", "Connection")).Length = 10000


        obj.addProperty("App::PropertyAngle",
                        "EmbankmentSlope",
                        "Platform",
                        QT_TRANSLATE_NOOP("App::Property", "Connection")).EmbankmentSlope = 25.00

        obj.addProperty("App::PropertyAngle",
                        "CutSlope",
                        "Platform",
                        QT_TRANSLATE_NOOP("App::Property", "Connection")).CutSlope = 60.00

        # Output values:
        obj.addProperty("App::PropertyVolume",
                        "CutVolume",
                        "Output",
                        QT_TRANSLATE_NOOP("App::Property", "Connection")).CutVolume = 0.00
        obj.setEditorMode("CutVolume", 1)

        obj.addProperty("App::PropertyVolume",
                        "FillVolume",
                        "Output",
                        QT_TRANSLATE_NOOP("App::Property", "Connection")).FillVolume = 0.00
        obj.setEditorMode("FillVolume", 1)

    def onDocumentRestored(self, obj):
        """Method run when the document is restored.
        Re-adds the Arch component, and object properties."""

        ArchComponent.Component.onDocumentRestored(self, obj)
        self.obj = obj
        self.Type = "Trench"
        obj.Proxy = self

    def onChanged(self, fp, prop):
        '''Do something when a property has changed'''


        '''
        self.changed = True

        if prop in ["MaxPhi", "MinPhi", ]:
            self.changed = False

        if prop == "Tilt":
            if not hasattr(self, "obj"):
                return
            if hasattr(self.obj, "MaxPhi"):
                if self.obj.Tilt > self.obj.MaxPhi:
                    self.obj.Tilt = self.obj.MaxPhi

                if self.obj.Tilt < self.obj.MinPhi:
                    self.obj.Tilt = self.obj.MinPhi

            compound = self.obj.Shape.SubShapes[0]
            compound.Placement.Rotation = FreeCAD.Rotation(FreeCAD.Vector(1, 0, 0), 45)
            # a = compound.rotate(base, FreeCAD.Vector(1, 0, 0), obj.Tilt)
            self.changed = True
        '''


    def execute(self, obj):
        import Part, DraftGeomUtils
        import Draft
        import math

        pl = obj.Placement.Base
        shapes = []
        base = None

        # Inicialmente hacemos una base rectangular:
        # TODO: que valga cualquier tipo de forma. Se debe seleccionar una base
        if obj.Base:
            base = obj.Base
        else:
            halfWidth = obj.Width.Value / 2
            halfLength = obj.Length.Value / 2

            p1 = FreeCAD.Vector(-halfLength, -halfWidth, 0)
            p2 = FreeCAD.Vector(halfLength, -halfWidth, 0)
            p3 = FreeCAD.Vector(halfLength, halfWidth, 0)
            p4 = FreeCAD.Vector(-halfLength, halfWidth, 0)
            base = Part.makePolygon([p1, p2, p3, p4, p1])

        # 1. Terraplén (embankment / fill):
        fill = self.createSolid(obj, base, 0)
        fill.Placement.Base += pl
        fill = self.calculateFill(obj, fill)

        # 2. Desmonte (cut):
        cut = self.createSolid(obj, base, 1)
        cut.Placement.Base += pl
        cut = self.calculateCut(obj, cut)

        if not fill and not cut:
            shapes.append(Part.Face(base))
        else:
            if fill:
                fill.Placement.Base -= pl
                shapes.append(fill)
            if cut:
                cut.Placement.Base -= pl
                shapes.append(cut)

        obj.Shape = Part.makeCompound(shapes)

    def createSolid(self, obj, base, dir = 0):
        import math
        import BOPTools.SplitAPI as splitter

        zz = FreeCAD.ActiveDocument.Site.Terrain.Shape.BoundBox.ZMin if dir == 0 \
            else FreeCAD.ActiveDocument.Site.Terrain.Shape.BoundBox.ZMax
        height = abs(zz - base.Placement.Base.z)
        angle = obj.EmbankmentSlope.Value if dir == 0 else obj.CutSlope.Value

        offset = base.Wires[0].makeOffset2D((height - 10) / math.tan(math.radians(angle)), join=0)
        offset.Placement.Base.z = zz

        offset1 = base.Wires[0].makeOffset2D(10 / math.tan(math.radians(angle)), join=0)
        offset1.Placement.Base.z = base.Placement.Base.z + (-10 if dir == 0 else 10)

        loft1 = Part.makeLoft([base, offset1], True)
        loft2 = Part.makeLoft([offset1, offset], True)
        solid = loft1.fuse(loft2)

        ''' old code. Only for rectagle pad:
        faces = []
        faces.append(Part.Face(base))
        faces.append(Part.Face(offset))
        count = -1
        lines = []
        for vertex in base.Vertexes:
            for i in range(2):
                lines.append(Part.LineSegment(vertex.Point, offset.Vertexes[count].Point))
                count += 1

        count = -1
        count1 = 0
        for i in range(len(lines)):
            if i % 2 == 0:
                line = lines[i].toShape()
                faces.append(line.revolve(line.Vertexes[0].Point, FreeCAD.Vector(0, 0, 1), 90))
            else:
                faces.append(Part.makeLoft([base.Edges[count1], offset.Edges[count]]))
                count1 += 1
            count += 1

        solid = Part.makeSolid(Part.makeShell(Part.makeCompound(faces).Faces))
        '''
        return solid

    def calculateFill(self, obj, solid):
        import BOPTools.SplitAPI as splitter

        common = solid.common(FreeCAD.ActiveDocument.Site.Terrain.Shape)
        if common.Area > 0:
            sp = splitter.slice(solid, [common, ], "Split")
            common.Placement.Base.z += 10
            for sol in sp.Solids:
                common1 = sol.common(common)
                if common1.Area > 0:
                    obj.FillVolume = sol.Volume
                    return sol
        return None

    def calculateCut(self, obj, solid):
        import BOPTools.SplitAPI as splitter

        common = solid.common(FreeCAD.ActiveDocument.Site.Terrain.Shape)
        if common.Area > 0:
            sp = splitter.slice(solid, [common, ], "Split")
            sp = sp.Solids[0]
            sp = sp.Shells[0]
            sp = sp.cut(common)
            #sp = sp.cut(solid.Faces[0])
            shell = sp.cut(common)
            obj.CutVolume = sp.Volume
            if shell:
                return  shell
        return None


class _ViewProviderPlatform(ArchComponent.ViewProviderComponent):
    def __init__(self, vobj):
        ArchComponent.ViewProviderComponent.__init__(self, vobj)

    def getIcon(self):
        return str(os.path.join(PVPlantResources.DirIcons, "platform.svg"))




class _PlatformTaskPanel:

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


class _CommandPlatform(gui_base_original.Creator):
    """Gui command for the Line tool."""

    def __init__(self):
        # super(_CommandTrench, self).__init__()
        gui_base_original.Creator.__init__(self)
        self.path = None

    def GetResources(self):
        """Set icon, menu and tooltip."""
        return {'Pixmap': str(os.path.join(DirIcons, "platform.svg")),
                'MenuText': QtCore.QT_TRANSLATE_NOOP("PVPlantPlatform", "Platform"),
                'Accel': "C, T",
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("PVPlantPlatform",
                                                    "Creates a Platform object from setup dialog.")}

    def Activated(self, name=translate("draft", "Line")):
        """Execute when the command is called."""
        makePlatform()

        return
        # super(_CommandTrench, self).Activated(name)
        gui_base_original.Creator.Activated(self, name=translate("draft", "Line"))

        if not self.doc:
            return
        self.obj = None  # stores the temp shape
        self.oldWP = None  # stores the WP if we modify it

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

        self.makePlatform()

    def makePlatform(self):
        makePlatform(self.path)

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
    FreeCADGui.addCommand('PVPlantPlatform', _CommandPlatform())
