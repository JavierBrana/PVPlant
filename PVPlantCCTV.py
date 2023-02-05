
import FreeCAD
import ArchComponent
import PVPlantSite
import Part
import Draft

if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore, QtGui, QtSvg
    from DraftTools import translate
    from PySide.QtCore import QT_TRANSLATE_NOOP

else:
    # \cond
    def translate(ctxt, txt):
        return txt


    def QT_TRANSLATE_NOOP(ctxt, txt):
        return txt
    # \endcond

__title__ = "PVPlant Frames"
__author__ = "Javier Braña"
__url__ = "http://www.sogos-solar.com"

import os
import PVPlantResources
from PVPlantResources import DirIcons as DirIcons

def makePole(diameter=48, length=3000, placement=None, name="Post"):
    "makePipe([baseobj,diamerter,length,placement,name]): creates an pipe object from the given base object"

    if not FreeCAD.ActiveDocument:
        FreeCAD.Console.PrintError("No active document. Aborting\n")
        return

    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", name)
    obj.Label = name
    Poles(obj)

    if FreeCAD.GuiUp:
        ViewProviderPost(obj.ViewObject)

    if placement:
        obj.Placement = placement
    return obj

class Poles(ArchComponent.Component):
    "A Base Frame Obcject - Class"

    def __init__(self, obj):
        # Definición de Variables:
        ArchComponent.Component.__init__(self, obj)
        self.obj = obj
        self.setCommonProperties(obj)

        # Does a IfcType exist?
        obj.IfcType = "Structural Item"
        obj.setEditorMode("IfcType", 1)

        self.totalAreaShape = None
        self.changed = True

    def setCommonProperties(self, obj):
        # Definicion de Propiedades:
        ArchComponent.Component.setProperties(self, obj)

        pl = obj.PropertiesList

        if not "TopDiameter" in pl:
            obj.addProperty("App::PropertyLength",
                            "TopDiameter",
                            "Post",
                            QT_TRANSLATE_NOOP("App::Property", "The height of this object")
                            ).TopDiameter = 40

        if not "BottomDiameter" in pl:
            obj.addProperty("App::PropertyLength",
                            "BottomDiameter",
                            "Post",
                            QT_TRANSLATE_NOOP("App::Property", "The width of this object")
                            ).BottomDiameter = 60

        if not "Height" in pl:
            obj.addProperty("App::PropertyLength",
                            "Height",
                            "Post",
                            QT_TRANSLATE_NOOP("App::Property", "The Length of this object")
                            ).Height = 6000

        if not "BaseWidth" in pl:
            obj.addProperty("App::PropertyLength",
                            "BaseWidth",
                            "Post",
                            QT_TRANSLATE_NOOP("App::Property", "The Length of this object")
                            ).BaseWidth = 300

        if not "BaseHeight" in pl:
            obj.addProperty("App::PropertyLength",
                            "BaseHeight",
                            "Post",
                            QT_TRANSLATE_NOOP("App::Property", "The Length of this object")
                            ).BaseHeight = 6

        self.Type = "Post"

    def onChanged(self, obj, prop):
        ''''''

    def execute(self, obj):
        pl = obj.Placement

        base = Part.makeBox(obj.BaseWidth, obj.BaseWidth, obj.BaseHeight)
        base1 = Part.show(Part.makeSphere(45, FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 0, 1), 30, 90, 360))
        tube = Part.makeCone(obj.BottonDiameter / 2, obj.TopDiameter / 2, obj.Height)

        obj.Shape = base.fuse([base1, tube])
        obj.Placement = pl


class ViewProviderPost(ArchComponent.ViewProviderComponent):
    "A View Provider for the Pipe object"

    def __init__(self, vobj):
        ArchComponent.ViewProviderComponent.__init__(self, vobj)

    def getIcon(self):
        import Arch_rc
        return ":/icons/Arch_Pipe_Tree.svg"


class CommandMultiRowTracker:
    "the Arch Building command definition"

    def GetResources(self):
        return {'Pixmap': str(os.path.join(DirIcons, "solar-tracker.svg")),
                'MenuText': "Multi-row Tracker",
                'Accel': "R, M",
                'ToolTip': "Creates a multi-row Tracker object from trackers."}

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

        if FreeCAD.ActiveDocument is not None:
            if FreeCADGui.Selection.getCompleteSelection():
                for ob in FreeCAD.ActiveDocument.Objects:
                    if ob.Name[:4] == "Site":
                        return True

    def Activated(self):
        self.TaskPanel = _FixedRackTaskPanel()
        FreeCADGui.Control.showDialog(self.TaskPanel)
        return

if FreeCAD.GuiUp:
    class CommandRackGroup:

        def GetCommands(self):
            return tuple(['PVPlantFixedRack',
                          'PVPlantTracker'
                          ])

        def GetResources(self):
            return {'MenuText': QT_TRANSLATE_NOOP("", 'Rack Types'),
                    'ToolTip': QT_TRANSLATE_NOOP("", 'Rack Types')
                    }

        def IsActive(self):
            return not FreeCAD.ActiveDocument is None


    FreeCADGui.addCommand('PVPlantCreatePost', CommandFixedRack())