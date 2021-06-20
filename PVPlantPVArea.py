import math
import FreeCAD, Draft
import ArchComponent

if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore, QtGui, QtSvg
    from DraftTools import translate
    from PySide.QtCore import QT_TRANSLATE_NOOP

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

__title__ = "FreeCAD Fixed Rack"
__author__ = "Javier Braña"
__url__ = "http://www.sogos-solar.com"
__dir__ = os.path.join(FreeCAD.getUserAppDataDir(), "Mod", "PVPlant")

DirResources = os.path.join(__dir__, "Resources")
DirIcons = os.path.join(DirResources, "Icons")
DirImages = os.path.join(DirResources, "Images")



def makeTree(objectslist=None, baseobj=None, name="Tree"):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Tree")
    _Tree(obj)
    _ViewProviderTree(obj.ViewObject)
    FreeCAD.ActiveDocument.recompute()
    return obj


class _Tree(ArchComponent.Component):
    "A Shadow Tree Obcject"

    def __init__(self, obj):
        # Definición de  variables:
        ArchComponent.Component.__init__(self, obj)
        self.setProperties(obj)
        self.obj = obj
        # Does a IfcType exist?
        # obj.IfcType = "Fence"
        # obj.MoveWithHost = False

    def setProperties(self, obj):
        # Definicion de Propiedades:
        ArchComponent.Component.setProperties(self, obj)

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = stat

    def onChanged(self, fp, prop):
        '''Do something when a property has changed'''
        FreeCAD.Console.PrintMessage("Change property: " + str(prop) + "\n")

    def execute(self, obj):
        print("  -----  TREE  -  EXECUTE  ----------")



class _ViewProviderPVArea(ArchComponent.ViewProviderComponent):
    "A View Provider for the Pipe object"

    def __init__(self, vobj):
        ArchComponent.ViewProviderComponent.__init__(self, vobj)

    def getIcon(self):
        return str(os.path.join(DirIcons, "tree(1).svg"))


class _PVAreaTaskPanel:

    def __init__(self):
        self.form = FreeCADGui.PySideUic.loadUi(__dir__ + "/PVPlantRack.ui")

        self.form = self.formRack

        # signals/slots
        # QtCore.QObject.connect(self.valueModuleLength,QtCore.SIGNAL("valueChanged(double)"),self.setModuleLength)
        # QtCore.QObject.connect(self.valueModuleWidth,QtCore.SIGNAL("valueChanged(double)"),self.setModuleWidth)
        # QtCore.QObject.connect(self.valueModuleHeight,QtCore.SIGNAL("valueChanged(double)"),self.setModuleHeight)
        # QtCore.QObject.connect(self.valueModuleFrame, QtCore.SIGNAL("valueChanged(double)"), self.setModuleFrame)
        # QtCore.QObject.connect(self.valueModuleColor, QtCore.SIGNAL("valueChanged(double)"), self.setModuleColor)
        # QtCore.QObject.connect(self.valueModuleGapX, QtCore.SIGNAL("valueChanged(double)"), self.setModuleGapX)
        # QtCore.QObject.connect(self.valueModuleGapY, QtCore.SIGNAL("valueChanged(double)"), self.setModuleGapY)

    def accept(self):
        FreeCADGui.Control.closeDialog()
        return True

    def reject(self):
        FreeCAD.ActiveDocument.removeObject(self.obj.Name)
        FreeCADGui.Control.closeDialog()
        return True


class _CommandPVArea:
    "the PVPlant Tree command definition"

    def GetResources(self):
        return {'Pixmap': str(os.path.join(DirIcons, "tree(1).svg")),
                'MenuText': QtCore.QT_TRANSLATE_NOOP("PVPlantTree", "Tree"),
                'Accel': "S, T",
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("PVPlanTree",
                                                    "Creates a Tree object from setup dialog.")}

    #def IsActive(self):
    #    return not FreeCAD.ActiveDocument is None

    def IsActive(self):
        if FreeCAD.ActiveDocument is not None:
            if FreeCADGui.Selection.getCompleteSelection():
                for o in FreeCAD.ActiveDocument.Objects:
                    if o.Name[:4] == "Site":
                        return True

        return False

    def Activated(self):
        task = _PVAreaTaskPanel()
        FreeCADGui.Control.showDialog(task)
        return


if FreeCAD.GuiUp:
    FreeCADGui.addCommand('PVArea', _CommandPVArea())