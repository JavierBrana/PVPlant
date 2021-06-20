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

def makeFencePost(diameter = 48, length = 3000, placement = None, name = "Post"):

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

def makeFenceReinforcePost(diameter = 48, length = 3000, placement = None, name = "Post"):

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
        ArchComponent.Component.__init__(self,obj)
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

    def onDocumentRestored(self,obj):

        ArchComponent.Component.onDocumentRestored(self,obj)
        self.setProperties(obj)

    def execute(self,obj):
        pl = obj.Placement

        if obj.CloneOf:
            obj.Shape = obj.CloneOf.Shape
        else:
            w = self.getProfile(obj)
            try:
                #sh = w.makePipeShell([p], True, False, 2)
                sh = w.revolve(FreeCAD.Vector(0.0, 0.0, 0.0), FreeCAD.Vector(0.0, 0.0, 1.0), 360)

            except:
                FreeCAD.Console.PrintError(translate("PVPlant", "Unable to build the pipe")+"\n")

            else:
                obj.Shape = sh

        obj.Placement = pl

    def getProfile(self,obj):
        import Part
        sin45 = 0.707106781
        radio = obj.Diameter.Value / 2
        taph = 20
        tapw = radio + 2
        chamfer = 5
        chamfer2 = chamfer * sin45

        edge1 = Part.makeLine(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(radio, 0, 0))
        edge2 = Part.makeLine(FreeCAD.Vector(radio, 0, 0), FreeCAD.Vector(radio, 0, obj.Length.Value - taph))
        edge3 = Part.makeLine(FreeCAD.Vector(radio, 0, obj.Length.Value - taph), FreeCAD.Vector(tapw, 0, obj.Length.Value - taph))
        edge4 = Part.makeLine(FreeCAD.Vector(tapw, 0, obj.Length.Value - taph), FreeCAD.Vector(tapw, 0, obj.Length.Value - chamfer))
        if True:
            edge5 = Part.makeLine(FreeCAD.Vector(tapw, 0, obj.Length.Value - chamfer), FreeCAD.Vector(tapw - chamfer, 0, obj.Length.Value))
        else:
            edge5 = Part.Arc(FreeCAD.Vector(tapw, 0, obj.Length.Value - chamfer),
                         FreeCAD.Vector(tapw - chamfer2, 0, obj.Length.Value - chamfer2),
                         FreeCAD.Vector(tapw - chamfer, 0, obj.Length.Value)
                         ).toShape()
        edge6 = Part.makeLine(FreeCAD.Vector(tapw - chamfer, 0, obj.Length.Value), FreeCAD.Vector(0, 0, obj.Length.Value))
        w = Part.Wire([edge1, edge2, edge3, edge4, edge5, edge6])

        return w

class _FenceReinforcePost(ArchComponent.Component):
    def __init__(self, obj):
        ArchComponent.Component.__init__(self,obj)
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

    def onDocumentRestored(self,obj):

        ArchComponent.Component.onDocumentRestored(self,obj)
        self.setProperties(obj)

    def execute(self,obj):

        import Part,DraftGeomUtils,math
        pl = obj.Placement
        w = self.getWire(obj)

        try:
            #sh = w.makePipeShell([p], True, False, 2)
            sh = w.revolve(FreeCAD.Vector(0.0, 0.0, 0.0), FreeCAD.Vector(0.0, 0.0, 1.0), 360)
        except:
            FreeCAD.Console.PrintError(translate("Arch","Unable to build the pipe")+"\n")
        else:
            obj.Shape = sh
            obj.Placement = pl

    def getWire(self,obj):

        import Part
        sin45 = 0.707106781
        radio = obj.Diameter.Value / 2
        taph = 20
        tapw = radio + 2
        chamfer = 5
        chamfer2 = chamfer * sin45

        edge1 = Part.makeLine(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(radio, 0, 0))
        edge2 = Part.makeLine(FreeCAD.Vector(radio, 0, 0), FreeCAD.Vector(radio, 0, obj.Length.Value - taph))
        edge3 = Part.makeLine(FreeCAD.Vector(radio, 0, obj.Length.Value - taph), FreeCAD.Vector(tapw, 0, obj.Length.Value - taph))
        edge4 = Part.makeLine(FreeCAD.Vector(tapw, 0, obj.Length.Value - taph), FreeCAD.Vector(tapw, 0, obj.Length.Value - chamfer))

        if True:
            edge5 = Part.makeLine(FreeCAD.Vector(tapw, 0, obj.Length.Value - chamfer), FreeCAD.Vector(tapw - chamfer, 0, obj.Length.Value))
        else:
            edge5 = Part.Arc(FreeCAD.Vector(tapw, 0, obj.Length.Value - chamfer),
                         FreeCAD.Vector(tapw - chamfer2, 0, obj.Length.Value - chamfer2),
                         FreeCAD.Vector(tapw - chamfer, 0, obj.Length.Value)
                         ).toShape()
        edge6 = Part.makeLine(FreeCAD.Vector(tapw - chamfer, 0, obj.Length.Value), FreeCAD.Vector(0, 0, obj.Length.Value))
        w = Part.Wire([edge1, edge2, edge3, edge4, edge5, edge6])

        return w

class _ViewProviderFencePost(ArchComponent.ViewProviderComponent):


    "A View Provider for the Pipe object"

    def __init__(self,vobj):

        ArchComponent.ViewProviderComponent.__init__(self,vobj)

    def getIcon(self):

        import Arch_rc
        return ":/icons/Arch_Pipe_Tree.svg"

class _CommandFencePost:


    "the Arch Pipe command definition"

    def GetResources(self):

        return {'Pixmap'  : 'Arch_Pipe',
                'MenuText': QT_TRANSLATE_NOOP("Arch_Pipe","Pipe"),
                'Accel': "P, I",
                'ToolTip': QT_TRANSLATE_NOOP("Arch_Pipe","Creates a pipe object from a given Wire or Line")}

    def IsActive(self):

        return not FreeCAD.ActiveDocument is None

    def Activated(self):
        if True:
            makeFencePost()
        else:
            FreeCAD.ActiveDocument.openTransaction(translate("Arch","Create Pipe"))
            FreeCADGui.addModule("Arch")
            FreeCADGui.doCommand("obj = Arch.makePipe()")
            FreeCADGui.addModule("Draft")
            FreeCADGui.doCommand("Draft.autogroup(obj)")
            FreeCAD.ActiveDocument.commitTransaction()
        FreeCAD.ActiveDocument.recompute()


if FreeCAD.GuiUp:
    FreeCADGui.addCommand('FencePost', _CommandFencePost())

