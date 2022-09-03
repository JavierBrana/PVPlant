import FreeCAD
import ArchComponent

if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore, QtGui, QtSvg
    from PySide.QtCore import QT_TRANSLATE_NOOP
    import PySide.QtGui as QtGui
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

import os
from PVPlantResources import DirIcons as DirIcons


def makeFencePost(diameter=48, length=3000, placement=None, name="Post"):
    "makePipe([baseobj,diamerter,length,placement,name]): creates an pipe object from the given base object"

    if not FreeCAD.ActiveDocument:
        FreeCAD.Console.PrintError("No active document. Aborting\n")
        return

    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", name)
    obj.Label = name
    _FencePost(obj)

    if FreeCAD.GuiUp:
        _ViewProviderFencePost(obj.ViewObject)

    obj.Length = length
    obj.Diameter = diameter

    if placement:
        obj.Placement = placement
    return obj


def makeFenceReinforcePost(diameter=48, length=3000, placement=None, name="Post"):
    "makePipe([baseobj,diamerter,length,placement,name]): creates an pipe object from the given base object"

    if not FreeCAD.ActiveDocument:
        FreeCAD.Console.PrintError("No active document. Aborting\n")
        return

    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", name)
    obj.Label = name
    _FenceReinforcePostPost(obj)

    if FreeCAD.GuiUp:
        _ViewProviderFencePost(obj.ViewObject)

    obj.Length = length
    obj.Diameter = diameter

    if placement:
        obj.Placement = placement
    return obj


class _FencePost(ArchComponent.Component):
    def __init__(self, obj):
        ArchComponent.Component.__init__(self, obj)
        self.setProperties(obj)
        obj.IfcType = "Pipe Segment"
        self.Type = "FencePost"

    def setProperties(self, obj):

        pl = obj.PropertiesList
        if not "Diameter" in pl:
            obj.addProperty("App::PropertyLength", "Diameter", "Pipe",
                            QT_TRANSLATE_NOOP("App::Property", "The diameter of this pipe, if not based on a profile")
                            ).Diameter = 48
        if not "Thickness" in pl:
            obj.addProperty("App::PropertyLength", "Thickness", "Pipe",
                            QT_TRANSLATE_NOOP("App::Property", "The Thickness of this pipe, if not based on a profile")
                            ).Thickness = 4
        if not "Length" in pl:
            obj.addProperty("App::PropertyLength", "Length", "Pipe",
                            QT_TRANSLATE_NOOP("App::Property", "The length of this pipe, if not based on an edge")
                            ).Length = 3000

    def onDocumentRestored(self, obj):

        ArchComponent.Component.onDocumentRestored(self, obj)
        self.setProperties(obj)

    def execute(self, obj):
        import Part
        pl = obj.Placement

        if obj.CloneOf:
            obj.Shape = obj.CloneOf.Shape
        else:
            w = self.getProfile(obj)
            try:
                # sh = w.makePipeShell([p], True, False, 2)
                sh = w.revolve(FreeCAD.Vector(0.0, 0.0, 0.0), FreeCAD.Vector(0.0, 0.0, 1.0), 360)
                sh = Part.Solid(sh)
            except:
                FreeCAD.Console.PrintError("Unable to build the pipe \n")
            else:
                obj.Shape = sh
        obj.Placement = pl

        return

        #       -------------------------  Prueba para apoyos de refuerzo:
        import math
        L = math.pi / 2 * (obj.Diameter.Value - 2 * obj.Thickness.Value)

        v1 = FreeCAD.Vector(L / 2, 0, obj.Thickness.Value)
        vc1 = FreeCAD.Vector(L / 2 + obj.Thickness.Value, 0, 0)
        v2 = FreeCAD.Vector(L / 2, 0, -obj.Thickness.Value)

        v11 = FreeCAD.Vector(-L / 2, 0, obj.Thickness.Value)
        vc11 = FreeCAD.Vector(-(L / 2 + obj.Thickness.Value), 0, 0)
        v21 = FreeCAD.Vector(-L / 2, 0, -obj.Thickness.Value)

        arc1 = Part.Arc(v1, vc1, v2).toShape()
        arc11 = Part.Arc(v11, vc11, v21).toShape()
        line1 = Part.LineSegment(v11, v1).toShape()
        line2 = Part.LineSegment(v21, v2).toShape()
        w = Part.Wire([arc1, line2, arc11, line1])
        face = Part.Face(w)
        pro = face.extrude(FreeCAD.Vector(0, 40, 0))

        #Part.Circle(Center, Normal, Radius)
        cir1 = Part.Face(Part.Wire(Part.Circle(FreeCAD.Vector(0, -200, 0), FreeCAD.Vector(0, 1, 0), obj.Diameter.Value / 2).toShape()))
        ext = cir1.extrude(FreeCAD.Vector(0, 170, 0))
        cir2 = Part.Circle(FreeCAD.Vector(0, -30, 0), FreeCAD.Vector(0, 1, 0), obj.Diameter.Value/2).toShape()
        loft = Part.makeLoft([cir2, w], True)
        ext = ext.fuse([loft, pro])
        Part.show(ext)


    def getProfile(self, obj):
        import Part
        sin45 = 0.707106781
        radio = obj.Diameter.Value / 2
        taph = 20
        tapw = radio + 2
        chamfer = 5
        chamfer2 = chamfer * sin45

        edge1 = Part.makeLine(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(radio, 0, 0))
        edge2 = Part.makeLine(FreeCAD.Vector(radio, 0, 0), FreeCAD.Vector(radio, 0, obj.Length.Value - taph))
        edge3 = Part.makeLine(FreeCAD.Vector(radio, 0, obj.Length.Value - taph),
                              FreeCAD.Vector(tapw, 0, obj.Length.Value - taph))
        edge4 = Part.makeLine(FreeCAD.Vector(tapw, 0, obj.Length.Value - taph),
                              FreeCAD.Vector(tapw, 0, obj.Length.Value - chamfer))
        if True:
            edge5 = Part.makeLine(FreeCAD.Vector(tapw, 0, obj.Length.Value - chamfer),
                                  FreeCAD.Vector(tapw - chamfer, 0, obj.Length.Value))
        else:
            edge5 = Part.Arc(FreeCAD.Vector(tapw, 0, obj.Length.Value - chamfer),
                             FreeCAD.Vector(tapw - chamfer2, 0, obj.Length.Value - chamfer2),
                             FreeCAD.Vector(tapw - chamfer, 0, obj.Length.Value)
                             ).toShape()
        edge6 = Part.makeLine(FreeCAD.Vector(tapw - chamfer, 0, obj.Length.Value),
                              FreeCAD.Vector(0, 0, obj.Length.Value))
        w = Part.Wire([edge1, edge2, edge3, edge4, edge5, edge6])

        return w


class _FenceReinforcePost(ArchComponent.Component):
    def __init__(self, obj):
        ArchComponent.Component.__init__(self, obj)
        self.setProperties(obj)
        obj.IfcType = "Pipe Segment"
        self.Type = "FencePost"

    def setProperties(self, obj):

        pl = obj.PropertiesList
        if not "Diameter" in pl:
            obj.addProperty("App::PropertyLength", "Diameter", "Pipe",
                            QT_TRANSLATE_NOOP("App::Property", "The diameter of this pipe, if not based on a profile")
                            ).Diameter = 48
        if not "Length" in pl:
            obj.addProperty("App::PropertyLength", "Length", "Pipe",
                            QT_TRANSLATE_NOOP("App::Property", "The length of this pipe, if not based on an edge")
                            ).Length = 3000
        self.Type = "Pipe"

    def onDocumentRestored(self, obj):

        ArchComponent.Component.onDocumentRestored(self, obj)
        self.setProperties(obj)

    def execute(self, obj):

        import Part, DraftGeomUtils, math
        pl = obj.Placement
        w = self.getWire(obj)

        try:
            # sh = w.makePipeShell([p], True, False, 2)
            sh = w.revolve(FreeCAD.Vector(0.0, 0.0, 0.0), FreeCAD.Vector(0.0, 0.0, 1.0), 360)
        except:
            FreeCAD.Console.PrintError(translate("Arch", "Unable to build the pipe") + "\n")
        else:
            obj.Shape = sh
            obj.Placement = pl

    def getWire(self, obj):

        import Part
        sin45 = 0.707106781
        radio = obj.Diameter.Value / 2
        taph = 20
        tapw = radio + 2
        chamfer = 5
        chamfer2 = chamfer * sin45

        edge1 = Part.makeLine(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(radio, 0, 0))
        edge2 = Part.makeLine(FreeCAD.Vector(radio, 0, 0), FreeCAD.Vector(radio, 0, obj.Length.Value - taph))
        edge3 = Part.makeLine(FreeCAD.Vector(radio, 0, obj.Length.Value - taph),
                              FreeCAD.Vector(tapw, 0, obj.Length.Value - taph))
        edge4 = Part.makeLine(FreeCAD.Vector(tapw, 0, obj.Length.Value - taph),
                              FreeCAD.Vector(tapw, 0, obj.Length.Value - chamfer))

        if True:
            edge5 = Part.makeLine(FreeCAD.Vector(tapw, 0, obj.Length.Value - chamfer),
                                  FreeCAD.Vector(tapw - chamfer, 0, obj.Length.Value))
        else:
            edge5 = Part.Arc(FreeCAD.Vector(tapw, 0, obj.Length.Value - chamfer),
                             FreeCAD.Vector(tapw - chamfer2, 0, obj.Length.Value - chamfer2),
                             FreeCAD.Vector(tapw - chamfer, 0, obj.Length.Value)
                             ).toShape()
        edge6 = Part.makeLine(FreeCAD.Vector(tapw - chamfer, 0, obj.Length.Value),
                              FreeCAD.Vector(0, 0, obj.Length.Value))
        w = Part.Wire([edge1, edge2, edge3, edge4, edge5, edge6])

        return w


class _ViewProviderFencePost(ArchComponent.ViewProviderComponent):
    "A View Provider for the Pipe object"

    def __init__(self, vobj):
        ArchComponent.ViewProviderComponent.__init__(self, vobj)

    def getIcon(self):
        import Arch_rc
        return ":/icons/Arch_Pipe_Tree.svg"


class _CommandFencePost:
    "the Arch Pipe command definition"

    def GetResources(self):

        return {'Pixmap': 'Arch_Pipe',
                'MenuText': QT_TRANSLATE_NOOP("Arch_Pipe", "Pipe"),
                'Accel': "P, I",
                'ToolTip': QT_TRANSLATE_NOOP("Arch_Pipe", "Creates a pipe object from a given Wire or Line")}

    def IsActive(self):

        return not FreeCAD.ActiveDocument is None

    def Activated(self):
        if True:
            makeFencePost()
        else:
            FreeCAD.ActiveDocument.openTransaction(translate("Arch", "Create Pipe"))
            FreeCADGui.addModule("Arch")
            FreeCADGui.doCommand("obj = Arch.makePipe()")
            FreeCADGui.addModule("Draft")
            FreeCADGui.doCommand("Draft.autogroup(obj)")
            FreeCAD.ActiveDocument.commitTransaction()
        FreeCAD.ActiveDocument.recompute()


if FreeCAD.GuiUp:
    FreeCADGui.addCommand('FencePost', _CommandFencePost())
